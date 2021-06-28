import xmltodict
import json 

def parse_xml_file_to_dict(filename):
    with open(filename) as xml_file:
        data_dict = xmltodict.parse(xml_file.read())
    return json.loads(json.dumps(data_dict))

def parse_xml_string_to_dict(xml_string):
    data_dict = xmltodict.parse(xml_string)
    return json.loads(json.dumps(data_dict))

if __name__ == "__main__":

    print(parse_xml_file_to_dict("../data/9a009967-00f6-480c-aa70-78ffe52221fc.xml"))