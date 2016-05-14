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
    help = 'Imports all hansard data post-1993 from opdump.'
    
    def handle(self, *args, **options):

        path = os.path.join(os.getcwd(), "canada", "opdump.csv")
        
        with io.open(path,'rb') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                h = row['hid']
                b, created = basehansard.objects.get_or_create(hid = h)
                if created is True:
                    b.speechtext=row['speechtext']
                    b.speakeroldname=row['speakeroldname']
                    b.basepk=0
                    b.speechdate=datetime.datetime.strptime(row['speechdate'][:19],('%Y-%m-%d %H:%M:%S'))
                    b.speakername=row['speakername']
                    slugtest = row['slug'].split('-')
                    
                    if "interjection" in row['statement_type']:
                        b.speakerposition="Interjection"
                    
                    elif "some" in slugtest[0]:
                        if "hon" in slugtest[1]:
                            b.speakerposition="intervention"

                    elif "an" in slugtest[0]:
                        if "hon" in slugtest[1]:
                            b.speakerposition="intervention"

                    elif "procedural" in slugtest[0]:
                        b.speakerposition="stagedirection"
                        
                    else:
                        b.speakerposition=""

                    b.speakerriding=row['speakerriding']
                    b.speakerparty=row['speakerparty']
                    b.speakerid =row['speakerid']
                    b.maintopic = row['h1_en']
                    b.subtopic = row['h2_en']
                    b.pid = row['speakerid']
                    b.opid = row['politician_id']

                    if row['speakerid'] != "":
                        b.speakerurl= ("http://www.parl.gc.ca/parlinfo/Files/Parliamentarian.aspx?Item="+row['speakerid']+"&Language=E&Section=ALL")
                    else:
                        b.speakerurl = ""
                        
                    b.save()

