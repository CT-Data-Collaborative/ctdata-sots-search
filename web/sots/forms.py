from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, BooleanField, validators, DateField, HiddenField
from wtforms.fields.html5 import DateField
from sots.config import BaseConfig as ConfigObject
from datetime import datetime
from wtforms.widgets import TextArea

# Format: 'index_name', 'displayed search field'
class SearchForm(FlaskForm):
    #query = StringField('Search Term', [validators.Length(max=255)])
    query = StringField('Search Term', [validators.InputRequired(), validators.Length(min=2,max=255)])
    sort_by = HiddenField(default='nm_name')
    sort_order = HiddenField(default='asc')
    end_date_default = datetime.strptime(ConfigObject.END_DATE, '%Y-%m-%d')
    end_date_nice = end_date_default.strftime('%B %d, %Y')
    index_field = SelectField('Choices',
                         choices=[
                             ('business_name', 'Business Name'),
                             ('place_of_business_address', 'Business Address'),
                             ('place_of_business_city', 'Business City (Spell Correctly)'),
                             ('bus_id', 'Business ID'),
                             ('filing_number', 'Filing Number'),
                             ('principal_name', 'Principal Name'),
                             ('agent_name', 'Agent Name'),
                         ])


# TODO Break out index into components -- individual fields w/ and/or
class AdvancedSearchForm(FlaskForm):
    #start_date_default = datetime.strptime('01-01-1803', '%Y-%m-%d')
    #end_date_default = datetime.strptime('08-07-2018', '%Y-%m-%d')
    start_date_default = datetime.strptime(ConfigObject.START_DATE, '%Y-%m-%d')
    end_date_default = datetime.strptime(ConfigObject.END_DATE, '%Y-%m-%d')
    end_date_nice = end_date_default.strftime('%B %d, %Y')
    sort_by = HiddenField(default='nm_name')
    sort_order = HiddenField(default='asc')
    #query = StringField('Search Term', [validators.Length(max=255)])
    query = StringField('Search Term', [validators.InputRequired(), validators.Length(min=2,max=255)])
    query_limit = StringField('Search Term Limit', [validators.Length(max=255), validators.optional()])
    index_field = SelectField('Choices',
                         choices=[
                             ('business_name', 'Business Name'),
                             ('place_of_business_address', 'Business Address'),
                             ('place_of_business_city', 'Business City (Spell Correctly)'),
                             ('bus_id', 'Business ID'),
                             ('filing_number', 'Filing Number'),
                             ('principal_name', 'Principal Name'),
                             ('agent_name', 'Agent Name'),
                         ])
    start_date = DateField('Start Date', default=start_date_default, validators=[validators.optional()])
    end_date = DateField('End Date', default=end_date_default, validators=[validators.optional()])
    #active = BooleanField('Active Businesses Only', default=False, validators=[validators.optional()])
    active = BooleanField('Active Businesses Only')#,
    business_type = SelectMultipleField('Business Type',
                                        validators=[validators.optional()],
                                        default='All Entities',
                                        choices=[('All Entities', 'All Entities'),
                                                #('Corporation', 'Corporation'),
                                                 ('Domestic Stock Corporation', 'Domestic Stock Corporation'),
                                                 ('Foreign Stock Corporation', 'Foreign Stock Corporation'),
                                                 ('Domestic Non-Stock Corporation', 'Domestic Non-Stock Corporation'),
                                                 ('Foreign Non-Stock Corporation', 'Foreign Non-Stock Corporation'),
                                                 ('Benefit Corporation', 'Benefit Corporation'),
                                                 ('Domestic Limited Partnership', 'Domestic Limited Partnership'),
                                                 ('Foreign Limited Partnership', 'Foreign Limited Partnership'),
                                                 ('Domestic Limited Liability Company', 'Domestic Limited Liability Company'),
                                                 ('Foreign Limited Liability Company', 'Foreign Limited Liability Company'),
                                                 ('Domestic Limited Liability Partnership', 'Domestic Limited Liability Partnership'),
                                                 ('Foreign Limited Liability Partnership', 'Foreign Limited Liability Partnership'),
                                                 ('General Partnership', 'General Partnership'),
                                                 ('Domestic Statutory Trust', 'Domestic Statutory Trust'),
                                                 ('Foreign Statutory Trust', 'Foreign Statutory Trust'),
                                                 ('Other', 'Other'),
                                                 #('Domestic Stock Corporation', 'Domestic Stock Corporation'),
                                                 #('Foreign Stock Corporation', 'Foreign Stock Corporation'),
                                                 #('Domestic Non-Stock Corporation', 'Domestic Non-Stock Corporation'),
                                                 #('Foreign Non-Stock Corporation', 'Foreign Non-Stock Corporation'),
                                                 #('Domestic Credit Union Stock', 'Domestic Credit Union Stock'),
                                                 #('Domestic Credit Union Non-Stock', 'Domestic Credit Union Non-Stock'),
                                                 #('Domestic Bank Stock', 'Domestic Bank Stock'),
                                                 #('Domestic Bank Non-Stock', 'Domestic Bank Non-Stock'),
                                                 #('Domestic Insurance Stock', 'Domestic Insurance Stock'),
                                                 #('Domestic Insurance Non-Stock', 'Domestic Insurance Non-Stock'),
                                                 ])


class FeedbackForm(FlaskForm):
    goal_label = 'What were you trying to do and how can we improve it?*'
    general_label = 'How can we get in touch with you?'
    submitter_label = ''
    goal = StringField(goal_label, [validators.required()], widget=TextArea())
    general = StringField(general_label, widget=TextArea())
    submitter = StringField(submitter_label, widget=TextArea())
    user_agent = HiddenField('user-agent', [validators.required()])
