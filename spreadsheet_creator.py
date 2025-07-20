import json
import pandas as pd

# Load JSON data
with open("results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Lists for each sheet
no_address_data = []
address_data = []

for entry in data:
    url = entry.get("url")
    postcode = entry.get("postcode")
    addresses = entry.get("address_results", [])

    if not addresses:
        no_address_data.append({"url": url, "postcode": postcode})
    else:
        num_addresses = len(addresses)
        for addr in addresses:
            address_data.append({
                "address": addr.get("address"),
                "url": url,
                "num_addresses_for_url": num_addresses
            })

# Create DataFrames
df_no_address = pd.DataFrame(no_address_data)
df_address = pd.DataFrame(address_data)

# Write to Excel
with pd.ExcelWriter("epc_results.xlsx", engine="xlsxwriter") as writer:
    df_no_address.to_excel(writer, sheet_name="no_address_found", index=False)
    df_address.to_excel(writer, sheet_name="address_found", index=False)

print("epc_results.xlsx created successfully.")
