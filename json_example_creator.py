import json
import random
from datetime import datetime, timedelta

OUTPUT_FILE = "random_noise_data.json"
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


def main():
    data = []
    current_time = START_TIME

    for _ in range(TOTAL_ENTRIES):
        data.append(generate_record(current_time))
        current_time += INTERVAL

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=4)

    print(f"✅ Generated {TOTAL_ENTRIES} records in {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
