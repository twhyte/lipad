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
        
        for datadir in ["ca-members"]:
            self.importMember(datadir)
            self.stdout.write('Successfully imported "%s"' % datadir)

    def stringify_children(self,node):
        '''workaround for bug in lxml'''
        s = node.text
        if s is None:
            s = ''
        for child in node:
            s += etree.tostring(child, encoding='unicode')
        return s

    
    def importMember(self, datadir):
        '''imports ca-proc files to database basehansard objects.  There's a lot of repetition but given
        our xml or db standard may change in the future I think it's worth keeping verbose'''

        def fileLoop(file,path): # helper function allowing sanitycheck to break
            
            with open (os.path.join(path, file), 'rb') as xmlfile:

                doc = etree.parse(xmlfile)
                root =  doc.getroot()

                m = ""
                firstname = ""
                lastname = ""
                fulltitle = ""
                pid = ""
                gender = ""
                

                for child in root.findall('pm:member',root.nsmap):
                    m = child.attrib['{http://www.politicalmashup.nl}id']
                    self.stdout.write('Importing "%s"' % m)

                for child in root.findall('pm:member//pm:name//pm:full',root.nsmap):
                    fulltitle = self.stringify_children(child)

                for child in root.findall('pm:member//pm:name//pm:first',root.nsmap):
                    firstname = self.stringify_children(child)
                    
                for child in root.findall('pm:member//pm:name//pm:last',root.nsmap):
                    lastname = self.stringify_children(child)

                for child in root.findall('pm:member//pm:personal//pm:gender',root.nsmap):
                    gender = self.stringify_children(child)

                for link in root.findall('pm:member//pm:links//pm:link',root.nsmap):
                    if u"Parliamentarian.aspx" in link.text:
                        url = link.text
                        pid = url.split("/")[-1]
                        pid = pid.split('&')[0]
                        pid = pid.split('=')[1]

                b, created = member.objects.update_or_create(opid = m, defaults = {'pid':pid,
                                                               'firstname':firstname,
                                                               'lastname':lastname,
                                                                'fulltitle':fulltitle,
                                                               'gender':gender})

        path = os.path.join(os.getcwd(), "canada", datadir)
        lst = os.listdir(path)
        lst.sort()
        for file in lst:
            fileLoop(file,path)
