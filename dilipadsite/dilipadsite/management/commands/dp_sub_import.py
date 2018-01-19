from django.core.management.base import BaseCommand, CommandError
from dilipadsite.models import *
import datetime
import re
import string
import os
import csv
import io
from lxml import etree

class WeirdXMLError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Command(BaseCommand):
    help = 'Imports all missing subsubtopics from dilipad xml files'

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
        
        # "ca-proc", 
        for datadir in ["ca-proc"]:
            self.importSub(datadir)
            self.stdout.write('Successfully imported "%s"' % datadir)

    def stringify_children(self,node):
        '''workaround for bug in lxml'''
        s = node.text
        if s is None:
            s = ''
        for child in node:
            s += etree.tostring(child, encoding='unicode')
        return s

    
    def importSub(self, datadir):

        def fileLoop(file,path): # helper function allowing sanitycheck to break
            
            with open (os.path.join(path, file), 'rb') as xmlfile:

                doc = etree.parse(xmlfile)
                root =  doc.getroot()

                sanitycheck = False # testing for committee proceedings and excluding them

                for child in root.findall('pm:proceedings//pm:topic//pm:scene//pm:speech', root.nsmap):
                    try:
                        urltest = child.attrib['{https://openparliament.ca/}url']
                        if "/committees/" in urltest:
                            sanitycheck = True
                    except KeyError:
                        break
                    
                if sanitycheck is True:
                    return

                # we should have a confirmed house debate at this point

                date = ""

                for child in root.findall('meta//dc:date',root.nsmap):
                    date = child.text
                    self.stdout.write('Importing "%s"' % date)   # this is still here just for tracking our progress

                # collects subtopic events (can't really create these yet as events ... but for now we'll just put them in records)

                for child in root.findall('pm:proceedings//pm:topic//pm:scene//dp:subtopic',root.nsmap):
                    sst = child.attrib['{http://www.politicalmashup.nl}title']
                    h = child.attrib['{http://www.politicalmashup.nl}id']
                    # we could create an event here in future
                    self.stdout.write('Subsubtopic "%s"' % sst)

                    for speechchild in child.getiterator(tag='{http://www.politicalmashup.nl}speech'):

                        pid = speechchild.attrib['{http://www.politicalmashup.nl}id']

                        record = basehansard.objects.get(hid = pid)
                        record.subsubtopic = sst
                        record.save()
                    
        path = os.path.join(os.getcwd(), "canada", "ca-proc-updated-10-03-2016")
        lst = os.listdir(path)
        lst.sort()
        for file in lst:
            # adding in simple resume for now
            if int(file[10:14]) >= 1985:
                fileLoop(file,path)
