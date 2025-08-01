import json
import threading
from typing import List

DATA_FILE = "data.json"
lock = threading.Lock()

def load_data() -> List[dict]:
    with lock:
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

def save_data(data: List[dict]):
    with lock:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)

def add_entry(entry: dict) -> bool:
    data = load_data()

    # Avoid duplicates
    if any(e["url"] == entry["url"] for e in data):
        return False

    # Set defaults for required fields
    entry.setdefault("steps", {
        "epc_url_extracted": True,
        "epc_ratings_fetched": False,
        "epc_address_fetched": False,
        "completed": False
    })

    entry.setdefault("current", None)
    entry.setdefault("potential", None)
    entry.setdefault("address_results", [])

    data.append(entry)
    save_data(data)
    return True

def update_entry_data(url: str, key: str, value):
    data = load_data()
    for entry in data:
        if entry["url"] == url:
            entry[key] = value
            break
    save_data(data)

def update_step_flag(url: str, step_name: str, value=True):
    data = load_data()
    for entry in data:
        if entry["url"] == url:
            if "steps" not in entry:
                entry["steps"] = {}
            entry["steps"][step_name] = value
            break
    save_data(data)
