import json

def extract_postcode_and_epc(html):
    # Look for the start of the adInfo object
    marker = "window.adInfo ="
    start_index = html.find(marker)
    if start_index == -1:
        print("Start marker not found.")
        return None

    # Find the start of JSON and track braces to extract it safely
    json_start = html.find("{", start_index)
    brace_depth = 0
    for i in range(json_start, len(html)):
        if html[i] == "{":
            brace_depth += 1
        elif html[i] == "}":
            brace_depth -= 1
            if brace_depth == 0:
                json_end = i + 1
                break
    else:
        print("Could not find end of JSON block.")
        return None

    json_str = html[json_start:json_end]

    try:
        data = json.loads(json_str)
        property_data = data.get("propertyData", {})
        address = property_data.get("address", {})
        outcode = address.get("outcode", "")
        incode = address.get("incode", "")
        postcode = f"{outcode} {incode}" if outcode and incode else None

        epc_graphs = property_data.get("epcGraphs", [])
        epc_url = epc_graphs[0]["url"] if epc_graphs else None

        return {
            "postcode": postcode,
            "epc_url": epc_url
        }

    except json.JSONDecodeError as e:
        print("JSON decoding error:", e)
        return None
