from django.core.management.base import BaseCommand, CommandError
from dilipadsite.models import *
import datetime
import re
import string
import os
import unicodecsv as csv
import io
from lxml import etree

class WeirdXMLError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Command(BaseCommand):
    help = 'Imports all member data data from the dilipad XML data dumps, no args needed'

    # Tree looks like this by default (ie. nearly identical to on the cs server, except for OP data.)
    #
    # canada/
    #   ca-members/
    #      ca.m.1.xml
    #      ...
    #   ca-parties/
    #      ca.p.partynamehere.xml
    #      ...
    #   ca-proc/
    #      ca.proc.d.1901-01-01.xml
    #      ...
    #   ca-proc-new/
    #      ca.proc.d.19940117-1011_1994-01-01.xml
    #      ...
    #   constituency_file.tsv
    
    def handle(self, *args, **options):
        
        datafile = "constituency_file.tsv"
        self.importRidings(datafile)
        self.stdout.write('Successfully imported "%s"' % datafile)

    def importRidings(self, datafile):
        '''imports kaspar's constituency file to a django model'''

        path = os.path.join(os.getcwd(), "canada")

        with io.open (os.path.join(path, datafile), 'rb') as csvfile:
            reader = csv.DictReader(csvfile, delimiter='\t')
            counter = 1
            for row in reader:
                c = counter
                b, created = constituency.objects.get_or_create(cid = c)
                counter += 1
                b.riding=row['Riding']
                b.province=row['Province']
                b.opid=row['MemberID']
                b.partyname=row['PartyName']
                b.partyref=row['PartyRef']
                b.dateelected=datetime.datetime.strptime(row['DateElected'],('%Y-%m-%d')).date()
                b.save()
