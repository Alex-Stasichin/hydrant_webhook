import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

FEATURE_LAYER_URL = os.environ.get("FEATURE_LAYER_URL")  # must end in /applyEdits
TOKEN = os.environ.get("AGOL_TOKEN")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    try:
        feature = data['feature']
        attrs = feature['attributes']

        print("ATTRIBUTES:", attrs)

        hydrant_gid = attrs.get('hydrant_globalid')
        inservice_val = attrs.get('inservice')

        print("hydrant_gid:", hydrant_gid)
        print("inservice_val:", inservice_val)

        if not hydrant_gid:
            return "Missing hydrant_globalid", 400

        if inservice_val is None:
            return "Missing inservice value", 400

        # ensure GUID format
        if not hydrant_gid.startswith("{"):
            hydrant_gid = "{" + hydrant_gid + "}"

        # convert to int
        inservice = int(inservice_val)

        # -----------------------------------
        # STEP 1: QUERY for OBJECTID
        # -----------------------------------
        query_url = FEATURE_LAYER_URL.replace("/applyEdits", "/query")

        query_params = {
            "f": "json",
            "where": f"globalid='{hydrant_gid}'",
            "outFields": "OBJECTID",
            "returnGeometry": "false",
            "token": TOKEN
        }

        query_response = requests.get(query_url, params=query_params)
        query_json = query_response.json()

        print("Query response:", query_json)

        features = query_json.get("features")

        if not features:
            return "Hydrant not found", 404

        objectid = features[0]["attributes"]["OBJECTID"]

        print("OBJECTID:", objectid)

        # -----------------------------------
        # STEP 2: UPDATE using OBJECTID
        # -----------------------------------
        payload = {
            "f": "json",
            "updates": [{
                "attributes": {
                    "OBJECTID": objectid,
                    "inservice": inservice
                }
            }],
            "token": TOKEN
        }

        r = requests.post(FEATURE_LAYER_URL, data=payload)

        print("ArcGIS response:", r.text)

        return jsonify(r.json())

    except Exception as e:
        print("ERROR:", str(e))
        return str(e), 500


if __name__ == "__main__":
    app.run()
