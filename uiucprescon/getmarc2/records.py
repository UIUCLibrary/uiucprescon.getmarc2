"""Module for records."""
import warnings
from importlib.resources import read_text
from typing import Optional

import requests
from lxml import etree  # nosec

from . import query
from .query import AbsAlmaQueryIdentityStrategy


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

    def get_record(self, identifier, identifier_type: str) -> str:
        """Retrieve a record.

        Args:
            identifier:
            identifier_type: the type of identifier used

        Returns:
            xml record as a string
        """
        id_strategy = {
            "bibid": query.QueryIdentityBibid(),
            "mmsid": query.QueryIdentityMMSID()
        }.get(identifier_type)

        if id_strategy is None:
            raise AttributeError(
                "Unknown identifier type, {}".format(identifier_type)
            )

        url = self.build_request_url(identifier, id_strategy)
        response = requests.request("GET", url)
        if response.status_code != 200:
            raise ConnectionError(
                f"Failed to access from server: Reason {response.reason}"
            )

        request_data = response.text.encode("utf-8")
        record_count = self.parse_record_count(request_data)
        if record_count == 0:
            raise ValueError("No record found")
        my_record = self._process_record(request_data)
        return self.add_record_decorations(record_data=my_record)

    @staticmethod
    def _process_record(request_data: bytes) -> str:
        data = etree.fromstring(request_data)
        try:
            record = next(data.iter("record"))
        except StopIteration:
            raise ValueError("Invalid data")
        return str(
            etree.tostring(
                record,
                encoding="utf-8"
            ),
            encoding="utf-8"
        )

    def build_request_url(self,
                          identifier,
                          identifier_strategy: AbsAlmaQueryIdentityStrategy
                          ) -> str:
        """Build a url for the api.

        Args:
            identifier: identifier for record
            identifier_strategy: type of identifier

        Returns:
            url for making a request

        """
        api_route = "almaws/v1/bibs"
        item_query_string = identifier_strategy.make_query_fragment(identifier)
        url = f"{self.domain}/{api_route}?{item_query_string}&apikey={self.api_key}"  # noqa: E501 pylint: disable=line-too-long
        return url

    @staticmethod
    def parse_record_count(request_data) -> int:
        """Parse the data for a record count.

        Args:
            request_data:

        Returns:
            number of records

        >>> RecordServer.parse_record_count(\
                b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'\
                b'<bibs total_record_count="0"/>'\
            )
        0

        >>> RecordServer.parse_record_count(\
                b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'\
                b'<bibs total_record_count="d"/>'\
            )
        Traceback (most recent call last):
            ...
        ValueError: invalid literal for int() with base 10: 'd'

        >>> RecordServer.parse_record_count(b'spam eggs')
        Traceback (most recent call last):
            ...
        ValueError: Unable to parse data. ...

        """
        try:
            xml = etree.fromstring(request_data)
            return int(xml.attrib['total_record_count'])
        except etree.XMLSyntaxError as error:
            raise ValueError(
                "Unable to parse data. Reason {}".format(error)
            ) from error


class BibidRecordServer(RecordServer):
    """Used for managing the connection with the server API."""

    id_query_strategy = query.AlmaRecordIdentityQuery(
        query.QueryIdentityBibid()
    )

    def get_record(self, identifier, identifier_type=None) -> str:
        """Retrieve a record.

        Args:
            identifier:
            identifier_type: the type of identifier used

        Returns:
            record as an xml string

        """
        url = self._get_request_url(identifier)

        response = requests.request("GET", url)
        if response.status_code != 200:
            raise AttributeError(
                f"Failed to access from server: Reason {response.reason}"
            )

        request_data = response.text.encode("utf-8")
        my_record = self._process_record(request_data)
        return self.add_record_decorations(record_data=my_record)

    def bibid_record(self, bib_id: str) -> str:
        """Request a MARC xml record of a given bib id.

        Args:
            bib_id: UIUC bib id

        Returns: XML data as a string

        """
        warnings.warn(
            "Pending dep use get_record instead", DeprecationWarning
        )

        url = self._get_request_url(bib_id)
        response = requests.request("GET", url)
        if response.status_code != 200:
            raise AttributeError(
                f"Failed to access from server: Reason {response.reason}"
            )

        request_data = response.text.encode("utf-8")
        my_record = self._process_record(request_data)
        return self.add_record_decorations(record_data=my_record)

    def _get_request_url(self, bib_id):
        api_route = "almaws/v1/bibs"
        item_query_string = self.id_query_strategy.make_query_fragment(bib_id)
        url = f"{self.domain}/{api_route}?{item_query_string}&apikey={self.api_key}"  # noqa: E501 pylint: disable=line-too-long
        return url


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
