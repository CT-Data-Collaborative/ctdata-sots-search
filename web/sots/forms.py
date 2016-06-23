from flask_wtf import Form
from wtforms import StringField, validators


class SearchForm(Form):
    search_term = StringField('Search Term', [validators.Length(max=255)])