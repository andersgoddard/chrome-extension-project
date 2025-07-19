from flask import Flask, request, jsonify
from flask_cors import CORS
from data_store import add_entry, load_data

app = Flask(__name__)
CORS(app)

@app.route("/add-rightmove", methods=["POST"])
def add_rightmove():
    data = request.get_json()
    required = {"url", "postcode", "epc_url"}

    if not data or not required.issubset(data.keys()):
        return jsonify({"error": "Missing fields"}), 400

    entry = {
        "url": data["url"],
        "postcode": data["postcode"],
        "epc_url": data["epc_url"],
        "consumed": False
    }

    added = add_entry(entry)
    return jsonify({"status": "ok" if added else "duplicate"})

@app.route("/entries", methods=["GET"])
def get_entries():
    return jsonify(load_data())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0")
