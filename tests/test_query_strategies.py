import pytest

from uiucprescon.getmarc2 import query

bibid_values = [
    ("5539966", "mms_id=99553996612205899"),
    ("4671245", "mms_id=99467124512205899"),
]


@pytest.mark.parametrize("identifier,expected_query", bibid_values)
def test_bibid_query(identifier, expected_query):
    query_strat = query.AlmaRecordIdentityQuery(query.QueryIdentityBibid())
    new_query_string = query_strat.make_query_fragment(identifier)
    assert new_query_string == expected_query


mmsid_values = [
    ("99553996612205899", "mms_id=99553996612205899"),
    ("99467124512205899", "mms_id=99467124512205899"),
]


@pytest.mark.parametrize("identifier,expected_query", mmsid_values)
def test_mmsid_query(identifier, expected_query):
    query_strat = query.AlmaRecordIdentityQuery(query.QueryIdentityMMSID())
    new_query_string = query_strat.make_query_fragment(identifier)
    assert new_query_string == expected_query

