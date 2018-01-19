from django.core.management.base import BaseCommand, CommandError
from dilipadsite.models import *
import datetime
import re
import string
from natsort import natsorted
import os
import csv
import io
from lxml import etree
from collections import OrderedDict

class WeirdXMLError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Command(BaseCommand):
    help = 'populates a model datenav containing a date list of all hansarddays, creates the full dictionary, and pickles'

    # this needs to be rewritten for simple updates as well, ie. daily update. Way too inefficient.

    def handle(self, *args, **options):

        
        
        qs = basehansard.objects.order_by('speechdate').values_list('speechdate', flat=True).distinct()
        for result in qs: # this is a datetime.date:
            decade = (str(result.year)[:3])+"0"
            day = result.day
            month = result.month
            year = result.year
            b, created = datenav.objects.update_or_create(hansarddate = result, defaults = {'decade':decade,'year':year,
                                                                   'month':month,
                                                                  'day':day})

        dq = datenav.objects.order_by('hansarddate').distinct()

        timeline = OrderedDict()
        for i in dq.iterator():
            decade = i.decade
            year = i.year
            month = i.month
            day = i.day
            fulldate=i.get_fulldate()
            
            if i.decade in timeline and not (timeline[decade]) is None:
                if i.year in timeline[decade] and not (timeline[decade][year]) is None:
                    if i.month in timeline[decade][year] and not (timeline[decade][year][month]) is None:
                        if i.day in timeline[decade][year][month] and not (timeline[decade][year][month][day]) is None:
                            timeline[decade][year][month][day]=i.hansarddate
                        else:
                            timeline[decade][year][month][day]=OrderedDict()
                            timeline[decade][year][month][day]=i.hansarddate 
                    else:
                        timeline[decade][year][month]=OrderedDict()
                        timeline[decade][year][month][day]=OrderedDict()
                        timeline[decade][year][month][day]=i.hansarddate
                else:
                    timeline[decade][year]=OrderedDict()
                    timeline[decade][year][month]=OrderedDict()
                    timeline[decade][year][month][day]=OrderedDict()
                    timeline[decade][year][month][day]=i.hansarddate     
            else:
                timeline[decade]=OrderedDict()
                timeline[decade][year]=OrderedDict()
                timeline[decade][year][month]=OrderedDict()
                timeline[decade][year][month][day]=OrderedDict()
                timeline[decade][year][month][day]=i.hansarddate

        obj, created = datePickle.objects.get_or_create(pk=1)
        obj.fullmap = timeline
        obj.save()
    

        
    def clearNullRows(self):
        basehansard.objects.filter(opid__isnull=True,pid__isnull=True,
                                   speakeroldname__isnull=True,speakerposition__isnull=True,
                                   maintopic__isnull=True,subtopic__isnull=True,
                                   speechtext__isnull=True,speakerparty__isnull=True,
                                   speakerriding__isnull=True,speakername__isnull=True).delete()
        
