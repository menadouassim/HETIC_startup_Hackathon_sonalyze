import json
from datetime import datetime, timedelta

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


def main():
    with open(INPUT_FILE, "r") as f:
        data = json.load(f)

    result = sample_every_2_minutes(data)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(result, f, indent=4)

    print(f"Done ✅ {len(result)} records saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
