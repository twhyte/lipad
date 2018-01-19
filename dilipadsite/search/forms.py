from django import forms
from haystack.forms import FacetedSearchForm
from django.forms.extras.widgets import SelectDateWidget
from haystack.query import SearchQuerySet
from haystack.inputs import AutoQuery, Raw
from haystack.inputs import AltParser
import datetime


class TextSearchForm(FacetedSearchForm):
        
    q = forms.CharField(required=False, label=('Search'),widget=forms.TextInput())
    
    def search(self):

        sqs = super(TextSearchForm, self).search()

        if not self.is_valid():
            return self.searchqueryset.all().exclude(speakerposition__exact="subtopic").exclude(speakerposition__exact="topic")

        if not self.cleaned_data.get('q'):
            return self.searchqueryset.all().exclude(speakerposition__exact="subtopic").exclude(speakerposition__exact="topic")

        sqs = sqs.exclude(speakerposition__exact="subtopic").exclude(speakerposition__exact="topic")
        
        if self.cleaned_data.get('q'):
            alt_q = AltParser("edismax", self.cleaned_data["q"],
                  qf="speechtext^1.5 text",
                    )

            sqs = sqs.filter(content=alt_q)

            
        #sqs = sqs.filter(text__exact=AutoQuery(self.cleaned_data['q']))

        if self.load_all:
            sqs = sqs.load_all()

        return sqs

    def no_query_found(self):
        return self.searchqueryset.all()

class DateRangeSearchForm(TextSearchForm):

    errorsdict = {
    'required': 'Enter a valid year, month, and day.',
    'invalid': 'Enter a valid year, month, and day.'
}

    thedate = datetime.datetime.now().date()

    sd = forms.DateField(widget=SelectDateWidget(years=list(range(1900,thedate.year+1)), months={
    1:('Jan'), 2:('Feb'), 3:('Mar'), 4:('Apr'),
    5:('May'), 6:('Jun'), 7:('Jul'), 8:('Aug'),
    9:('Sep'), 10:('Oct'), 11:('Nov'), 12:('Dec')}),required=False, input_formats=['%Y-%m-%d'], error_messages = errorsdict, initial=datetime.date(1901,01,01))
    
    ed = forms.DateField(widget=SelectDateWidget(years=list(range(1900,thedate.year+1)), months={
    1:('Jan'), 2:('Feb'), 3:('Mar'), 4:('Apr'),
    5:('May'), 6:('Jun'), 7:('Jul'), 8:('Aug'),
    9:('Sep'), 10:('Oct'), 11:('Nov'), 12:('Dec')}),required=False, input_formats=['%Y-%m-%d'], error_messages = errorsdict, initial=thedate)

    def search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(DateRangeSearchForm, self).search()

        if not self.is_valid():
            return self.no_query_found()

        # Check to see if a start_date was chosen.
        if self.cleaned_data['sd']:
            sqs = sqs.filter(speechdate__gte=self.cleaned_data['sd'])

        # Check to see if an end_date was chosen.
        if self.cleaned_data['ed']:
            sqs = sqs.filter(speechdate__lte=self.cleaned_data['ed'])

        return sqs


# code for js datepicker integration -- unfinished/maybe not even needed in forms.py?

    ##    start_date = forms.DateField(widget=forms.DateInput(attrs=
##                                {
##                                    "data-uk-datepicker" : "{format:'DD-MM-YYYY', minDate:'01-01-1901', maxDate:-1}",
##                                    'format': "%d-%m-%Y"
##                                }), required=False)
##    end_date = forms.DateField(widget=forms.DateInput(attrs=
##                                {
##                                    "data-uk-datepicker" : "{format:'DD-MM-YYYY', minDate:'01-01-1901', maxDate:-1}",
##                                    'format': "%d-%m-%Y"
##                                }), required=False)

##    def search(self):
##        
##        sqs = super(DateRangeSearchForm, self).search()
##
####        def dateConverter(self,sd):
####            year = sd[-4:]
####            month =sd[3:5]
####            day = sd[:2]
####            return(datetime.date(year, month, day))
####
####        # Check to see if a start_date was chosen.
####        if self.cleaned_data['start_date']:
####            sd = self.cleaned_data['start_date']
####            
####            sqs = sqs.filter(speechdate__gte=dateConverter(sd))
####
####        # Check to see if an end_date was chosen.
####        if self.cleaned_data['end_date']:
####            ed = self.cleaned_data['end_date']
####            sqs = sqs.filter(speechdate__lte=dateConverter(ed))
##
##        return sqs


class SortedDateRangeSearchForm(DateRangeSearchForm):

    sb = forms.BooleanField(required=False)
    so = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(SortedDateRangeSearchForm, self).__init__(*args, **kwargs)

    def search(self):
        
        sqs = super(SortedDateRangeSearchForm, self).search()

        if not self.is_valid():
            return self.no_query_found()

        if self.cleaned_data['sb'] is True:
            if self.cleaned_data['so'] is True:
                sqs = sqs.order_by('speechdate')
            else:
                sqs = sqs.order_by('-speechdate')
            
        return sqs


class AdvancedSearchForm(SortedDateRangeSearchForm):

    pol = forms.CharField(required=False, label=('Politician'),widget=forms.TextInput())
    polexact = forms.BooleanField(required=False) 
    par = forms.CharField(required=False, label=('Party'),widget=forms.TextInput())
    parexact = forms.BooleanField(required=False) 

    def __init__(self, *args, **kwargs):
        super(AdvancedSearchForm, self).__init__(*args, **kwargs)

    def search(self):
        
        sqs = super(AdvancedSearchForm, self).search()

        if not self.is_valid():
            return self.no_query_found()

        if self.cleaned_data['pol']:
            if self.cleaned_data['polexact']:
                sqs = sqs.filter(speakername__exact=self.cleaned_data['pol']) 
            else:
                sqs = sqs.filter(speakername=self.cleaned_data['pol'])

        if self.cleaned_data['par']:

            if self.cleaned_data['polexact']:
                sqs = sqs.filter(speakerparty__exact=self.cleaned_data['par']) 
            else:
                sqs = sqs.filter(speakerparty=self.cleaned_data['par'])
            
        return sqs

        

