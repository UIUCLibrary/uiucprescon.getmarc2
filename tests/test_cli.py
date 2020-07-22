from unittest.mock import mock_open, patch

from uiucprescon.getmarc2 import cli
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
    printed_data = bytes(capsys.readouterr().out, encoding="utf-8")
    output = ET.fromstring(printed_data)

    for e in output.iter("{http://www.loc.gov/MARC21/slim}datafield"):
        if e.attrib['tag'] != "035":
            continue
        subfield = next(e.iter("{http://www.loc.gov/MARC21/slim}subfield"))
        if subfield.text == "(UIUdb)5539966":
            return
    assert False, "(UIUdb)5539966 not found in record"


def test_write_output_file(monkeypatch):
    cli_args = [
        "--bibid", "5539966",
        "--alma-apikey", "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "-o", "5539966.xml",
    ]

    def mock_get(*args, **kwargs):
        return MockResponse()

    parsed_args = cli.get_arg_parse().parse_args(cli_args)
    monkeypatch.setattr(requests, "request", mock_get)
    m = mock_open()
    with patch('builtins.open', m):
        cli.run(parsed_args)
    m.assert_called_once_with('5539966.xml', 'w')

