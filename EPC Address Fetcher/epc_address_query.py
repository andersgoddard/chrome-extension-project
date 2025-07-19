import requests
from requests.auth import HTTPBasicAuth

def query_epc_by_postcode_and_rating(postcode, current_rating, potential_rating, username, api_key):
    url = "https://epc.opendatacommunities.org/api/v1/domestic/search"
    headers = {
        "Accept": "application/json"
    }
    params = {
        "postcode": postcode,
        "size": 5000,   # Maximum results per page
        "page": 0       # First page (pagination starts at 0)
    }

    response = requests.get(url, headers=headers, params=params, auth=HTTPBasicAuth(username, api_key))

    if response.status_code != 200:
        print(f"Error: {response.status_code} — {response.text}")
        return []

    data = response.json()
    records = data.get("rows", [])

    # Filter results
    matching = [
        r for r in records
        if r.get("current-energy-efficiency") == str(current_rating)
        and r.get("potential-energy-efficiency") == str(potential_rating)
    ]

    return matching
