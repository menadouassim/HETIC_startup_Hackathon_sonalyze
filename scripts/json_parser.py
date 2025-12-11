import json
from datetime import datetime, timedelta
import os
INPUT_FILE = "original.json"
OUTPUT_FILE = "sampled_2min.json"

FIELDS = ["box_id", "LAeq_segment_dB", "LAeq_rating", "top_5_labels"]
INTERVAL = timedelta(minutes=2)


def parse_time(ts):
    return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")


def filter_fields(entry):
    return {k: entry.get(k) for k in FIELDS}


def sample_every_2_minutes(data):
    sampled = []
    last_kept_time = None

    for entry in data:
        current_time = parse_time(entry["timestamp"])

        if last_kept_time is None or (current_time - last_kept_time) >= INTERVAL:
            sampled.append(filter_fields(entry))
            last_kept_time = current_time

    return sampled



def process_and_sample_folder(input_folder="data/rooms", output_folder="exports/parsed_json"):
    # Make sure output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    results_summary = []

    # Loop through all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            # Load the file
            with open(input_path, "r") as f:
                data = json.load(f)

            # Process / sample every 2 minutes
            result = sample_every_2_minutes(data)

            # Save the result
            with open(output_path, "w") as f:
                json.dump(result, f, indent=4)

            # Add summary
            results_summary.append({
                "file": filename,
                "records": len(result),
                "output_file": output_path
            })

    return {
        "message": "Done",
        "processed_files": len(results_summary),
        "details": results_summary
    }

process_and_sample_folder()