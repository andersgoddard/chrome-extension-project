import os
import threading
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

from data_store import add_entry, load_data, update_step_flag, update_entry_data
from epc_rating_reader.epc_rating_reader import fetch_epc_ratings
from epc_rating_reader.ocr_engine_loader import OCREngine
from epc_address_fetcher.epc_address_query import query_epc_by_postcode_and_rating

app = Flask(__name__)
CORS(app, origins=["https://www.rightmove.co.uk"], supports_credentials=True)

def load_epc_register_credentials(file_path="epc_address_fetcher/epc_cred.txt"):
    creds = {}
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                creds[key.strip()] = value.strip()
    return creds["username"], creds["api_key"]

@app.route("/add-rightmove", methods=["POST", "OPTIONS"])
def add_rightmove():
    if request.method == 'OPTIONS':
        return '', 204

    data = request.get_json()
    required = {"url", "postcode", "epc_url"}

    if not data or not required.issubset(data.keys()):
        return jsonify({"error": "Missing fields"}), 400

    entry = {
        "url": data["url"],
        "postcode": data["postcode"],
        "epc_url": data["epc_url"]
    }

    added = add_entry(entry)
    return jsonify({"status": "ok" if added else "duplicate"})

@app.route("/entries", methods=["GET"])
def get_entries():
    return jsonify(load_data())

def epc_background_worker(poll_interval=20):
    reader = OCREngine()
    epc_register_username, epc_register_api_key = load_epc_register_credentials()

    while True:
        time.sleep(poll_interval)
        try:
            entries = load_data()
            for entry in entries:
                url = entry["url"]
                steps = entry.get("steps", {})

                # Step 2: Read EPC ratings if not done
                if steps.get("epc_url_extracted", False) and not steps.get("epc_ratings_fetched", False):
                    try:
                        current, potential = fetch_epc_ratings(entry["epc_url"], reader)
                        update_entry_data(url, "current", current)
                        update_entry_data(url, "potential", potential)
                        update_step_flag(url, "epc_ratings_fetched", True)
                        print(f"[INFO] EPC ratings fetched for {url}")
                    except Exception as e:
                        update_step_flag(url, "epc_ratings_fetched", True)
                        print(f"[ERROR] EPC read failed for {url}: {e}")

                # Step 3: Fetch full addresses
                if steps.get("epc_ratings_fetched", False) and not steps.get("epc_address_fetched", False):
                    try:
                        addresses = query_epc_by_postcode_and_rating(
                            entry["postcode"],
                            entry.get("current"),
                            entry.get("potential"),
                            epc_register_username, 
                            epc_register_api_key
                        )
                        
                        matches = []
                        for r in addresses:
                            address_parts = [
                                r.get("address"),
                                r.get("postcode")
                            ]
                            full_address = ", ".join(part for part in address_parts if part and part.strip())

                            matches.append({
                                "address": full_address,
                                "current_rating": r.get("current-energy-efficiency"),
                                "potential_rating": r.get("potential-energy-efficiency")
                            })

                        update_entry_data(url, "address_results", matches)
                        update_step_flag(url, "epc_address_fetched", True)
                        print(f"[INFO] Addresses fetched for {url}")
                    except Exception as e:
                        print(f"[ERROR] Addresses fetch failed for {url}: {e}")

                # Step 4: Mark complete
                if steps.get("epc_address_fetched", False) and not steps.get("completed", False):
                    update_step_flag(url, "completed", True)
                    print(f"[INFO] Record complete for {url}")

        except Exception as outer:
            print(f"[ERROR] EPC worker error: {outer}")

if __name__ == "__main__":
    threading.Thread(target=epc_background_worker, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
