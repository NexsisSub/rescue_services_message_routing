import xml.dom.minidom

class Sender:
    def __init__(self, name):
        self.name = name

    @classmethod
    def from_xml(cls, xml):
        name = get_data_from_tag_name(xml, "senderID")
        return cls(name= name)


class Recipient:
    def __init__(self, scheme, address):
        self.scheme = scheme
        self.address = address

    @classmethod
    def from_xml(cls, xml):
        explicitAddressScheme = get_data_from_tag_name(xml, "explicitAddressScheme")
        explicitAddressValue= get_data_from_tag_name(xml, "explicitAddressValue")
        return cls(scheme= explicitAddressScheme, address=explicitAddressValue)

def get_data_from_tag_name(xml, tag, class_mapping=str, index=0):
    tags = get_xml_from_tag_name(xml=xml, tag=tag)
    if tags:
        data = [class_mapping(tag.firstChild.nodeValue) for tag in tags]
        return data[index] if index is not None else data


def get_xml_from_tag_name(xml, tag):
    return xml.getElementsByTagName(tag)


def get_sender_from_xml(xml):
    sender = Sender.from_xml(xml)
    return sender

def get_recipients_and_protocol_from_edxl_string(xml_string):
    dom = xml.dom.minidom.parseString(xml_string)
    return get_recipients_from_xml(dom), get_sender_from_xml(dom), get_protocol_from_xml(dom)

def get_recipients_from_xml(xml):
    tags = get_xml_from_tag_name(xml=xml, tag="explicitAddress")
    recipients = [Recipient.from_xml(tag) for tag in tags]
    return recipients


def get_protocol_from_xml(xml):
    try:
        message =  get_xml_from_tag_name(xml=xml, tag="message")[0]
        protocol = message.getAttribute("xmlns").split(":")[-2:-1][0]
    except:
        message =  get_xml_from_tag_name(xml=xml, tag="emsi")[0]
        print(message.getAttribute("xmlns"))
        protocol = message.getAttribute("xmlns").split("/")[-2:-1][0]

    return protocol.lower()



if __name__ == "__main__":
    with open("../data/9a009967-00f6-480c-aa70-78ffe52221fc.xml") as f:
        cisu = f.read()

    print(get_recipients_and_protocol_from_edxl_string(cisu))