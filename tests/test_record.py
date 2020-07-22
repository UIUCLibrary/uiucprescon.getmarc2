from unittest.mock import Mock
import xml.etree.ElementTree as ET
from uiucprescon.getmarc2 import records


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


def test_validate():
    sample_record = """<record xmlns="http://www.loc.gov/MARC21/slim" 
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
        xsi:schemaLocation="http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd">
            <leader>01044cam a2200301Ia 4500</leader>
            <controlfield tag="001">99553996612205899</controlfield>
            <controlfield tag="005">20200203175510.0</controlfield>
            <controlfield tag="008">080114s2008    nyua   a      000 1 eng d</controlfield>
            <datafield ind1=" " ind2=" " tag="020">
                <subfield code="a">9780375841941</subfield>
            </datafield>
            <datafield ind1=" " ind2=" " tag="020">
                <subfield code="a">0375841946</subfield>
            </datafield>
            <datafield ind1=" " ind2=" " tag="035">
                <subfield code="a">(OCoLC)ocn190789234</subfield>
            </datafield>
            <datafield ind1=" " ind2=" " tag="035">
                <subfield code="a">(UIUdb)5539966</subfield>
            </datafield>
            <datafield ind1=" " ind2=" " tag="040">
                <subfield code="a">DAD</subfield>
                <subfield code="c">DAD</subfield>
                <subfield code="d">BAKER</subfield>
                <subfield code="d">IHI</subfield>
                <subfield code="d">UIU</subfield>
            </datafield>
            <datafield ind1=" " ind2=" " tag="049">
                <subfield code="a">UIUU</subfield>
            </datafield>
            <datafield ind1="1" ind2=" " tag="100">
                <subfield code="a">Seuss,</subfield>
                <subfield code="c">Dr.</subfield>
            </datafield>
            <datafield ind1="1" ind2="0" tag="245">
                <subfield code="a">Horton hears a Who! /</subfield>
                <subfield code="c">by Dr. Seuss ; pop-ups by David A. Carter.</subfield>
            </datafield>
            <datafield ind1="1" ind2=" " tag="246">
                <subfield code="i">At head of title :</subfield>
                <subfield code="a">Dr. Seuss's</subfield>
            </datafield>
            <datafield ind1=" " ind2=" " tag="260">
                <subfield code="a">New York :</subfield>
                <subfield code="b">Robin Corey Books,</subfield>
                <subfield code="c">2008.</subfield>
            </datafield>
            <datafield ind1=" " ind2=" " tag="300">
                <subfield code="a">1 v. (unpaged) :</subfield>
                <subfield code="b">col. ill. ;</subfield>
                <subfield code="c">26 cm.</subfield>
            </datafield>
            <datafield ind1=" " ind2=" " tag="520">
                <subfield code="a">Horton finds an entire city of Whos on a speck of dust, but, since no one else can see them, no one believes they exist.</subfield>
            </datafield>
            <datafield ind1=" " ind2=" " tag="521">
                <subfield code="a">For ages 3 and up.</subfield>
            </datafield>
            <datafield ind1=" " ind2="0" tag="650">
                <subfield code="a">Elephants</subfield>
                <subfield code="v">Juvenile fiction.</subfield>
            </datafield>
            <datafield ind1=" " ind2="1" tag="655">
                <subfield code="a">Stories in rhyme.</subfield>
            </datafield>
            <datafield ind1=" " ind2="1" tag="655">
                <subfield code="a">Fantasy fiction.</subfield>
            </datafield>
            <datafield ind1=" " ind2="1" tag="655">
                <subfield code="a">Toy and movable books.</subfield>
            </datafield>
            <datafield ind1="1" ind2=" " tag="700">
                <subfield code="a">Carter, David A.</subfield>
            </datafield>
            <datafield ind1=" " ind2=" " tag="938">
                <subfield code="a">Baker &amp; Taylor</subfield>
                <subfield code="b">BKTY</subfield>
                <subfield code="c">25.99</subfield>
                <subfield code="d">19.49</subfield>
                <subfield code="i">0375841946</subfield>
                <subfield code="n">0007257087</subfield>
                <subfield code="s">active</subfield>
            </datafield>
            <datafield ind1=" " ind2=" " tag="959">
                <subfield code="a">(UIUdb)5539966</subfield>
            </datafield>
            <datafield ind1=" " ind2=" " tag="994">
                <subfield code="a">C0</subfield>
                <subfield code="b">UIU</subfield>
            </datafield>
        </record>"""
    assert records.is_validate_xml(sample_record) is True
