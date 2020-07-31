import difflib
from pprint import pprint
from xml.etree import ElementTree as et

import pytest

from uiucprescon import getmarc2

GIVEN = """
<?xml version="1.0" encoding="utf-8"?>
<record xmlns="http://www.loc.gov/MARC21/slim" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd">
<leader>02234cam a2200457Ii 4500</leader>
<controlfield tag="001">6852844</controlfield>
<controlfield tag="005">20171117143919.0</controlfield>
<controlfield tag="008">120424s1867    it af         000 0 ita d</controlfield>
<datafield ind1=" " ind2=" " tag="035">
<subfield code="a">(OCoLC)ocn788623005</subfield>
</datafield>
<datafield ind1=" " ind2=" " tag="040">
<subfield code="a">UIU</subfield>
<subfield code="b">eng</subfield>
<subfield code="e">rda</subfield>
<subfield code="c">UIU</subfield>
<subfield code="d">UIU</subfield>
<subfield code="d">OCLCO</subfield>
<subfield code="d">OCLCQ</subfield>
<subfield code="d">OCLCF</subfield>
<subfield code="d">UIU</subfield>
</datafield>
<datafield ind1=" " ind2=" " tag="043">
<subfield code="a">e-it---</subfield>
</datafield>
<datafield ind1=" " ind2=" " tag="049">
<subfield code="a">UIUU</subfield>
<subfield code="o">skip</subfield>
</datafield>
<datafield ind1="1" ind2=" " tag="100">
<subfield code="a">Finazzi, Giovanni,</subfield>
<subfield code="d">1802-1877,</subfield>
<subfield code="e">author.</subfield>
</datafield>
<datafield ind1="1" ind2="3" tag="245">
<subfield code="a">La lega Lombarda e la battaglia di Legnano :</subfield>
<subfield code="b">appunti storici pubblicati nell'occasione del settimo centenario del Congresso di Pontida.</subfield>
</datafield>
<datafield ind1=" " ind2="1" tag="264">
<subfield code="a">Bergamo :</subfield>
<subfield code="b">Tipografia Fratelli Bolis,</subfield>
<subfield code="c">1867.</subfield>
</datafield>
<datafield ind1=" " ind2=" " tag="300">
<subfield code="a">31, [1] pages, [1] leaf of plates :</subfield>
<subfield code="b">illustrations ;</subfield>
<subfield code="c">24 cm</subfield>
</datafield>
<datafield ind1=" " ind2=" " tag="336">
<subfield code="a">text</subfield>
<subfield code="b">txt</subfield>
<subfield code="2">rdacontent</subfield>
</datafield>
<datafield ind1=" " ind2=" " tag="337">
<subfield code="a">unmediated</subfield>
<subfield code="b">n</subfield>
<subfield code="2">rdamedia</subfield>
</datafield>
<datafield ind1=" " ind2=" " tag="338">
<subfield code="a">volume</subfield>
<subfield code="b">nc</subfield>
<subfield code="2">rdacarrier</subfield>
</datafield>
<datafield ind1=" " ind2=" " tag="500">
<subfield code="a">Signed on page 31: Can. Giovanni Finazzi.</subfield>
</datafield>
<datafield ind1=" " ind2=" " tag="500">
<subfield code="a">Last page blank.</subfield>
</datafield>
<datafield ind1=" " ind2=" " tag="500">
<subfield code="a">Frontispiece affixed to page [2].</subfield>
</datafield>
<datafield ind1=" " ind2=" " tag="500">
<subfield code="a">Errata slip affixed to inside rear cover.</subfield>
</datafield>
<datafield ind1=" " ind2=" " tag="500">
<subfield code="a">Cavagna 1911 cop.1, Cavagna 7065, and Cavagna 10362: University of Illinois bookplate on front paste-down: "From the library of Conte Antonio Cavagna Sangiuliani di Gualdana Lazelada di Bereguardo, purchased 1921."</subfield>
<subfield code="5">IU-R</subfield>
</datafield>
<datafield ind1=" " ind2=" " tag="500">
<subfield code="a">Acquisition made accessible thanks to a 2015-2017 grant from the Council on Libraries and Information Resources.</subfield>
<subfield code="5">IU-R</subfield>
</datafield>
<datafield ind1="2" ind2="0" tag="610">
<subfield code="a">Lombard League</subfield>
<subfield code="x">History.</subfield>
</datafield>
<datafield ind1=" " ind2="0" tag="650">
<subfield code="a">Legnano, Battle of, Legnano, Italy, 1176</subfield>
<subfield code="x">Anniversaries, etc.</subfield>
</datafield>
<datafield ind1=" " ind2="0" tag="651">
<subfield code="a">Lombardy (Italy)</subfield>
<subfield code="x">History</subfield>
<subfield code="y">To 1535.</subfield>
</datafield>
<datafield ind1=" " ind2="0" tag="651">
<subfield code="a">Pontida (Italy)</subfield>
<subfield code="x">History</subfield>
<subfield code="y">To 1535.</subfield>
</datafield>
<datafield ind1="2" ind2="7" tag="610">
<subfield code="a">Lombard League.</subfield>
<subfield code="2">fast</subfield>
<subfield code="0">(OCoLC)fst00631094</subfield>
</datafield>
<datafield ind1="0" ind2="7" tag="611">
<subfield code="a">Legnano, Battle of (Italy : 1176)</subfield>
<subfield code="2">fast</subfield>
<subfield code="0">(OCoLC)fst00995923</subfield>
</datafield>
<datafield ind1=" " ind2="7" tag="650">
<subfield code="a">Anniversaries.</subfield>
<subfield code="2">fast</subfield>
<subfield code="0">(OCoLC)fst00809757</subfield>
</datafield>
<datafield ind1=" " ind2="7" tag="651">
<subfield code="a">Italy</subfield>
<subfield code="z">Legnano.</subfield>
<subfield code="2">fast</subfield>
<subfield code="0">(OCoLC)fst01253333</subfield>
</datafield>
<datafield ind1=" " ind2="7" tag="651">
<subfield code="a">Italy</subfield>
<subfield code="z">Lombardy.</subfield>
<subfield code="2">fast</subfield>
<subfield code="0">(OCoLC)fst01213473</subfield>
</datafield>
<datafield ind1=" " ind2="7" tag="651">
<subfield code="a">Italy</subfield>
<subfield code="z">Pontida.</subfield>
<subfield code="2">fast</subfield>
<subfield code="0">(OCoLC)fst01216841</subfield>
</datafield>
<datafield ind1=" " ind2="7" tag="648">
<subfield code="a">To 1535</subfield>
<subfield code="2">fast</subfield>
</datafield>
<datafield ind1=" " ind2="7" tag="655">
<subfield code="a">History.</subfield>
<subfield code="2">fast</subfield>
<subfield code="0">(OCoLC)fst01411628</subfield>
</datafield>
<datafield ind1="1" ind2=" " tag="700">
<subfield code="a">Cavagna Sangiuliani di Gualdana, Antonio,</subfield>
<subfield code="c">conte,</subfield>
<subfield code="d">1843-1913,</subfield>
<subfield code="e">former owner.</subfield>
<subfield code="5">IU-R</subfield>
</datafield>
<datafield ind1="2" ind2=" " tag="710">
<subfield code="a">Cavagna Collection (University of Illinois at Urbana-Champaign. Library)</subfield>
<subfield code="5">IU-R</subfield>
</datafield>
<datafield ind1=" " ind2=" " tag="752">
<subfield code="a">Italy</subfield>
<subfield code="d">Bergamo.</subfield>
</datafield>
<datafield ind1=" " ind2=" " tag="994">
<subfield code="a">C0</subfield>
<subfield code="b">UIU</subfield>
</datafield>
</record>
""".strip()

EXPECTED = """
<?xml version="1.0" encoding="utf-8"?>
<record xmlns="http://www.loc.gov/MARC21/slim" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd">
  <leader>02234cam a2200457Ii 4500</leader>
  <controlfield tag="001">6852844</controlfield>
  <controlfield tag="005">20171117143919.0</controlfield>
  <controlfield tag="008">120424s1867    it af         000 0 ita d</controlfield>
  <datafield ind1=" " ind2=" " tag="035">
    <subfield code="a">(OCoLC)ocn788623005</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="040">
    <subfield code="a">UIU</subfield>
    <subfield code="b">eng</subfield>
    <subfield code="e">rda</subfield>
    <subfield code="c">UIU</subfield>
    <subfield code="d">UIU</subfield>
    <subfield code="d">OCLCO</subfield>
    <subfield code="d">OCLCQ</subfield>
    <subfield code="d">OCLCF</subfield>
    <subfield code="d">UIU</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="043">
    <subfield code="a">e-it---</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="049">
    <subfield code="a">UIUU</subfield>
    <subfield code="o">skip</subfield>
  </datafield>
  <datafield ind1="1" ind2=" " tag="100">
    <subfield code="a">Finazzi, Giovanni,</subfield>
    <subfield code="d">1802-1877,</subfield>
    <subfield code="e">author.</subfield>
  </datafield>
  <datafield ind1="1" ind2="3" tag="245">
    <subfield code="a">La lega Lombarda e la battaglia di Legnano :</subfield>
    <subfield code="b">appunti storici pubblicati nell'occasione del settimo centenario del Congresso di Pontida.</subfield>
  </datafield>
  <datafield ind1=" " ind2="1" tag="264">
    <subfield code="a">Bergamo :</subfield>
    <subfield code="b">Tipografia Fratelli Bolis,</subfield>
    <subfield code="c">1867.</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="300">
    <subfield code="a">31, [1] pages, [1] leaf of plates :</subfield>
    <subfield code="b">illustrations ;</subfield>
    <subfield code="c">24 cm</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="336">
    <subfield code="a">text</subfield>
    <subfield code="b">txt</subfield>
    <subfield code="2">rdacontent</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="337">
    <subfield code="a">unmediated</subfield>
    <subfield code="b">n</subfield>
    <subfield code="2">rdamedia</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="338">
    <subfield code="a">volume</subfield>
    <subfield code="b">nc</subfield>
    <subfield code="2">rdacarrier</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="500">
    <subfield code="a">Signed on page 31: Can. Giovanni Finazzi.</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="500">
    <subfield code="a">Last page blank.</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="500">
    <subfield code="a">Frontispiece affixed to page [2].</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="500">
    <subfield code="a">Errata slip affixed to inside rear cover.</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="500">
    <subfield code="a">Cavagna 1911 cop.1, Cavagna 7065, and Cavagna 10362: University of Illinois bookplate on front paste-down: "From the library of Conte Antonio Cavagna Sangiuliani di Gualdana Lazelada di Bereguardo, purchased 1921."</subfield>
    <subfield code="5">IU-R</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="500">
    <subfield code="a">Acquisition made accessible thanks to a 2015-2017 grant from the Council on Libraries and Information Resources.</subfield>
    <subfield code="5">IU-R</subfield>
  </datafield>
  <datafield ind1="2" ind2="0" tag="610">
    <subfield code="a">Lombard League</subfield>
    <subfield code="x">History.</subfield>
  </datafield>
  <datafield ind1=" " ind2="0" tag="650">
    <subfield code="a">Legnano, Battle of, Legnano, Italy, 1176</subfield>
    <subfield code="x">Anniversaries, etc.</subfield>
  </datafield>
  <datafield ind1=" " ind2="0" tag="651">
    <subfield code="a">Lombardy (Italy)</subfield>
    <subfield code="x">History</subfield>
    <subfield code="y">To 1535.</subfield>
  </datafield>
  <datafield ind1=" " ind2="0" tag="651">
    <subfield code="a">Pontida (Italy)</subfield>
    <subfield code="x">History</subfield>
    <subfield code="y">To 1535.</subfield>
  </datafield>
  <datafield ind1="2" ind2="7" tag="610">
    <subfield code="a">Lombard League.</subfield>
    <subfield code="2">fast</subfield>
    <subfield code="0">(OCoLC)fst00631094</subfield>
  </datafield>
  <datafield ind1="0" ind2="7" tag="611">
    <subfield code="a">Legnano, Battle of (Italy : 1176)</subfield>
    <subfield code="2">fast</subfield>
    <subfield code="0">(OCoLC)fst00995923</subfield>
  </datafield>
  <datafield ind1=" " ind2="7" tag="650">
    <subfield code="a">Anniversaries.</subfield>
    <subfield code="2">fast</subfield>
    <subfield code="0">(OCoLC)fst00809757</subfield>
  </datafield>
  <datafield ind1=" " ind2="7" tag="651">
    <subfield code="a">Italy</subfield>
    <subfield code="z">Legnano.</subfield>
    <subfield code="2">fast</subfield>
    <subfield code="0">(OCoLC)fst01253333</subfield>
  </datafield>
  <datafield ind1=" " ind2="7" tag="651">
    <subfield code="a">Italy</subfield>
    <subfield code="z">Lombardy.</subfield>
    <subfield code="2">fast</subfield>
    <subfield code="0">(OCoLC)fst01213473</subfield>
  </datafield>
  <datafield ind1=" " ind2="7" tag="651">
    <subfield code="a">Italy</subfield>
    <subfield code="z">Pontida.</subfield>
    <subfield code="2">fast</subfield>
    <subfield code="0">(OCoLC)fst01216841</subfield>
  </datafield>
  <datafield ind1=" " ind2="7" tag="648">
    <subfield code="a">To 1535</subfield>
    <subfield code="2">fast</subfield>
  </datafield>
  <datafield ind1=" " ind2="7" tag="655">
    <subfield code="a">History.</subfield>
    <subfield code="2">fast</subfield>
    <subfield code="0">(OCoLC)fst01411628</subfield>
  </datafield>
  <datafield ind1="1" ind2=" " tag="700">
    <subfield code="a">Cavagna Sangiuliani di Gualdana, Antonio,</subfield>
    <subfield code="c">conte,</subfield>
    <subfield code="d">1843-1913,</subfield>
    <subfield code="e">former owner.</subfield>
    <subfield code="5">IU-R</subfield>
  </datafield>
  <datafield ind1="2" ind2=" " tag="710">
    <subfield code="a">Cavagna Collection (University of Illinois at Urbana-Champaign. Library)</subfield>
    <subfield code="5">IU-R</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="752">
    <subfield code="a">Italy</subfield>
    <subfield code="d">Bergamo.</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="994">
    <subfield code="a">C0</subfield>
    <subfield code="b">UIU</subfield>
  </datafield>
  <datafield ind1=" " ind2=" " tag="955">
    <subfield code="b">6852844</subfield>
  </datafield>
</record>
""".strip()


def test_add_955():

    # ########################################################
    #  Create a enrichment XML string by adding a 955 field
    # ########################################################

    # Get the Add_955 strategy
    field_adder = getmarc2.modifiers.Add955()
    field_adder.bib_id = "6852844"

    # apply the the transformation
    transformed = field_adder.enrich(src=GIVEN)


    # Get The reflow strategy for cleaning up the data
    reflowr = getmarc2.modifiers.Reflow()
    transformed = reflowr.enrich(transformed)

    # ########################################################
    #   Test the results
    # ########################################################
    def filter_955(element) -> bool:
        return "tag" in element.attrib and element.attrib['tag'] == "955"

    actual = next(filter(filter_955, et.fromstring(transformed).findall(
        '{http://www.loc.gov/MARC21/slim}datafield')))
    expected = next(filter(filter_955, et.fromstring(EXPECTED).findall(
        '{http://www.loc.gov/MARC21/slim}datafield')))
    assert expected.attrib == actual.attrib
    assert expected.tag == actual.tag
    assert expected.text == actual.text
    assert expected.tail == actual.tail


def test_reflow():
    source = """<?xml version="1.0" encoding="utf-8"?>
<record xmlns="http://www.loc.gov/MARC21/slim" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd">
    
  <leader>01439cam a2200289Ka 4500</leader>
    
  <controlfield tag="001">2693684</controlfield>
    
  <controlfield tag="005">20170710104251.0</controlfield>
    
  <controlfield tag="008">900530s1845    it bf         000 0 ita d</controlfield>
    
  <datafield ind1=" " ind2=" " tag="035">
        
    <subfield code="a">(OCoLC)ocm77313810</subfield>
      
  </datafield>
    
  <datafield ind1=" " ind2=" " tag="040">
        
    <subfield code="a">UIU</subfield>
        
    <subfield code="e">dcrmb</subfield>
        
    <subfield code="c">UIU</subfield>
        
    <subfield code="d">UKMGB</subfield>
        
    <subfield code="d">UIU</subfield>
      
  </datafield>
    
  <datafield ind1=" " ind2=" " tag="019">
        
    <subfield code="a">561873437</subfield>
      
  </datafield>
    
  <datafield ind1=" " ind2=" " tag="035">
        
    <subfield code="a">(OCoLC)77313810</subfield>
        
    <subfield code="z">(OCoLC)561873437</subfield>
      
  </datafield>
    
  <datafield ind1=" " ind2=" " tag="043">
        
    <subfield code="a">e-it---</subfield>
      
  </datafield>
    
  <datafield ind1=" " ind2=" " tag="049">
        
    <subfield code="a">UIUU</subfield>
        
    <subfield code="o">skip</subfield>
      
  </datafield>
    
  <datafield ind1="1" ind2=" " tag="100">
        
    <subfield code="a">Monti, Carlo,</subfield>
        
    <subfield code="d">19th cent.</subfield>
      
  </datafield>
    
  <datafield ind1="1" ind2="0" tag="245">
        
    <subfield code="a">Studio topografico intorno alla piuu breve congiunzione stradale fra i due mari nell'alta Italia mercee un varco esistente nel tronco settentrionale dell'Apennino :</subfield>
        
    <subfield code="b">memoria /</subfield>
        
    <subfield code="c">dell'avvocato Carlo Monti.</subfield>
      
  </datafield>
    
  <datafield ind1=" " ind2=" " tag="260">
        
    <subfield code="a">Bologna :</subfield>
        
    <subfield code="b">Tipi governativi alla Volpe,</subfield>
        
    <subfield code="c">1845.</subfield>
      
  </datafield>
    
  <datafield ind1=" " ind2=" " tag="300">
        
    <subfield code="a">48 p., [1] folded leaf of plates :</subfield>
        
    <subfield code="b">map ;</subfield>
        
    <subfield code="c">27 cm.</subfield>
      
  </datafield>
    
  <datafield ind1=" " ind2=" " tag="500">
        
    <subfield code="a">Cavagna 1693: University of Illinois bookplate: "From the library of Conte Antonio Cavagna Sangiuliani di Gualdana Lazelada di Bereguardo, purchased 1921".</subfield>
        
    <subfield code="5">IU-R</subfield>
      
  </datafield>
    
  <datafield ind1=" " ind2=" " tag="500">
        
    <subfield code="a">625.7 M767s: Cavagna Library stamp on p. [3].</subfield>
        
    <subfield code="5">IU-R</subfield>
      
  </datafield>
    
  <datafield ind1=" " ind2="0" tag="650">
        
    <subfield code="a">Roads</subfield>
        
    <subfield code="z">Italy.</subfield>
      
  </datafield>
    
  <datafield ind1="1" ind2=" " tag="700">
        
    <subfield code="a">Cavagna Sangiuliani di Gualdana, Antonio,</subfield>
        
    <subfield code="c">conte,</subfield>
        
    <subfield code="d">1843-1913,</subfield>
        
    <subfield code="e">former owner.</subfield>
        
    <subfield code="5">IU-R</subfield>
      
  </datafield>
    
  <datafield ind1="2" ind2=" " tag="710">
        
    <subfield code="a">Cavagna Collection (University of Illinois at Urbana-Champaign Library)</subfield>
        
    <subfield code="5">IU-R</subfield>
      
  </datafield>
    
  <datafield ind1=" " ind2=" " tag="752">
        
    <subfield code="a">Italy</subfield>
        
    <subfield code="d">Bologna.</subfield>
      
  </datafield>
    
  <datafield ind1="4" ind2="1" tag="856">
        
    <subfield code="u">https://hdl.handle.net/2027/uiug.30112088620619</subfield>
        
    <subfield code="3">HathiTrust Digital Library</subfield>
      
  </datafield>
    
  <datafield ind1=" " ind2=" " tag="994">
        
    <subfield code="a">C0</subfield>
        
    <subfield code="b">UIU</subfield>
      
  </datafield>
    
  <datafield ind1="4" ind2="1" tag="856">
        
    <subfield code="3">Full text - HathiTrust Digital Library</subfield>
        
    <subfield code="u">https://hdl.handle.net/2027/uiuc.2693684</subfield>
      
  </datafield>
  <datafield tag="955" ind1=" " ind2=" ">
    <subfield code="b">2693684</subfield>
  </datafield>
</record>

    """
    reflowr = getmarc2.modifiers.Reflow()
    transformed = reflowr.enrich(source)
    for line_number, line in enumerate(transformed.split("\n")):
        print("{}:{}".format(line_number+1, line))

