import xml.dom.minidom
import json

def parse_subsucriptions():
    with open("data/subscriptions.json") as f:
        subscriptions = json.load(f)

    subscriptions = {
        sub["adresses"][0]["valeur"]:{
            **sub, **{
                "uri":f"http://my-http-listener:8890/{sub['adresses'][0]['valeur']}"
            }
        } 
        for sub in subscriptions
    }
    return subscriptions

    

if __name__ == "__main__":
    with open("../data/9a009967-00f6-480c-aa70-78ffe52221fc.xml") as f:
        cisu = f.read()

    print(get_recipients_and_protocol_from_edxl_string(cisu))