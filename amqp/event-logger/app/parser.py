import xmltodict
import json 
import xml.dom.minidom


def get_xml_from_tag_name(xml, tag):
    return xml.getElementsByTagName(tag)

def parse_xml_file_to_dict(filename):
    with open(filename) as xml_file:
        data_dict = xmltodict.parse(xml_file.read())
    return json.loads(json.dumps(data_dict))


def parse_xml_string_to_dict(xml_string):
    data_dict = xmltodict.parse(xml_string)
    return json.loads(json.dumps(data_dict))


def get_protocol_from_xml_string(xml_string):
    xml_ = xml.dom.minidom.parseString(xml_string)
    message =  get_xml_from_tag_name(xml=xml_, tag="message")[0]
    protocol = message.getAttribute("xmlns").split(":")[-2:-1][0]
    return protocol


if __name__ == "__main__":

    print(parse_xml_file_to_dict("../data/9a009967-00f6-480c-aa70-78ffe52221fc.xml"))