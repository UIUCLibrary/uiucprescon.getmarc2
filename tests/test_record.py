from unittest.mock import Mock
import xml.etree.ElementTree as ET
from uiucprescon.getalmarc2 import records


def test_uiuc_bibid_in_record(sample_record):
    server = Mock(**{"bibid_record.return_value": sample_record})
    record_data = ET.fromstring(
        records.get_from_bibid(bibid="5539966", server=server))
    for e in record_data.iter("datafield"):
        if e.attrib['tag'] != "035":
            continue
        subfield = next(e.iter("subfield"))
        if subfield.text == "(UIUdb)5539966":
            return
    assert False, "(UIUdb)5539966 not found in record"
