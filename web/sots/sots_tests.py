import pytest
import flask
from flask import url_for
from sots import app
from sots.views import check_none, simple_date, corp_domesticity, dom_domesticity, for_lmt_liab_cmpy_domesticity, \
    for_lmt_liab_part_domesticity, for_lmt_part_domesticity, for_stat_trust_domesticity, gen_part_domesticity, \
    other_domesticity, domesticity_lookup
from sots.models import FullTextIndex, BusMaster
from datetime import datetime
from urllib.parse import urlparse


@pytest.fixture
def client(request):
    app.config['WTF_CSRF_ENABLED'] = False
    client = app.test_client()
    def teardown():
        pass
    request.addfinalizer(teardown)
    return client

##########################################################################################
#
# Non-database dependent view tests
#
##########################################################################################

def test_home(client):
    rv = client.get('/')
    assert rv.status_code == 200

def test_home_content(client):
    rv = client.get('/')
    content_type = 'text/html; charset=utf-8'
    assert content_type == rv.headers['content-type']



##########################################################################################
#
# Filter tests
#
##########################################################################################

def test_check_none_filter_none():
    assert '' == check_none(None)

def test_check_none_filter_empty():
    assert '' == check_none('')

def test_check_none_filter_empty_whitespace():
    assert '' == check_none(' ')

def test_check_none_filter_default():
    assert 'default' == check_none(None, default = 'default')

def test_check_none_filter_text():
    assert 'test, ' == check_none('test', default = 'default')

def test_check_none_filter_post():
    assert 'test:' == check_none('test', default = 'default', post = ':')

def test_simple_date():
    d = datetime(year=2016, day=23, month=6)
    assert simple_date(d) == 'Jun 23, 2016'

def test_simple_date_custom_format():
    d = datetime(year=2016, day=23, month=6)
    f = '%y/%m/%d'
    assert simple_date(d, format=f) == '16/06/23'


##########################################################################################
#
# Form tests
#
##########################################################################################

def test_search_form_submit(client):
    """ Do we get back a valid result including a redirect"""
    rv = client.post('/', data={'search_term': '342sdfjkl;ajs'}, follow_redirects=True)
    assert rv.status_code == 200

##########################################################################################
#
# Database Tests
#
# Notes: Our application is strictly read-only. There is no functionality that creates,
# updates, or deletes data from the db. The schema pre-exists the declaration of models
# and as such, must be taken as is. This will be refactored at some point to be explicit.
# As a result, we are doing our tests on our live, local DB.
#
##########################################################################################

def test_search_form_live_data(client):
    """ Do we get back a valid result including a redirect"""
    with app.test_request_context():
        rv = client.post('/', data={'search_term': 'r.c. bigelow'}, follow_redirects=False)
        assert rv.status_code == 302
        expected = url_for('search_results', query='r.c. bigelow') + '/1'
        assert urlparse(rv.location).path == expected

def test_bus_id_lookup(client):
    rv = client.get('/business/0038096')
    assert rv.status_code == 200


def test_invalid_bus_id_redirect(client):
    with app.test_request_context():
        rv = client.get('/business/0038096a', follow_redirects=False)
        assert rv.status_code == 302
        expected = url_for('index')
        assert urlparse(rv.location).path == expected

##########################################################################################
#
# Tests for View Helpers
#
##########################################################################################

def test_foreign_corp():
    r = corp_domesticity('0000033')
    assert r == {'domesticity': "Foreign / IL", 'type': 'Stock', 'category': None}

def test_dom_domesticity():
    r = dom_domesticity(1)
    assert r == {'domesticity': "Domestic / CT",'type': None, 'category':None}

def test_for_lmt_liab_cmpy_domesticity():
    r = for_lmt_liab_cmpy_domesticity('0500003')
    assert r == {'domesticity': "Foreign / WY", 'type': None, 'category': None}

def test_for_lmt_liab_part_domesticity():
    r = for_lmt_liab_part_domesticity('0500003')
    assert r == {'domesticity': "Foreign", 'type': None, 'category': None}

def test_for_lmt_part_domesticity():
    r = for_lmt_part_domesticity('0500003')
    assert r == {'domesticity': "Foreign", 'type': None, 'category': None}

def test_for_stat_trust_domesticity():
    r = for_stat_trust_domesticity('0573748')
    assert r == {'domesticity': 'Foreign / DE', 'type': None, 'category': None}

def test_gen_part_domesticity():
    r = gen_part_domesticity('0584804')
    assert r == {'domesticity': "", 'type':None, 'category':None}

def test_other_domesticity():
    r = other_domesticity('0053377')
    assert r == {'domesticity': None, 'type': 'Non-Stock', 'category': None}

def test_domesticity_lookup():
    r = domesticity_lookup('0000033', 'C')
    assert r == {'domesticity': "Foreign / IL", 'type': 'Stock', 'category': None}

##########################################################################################
#
# Tests for Model Tests
#
##########################################################################################

def test_full_text_index():
    fti = FullTextIndex.query.filter(FullTextIndex.id_bus == '0230145').first()
    assert fti.address == '1258 BROAD STREET, HARTFORD, CT 06106 '

def test_bus_master():
    bm = BusMaster.query.filter(BusMaster.id_bus == '0230145').first()
    assert bm.status == 'Active'
    assert bm.subtype == 'Corporation'
    assert bm.address == '1258 BROAD STREET, HARTFORD, CT 06106 '
    assert bm.mailing_address == '1258 BROAD STREET, HARTFORD, CT 06106 '
    assert bm.agent_res_address == '119 BUTLER DRIVE, GLASTONBURY, CT 06033 '
    assert bm.agent_bus_address == '750 MAIN STREET, HARTFORD, CT 06103 '
    assert bm.__repr__() == "<BUS_MASTER(id='0230145', name='CAMPUS PIZZA, INC.', date_of_origin='1989-02-03')>"

