"""Modify documents."""

import abc
import re
from typing import Optional
from xml.dom import minidom  # nosec
from xml.etree import ElementTree as ET  # nosec

try:
    from importlib.resources import files  # type: ignore
except ModuleNotFoundError:
    from importlib_resources import files  # type: ignore


class AbsEnrichment(metaclass=abc.ABCMeta):
    """Base class to enhance a string."""

    @abc.abstractmethod
    def enrich(self, src: str) -> str:
        """Perform enrichment of some type to the string.

        Args:
            src: source data

        Returns:
            Newly enhanced string

        """


class Add955(AbsEnrichment):
    """Add the 955 field values.

    Attributes:
        bib_id (str): bib id to be added to the 955 field.
        contains_v (:obj:`bool`, optional): The package record contains the
            letter v. Defaults to False.
    """

    questNS = "http://www.loc.gov/MARC21/slim"
    template_955 =\
        files("uiucprescon.getmarc2").joinpath("955_template.xml").read_text()

    def __init__(self) -> None:
        """Modify 955 fields."""
        self.bib_id: Optional[str] = None
        self.contains_v = False

    def enrich(self, src: str) -> str:
        """Add a 955 field based on the bib_id."""
        bib_id = self.bib_id
        contains_v = self.contains_v

        xml_data = src.strip()

        root = ET.fromstring(xml_data)

        new_955_element = ET.fromstring(
            Add955._create_new_955_field(bib_id, contains_v))

        # Add the 955 edited value to the tree from online
        root.append(new_955_element)

        ET.register_namespace("", Add955.questNS)

        new_xml = ET.tostring(root, encoding="unicode", method="xml")
        return new_xml

    @classmethod
    def _create_new_955_field(cls, bib_id, contains_v) -> str:
        new_966_field = ET.fromstring(Add955.template_955)
        new_966_field[0][0].text = bib_id
        if contains_v:
            new_966_field[0][1].text = "v." + str(
                bib_id[bib_id.index("v") + 1:])
        else:
            new_966_field[0].remove(new_966_field[0][1])
        element: ET.Element = new_966_field[0]
        return ET.tostring(element, encoding="unicode")


class Reflow(AbsEnrichment):
    """Parses and re-renders the xml text.

    Useful for cleaning up after using modifiers.
    """

    remove_whitespace_regex = re.compile(r">\s*<")

    def enrich(self, src: str) -> str:
        """Redraw the xml text."""
        no_line_endings = src.replace("\n", "")
        no_extra_whitespace = \
            Reflow.remove_whitespace_regex.sub("><", no_line_endings)
        # = re.sub(Reflow.remove_whitespace_regex, )
        reparsed = minidom.parseString(no_extra_whitespace)

        # declaring the encoding forces it to be in the xml declaration
        with_dec = reparsed.toprettyxml(indent="  ", encoding="utf-8")

        # forcing the declaration causes it to return bytes and escape quotes
        # that shouldn't be escaped. This fixes it back before returning
        return with_dec.decode("utf-8").replace("&quot;", '"')
