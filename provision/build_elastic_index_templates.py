import requests
import json


protocols = ["emsi", "cisu"]
for protocol in protocols:

    url = f"http://elasticsearch:9200/_index_template/template_{protocol}"

    with open(f"elasticsearch/templates/{protocol}.json") as f:
        payload = json.load(f)

    headers = {
        'Content-Type': "application/json",
        'cache-control': "no-cache",
    }

    response = requests.request("PUT", url, json=payload, headers=headers)
    print(response.json())