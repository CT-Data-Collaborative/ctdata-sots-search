from sots import app, db
from flask import render_template,  redirect, url_for
from sqlalchemy import func
from sots.models import FullTextIndex, BusMaster, Principal, Status, Subtype, Corp, DomLmtCmpy, ForLmtCmpy, \
    ForLmtLiabPart, ForLmtPart, BusOther, ForStatTrust
from sots.forms import SearchForm
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
    return {'domesticity': "{} / {}".format(domesticity, place_of_formation), 'type':type, 'category':None}

def dom_domesticity(bus_id):
    return {'domesticity': "Domestic / CT",'type': None, 'category':None}

def for_lmt_liab_cmpy_domesticity(bus_id):
    r = ForLmtCmpy.query.filter(ForLmtCmpy.id_bus == str(bus_id)).first()
    place_of_formation = r.cd_pl_of_form
    return {'domesticity': "Foreign / {}".format(place_of_formation), 'type': None, 'category': None }

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
    return {'domesticity': "Foreign / {}".format(r.cd_pl_of_form), 'type':None, 'category':None}

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



@app.route('/search_results/<query>', methods=['GET'])
@app.route('/search_results/<query>/<int:page>', methods=['GET'])
def search_results(query, page=1):
    tq = func.plainto_tsquery('english', query)
    results = FullTextIndex.query. \
        filter(FullTextIndex.document.op('@@')(tq)).paginate(page, ConfigObject.RESULTS_PER_PAGE, False)

    return render_template('results.html', query=query, results=results)


@app.route('/business/<id>', methods=['GET'])
def detail(id):
    result = BusMaster.query.filter(BusMaster.id_bus == str(id)).first()
    try:
        domesticity = domesticity_lookup(result.id_bus, result.cd_subtype)
    except AttributeError:
        return redirect(url_for('index'))
    principals = Principal.query.filter(Principal.id_bus == str(id)).all()
    return render_template('results_detail.html', result=result,  principals=principals, domesticity=domesticity)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('search_results', query=form.search_term.data, page=1))
    return render_template('index.html', form=form)



# Filters for Jinja
app.template_filter('checknone')(check_none)


@app.template_filter('simpledate')
def simple_date(value, format='%b %d, %Y'):
    # try:
    return value.strftime(format)

