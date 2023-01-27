"""Module for records."""
try:
    from importlib.resources import files   # type: ignore
except ImportError:
    from importlib_resources import files   # type: ignore

from typing import Optional

import requests
from lxml import etree  # nosec

from . import query
from .query import AbsAlmaQueryIdentityStrategy


class NoRecordsFound(ValueError):
    """NoRecordsFound is when no records were located."""

    def __init__(
            self,
            response: requests.Response,
            message="No record found"
    ) -> None:
        """Create a new NoRecordsFound exception."""
        self.message = message
        self._response = response
        self.record_identifier: Optional[str] = None
        self.identifier_type: Optional[str] = None
        super().__init__(message)

    def get_response(self):
        """Get the request response used."""
        return self._response


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
            raise AttributeError(f"Unknown identifier type, {identifier_type}")

        url = self.build_request_url(identifier, id_strategy)
        response = requests.request("GET", url)
        if response.status_code != 200:
            raise ConnectionError(
                f"Failed to access from server: Reason {response.reason}"
            )

        request_data = response.text.encode("utf-8")
        record_count = self.parse_record_count(request_data)
        if record_count == 0:
            raise NoRecordsFound(response)
        my_record = self._process_record(request_data)
        return self.add_record_decorations(record_data=my_record)

    @staticmethod
    def _process_record(request_data: bytes) -> str:
        data = etree.fromstring(request_data)
        try:
            record = next(data.iter("record"))
        except StopIteration as error:
            raise ValueError("Invalid data") from error
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
                f"Unable to parse data. Reason {error}"
            ) from error


def get_from_bibid(bibid: str, server: RecordServer) -> str:
    """Get the xml from a UIUC bib id.

    Args:
        bibid: UIUC bibid
        server: a valid server connection to the ALMA API server

    Returns: MARC XML as a string

    """
    return str(server.get_record(bibid, "bibid"))


def is_validate_xml(data: str) -> bool:
    """Check if the xml file is valid.

    Args:
        data: xml data

    Returns:
        returns True if xml matches the schema

    """
    validation_file = files("uiucprescon.getmarc2").joinpath("MARC21slim.xsd")
    schema_root = etree.XML(
        validation_file.read_text()
    )

    schema = etree.XMLSchema(schema_root)
    parser = etree.XMLParser(schema=schema)
    try:
        etree.fromstring(data, parser)
        return True
    except etree.XMLSyntaxError:
        return False
