def fetch_epc_ratings(epc_url, reader):
    """
    Fetches current and potential EPC scores using the reader object.

    Args:
        epc_url (str): The URL of the EPC image or PDF.
        reader (object): An object with a `readtext(url)` method that returns a dict.

    Returns:
        tuple: (current_score, potential_score)
    """
    result = reader.readtext(epc_url)

    # Validate result structure
    if not isinstance(result, dict):
        raise ValueError("Expected result to be a dict")

    current = result.get("current")
    potential = result.get("potential")

    if not isinstance(current, (dict, int)) or not isinstance(potential, (dict, int)):
        raise ValueError("Missing or invalid EPC data")

    # Handle both detailed and simplified forms
    current_score = current["score"] if isinstance(current, dict) else current
    potential_score = potential["score"] if isinstance(potential, dict) else potential

    return current_score, potential_score
