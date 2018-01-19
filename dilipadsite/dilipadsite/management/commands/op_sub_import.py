import psycopg2
from django.core.management.base import BaseCommand, CommandError
import datetime
import re
import string
import os, sys
import unicodecsv as csv
import io
from dilipadsite.models import basehansard
from django.db import DataError
from natsort import natsorted

class Command(BaseCommand):
    help = 'Imports subsubtopics (h3) from opdump. Catches dates with errors for future fixes'
    
    def handle(self, *args, **options):

        path = os.path.join(os.getcwd(), "canada", "opdump.csv")

        problemdates = {}
        
        with io.open(path,'rb') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                sst = row['h3_en']
                if sst == None:
                    pass
                elif sst == "":
                    pass
                else:
                    # datetest for May 2016 on format change
                    thedate = datetime.datetime.strptime(row['speechdate'][:19],('%Y-%m-%d %H:%M:%S'))
                    h = ""
                    if thedate < datetime.datetime(2016, 5, 1):
                        h = row['hid']
                    else:
                        h = 'ca.proc.d.'+(str(thedate)[:10])+"."+row["source_id"]
                    print(h)
                    try:
                        b = basehansard.objects.get(hid = h)
                    except:
                        strdate = (str(thedate)[:10])
                        if strdate in problemdates:
                            problemdates[strdate] += 1
                        else:
                            problemdates[strdate] = 1
                    b.subsubtopic = sst
                    b.save()

        print("Import finished. Date failures and counts:")
        print(problemdates)

