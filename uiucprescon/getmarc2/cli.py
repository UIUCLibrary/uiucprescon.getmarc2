"""Module for handling command line runner."""

import argparse
from typing import Optional

from lxml import etree  # nosec
from uiucprescon.getmarc2.records import RecordServer, is_validate_xml, \
    ValidationException
from . import modifiers


def get_arg_parse() -> argparse.ArgumentParser:
    """Get the CLI parser factory.

    Returns: parser

    """
    parser = argparse.ArgumentParser(description='Get Marc XML data.')
    parser.add_argument("--bibid")
    parser.add_argument("--alma-apikey", required=True)
    parser.add_argument("-o", "--output")
    parser.add_argument("--domain",
                        default="https://api-na.hosted.exlibrisgroup.com")
    return parser


def fix_up_xml(xml_result, bibid):
    field_adder = modifiers.Add955()
    field_adder.bib_id = bibid
    if "v" in bibid:
        field_adder.contains_v = True
    return field_adder.enrich(xml_result)


def run(args: Optional[argparse.Namespace] = None) -> None:
    """Run the main entry point for the command line script.

    Args:
        args: Command line arguments

    """
    args = args or get_arg_parse().parse_args()

    server = RecordServer(
        domain=args.domain,
        alma_api_key=args.alma_apikey
    )
    xml_result = str(
        etree.tostring(
            etree.fromstring(server.bibid_record(args.bibid)),
            pretty_print=True,
            encoding="UTF-8"
        ),
        encoding="utf-8"
    )
    xml_result = fix_up_xml(xml_result, bibid=args.bibid)

    if is_validate_xml(xml_result) is False:
        raise ValidationException("invalid xml file")
    if args.output is not None:
        with open(args.output, "w") as xml_file:
            xml_file.write(xml_result)
    else:
        print(xml_result)
