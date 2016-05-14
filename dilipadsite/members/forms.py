from django import forms
from django.forms.extras.widgets import SelectDateWidget
import datetime

class CSVForm(forms.Form):
    
    errorsdict = {
    'required': 'Enter a valid year, month, and day.',
    'invalid': 'Enter a valid year, month, and day.'
}
    
    sd = forms.DateField(widget=SelectDateWidget(years=list(range(1900,2017)), months={
    1:('Jan'), 2:('Feb'), 3:('Mar'), 4:('Apr'),
    5:('May'), 6:('Jun'), 7:('Jul'), 8:('Aug'),
    9:('Sep'), 10:('Oct'), 11:('Nov'), 12:('Dec')}),required=True, input_formats=['%Y-%m-%d'], error_messages = errorsdict)
    
    ed = forms.DateField(widget=SelectDateWidget(years=list(range(1900,2017)), months={
    1:('Jan'), 2:('Feb'), 3:('Mar'), 4:('Apr'),
    5:('May'), 6:('Jun'), 7:('Jul'), 8:('Aug'),
    9:('Sep'), 10:('Oct'), 11:('Nov'), 12:('Dec')}),required=True, input_formats=['%Y-%m-%d'], error_messages = errorsdict)
