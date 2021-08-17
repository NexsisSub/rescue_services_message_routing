import xml.dom.minidom
import json
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class SubScription:
    code: str
    name: str
    sge_name: str
    webhook: str

@dataclass
class SubScriptions:
    http_subscriptions: List[SubScription]
    @classmethod
    def from_json(cls, json_data: Dict):
        
        return cls(http_subscriptions=[
            cls.get_data_subscription_name(sub)
            for sub in json_data
        ])

    @classmethod
    def from_json_file(cls, json_file_path: str):

        with open(json_file_path) as f:
            subscriptions = json.load(f)
        return cls.from_json(json_data=subscriptions)

    @classmethod
    def get_data_subscription_name(clf, sub) -> Dict:
        addresses = sub["adresses"]
        sge_address = [add for add in addresses if add["protocole"] == "sge:"][0]
        http_address = [add for add in addresses if add["protocole"] == "http:"][0]
        return SubScription(
            sge_name=sge_address["valeur"],
            webhook=http_address["valeur"],
            name=sub["nom"], 
            code=sub["code"]
        )

    def get_from_sge_name(self, sge_name: str) -> Dict:
        try:
            return [sub for sub in self.http_subscriptions if sub.sge_name == sge_name][0]
        except:
            return SubScription(
                code="failed",
                name="failed",
                sge_name="failed", 
                webhook="http://http-listener:8890/not-found"
            )



if __name__ == "__main__":
    sub = SubScriptions.from_json_file("data/subscriptions.json")
    print(sub.get_from_sge_name("77-cgo"))