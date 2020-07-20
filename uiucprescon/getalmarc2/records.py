import requests
from lxml import etree


class RecordServer:

    def __init__(self, domain, alma_api_key) -> None:
        self._domain = domain
        self._api_key = alma_api_key

    def bibid_record(self, bib_id: str) -> bytes:
        api_route = "almaws/v1/bibs"
        url = f"{self._domain}/{api_route}?mms_id=99{bib_id}12205899&apikey={self._api_key}"
        response = requests.request("GET", url)

        request_data = response.text
        my_record = self._get_record(request_data)
        return my_record

    def _get_record(self, request_data: str) -> str:
        raw_data = bytes(request_data, encoding="utf-8")
        data = etree.fromstring(raw_data)
        d = next(data.iter("record"))
        return str(etree.tostring(d, encoding="utf-8"), encoding="utf-8")


def get_from_bibid(bibid: str, server: RecordServer) -> str:
    return str(server.bibid_record(bibid))
