"""Module for records."""

from importlib.resources import read_text
from typing import Optional

import requests
from lxml import etree  # nosec

from . import query


class ValidationException(Exception):
    """Raises if validation check fails."""


class RecordServer:
    """Manage the API server."""

    def __init__(self, domain: str, alma_api_key: str) -> None:
        """Manage the API server.

        Args:
            domain: server domain used by the api
            alma_api_key: API key as a string
        """
        self.domain = domain
        self.api_key = alma_api_key

    @staticmethod
    def addns(root: etree._Element,  # pylint: disable=protected-access
              alias: Optional[str],
              uri: str) -> etree._Element:  # pylint: disable=W0212
        """Add namespace to a element.

        Args:
            root: root element
            alias: namespace alias
            uri: namespace url

        Returns: New lxml etree element with new namespace added

        """
        nsmap = root.nsmap
        nsmap[alias] = uri
        new_root = etree.Element(root.tag, attrib=root.attrib, nsmap=nsmap)
        new_root[:] = root[:]
        return new_root

    def add_record_decorations(self, record_data: str) -> str:
        """Add the namespace declarations expected for this xml type.

        Args:
            record_data: row xml data as a string

        Returns: Updated xml as a string

        """
        data = etree.fromstring(record_data)
        data = self.addns(data, None, "http://www.loc.gov/MARC21/slim")

        data = self.addns(
            data, "xsi", "http://www.w3.org/2001/XMLSchema-instance")

        data.set(
            "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation",
            "http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd"  # noqa: E501 pylint: disable=line-too-long
        )
        return str(
            etree.tostring(
                data,
                encoding="utf-8"
            ),
            encoding="utf-8"
        )


class BibidRecordServer(RecordServer):
    """Used for managing the connection with the server API."""

    id_query_strategy = query.AlmaRecordIdentityQuery(
        query.QueryIdentityBibid()
    )

    def bibid_record(self, bib_id: str) -> str:
        """Request a MARC xml record of a given bib id.

        Args:
            bib_id: UIUC bib id

        Returns: XML data as a string

        """
        api_route = "almaws/v1/bibs"
        item_query_string = self.id_query_strategy.make_query_fragment(bib_id)
        url = f"{self.domain}/{api_route}?{item_query_string}&apikey={self.api_key}"  # noqa: E501 pylint: disable=line-too-long
        response = requests.request("GET", url)
        if response.status_code != 200:
            raise AttributeError(
                f"Failed to access from server: Reason {response.reason}"
            )

        request_data = response.text.encode("utf-8")
        my_record = self._get_record(request_data)
        return self.add_record_decorations(record_data=my_record)

    @staticmethod
    def _get_record(request_data: bytes) -> str:
        data = etree.fromstring(request_data)
        return str(
            etree.tostring(
                next(data.iter("record")),
                encoding="utf-8"
            ),
            encoding="utf-8"
        )


def get_from_bibid(bibid: str, server: BibidRecordServer) -> str:
    """Get the xml from a UIUC bib id.

    Args:
        bibid: UIUC bibid
        server: a valid server connection to the ALMA API server

    Returns: MARC XML as a string

    """
    return str(server.bibid_record(bibid))


def is_validate_xml(data: str) -> bool:
    """Check if the xml file is valid.

    Args:
        data: xml data

    Returns:
        returns True if xml matches the schema

    """
    schema_root = etree.XML(
        read_text("uiucprescon.getmarc2", "MARC21slim.xsd")
    )

    schema = etree.XMLSchema(schema_root)
    parser = etree.XMLParser(schema=schema)
    try:
        etree.fromstring(data, parser)
        return True
    except etree.XMLSyntaxError:
        return False
