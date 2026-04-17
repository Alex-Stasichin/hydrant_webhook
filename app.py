from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

FEATURE_LAYER_URL = "https://gis.hempsteadwatermaps.com/server/rest/services/Hosted/Hydrant_Publishing_gdb/FeatureServer/0/applyEdits"
TOKEN = os.environ.get("AGOL_TOKEN")  # store token securely

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    try:
        feature = data['feature']
        attrs = feature['attributes']

        print("ATTRIBUTES:", attrs)

        hydrant_gid = attrs.get('hydrant_globalid')
        inservice_val = str(attrs.get('inservice_temp'))

        print("inservice_val:", inservice_val)
      
        if not hydrant_gid:
            return "Missing GlobalID", 400

        # ensure correct GUID format
        if not hydrant_gid.startswith("{"):
            hydrant_gid = "{" + hydrant_gid + "}"

        # convert values
       if inservice_val == "0":
            inservice = 0   # Yes
        elif inservice_val == "1":
            inservice = 1   # No
        else:
            return f"Invalid value: {inservice_val}", 400

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

        return jsonify(r.json())

    except Exception as e:
        return str(e), 500


if __name__ == "__main__":
    app.run()
