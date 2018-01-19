from django.core.management.base import BaseCommand, CommandError
from dilipadsite.models import *
import os, csv
from dilipadsite.settings import MEDIA_ROOT

class Command(BaseCommand):
    help = 'Dumps a .csv of each day in a year/month dir structure, to media/'

    def dump(self, qs, outfile_path):
	"""
	Takes in a Django queryset and spits out a CSV file.
	
	Usage::
	
		>> from utils import dump2csv
		>> from dummy_app.models import *
		>> qs = DummyModel.objects.all()
		>> dump2csv.dump(qs, './data/dump.csv')
	
	Based on a snippet by zbyte64::
		
		http://www.djangosnippets.org/snippets/790/
	
	"""
        model = qs.model
	writer = csv.writer(open(outfile_path, 'w'))
	
	headers = []
	for field in model._meta.fields:
		headers.append(field.name)
	writer.writerow(headers)
	
	for obj in qs:
		row = []
		for field in headers:
			val = getattr(obj, field)
			if callable(val):
				val = val()
			if type(val) == unicode:
				val = val.encode("utf-8")
			row.append(val)
		writer.writerow(row)

    def handle(self, *args, **options):

        datelist = datenav.objects.values_list('hansarddate', flat=True)
        basefilepath = os.path.join(MEDIA_ROOT,'lipad')
##        remainder = [] # this is a doublecheck for broken days
        for date in datelist:
            m = str(date.month)
            d = str(date.day)
            y = str(date.year)
            outpath = os.path.join(basefilepath, y, m)
            if not os.path.exists(outpath):
                os.makedirs(outpath)
            filename = y+"-"+m+"-"+d+".csv"
            filepath = os.path.join(outpath,filename)
            print(filepath)
            if os.path.exists(filepath) and os.path.getsize(filepath) > 1024:
                print ('skipping...')
            else:
                qs = basehansard.objects.filter(speechdate=date).order_by('basepk')
                self.dump(qs, filepath)
##                remainder.append(date)
##        for r in remainder:
##            print r.isoformat()

                



                
                
