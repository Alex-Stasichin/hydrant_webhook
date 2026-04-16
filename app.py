from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

FEATURE_LAYER_URL = "https://gis.hempsteadwatermaps.com/server/rest/services/Hosted/Hydrant_Publishing_gdb/FeatureServer/0/applyEdits"
TOKEN = "YOUR_TOKEN_HERE"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    try:
        feature = data['feature']
        attrs = feature['attributes']

        hydrant_gid = attrs.get('hydrant_globalid')
        inservice_val = attrs.get('inservice_temp')

        if not hydrant_gid:
            return "Missing GlobalID", 400

        # Convert value
        if inservice_val == "Yes":
            inservice = 1
        elif inservice_val == "No":
            inservice = 0
        else:
            return "Invalid value", 400

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
