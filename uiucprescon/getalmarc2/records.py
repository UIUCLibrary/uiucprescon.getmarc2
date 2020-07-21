"""Module for records."""

import requests
from lxml import etree  # nosec


class RecordServer:
    """Used for managing the connection with the server API."""

    def __init__(self, domain, alma_api_key) -> None:
        self._domain = domain
        self._api_key = alma_api_key

    def bibid_record(self, bib_id: str) -> str:
        """Request a MARC xml record of a given bib id

        Args:
            bib_id: UIUC bib id

        Returns: XML data as a string

        """
        api_route = "almaws/v1/bibs"
        url = f"{self._domain}/{api_route}?mms_id=99{bib_id}12205899&apikey={self._api_key}"
        response = requests.request("GET", url)

        request_data = response.text
        my_record = self._get_record(request_data)
        return my_record

    @staticmethod
    def _get_record(request_data: str) -> str:
        raw_data = bytes(request_data, encoding="utf-8")
        data = etree.fromstring(raw_data)
        return str(
            etree.tostring(next(data.iter("record")),
                           encoding="utf-8"),
            encoding="utf-8")


def get_from_bibid(bibid: str, server: RecordServer) -> str:
    """Get the xml from a UIUC bib id.

    Args:
        bibid: UIUC bibid
        server: a valid server connection to the ALMA API server

    Returns:

    """
    return str(server.bibid_record(bibid))
