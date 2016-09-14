import pytest
import flask
from flask import url_for
from sots import app
from sots.views import check_none, simple_date, corp_domesticity, dom_domesticity, for_lmt_liab_cmpy_domesticity, \
    for_lmt_liab_part_domesticity, for_lmt_part_domesticity, for_stat_trust_domesticity, gen_part_domesticity, \
    other_domesticity, domesticity_lookup, basic_search_results
from sots.models import FullTextIndex, BusMaster
from sots.forms import SearchForm, AdvancedSearchForm
from datetime import datetime
from urllib.parse import urlparse
from wtforms import SelectField
from werkzeug.debug import DebuggedApplication

app.wsgi_app = DebuggedApplication(app.wsgi_app, False)

@pytest.fixture
def client(request):
    app.config['WTF_CSRF_ENABLED'] = False
    app.testing = True
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

def test_advanced(client):
    rv = client.get('/advanced_search')
    assert rv.status_code == 200

def test_advanced_headers(client):
    rv = client.get('/advanced_search')
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
    form_data = {'search_term': '342sdfjkl;ajs', 'choice': 'bus_name'}
    rv = client.post('/', data= form_data, follow_redirects=True)
    assert rv.status_code == 200

def test_search_form_fields(client):
    with app.test_request_context():
        f = SearchForm()
        assert f.data == {'search_term': None, 'choice': 'None'}
        assert isinstance(f.choice, SelectField)

def test_search_form_live_data(client):
    """ Do we get back a valid result including a redirect"""
    with app.test_request_context():
        form_data = {'search_term': 'r.c. bigelow', 'choice': 'business_name'}
        rv = client.post('/', data=form_data, follow_redirects=False)
        assert rv.status_code == 302
        expected = url_for('basic_search_results', query='r.c. bigelow', index_field='business_name', page=1)
        assert urlparse(rv.location).path == expected

def test_advanced_search_form_field(client):
    with app.test_request_context():
        f = AdvancedSearchForm()
        assert f.data == {
            'start_date': None, 'end_date': None, 'business_type': None,
            'active': False, 'choice': 'None', 'search_term': None
        }

def test_advanced_search_form_search_field_choices(client):
    with app.test_request_context():
        f = AdvancedSearchForm()
        choices = [
            ('business_name', 'Business Name'),
            ('place_of_business_address', 'Business Address'),
            ('bus_id', 'Business ID'),
            ('filing_number', 'Filing Number'),
            ('principal_name', 'Principal Name'),
            ('principal_business_address', 'Principal Address')
        ]
        assert f.choice.choices == choices

def test_advanced_search_form_business_type_choices(client):
    with app.test_request_context():
        f = AdvancedSearchForm()
        choices = [('C', 'Corporation'),
                   ('D', 'Domestic Limited Partnership'),
                   ('F', 'Foreign Limited Partnership'),
                   ('G', 'Domestic Limited Liability Company'),
                   ('H', 'Foreign Limited Liability Company'),
                   ('I', 'Domestic Limited Liability Partnership'),
                   ('J', 'Foreign Limited Liability Partnership'),
                   ('K', 'General Partnership'),
                   ('L', 'Domestic Statutory Trust'),
                   ('M', 'Foreign Statutory Trust'),
                   ('O', 'Other'),
                   ('P', 'Domestic Stock Corporation'),
                   ('Q', 'Foreign Stock Corporation'),
                   ('R', 'Domestic Non-Stock Corporation'),
                   ('S', 'Foreign Non-Stock Corporation'),
                   ('T', 'All Entities'),
                   ('U', 'Domestic Credit Union Stock'),
                   ('V', 'Domestic Credit Union Non-Stock'),
                   ('W', 'Domestic Bank Stock'),
                   ('X', 'Domestic Bank Non-Stock'),
                   ('Y', 'Domestic Insurance Stock'),
                   ('Z', 'Domestic Insurance Non-Stock'),
                   ('B', 'Benefit Corporation')]
        assert f.business_type.choices == choices


def test_advanced_search_form_submit(client):
    """ Do we get back a valid result including a redirect"""
    form_data = {'search_term': '342sdfjkl;ajs',
                 'choice': 'bus_name',
                 'start_date': None,
                 'end_date': None,
                 'active': False,
                 'business_type': None}
    rv = client.post('/advanced_search', data= form_data, follow_redirects=True)
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

def test_search_type_processing(client):
    with app.test_request_context():
        page = basic_search_results(query='r.c. bigelow', page=1, index_field = 'bus_name')
        assert isinstance(page, str)

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

