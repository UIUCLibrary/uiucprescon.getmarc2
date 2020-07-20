from uiucprescon.getalmarc2 import cli
from xml.etree import ElementTree as ET
import pytest
import requests
from .conftest import _sample_record
arg_values = [
    (
        [
            "--bibid", "5539966",
            "--alma-apikey", "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        ],
        {
            "bibid": "5539966",
            'domain': 'https://api-na.hosted.exlibrisgroup.com'
        }
    ),
    (
        [
            "--alma-apikey", "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        ],
        {
            'domain': 'https://api-na.hosted.exlibrisgroup.com'
        }
    ),
    (
        [
            "-o", "5539966.xml",
            "--alma-apikey", "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        ],
        {
            'domain': 'https://api-na.hosted.exlibrisgroup.com'
        }
    ),
    (
        ["--alma-apikey", "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"],
        {
            'alma_apikey': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
            'domain': 'https://api-na.hosted.exlibrisgroup.com'
        }
    )
]

@pytest.mark.parametrize("arg,expected_values", arg_values)
def test_parser(arg, expected_values):
    arg_parser = cli.get_arg_parse()
    args = arg_parser.parse_args(arg)
    assert expected_values.items() <= vars(args).items()


class MockResponse:
    @property
    def text(self):
        return _sample_record

def test_get_bibid_record(capsys, monkeypatch):

    def mock_get(*args, **kwargs):
        return MockResponse()

    cli_args = [
        "--bibid", "5539966",
        "--alma-apikey", "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    ]

    parsed_args = cli.get_arg_parse().parse_args(cli_args)
    monkeypatch.setattr(requests, "request", mock_get)
    cli.run(parsed_args)
    output = ET.fromstring(capsys.readouterr().out)

    for e in output.iter("datafield"):
        if e.attrib['tag'] != "035":
            continue
        subfield = next(e.iter("subfield"))
        if subfield.text == "(UIUdb)5539966":
            return
    assert False, "(UIUdb)5539966 not found in record"
