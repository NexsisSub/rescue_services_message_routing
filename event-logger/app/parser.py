import xmltodict
import json 

def parse_xml_string_to_dict(xml_string):
    data_dict = xmltodict.parse(xml_string)
    return json.loads(json.dumps(data_dict))