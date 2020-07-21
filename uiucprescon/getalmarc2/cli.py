import argparse
from lxml import etree
from uiucprescon.getalmarc2.records import RecordServer


def get_arg_parse():
    parser = argparse.ArgumentParser(description='Get Marc XML data.')
    parser.add_argument("--bibid")
    parser.add_argument("--alma-apikey", required=True)
    parser.add_argument("-o", "--output")
    parser.add_argument("--domain",
                        default="https://api-na.hosted.exlibrisgroup.com")
    return parser


def run(args=None) -> None:
    """Main entry point.

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
    if args.output:
        with open(args.output, "w") as xml_file:
            xml_file.write(xml_result)
    else:
        print(xml_result)
