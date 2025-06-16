import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
import re

def _parse_time(time_str: Optional[str]) -> Optional[float]:
    """Converts MoTeC time string (like 1.654e+08) to seconds."""
    if time_str is None:
        return None
    try:
        # Time seems to be in nanoseconds from some epoch?
        # For delta calculation, the absolute value might not matter as much as the difference.
        # Let's treat it as a high-resolution timestamp for now.
        return float(time_str) / 1e9 # Convert to seconds assuming nanoseconds
    except (ValueError, TypeError):
        return None

def _parse_lap_time(time_str: Optional[str]) -> Optional[float]:
    """Converts MoTeC lap time string (like 1:49.837) to seconds."""
    if time_str is None:
        return None
    match = re.match(r"(?:(\d+):)?(\d{1,2})\.(\d{3})", time_str)
    if match:
        minutes = int(match.group(1)) if match.group(1) else 0
        seconds = int(match.group(2))
        milliseconds = int(match.group(3))
        return float(minutes * 60 + seconds + milliseconds / 1000)
    return None

def parse_ldx_xml(filepath: str) -> Dict[str, Any]:
    """Parses an LDX XML file and extracts beacon and session details."""
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except ET.ParseError as e:
        raise ValueError(f"Failed to parse XML file {filepath}: {e}")
    except FileNotFoundError:
        raise FileNotFoundError(f"LDX file not found: {filepath}")

    results: Dict[str, Any] = {
        "beacons": [],
        "details": {},
        "metadata": {
            "format": "ldx_xml",
            "version": root.get("Version"),
            "locale": root.get("Locale")
        }
    }

    # Extract Beacons (Lap Markers)
    beacons = []
    for marker in root.findall(".//Layer/MarkerBlock/MarkerGroup[@Name=\"Beacons\"]/Marker"):
        beacon_time_str = marker.get("Time")
        beacon_time = _parse_time(beacon_time_str)
        beacon_name = marker.get("Name") # e.g., "0, id=99"
        lap_number = None
        if beacon_name:
            match = re.match(r"(\d+),", beacon_name)
            if match:
                try:
                    # Lap number seems to be 0-indexed in the name, adjust to 1-indexed?
                    # Or maybe it's just an index. Let's keep it as is for now.
                    lap_number = int(match.group(1))
                except ValueError:
                    pass 
                    
        if beacon_time is not None:
            beacons.append({
                "time": beacon_time,
                "name": beacon_name,
                "lap_index": lap_number # Store the index found in the name
            })
            
    # Sort beacons by time just in case they are out of order
    results["beacons"] = sorted(beacons, key=lambda x: x["time"])

    # Extract Details
    details = {}
    for detail in root.findall(".//Layers/Details/String"):
        detail_id = detail.get("Id")
        detail_value = detail.get("Value")
        if detail_id and detail_value:
            # Try to convert known numeric/time values
            if detail_id == "Total Laps":
                try: details[detail_id] = int(detail_value)
                except ValueError: details[detail_id] = detail_value
            elif detail_id == "Fastest Lap":
                try: details[detail_id] = int(detail_value)
                except ValueError: details[detail_id] = detail_value
            elif detail_id == "Fastest Time":
                details[detail_id] = _parse_lap_time(detail_value)
                details[detail_id + "_str"] = detail_value # Keep original string too
            else:
                details[detail_id] = detail_value
                
    results["details"] = details

    return results

# Example Usage (for testing)
if __name__ == "__main__":
    # Create a dummy XML file for testing if needed, or use a real one
    # test_file = "/path/to/your/test.ldx"
    # try:
    #     parsed = parse_ldx_xml(test_file)
    #     import json
    #     print(json.dumps(parsed, indent=2))
    # except Exception as e:
    #     print(f"Error: {e}")
    pass

