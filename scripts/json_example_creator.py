import json
import random
from datetime import datetime, timedelta

OUTPUT_FILE = "test_data_n5.json"
START_TIME = datetime(2025, 12, 5, 0, 0, 0)
INTERVAL = timedelta(minutes=2)
TOTAL_ENTRIES = 24 * 60 // 2  # 720 records

LABEL_POOL = [
    "Vehicle", "Engine", "Car", "Wind", "Rain",
    "Human speech", "Silence", "Footsteps",
    "Bird", "Fan", "AC", "Construction", "Traffic"
]

def random_rating(db):
    if db < 30:
        return "A"
    elif db < 40:
        return "B"
    elif db < 50:
        return "C"
    elif db < 60:
        return "D"
    elif db < 70:
        return "E"
    else:
        return "F"


def generate_record(timestamp):
    laeq = round(random.uniform(25, 85), 2)
    labels = random.sample(LABEL_POOL, k=5)

    return {
        "box_id": "pi4",
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "LAeq_segment_dB": laeq,
        "LAeq_rating": random_rating(laeq),
        "top_5_labels": labels
    }



def generate_random_records(output_path, start_time, total_entries, interval):
    data = []
    current_time = start_time

    for _ in range(total_entries):
        data.append(generate_record(current_time))
        current_time += interval

    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)

    return {
        "message": "Random data generated",
        "records": len(data),
        "output_file": output_path
    }

