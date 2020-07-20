import argparse
from uiucprescon.getalmarc2.records import RecordServer
from lxml import etree


def get_arg_parse():
    parser = argparse.ArgumentParser(description='Get Marc XML data.')
    parser.add_argument("--bibid")
    parser.add_argument("--alma-apikey", required=True)
    parser.add_argument("-o", "--output")
    parser.add_argument("--domain",
                        default="https://api-na.hosted.exlibrisgroup.com")
    return parser


def run(args=None):

    if args is None:
        parser = get_arg_parse()
        args = parser.parse_args()

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
        print("writing to ")
        with open(args.output, "w") as wf:
            wf.write(xml_result)
    else:
        print(xml_result)
