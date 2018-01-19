# coding: utf-8

from django.core.management.base import BaseCommand, CommandError
from dilipadsite.models import *
from dilipadsite.settings import BASE_DIR
import datetime
import re
import string
import os
import csv
import io
from lxml import etree
import urllib2
import simplejson as json
import time
from unidecode import unidecode
from dilipadsite.models import DoesNotExist
from django.core.exceptions import MultipleObjectsReturned
from exceptions import KeyError, ValueError

class WeirdXMLError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class RidingInstance(object):
    def __init__(self, startdate, enddate, riding, province):
        self.startdate = startdate
        self.enddate = enddate
        self.riding = riding
        self.province = province

    def get_startdate(self):
        return self.startdate

    def get_enddate(self):
        return self.enddate

    def get_riding(self):
        return self.riding

    def get_province(self):
        return self.province

    def instance_type(self):
        return "riding"

class PartyInstance(object):
    def __init__(self, startdate, enddate, partyname):
        self.startdate = startdate
        self.enddate = enddate
        self.partyname = partyname

    def get_startdate(self):
        return self.startdate

    def get_enddate(self):
        return self.enddate

    def get_partyname(self):
        return self.partyname

    def get_partyobj(self, m):
        '''Translates a partyname into a partyid'''

        x, created = party.objects.get_or_create(name=self.get_partyname(), defaults={'partyid':(party.objects.all().last().partyid + 1),
                                                                                      'colour':"#777777",
                                                                                      'wiki':"https://en.wikipedia.org/wiki/List_of_federal_political_parties_in_Canada",
                                                                                      'abbrev':'?'})
        return(x)


    
    def instance_type(self):
        return "party"

class Command(BaseCommand):
    help = 'Imports re-downloaded and postprocessed scraped ParlINFO files to fill in missing members'
    
    def handle(self, *args, **options):
        
        for datadir in ["ca-members-parlinfo"]:
            self.import_position(datadir)

    def url_open(self, url):
        return urllib2.urlopen(url)

    def stringify_children(self,node):
        '''workaround for bug in lxml'''
        s = node.text
        if s is None:
            s = ''
        for child in node:
            s += etree.tostring(child, encoding='unicode')
        return s

    def import_position(self, datadir):
        '''imports positions from downloaded parlinfo files (corrects problem with positions from earlier
    member files)'''

        def fileLoop(file,path):
            
            with open (os.path.join(path, file), 'rb') as xmlfile:

                doc = etree.parse(xmlfile)
                root =  doc.getroot()
                mpid = file.split('.')[0]

                for child in root.findall('pm:member//pm:memberships//pm:membership',root.nsmap):

                    # Prime Ministers and potentially other positions were missed in the first pass
                    # this is a second pass with different source files as a double-check

                    epd = None
                    spd = None
                    pnm = ''
                    body=''
                    try:
                        body=child.attrib['{http://www.politicalmashup.nl}body'] # throws out senate and commons memberships

                    except KeyError:

                        for period in child:
                            if period.text is None:
                                try:
                                    spd = datetime.datetime.strptime(period.attrib['{http://www.politicalmashup.nl}from'],'%Y-%m-%d')
                                except ValueError:
                                    print('From date error ('+period.attrib['{http://www.politicalmashup.nl}from']+") in "+mpid)
                                    return
  
                                if "present" in (period.attrib['{http://www.politicalmashup.nl}till']):
                                    epd = None
                                else:
                                    try:
                                        epd = datetime.datetime.strptime(period.attrib['{http://www.politicalmashup.nl}till'],'%Y-%m-%d')
                                    except ValueError:
                                        print('Till date error ('+period.attrib['{http://www.politicalmashup.nl}till']+") in "+mpid)
                                        return
                            else:
                                pnm = period.text


                        if period.text:
                            try:
                                psn, created = position.objects.update_or_create(pid = member.objects.get(pid=mpid),
                                                              positionname = pnm,
                                                              startdate = spd,
                                                            defaults={'enddate':epd})
                                    
                            except DoesNotExist:
                                pass

                            except MultipleObjectsReturned:
                                print("Multiple objects returned for"+mpid) # debugging code
   

        path = os.path.join(BASE_DIR, "canada", datadir)
        lst = os.listdir(path)
        lst.sort()
        for file in lst:
            fileLoop(file,path)

