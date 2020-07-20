import pytest

_sample_record = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<bibs total_record_count="1">
    <bib>
        <mms_id>99553996612205899</mms_id>
        <record_format>marc21</record_format>
        <linked_record_id/>
        <title>Horton hears a Who! /</title>
        <author>Seuss,</author>
        <isbn>0375841946</isbn>
        <network_numbers>
            <network_number>(UIUdb)5539966</network_number>
            <network_number>(OCoLC)ocn190789234</network_number>
        </network_numbers>
        <place_of_publication>New York :</place_of_publication>
        <date_of_publication>2008.</date_of_publication>
        <publisher_const>Robin Corey Books,</publisher_const>
        <holdings link="https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/99553996612205899/holdings"/>
        <created_by>import</created_by>
        <created_date>2020-06-04Z</created_date>
        <last_modified_by>System</last_modified_by>
        <last_modified_date>2020-07-16Z</last_modified_date>
        <suppress_from_publishing>false</suppress_from_publishing>
        <suppress_from_external_search>false</suppress_from_external_search>
        <sync_with_oclc>HOLDINGS</sync_with_oclc>
        <sync_with_libraries_australia>NONE</sync_with_libraries_australia>
        <originating_system>OTHER</originating_system>
        <originating_system_id>680071-01carli_network</originating_system_id>
        <record>
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
        </record>
    </bib>
</bibs>
'''


@pytest.fixture
def sample_record():
    return _sample_record
