import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

FEATURE_LAYER_URL = os.environ.get("FEATURE_LAYER_URL")  # hydrant layer /applyEdits
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

        # convert to int just in case
        inservice = int(inservice_val)

        payload = {
            "f": "json",
            "updates": [{
                "attributes": {
                    "globalid": hydrant_gid,
                    "inservice": inservice
                }
            }],
            "token": TOKEN
        }

        r = requests.post(FEATURE_LAYER_URL, data=payload)

        print("ArcGIS response:", r.text)

        return jsonify(r.json())

    except Exception as e:
        return str(e), 500
