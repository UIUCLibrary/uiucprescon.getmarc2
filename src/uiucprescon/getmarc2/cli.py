"""Module for handling command line runner."""

import argparse
import sys

try:
    from importlib import metadata
except ImportError:
    import importlib_metadata as metadata  # type: ignore

from typing import Optional

from lxml import etree  # nosec
from uiucprescon.getmarc2 import modifiers, records  # noqa: E501 pylint: disable=line-too-long,no-name-in-module


def get_arg_parse() -> argparse.ArgumentParser:
    """Get the CLI parser factory.

    Returns: parser
    """
    parser = argparse.ArgumentParser(description='Get Marc XML data.')
    parser.add_argument("identifier")

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("--bibid",
                       dest="identifier_type",
                       action='store_const',
                       const="bibid")

    group.add_argument("--mmsid",
                       dest="identifier_type",
                       action='store_const',
                       const="mmsid")

    parser.add_argument("--alma-apikey", required=True)
    parser.add_argument("-o", "--output")
    parser.add_argument("--domain",
                        default="https://api-na.hosted.exlibrisgroup.com")
    try:
        version = metadata.version(__package__)
    except metadata.PackageNotFoundError:
        version = "HEAD"

    parser.add_argument('--version', action='version',
                        version=f'%(prog)s {version}')

    return parser


def fix_up_xml(xml_src: str, bibid: str) -> str:
    """Fix up the xml and adds anything missing from the raw record.

    Args:
        xml_src: marc xml file
        bibid: uiuc bibid from the catalog

    Returns:
        Modified xml

    """
    field_adder = modifiers.Add955()
    field_adder.bib_id = bibid
    if "v" in bibid:
        field_adder.contains_v = True
    return field_adder.enrich(xml_src)


def run(args: Optional[argparse.Namespace] = None) -> None:
    """Run the main entry point for the command line script.

    Args:
        args: Command line arguments

    """
    args = args or get_arg_parse().parse_args()
    server = records.RecordServer(args.domain, args.alma_apikey)
    try:
        xml_result = str(
            etree.tostring(
                etree.fromstring(
                    server.get_record(
                        args.identifier, args.identifier_type
                    )
                ),
                pretty_print=True,
                encoding="UTF-8"
            ),
            encoding="utf-8"
        )
    except ValueError as error:
        print(error, file=sys.stderr)
        sys.exit(1)

    xml_result = fix_up_xml(xml_result, bibid=args.identifier)

    if records.is_validate_xml(xml_result) is False:
        raise records.ValidationException("invalid xml file")
    if args.output is not None:
        with open(args.output, "w", encoding="utf-8") as xml_file:
            xml_file.write(xml_result)
    else:
        print(xml_result)
