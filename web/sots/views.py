from sots import app, db
from flask import render_template, request, redirect, url_for, Response
from sqlalchemy import func, desc, or_
from sots.models import FullTextIndex, FullTextCompositeIndex, BusMaster, Principal, BusFiling, Status, Subtype, Corp, \
    DomLmtCmpy, ForLmtCmpy, ForLmtLiabPart, ForLmtPart, BusOther, ForStatTrust
from sots.forms import SearchForm, AdvancedSearchForm
from sots.config import BaseConfig as ConfigObject
from sots.helpers import corp_type_lookup, origin_lookup, category_lookup
from sots.helpers import check_empty as check_none
from datetime import datetime, date
from io import StringIO
import csv

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

def query(q_object):
    tq = func.plainto_tsquery('english', q_object['query'])
    if len(q_object['query_limit']) > 0:
        tql = func.plainto_tsquery('english', q_object['query_limit'])
        if q_object['index_field'] == 'business_name':
            address = tql
            name = tq
        else:
            address = tq
            name = tql
        results = FullTextCompositeIndex.query.filter(FullTextCompositeIndex.name.op('@@')(name)). \
            filter(or_(FullTextCompositeIndex.address1.op('@@')(address),
                       FullTextCompositeIndex.address2.op('@@')(address)))
        if q_object['active']:
            results = results.filter(FullTextCompositeIndex.status == 'Active')
        if q_object['start_date'] and q_object['end_date']:
            results = results.filter(
                FullTextCompositeIndex.dt_origin.between(q_object['start_date'], q_object['end_date']))
        if q_object['business_type']:
            if q_object['business_type'] == ['All Entities']:
                pass
            else:
                results = results.filter(FullTextCompositeIndex.type.in_(q_object['business_type']))

    else:
        results = FullTextIndex.query.filter(FullTextIndex.index_name == q_object['index_field']). \
            filter(FullTextIndex.document.op('@@')(tq))
        if q_object['active']:
            results = results.filter(FullTextIndex.status == 'Active')
        if q_object['start_date'] and q_object['end_date']:
            results = results.filter(FullTextIndex.dt_origin.between(q_object['start_date'], q_object['end_date']))
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
#
# def iter_csv(**kwargs):
#     q_object = {
#         'query': kwargs['query'],
#         'query_limit': kwargs['query_limit'],
#         'index_field': kwargs['index_field'],
#         'active': kwargs['active'],
#         'sort_by': kwargs['sort_by'],
#         'sort_order': kwargs['sort_order']
#     }
#     try:
#         q_object['start_date'] = datetime.strptime(kwargs['start_date'], '%Y-%m-%d')
#         q_object['end_date'] = datetime.strptime(kwargs['end_date'], '%Y-%m-%d')
#     except TypeError:
#         q_object['start_date'] = date(year=1990, month=1, day=1)
#         q_object['end_date'] = datetime.now()
#     q_object['business_type'] = kwargs['business_type']
#     results = query(q_object)
#     line = StringIO()
#     writer = csv.DictWriter(line, fieldnames=['name', 'id', 'origin date', 'status', 'type', 'address'])
#     writer.writeheader()
#     for biz in results.all():
#         row = {'name': biz.nm_name, 'id': biz.id_bus, 'origin date': biz.dt_origin, 'status': biz.status,
#                'type': biz.type, 'address': biz.address}
#         writer.writerow(row)
#         line.seek(0)
#         yield line.read()
#         line.truncate(0)
#


@app.route('/search_results', methods=['GET'])
def search_results():
    page = int(request.args.get('page'))
    q_object = {
        'query': request.args.get('query'),
        'query_limit': request.args.get('query_limit'),
        'index_field': request.args.get('index_field'),
        'active': request.args.get('active'),
        'sort_by': request.args.get('sort_by'),
        'sort_order': request.args.get('sort_order')
    }
    try:
        q_object['start_date'] = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
        q_object['end_date'] = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
    except TypeError:
        q_object['start_date'] = date(year=1990, month=1, day=1)
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
    report = get_latest_report(id)
    return render_template('results_detail.html',
                           result=result,
                           report=report,
                           principals=principals,
                           domesticity=domesticity,
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
            q_object['start_date'] = datetime.strptime(form.start_date.data, '%Y-%m-%d')
            q_object['end_date'] = datetime.strptime(form.end_date.data, '%Y-%m-%d')
        except TypeError:
            q_object['start_date'] = date(year=1990, month=1, day=1)
            q_object['end_date'] = datetime.now()
        q_object['business_type'] = form.business_type.data
        results = query(q_object)
        file = StringIO()
        writer = csv.DictWriter(file, fieldnames=['name', 'id', 'origin date', 'status', 'type', 'address'])
        writer.writeheader()
        for biz in results.all():
            row = {'name': biz.nm_name, 'id': biz.id_bus, 'origin date': biz.dt_origin, 'status': biz.status,
                   'type': biz.type, 'address': biz.address}
            writer.writerow(row)
        file.seek(0)
        response = Response(file, content_type='text/csv')
        response.headers['Content-Disposition'] = 'attachment; filename=data.csv'
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

# Filters for Jinja
app.template_filter('checknone')(check_none)

@app.template_filter('simpledate')
def simple_date(value, format='%b %d, %Y'):
    # try:
    return value.strftime(format)

