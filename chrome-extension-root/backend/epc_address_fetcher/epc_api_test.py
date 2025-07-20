import pandas as pd
import json
from epc_address_query import query_epc_by_postcode_and_rating

def load_credentials(file_path="epc_cred.txt"):
    creds = {}
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                creds[key.strip()] = value.strip()
    return creds["username"], creds["api_key"]


username, api_key = load_credentials()
input_file = "input_ratings.xlsx"
output_file = "epc_results.json"

df = pd.read_excel(input_file)

all_outputs = []

for idx, row in df.iterrows():
    postcode = str(row["postcode"]).strip()
    current = int(row["current_rating"])
    potential = int(row["potential_rating"])

    results = query_epc_by_postcode_and_rating(postcode, current, potential, username, api_key)

    matches = []
    for r in results:
        address_parts = [
            r.get("address"),
            r.get("town"),
            r.get("local-authority-label"),
            r.get("postcode")
        ]
        full_address = ", ".join(part for part in address_parts if part and part.strip())

        matches.append({
            "address": full_address,
            "current_rating": r.get("current-energy-efficiency"),
            "potential_rating": r.get("potential-energy-efficiency")
        })

    all_outputs.append({
        "input_postcode": postcode,
        "input_current_rating": current,
        "input_potential_rating": potential,
        "matches": matches
    })

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_outputs, f, indent=2)

print(f"✅ Results written to {output_file}")
