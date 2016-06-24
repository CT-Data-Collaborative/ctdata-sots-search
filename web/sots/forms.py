from flask_wtf import Form
from wtforms import StringField, SelectField, validators


class SearchForm(Form):
    search_term = StringField('Search Term', [validators.Length(max=255)])
    choice = SelectField('Choices',
                          choices = [
                              ('business_name', 'Business Name'),
                              ('place_of_business_address', 'Business Address'),
                              ('bus_id', 'Business ID'),
                              ('filing_number', 'Filing Number'),
                              ('principal_name', 'Principal Name'),
                              ('principal_business_address', 'Principal Address')
                          ])