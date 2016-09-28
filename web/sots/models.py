from sots import db
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sots.helpers import check_empty, status_lookup, subtype_lookup
import re

def camel_to_underscore(name):
    """coerce camelcase to lowercase with underscore separation"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

class FullTextCompositeIndex(db.Model):
    __tablename__ = 'busmaster_composite_index'
    id_bus = db.Column(db.String)
    nm_name = db.Column(db.String)
    dt_origin = db.Column(db.DateTime)
    type = db.Column(db.String)
    status = db.Column(db.String)
    address = db.Column(db.String)
    address1 = db.Column(TSVECTOR)
    address2 = db.Column(TSVECTOR)
    name = db.Column(TSVECTOR)
    city = db.Column(db.String)
    state = db.Column(db.String)

    @hybrid_property
    def city_state(self):
        if self.city and self.state:
            return "{}, {}".format(self.city, self.state)
        else:
            return ""

class FullTextIndex(db.Model):
    __tablename__ = 'full_text_index'
    index_key = db.Column(UUID, primary_key=True)
    primary_id = db.Column(UUID)
    id_bus = db.Column(db.String)
    nm_name = db.Column(db.String)
    dt_origin =  db.Column(db.DateTime)
    table_name = db.Column(db.String)
    index_name = db.Column(db.String)
    search_type = db.Column(db.String)
    type = db.Column(db.String)
    status = db.Column(db.String)
    address = db.Column(db.String)
    document = db.Column(TSVECTOR)
    city = db.Column(db.String)
    state = db.Column(db.String)

    @hybrid_property
    def city_state(self):
        if self.city and self.state:
            return "{}, {}".format(self.city, self.state)
        else:
            return ""

    # @hybrid_property
    # def address(self):
    #     st1 = check_empty(self.ad_str1)
    #     st2 = check_empty(self.ad_str2)
    #     st3 = check_empty(self.ad_str3)
    #     city = check_empty(self.ad_city)
    #     state = check_empty(self.ad_st, default='', post=' ')
    #     zipcode = check_empty(self.ad_zip5, default='', post=' ')
    #     country = check_empty(self.ad_cntry, default='', post='')
    #     return "{}{}{}{}{}{}{}".format(st1, st2, st3, city, state, zipcode, country)


class BusMaster(db.Model):
    __tablename__ = 'bus_master'
    __table_args__ = {'autoload': True, 'autoload_with': db.engine}

    # status = db.relationship('Status', backref='business', lazy='joined')

    @hybrid_property
    def status(self):
        return status_lookup[self.cd_status]

    @hybrid_property
    def subtype(self):
        return subtype_lookup[self.cd_subtype]

    @hybrid_property
    def address(self):
        st1 = check_empty(self.ad_str1)
        st2 = check_empty(self.ad_str2)
        st3 = check_empty(self.ad_str3)
        city = check_empty(self.ad_city)
        state = check_empty(self.ad_st, default='', post=' ')
        zipcode = check_empty(self.ad_zip5, default='', post=' ')
        country = check_empty(self.ad_cntry, default='', post='')
        return "{}{}{}{}{}{}{}".format(st1, st2, st3, city, state, zipcode, country)


    @hybrid_property
    def mailing_address(self):
        st1 = check_empty(self.ad_mail_str1)
        st2 = check_empty(self.ad_mail_str2)
        st3 = check_empty(self.ad_mail_str3)
        city = check_empty(self.ad_mail_city)
        state = check_empty(self.ad_mail_st, default='', post=' ')
        zipcode = check_empty(self.ad_mail_zip5, default='', post=' ')
        country = check_empty(self.ad_mail_cntry, default='', post=' ')
        return "{}{}{}{}{}{}{}".format(st1, st2, st3, city, state, zipcode, country)

    @hybrid_property
    def agent_res_address(self):
        st1 = check_empty(self.ad_agt_res_str1)
        st2 = check_empty(self.ad_agt_res_str2)
        st3 = check_empty(self.ad_agt_res_str3)
        city = check_empty(self.ad_agt_res_city)
        state = check_empty(self.ad_agt_res_st, default='', post=' ')
        zipcode = check_empty(self.ad_agt_res_zip5, default='', post=' ')
        country = check_empty(self.ad_agt_res_cntry, default='', post=' ')
        return "{}{}{}{}{}{}{}".format(st1, st2, st3, city, state, zipcode, country)

    @hybrid_property
    def agent_bus_address(self):
        st1 = check_empty(self.ad_agt_bus_str1)
        st2 = check_empty(self.ad_agt_bus_str2)
        st3 = check_empty(self.ad_agt_bus_str3)
        city = check_empty(self.ad_agt_bus_city)
        state = check_empty(self.ad_agt_bus_st, default='', post=' ')
        zipcode = check_empty(self.ad_agt_bus_zip5, default='', post=' ')
        country = check_empty(self.ad_agt_bus_cntry, default='', post=' ')
        return "{}{}{}{}{}{}{}".format(st1, st2, st3, city, state, zipcode, country)

    def __repr__(self):
        return "<BUS_MASTER(id='{}', name='{}', date_of_origin='{}')>".format(self.id_bus, self.nm_name, self.dt_origin)

class BusFiling(db.Model):
    __tablename__ = 'bus_filing'
    __table_args__ = {'autoload': True, 'autoload_with': db.engine}

class Principal(db.Model):
    __tablename__ = 'principal'
    __table_args__ = {'autoload': True, 'autoload_with': db.engine}

    @hybrid_property
    def business_address(self):
        st1 = check_empty(self.ad_bus_str1)
        st2 = check_empty(self.ad_bus_str2)
        st3 = check_empty(self.ad_bus_str3)
        city = check_empty(self.ad_bus_city)
        state = check_empty(self.ad_bus_st, default='', post=' ')
        zipcode = check_empty(self.ad_bus_zip5, default='', post=' ')
        country = check_empty(self.ad_bus_cntry, default='', post=' ')
        return "{}{}{}{}{}{}{}".format(st1, st2, st3, city, state, zipcode, country)

    @hybrid_property
    def res_address(self):
        st1 = check_empty(self.ad_res_str1)
        st2 = check_empty(self.ad_res_str2)
        st3 = check_empty(self.ad_res_str3)
        city = check_empty(self.ad_res_city)
        state = check_empty(self.ad_res_st, default='', post=' ')
        zipcode = check_empty(self.ad_res_zip5, default='', post=' ')
        country = check_empty(self.ad_res_cntry, default='', post=' ')
        return "{}{}{}{}{}{}{}".format(st1, st2, st3, city, state, zipcode, country)


class SOTSMixin(object):
    @declared_attr
    def __tablename__(cls):
        return camel_to_underscore(cls.__name__)

    __table_args__ = {'autoload': True, 'autoload_with': db.engine}


class Status(db.Model):
    __tablename__ = 'business_status'
    __table_args__ = {'autoload': True, 'autoload_with': db.engine}


class Subtype(db.Model):
    __tablename__ = 'business_subtype'
    __table_args__ = {'autoload': True, 'autoload_with': db.engine}


class Corp(SOTSMixin, db.Model):
    pass


class DomLmtCmpy(SOTSMixin, db.Model):
    pass


class DomLmtLiabPart(SOTSMixin, db.Model):
    pass


class DomLmtPart(SOTSMixin, db.Model):
    pass


class ForLmtCmpy(SOTSMixin, db.Model):
    pass


class ForLmtLiabPart(SOTSMixin, db.Model):
    pass


class ForLmtPart(SOTSMixin, db.Model):
    pass


class ForStatTrust(SOTSMixin, db.Model):
    pass

class BusOther(SOTSMixin, db.Model):
    pass