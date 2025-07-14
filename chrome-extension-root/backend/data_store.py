import json
import os

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_entry(entry):
    data = load_data()
    if not any(e["url"] == entry["url"] for e in data):
        data.append(entry)
        save_data(data)
        return True
    return False
