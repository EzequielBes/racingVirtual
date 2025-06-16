# Script to list channel names from an LD file
import sys
import os

# Add src directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from parsers.ldparser import ldData

LD_FILE = "/home/ubuntu/upload/misano-ferrari_296_gt3-6-2025.03.23-19.00.05.ld"

print(f"Listing channels from: {LD_FILE}")

try:
    ld_data = ldData.fromfile(LD_FILE)
    print("Available channels:")
    for i, channel in enumerate(ld_data.channs):
        print(f"  {i+1}. {channel.name} (Short: {channel.short_name}, Unit: {channel.unit}, Freq: {channel.freq}Hz)")
except Exception as e:
    print(f"Error reading LD file: {e}")

