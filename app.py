import os
from flask import Flask, request, jsonify
from arcgis.gis import GIS

app = Flask(__name__)

USERNAME = os.environ.get("AGOL_USERNAME")
PASSWORD = os.environ.get("AGOL_PASSWORD")
ITEM_ID = os.environ.get("HYDRANT_ITEM_ID")

#checking to see if its actually working
print(USERNAME)
print(ITEM_ID)

# enterprise portal
gis = GIS("https://gis.hempsteadwatermaps.com/portal", USERNAME, PASSWORD)

layer = gis.content.get(ITEM_ID).layers[0]

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    try:
        feature = data['feature']
        attrs = feature['attributes']

        hydrant_gid = attrs.get('hydrant_globalid')

        if hydrant_gid and not hydrant_gid.startswith("{"):
            hydrant_gid = "{" + hydrant_gid + "}"
            
        inservice_val = attrs.get('inservice_temp')

        if not hydrant_gid:
            return "Missing GlobalID", 400

        if inservice_val == "Yes":
            inservice = 1
        elif inservice_val == "No":
            inservice = 0
        else:
            return "Invalid value", 400

        layer.edit_features(updates=[{
            "attributes": {
                "globalid": hydrant_gid,
                "inservice": inservice
            }
        }])

        return jsonify({"status": "success"})

    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run()
