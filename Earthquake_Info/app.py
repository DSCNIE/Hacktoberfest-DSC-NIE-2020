from flask import Flask, jsonify
import http.client
import mimetypes
import xml.etree.ElementTree as ET

app = Flask(__name__)

def fetch_from_bmkg():
    conn = http.client.HTTPSConnection("data.bmkg.go.id")
    payload = ''
    headers = {}
    conn.request("GET", "/autogempa.xml", payload, headers)
    res = conn.getresponse()
    data = res.read()
    
    root = ET.fromstring(data.decode("utf-8"))
    return root

def bmkg_parser(earthquake):
    return {
        'time': '{} {}'.format(earthquake[0][0].text, earthquake[0][1].text),
        'coordinates': earthquake[0][2][0].text,
        'depth': earthquake[0][6].text,
        'is_tsunami': True if 'tidak' not in earthquake[0][13].text.lower() else False,
        'source': 'Source: BMKG | Badan Meteorologi, Klimatologi, dan Geofisika https://www.bmkg.go.id/'
    }

@app.route('/')
def home():
    earthquake = bmkg_parser(fetch_from_bmkg())
    return jsonify(earthquake)

if __name__ == '__main__':
    app.run()