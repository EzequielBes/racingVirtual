# Test script to validate MoTeC export using integrated stm modules
import sys
import os
from datetime import datetime

# Add src directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from parsers.ldparser import ldData, ldChan, ldHead, ldEvent # Existing parser
from stm.motec.ld import MotecLog, MotecChannel, MotecEvent # Integrated exporter
import numpy as np

INPUT_LD_FILE = "/home/ubuntu/upload/misano-ferrari_296_gt3-6-2025.03.23-19.00.05.ld"
OUTPUT_LD_FILE = "/home/ubuntu/test_export.ld"

print(f"Reading input file: {INPUT_LD_FILE}")

try:
    # 1. Read input LD file using existing parser
    input_data = ldData.fromfile(INPUT_LD_FILE)
    print(f"Successfully read {len(input_data.channs)} channels from input file.")

    # Select channels to export (example)
    channels_to_export = ["SPEED", "THROTTLE", "BRAKE", "RPMS", "GEAR"]
    selected_channels_data = {}
    selected_channels_meta = {}

    print(f"Filtering for channels: {', '.join(channels_to_export)}")
    for channel_name in channels_to_export:
        try:
            channel_obj = input_data[channel_name]
            selected_channels_data[channel_name] = channel_obj.data
            selected_channels_meta[channel_name] = channel_obj
            print(f" - Found channel: {channel_name} ({len(channel_obj.data)} samples)")
        except Exception as e:
            print(f" - Warning: Could not find or read channel '{channel_name}': {e}")

    if not selected_channels_data:
        raise ValueError("No channels selected or found for export.")

    # 2. Create MotecLog object for export
    print("Creating MotecLog object for export...")
    export_log = MotecLog()

    # Copy header info (basic example)
    export_log.driver = input_data.head.driver
    export_log.vehicle = input_data.head.vehicleid
    export_log.venue = input_data.head.venue
    export_log.comment = input_data.head.short_comment
    export_log.date = input_data.head.datetime.strftime("%d/%m/%Y")
    export_log.time = input_data.head.datetime.strftime("%H:%M:%S")

    # Create event (if available)
    if input_data.head.event:
        export_log.event = MotecEvent({
            "name": input_data.head.event.name,
            "session": input_data.head.event.session,
            "comment": input_data.head.event.comment,
            "venuepos": 0 # Venue pointer needs careful handling, setting to 0 for now
        })

    # 3. Define MotecChannel objects for selected channels
    print("Defining MotecChannel objects...")
    channel_id_counter = 0 # Initialize channel ID counter
    for name, meta in selected_channels_meta.items():
        channel_id_counter += 1 # Increment ID for each channel
        # Map data types (approximation)
        if meta.dtype == np.float32:
            motec_datatype = 0x0007
            motec_datasize = 4
        elif meta.dtype == np.float16:
            motec_datatype = 0x0007
            motec_datasize = 2
        elif meta.dtype == np.int32:
            motec_datatype = 0x0005
            motec_datasize = 4
        elif meta.dtype == np.int16:
            motec_datatype = 0x0003
            motec_datasize = 2
        else:
            print(f" - Warning: Unsupported dtype {meta.dtype} for channel {name}. Skipping.")
            continue

        channel_state = {
            "id": channel_id_counter, # Add the channel ID
            "name": meta.name,
            "shortname": meta.short_name,
            "units": meta.unit,
            "freq": meta.freq,
            "shift": meta.shift,
            "multiplier": meta.mul,
            "scale": meta.scale,
            "decplaces": meta.dec,
            "datatype": motec_datatype,
            "datasize": motec_datasize,
            # Pointers (prevpos, nextpos, datapos) will be calculated by MotecLog.to_string()
        }
        export_channel = MotecChannel(channel_state)

        # 4. Add sample data
        print(f" - Adding {len(selected_channels_data[name])} samples for {name}")
        export_channel.samples.samples = selected_channels_data[name] # Directly assign numpy array

        export_log.add_channel(export_channel)

    if not export_log.channels:
        raise ValueError("No valid channels were prepared for export.")

    # 5. Write the MotecLog to the output file
    print(f"Writing output file: {OUTPUT_LD_FILE}")
    output_bytes = export_log.to_string()

    with open(OUTPUT_LD_FILE, "wb") as f_out:
        f_out.write(output_bytes)

    print("MoTeC export test completed successfully.")

except Exception as e:
    print(f"Error during MoTeC export test: {e}")
    import traceback
    traceback.print_exc()


