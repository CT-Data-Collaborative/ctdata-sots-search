import sys
import csv
import requests
import json
from datetime import datetime, date
from io import StringIO
from sots import app, db
from flask import render_template, request, redirect, url_for, Response
from sqlalchemy import func, desc, or_, distinct, and_
#from sqlalchemy.orm import lazyload
from sots.models import FullTextIndex, FullTextCompositeIndex, BusMaster, Principal, BusFiling, Status, Subtype, Corp, \
    DomLmtCmpy, ForLmtCmpy, ForLmtLiabPart, ForLmtPart, BusOther, ForStatTrust, NameChange, PrincipalName
from sots.forms import SearchForm, AdvancedSearchForm, FeedbackForm
from sots.config import BaseConfig as ConfigObject
from sots.helpers import corp_type_lookup, origin_lookup, category_lookup
from sots.helpers import check_empty as check_none



def corp_domesticity(bus_id):
    r = Corp.query.filter(Corp.id_bus == str(bus_id)).first()
    if r.cd_citizen == 'F':
        domesticity = 'Foreign'
    else:
        domesticity = 'Domestic'
    place_of_formation = r.cd_pl_of_form
    type = corp_type_lookup[r.cd_bus_type]
    return {'domesticity': "{} / {}".format(domesticity, place_of_formation),
            'type':type,
            'category':None}

def dom_domesticity(bus_id):
    return {'domesticity': "Domestic / CT",'type': None, 'category':None}

def for_lmt_liab_cmpy_domesticity(bus_id):
    r = ForLmtCmpy.query.filter(ForLmtCmpy.id_bus == str(bus_id)).first()
    place_of_formation = r.cd_pl_of_form
    return {'domesticity': "Foreign / {}".format(place_of_formation),
            'type': None,
            'category': None }

def for_lmt_liab_part_domesticity(bus_id):
    # TODO Address data loading issues with this table. Currently 0 rows
    # r = ForLmtLiabPart.query.filter(ForLmtLiabPart.id_bus = str(bus_id)).first()
    # place_of_formation = r.cd_pl_of_form
    return {'domesticity': "Foreign", 'type': None, 'category': None }

def for_lmt_part_domesticity(bus_id):
    # TODO Address data loading issues with this table. Currently 0 rows
    # r = ForLmtPart.query.filter(ForLiabPart.id_bus = str(bus_id)).first()
    # place_of_formation = r.cd_pl_of_form
    return {'domesticity': "Foreign", 'type':None, 'category':None}

def for_stat_trust_domesticity(bus_id):
    r = ForStatTrust.query.filter(ForStatTrust.id_bus == str(bus_id)).first()
    return {'domesticity': "Foreign / {}".format(r.cd_pl_of_form),
            'type':None,
            'category':None}

def gen_part_domesticity(bus_id):
    return {'domesticity': "", 'type':None, 'category':None}

def other_domesticity(bus_id):
    r = BusOther.query.filter(BusOther.id_bus == str(bus_id)).first()
    type = corp_type_lookup[r.cd_bus_type]
    origin = origin_lookup[r.cd_origin]
    try:
        category = category_lookup[r.cd_category]
    except KeyError:
        category = None
    return {'domesticity': None, 'type': type, 'category': category}

def domesticity_lookup(bus_id, subtype):
    type_table_lookup = {'B': corp_domesticity,
                         'C': corp_domesticity,
                         'G': dom_domesticity,
                         'I': dom_domesticity,
                         'D': dom_domesticity,
                         'L': dom_domesticity,
                         'P': corp_domesticity,
                         'H': for_lmt_liab_cmpy_domesticity,
                         'J': for_lmt_liab_part_domesticity,
                         'F': for_lmt_part_domesticity,
                         'M': for_stat_trust_domesticity,
                         'K': gen_part_domesticity,
                         'O': other_domesticity}
    lookup = type_table_lookup[subtype]
    return lookup(bus_id)

def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)

def get_latest_report(bus_id):
    report_codes = ['CFRN', 'CFRS', 'CRLC', 'CRLCF', 'CRLLP', 'CRLLPF', 'CRLP',
                    'CRLPF', 'CRS', 'CRN', 'COB', 'CON', 'COS']
    latest_report = BusFiling.query.filter(BusFiling.id_bus == bus_id).filter(
        BusFiling.cd_trans_type.in_(report_codes)).order_by(BusFiling.id_bus_flng.desc()).first()
    if latest_report:
        return latest_report.tx_certif
    else:
        return "No Reports Found"
    
    #replace dt_origin with dt_filing
def query(q_object):
    results = FullTextIndex.query.filter(FullTextIndex.index_name == q_object['index_field'])
    if q_object['index_field'] == 'place_of_business_city':
        str = FullTextIndex.city
        results = results.filter(str.startswith(q_object['query'].upper()))
    if q_object['query'] != '':
        tq = func.plainto_tsquery('english', q_object['query'])
        results = results.filter(FullTextIndex.document.op('@@')(tq))
    if q_object['active']:
        results = results.filter(FullTextIndex.status == 'Active')
    if q_object['start_date'] and q_object['end_date']:
        results = results.filter(FullTextIndex.dt_filing >= q_object['start_date']).filter(FullTextIndex.dt_filing <= q_object['end_date'])
    if q_object['business_type']:
        if q_object['business_type'] == ['All Entities']:
            pass
        else:
            results = results.filter(FullTextIndex.type.in_(q_object['business_type']))
    if q_object['sort_order'] == 'desc':
        results = results.order_by(desc(q_object['sort_by']))
    else:
        results = results.order_by(q_object['sort_by'])
    return results

@app.route('/search_results', methods=['GET'])
def search_results():
    page = int(request.args.get('page'))
    q_object = {
        'query': request.args.get('query'),
        'index_field': request.args.get('index_field'),
        'active': request.args.get('active'),
        'sort_by': request.args.get('sort_by'),
        'sort_order': request.args.get('sort_order')
    }
    if request.args.get('query_limit') is not None:
        q_object['query_limit'] = request.args.get('query_limit')
    else:
        q_object['query_limit'] = ''
    try:
        q_object['start_date'] = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
        q_object['end_date'] = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
    except TypeError:
        q_object['start_date'] = date(year=1900, month=1, day=1)
        q_object['end_date'] = datetime.now()
    q_object['business_type'] = request.args.getlist('business_type')
    results = query(q_object)
    results = results.paginate(page, ConfigObject.RESULTS_PER_PAGE, False)
    form = AdvancedSearchForm(**q_object)
    return render_template('results.html', results=results, q_obj=q_object, form=form)

@app.route('/business/<id>', methods=['GET'])
def detail(id):
    result = BusMaster.query.filter(BusMaster.id_bus == str(id)).first()
    try:
        domesticity = domesticity_lookup(result.id_bus, result.cd_subtype)
    except AttributeError:
        return redirect(url_for('index'))
    principals = Principal.query.filter(Principal.id_bus == str(id)).all()
    filings = BusFiling.query.filter(BusFiling.id_bus == str(id)).order_by(desc(BusFiling.dt_filing)).all()
    name_changes = NameChange.query.filter(NameChange.id_bus == str(id)).order_by(desc(NameChange.dt_changed)).all()
    report = get_latest_report(id)
    return render_template('results_detail.html',
                           result=result,
                           report=report,
                           principals=principals,
                           domesticity=domesticity,
                           filings=filings,
                           name_changes=name_changes,
                           results_page=redirect_url())

@app.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('search_results',
                                query=form.query.data,
                                index_field=form.index_field.data,
                                sort_by=form.sort_by.data,
                                sort_order=form.sort_order.data,
                                page=1))
    return render_template('index.html', form=form)

@app.route('/download', methods=['POST'])
def download():
    form = AdvancedSearchForm()
    form.business_type.default = 'All Entities'
    if form.validate_on_submit():
        q_object = {
            'query': form.query.data,
            'query_limit': form.query_limit.data,
            'index_field': form.index_field.data,
            'active': form.active.data,
            'sort_by': form.sort_by.data,
            'sort_order': form.sort_order.data
        }
        try:
            q_object['start_date'] = datetime.strftime(form.start_date.data, '%Y-%m-%d')
            q_object['end_date'] = datetime.strftime(form.end_date.data, '%Y-%m-%d')
        except TypeError:
            q_object['start_date'] = date(year=1900, month=1, day=1)
            q_object['end_date'] = datetime.now()
        q_object['business_type'] = form.business_type.data
        results = query(q_object)
        file = StringIO()

        writer = csv.DictWriter(file, fieldnames=['name', 'id', 'principal', 'agent', 'origin date', 'status', 'type', 'street', 'city', 'state', 'zip'])
        writer.writeheader()
        for biz in results.all():
            row = {'name': biz.nm_name, 'id': biz.id_bus, 'principal': biz.principal_name, 'agent': biz.nm_agt, 'origin date': biz.dt_origin, 'status': biz.status,
                   'type': biz.type, 'street': biz.street, 'city': biz.city, 'state': biz.state, 'zip': biz.zip}
            writer.writerow(row)
        file.seek(0)
        response = Response(file, content_type='text/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=sots_search_results.csv'
        return response


@app.route('/advanced_search', methods=['GET', 'POST'])
def advanced():
    form = AdvancedSearchForm()
    form.business_type.default = 'All Entities'
    if form.validate_on_submit():
        return redirect(url_for('search_results',
                                query=form.query.data,
                                query_limit=form.query_limit.data,
                                index_field=form.index_field.data,
                                business_type=form.business_type.data,
                                start_date=form.start_date.data,
                                end_date=form.end_date.data,
                                active=form.active.data,
                                sort_by=form.sort_by.data,
                                sort_order=form.sort_order.data,
                                page=1))
    return render_template('advanced.html', form=form)


@app.route('/technical_details', methods=['GET'])
def technical_details():
    return render_template('technical_details.html')


def to_markup(form):
    text = "## Goal: \n{}\n".format(form.goal.data)
    text += "## General Feedback: \n{}\n".format(form.general.data)
    text += "## Details: \n - {}".format(form.user_agent.data)
    return text

def create_github_issue(form):
    '''Create an issue on github.com using the given parameters.'''
    # Our url to create issues via POST
    url = 'https://api.github.com/repos/%s/%s/issues' % (ConfigObject.GITHUB_OWNER, ConfigObject.GITHUB_REPO)
    headers = {'Authorization': 'token %s' % ConfigObject.GITHUB_TOKEN}
    # Create our issue
    issue = {'title': form.goal.data,
             'body': to_markup(form),
             'labels': ['site feedback']}
    # Add the issue to our repository
    return requests.post(url, data=json.dumps(issue), headers=headers)


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    repo = ConfigObject.GITHUB_REPO
    owner = ConfigObject.GITHUB_OWNER
    agent = request.headers.get('User-Agent')
    form = FeedbackForm(user_agent=agent)
    if form.validate_on_submit():
        r = create_github_issue(form)
        if r.status_code == 201:
            return render_template('feedback_confirm.html', url=r.json()['html_url'])
        else:
            return render_template('feedback.html', form=form, repo=repo, owner=owner)
    return render_template('feedback.html', form=form, repo=repo, owner=owner)

# Filters for Jinja
app.template_filter('checknone')(check_none)

@app.template_filter('simpledate')
def simple_date(value, format='%b %d, %Y'):
    # try:
    return value.strftime(format)


issue = {'title': 'test',
         'body': 'test issue'}
