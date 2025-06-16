"""
Core module for calculating advanced racing metrics from telemetry data.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)

# --- Consistency Metrics --- 

def calculate_lap_time_consistency(lap_times: List[float], outlier_threshold_std: float = 2.0) -> Dict[str, Optional[float]]:
    """Calculates lap time consistency metrics (average, std dev, consistency index).
    
    Args:
        lap_times: List of lap times in seconds.
        outlier_threshold_std: Standard deviation multiplier to identify outliers.
                                Set to 0 or None to disable outlier removal.

    Returns:
        Dictionary containing: 'average_lap_time', 'std_dev', 'consistency_index', 
        'valid_laps_count', 'outlier_laps_count'. Returns None for values if calculation fails.
    """
    if not lap_times or len(lap_times) < 2:
        logger.warning("Not enough lap times for consistency calculation.")
        return {
            "average_lap_time": None,
            "std_dev": None,
            "consistency_index": None, # Lower is better
            "valid_laps_count": len(lap_times) if lap_times else 0,
            "outlier_laps_count": 0
        }

    laps_array = np.array(lap_times)
    valid_laps = laps_array
    outlier_count = 0

    # Outlier removal (optional)
    if outlier_threshold_std and outlier_threshold_std > 0 and len(laps_array) > 2:
        mean = np.mean(laps_array)
        std = np.std(laps_array)
        lower_bound = mean - outlier_threshold_std * std
        upper_bound = mean + outlier_threshold_std * std
        
        valid_mask = (laps_array >= lower_bound) & (laps_array <= upper_bound)
        valid_laps = laps_array[valid_mask]
        outlier_count = len(laps_array) - len(valid_laps)
        logger.info(f"Outlier removal: {outlier_count} laps removed (Threshold: {outlier_threshold_std} std dev). Bounds: [{lower_bound:.3f}, {upper_bound:.3f}]")
        
        if len(valid_laps) < 2:
            logger.warning("Not enough valid laps remaining after outlier removal.")
            # Fallback to using all laps if outlier removal leaves too few
            valid_laps = laps_array 
            outlier_count = 0 

    try:
        avg_time = np.mean(valid_laps)
        std_dev = np.std(valid_laps)
        # Consistency Index: Standard deviation as a percentage of the average time
        consistency_index = (std_dev / avg_time) * 100 if avg_time > 0 else 0
        
        logger.info(f"Consistency calculated: Avg={avg_time:.3f}s, StdDev={std_dev:.3f}s, Index={consistency_index:.2f}% ({len(valid_laps)} valid laps)")
        
        return {
            "average_lap_time": avg_time,
            "std_dev": std_dev,
            "consistency_index": consistency_index,
            "valid_laps_count": len(valid_laps),
            "outlier_laps_count": outlier_count
        }
    except Exception as e:
        logger.error(f"Error calculating consistency: {e}", exc_info=True)
        return {
            "average_lap_time": None,
            "std_dev": None,
            "consistency_index": None,
            "valid_laps_count": len(valid_laps),
            "outlier_laps_count": outlier_count
        }

# --- Histogram Data --- 

def generate_histogram_data(data_series: List[float], bins: int = 10) -> Optional[Tuple[np.ndarray, np.ndarray]]:
    """Generates data for plotting a histogram.

    Args:
        data_series: List of numerical data points (e.g., speeds, brake pressures).
        bins: Number of bins for the histogram.

    Returns:
        Tuple containing (histogram_counts, bin_edges), or None if error.
    """
    if not data_series:
        logger.warning("Cannot generate histogram from empty data series.")
        return None
        
    try:
        counts, bin_edges = np.histogram(data_series, bins=bins)
        logger.info(f"Histogram data generated with {bins} bins.")
        return counts, bin_edges
    except Exception as e:
        logger.error(f"Error generating histogram data: {e}", exc_info=True)
        return None

# --- Reaction Time (Placeholder - Highly Dependent on Data Availability) --- 

def calculate_reaction_time(events: List[Dict[str, Any]]) -> Optional[float]:
    """Placeholder for reaction time calculation.
    
    Requires specific event data (e.g., light change time, throttle/clutch input time)
    which might not be available in standard telemetry.
    """
    logger.warning("Reaction time calculation requires specific event data (e.g., start lights) which is not implemented.")
    # Example logic if data existed:
    # start_signal_time = find_event_time(events, "StartSignalOn")
    # first_input_time = find_event_time(events, ["ThrottleInput", "ClutchInput"])
    # if start_signal_time and first_input_time:
    #     return first_input_time - start_signal_time
    return None

# --- Sector Analysis (Helper for Training Plan) --- 

def analyze_sector_times(all_laps_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """Analyzes sector times across multiple laps to find averages, bests, and consistency.
    
    Args:
        all_laps_data: List of dictionaries, where each dict represents a lap 
                       and contains a 'sectors' key with a list of sector times.
                       Example: [{'lap_number': 1, 'sectors': [30.1, 45.2, 28.5]}, ...]

    Returns:
        Dictionary keyed by sector index (str), containing 'average_time', 
        'best_time', 'std_dev' for each sector.
    """
    if not all_laps_data or not all_laps_data[0].get("sectors"):
        logger.warning("Insufficient data for sector time analysis.")
        return {}

    num_sectors = len(all_laps_data[0]["sectors"])
    sector_times_by_index = defaultdict(list)

    # Collect times for each sector across all laps
    for lap in all_laps_data:
        if len(lap.get("sectors", [])) == num_sectors:
            for i, sector_time in enumerate(lap["sectors"]):
                sector_times_by_index[str(i + 1)].append(sector_time)
        else:
            logger.warning(f"Lap {lap.get("lap_number", "N/A")} has inconsistent number of sectors. Skipping.")

    sector_analysis = {}
    for sector_idx, times in sector_times_by_index.items():
        if len(times) >= 2:
            times_arr = np.array(times)
            sector_analysis[sector_idx] = {
                "average_time": np.mean(times_arr),
                "best_time": np.min(times_arr),
                "std_dev": np.std(times_arr),
                "consistency_index": (np.std(times_arr) / np.mean(times_arr)) * 100 if np.mean(times_arr) > 0 else 0
            }
        elif len(times) == 1:
             sector_analysis[sector_idx] = {
                "average_time": times[0],
                "best_time": times[0],
                "std_dev": 0.0,
                "consistency_index": 0.0
            }
        else:
            sector_analysis[sector_idx] = {"average_time": None, "best_time": None, "std_dev": None, "consistency_index": None}
            
    logger.info(f"Sector analysis complete for {len(sector_analysis)} sectors.")
    return sector_analysis

# --- Main Function to Calculate All Metrics --- 

def calculate_all_advanced_metrics(telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculates a suite of advanced metrics from the parsed telemetry data.
    
    Args:
        telemetry_data: The dictionary containing parsed data (beacons, details, potentially full lap data).

    Returns:
        Dictionary containing calculated metrics.
    """
    logger.info("Calculating all advanced metrics...")
    metrics = {}
    
    # --- Lap Time Consistency --- 
    beacons = telemetry_data.get("beacons", [])
    lap_times = []
    if len(beacons) >= 2:
        for i in range(len(beacons) - 1):
            lap_time = beacons[i+1]["time"] - beacons[i]["time"]
            lap_times.append(lap_time)
            
    metrics["lap_time_consistency"] = calculate_lap_time_consistency(lap_times)
    
    # --- Sector Analysis --- 
    # Requires lap data with sector times - Placeholder for now
    # Assuming telemetry_data might have a 'laps' list in the future:
    # all_laps = telemetry_data.get("laps", []) 
    # metrics["sector_analysis"] = analyze_sector_times(all_laps)
    metrics["sector_analysis"] = {} # Placeholder
    logger.warning("Sector time analysis requires detailed lap data structure (not yet implemented).")

    # --- Histograms --- 
    # Requires full data series (e.g., speed per point) - Placeholder
    # Assuming telemetry_data might have 'full_data' with 'Speed' channel:
    # speed_data = telemetry_data.get("full_data", {}).get("Speed", [])
    # metrics["speed_histogram"] = generate_histogram_data(speed_data, bins=20)
    metrics["speed_histogram"] = None # Placeholder
    logger.warning("Histogram generation requires full data channels (not yet implemented).")

    # --- Reaction Time --- 
    metrics["reaction_time"] = calculate_reaction_time([]) # Placeholder

    logger.info("Advanced metrics calculation finished.")
    return metrics

# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Dummy data similar to parsed LDX, but needs more detail for full metrics
    dummy_data = {
        "beacons": [
            {"time": 0.1, "name": "0, id=99", "lap_index": 0},
            {"time": 110.5, "name": "1, id=99", "lap_index": 1}, # Lap 1: 110.4s
            {"time": 228.0, "name": "2, id=99", "lap_index": 2}, # Lap 2: 117.5s
            {"time": 335.2, "name": "3, id=99", "lap_index": 3}, # Lap 3: 107.2s
            {"time": 446.1, "name": "4, id=99", "lap_index": 4}, # Lap 4: 110.9s
            {"time": 560.0, "name": "5, id=99", "lap_index": 5}  # Lap 5: 113.9s
        ],
        "details": {"Total Laps": 5, "Fastest Lap": 3, "Fastest Time": 107.2},
        "metadata": {"format": "ldx_xml"}
        # Missing: Detailed lap data with sector times, full data channels (speed, brake etc.)
    }
    
    calculated_metrics = calculate_all_advanced_metrics(dummy_data)
    
    print("\n--- Calculated Metrics ---")
    import json
    print(json.dumps(calculated_metrics, indent=4, default=str)) # Use default=str for numpy arrays if any

