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
        
        for datadir in ["ca-members-missing"]:
            self.importMember(datadir)


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

    def importMember(self, datadir):
        '''imports re-downloaded and postprocessed scraped ParlINFO files to fill in missing members and update data if necessary'''

        def fileLoop(file,path): # helper function allowing sanitycheck to break
            
            with open (os.path.join(path, file), 'rb') as xmlfile:

                doc = etree.parse(xmlfile)
                root =  doc.getroot()

                # stop throwing out senators because they may have been in the house earlier

##                senator = False # throw out senators 
##
##                for child in root.findall('pm:member//pm:memberships//pm:membership',root.nsmap):
##                    try:
##                        body = child.attrib['{http://www.politicalmashup.nl}body']
##                        if body == "senate":
##                            senator = True
##                    except:
##                        pass
##
##                if senator is True:
##                    return

                m = ""
                mpid = ""
                firstname = ""
                lastname = ""
                fulltitle = ""
                gender = ""
                profession = []
                website = ""
                emailaddress = ""
                birthdate = None
                deceaseddate = None
                op_slug = ""

                for child in root.findall('pm:member//pm:name//pm:first',root.nsmap):
                    firstname = self.stringify_children(child)

                    
                for child in root.findall('pm:member//pm:name//pm:last',root.nsmap):
                    lastname = self.stringify_children(child)

                for child in root.findall('pm:member',root.nsmap):
                    m = child.attrib['{http://www.politicalmashup.nl}id']

                    if firstname == "Dr": # doctor manual fix (just have to watch the output here, alas)
                        print("DOCTOR FIRSTNAME ERROR FIXME " + m)

                    time.sleep(2)
                    mpid = m
                    firstname_strip = unidecode(firstname)
                    if len(firstname_strip.split()) >= 2:
                        if len(firstname_strip.split()[1].replace(".", ""))==1:
                            firstname_strip = firstname_strip.split()[0]
                    lastname_strip = unidecode(lastname)

                    website = "http://www.lop.parl.gc.ca/ParlInfo/Files/Parliamentarian.aspx?Item="+mpid+"&Language=E"

                for child in root.findall('pm:member//pm:personal//pm:born',root.nsmap):
                    try:
                        birthdate = child.attrib['{http://www.politicalmashup.nl}date']
                        if birthdate =="":
                            birthdate = None
                    except KeyError:
                        birthdate = None

                for child in root.findall('pm:member//pm:personal//pm:deceased',root.nsmap):
                    try:
                        deceaseddate = child.attrib['{http://www.politicalmashup.nl}date']
                        if deceaseddate =="":
                            deceaseddate = None
                        elif "Record of death" in deceaseddate:
                            deceaseddate = None
                    except KeyError:
                        deceaseddate = None


                for child in root.findall('pm:member//pm:curriculum//pm:extra-curricular//pm:name',root.nsmap):
                    professions = self.stringify_children(child)
                    try:
                        profession = professions.lower().split(", ")
                    except:
                        profession.append(professions.lower())

                for child in root.findall('pm:member//pm:name//pm:full',root.nsmap):
                    fulltitle = self.stringify_children(child)

                for child in root.findall('pm:member//pm:personal//pm:gender',root.nsmap):
                    gender = self.stringify_children(child)

                speakerurl = ("http://www.parl.gc.ca/parlinfo/Files/Parliamentarian.aspx?Item="+mpid+"&Language=E&Section=ALL")

                b, created = member.objects.update_or_create(pid = mpid, defaults = {'firstname':firstname,
                                                                                     'lastname':lastname.upper(),
                                                                                     'fulltitle':fulltitle,
                                                                                     'gender':gender,
                                                                                     'profession':profession,
                                                                                     'website':website,
                                                                                     'emailaddress':emailaddress,
                                                                                     'birthdate':birthdate,
                                                                                     'deceaseddate':deceaseddate,
                                                                                     'op_slug':op_slug
                                                                                     })
                if created is False:
                    pass  # most in this case are going to already exist; we'll keep track of the created members instead

                else:
                    print("Successfully created file for missing person: "+mpid)
                    
                    
                # now create constituency records for this person

                datesDict = {}

                for child in root.findall('pm:member//pm:memberships//pm:membership',root.nsmap):

                    try:

                        body = child.attrib['{http://www.politicalmashup.nl}body']

                        if body == "other":
                            pn = child.attrib['{http://www.politicalmashup.nl}party-name']
                            sd = ""
                            ed = ""
                            for period in child:
                                try:
                                    sd = datetime.datetime.strptime(period.attrib['{http://www.politicalmashup.nl}from'],'%Y-%m-%d')
                                    if "present" in (period.attrib['{http://www.politicalmashup.nl}till']):
                                        ed = None
                                    else:
                                        ed = datetime.datetime.strptime(period.attrib['{http://www.politicalmashup.nl}till'],'%Y-%m-%d')
                                except ValueError:
                                    print("Truncated datetime in file "+m)

                            if sd in datesDict:
                                datesDict[sd].append(PartyInstance(sd,ed,pn))
                            else:
                                datesDict[sd]=[PartyInstance(sd,ed,pn)]

                        elif body == "commons":
                            sd = ""
                            ed = ""
                            r = child.attrib['{http://www.politicalmashup.nl}district']
                            p = child.attrib['{https://openparliament.ca/extra}province']
                            for period in child:
                                sd = datetime.datetime.strptime(period.attrib['{http://www.politicalmashup.nl}from'],'%Y-%m-%d')
                                if "present" in (period.attrib['{http://www.politicalmashup.nl}till']):
                                    ed = None
                                else:
                                    ed = datetime.datetime.strptime(period.attrib['{http://www.politicalmashup.nl}till'],'%Y-%m-%d')

                            if sd in datesDict:
                                datesDict[sd].append(RidingInstance(sd,ed,r,p))
                            else:
                                datesDict[sd]=[RidingInstance(sd,ed,r,p)]

                    except KeyError:
                        pass

                        # this is a position, ie. ministerial, so create a position object
                        ##################### commenting this out for now because there are issues with Prime Ministers, and it will be redone on its own in a future pass!

##                        epd = None
##                        spd = None
##                        pnm = ''
##
##                        for period in child:
##
##                            try:
##                                spd = datetime.datetime.strptime(period.attrib['{http://www.politicalmashup.nl}from'],'%Y-%m-%d')
##                                if "present" in (period.attrib['{http://www.politicalmashup.nl}till']):
##                                    epd = None
##                                else:
##                                    epd = datetime.datetime.strptime(period.attrib['{http://www.politicalmashup.nl}till'],'%Y-%m-%d')
##                            except KeyError:
##                                try:
##                                    pnm = period.text
##                                except KeyError:
##                                    pass
##                                
##                        psn, created = position.objects.get_or_create(pid = member.objects.get(pid=mpid),
##                                                      positionname = pnm,
##                                                      startdate = spd,
##                                                      enddate = epd)

                try:
                    for child in root.findall('pm:member//openpx:party-affiliation',root.nsmap):
                        sd = ""
                        ed = ""
                        pn = child.attrib['{http://www.politicalmashup.nl}party-name']
                        for period in child:
                            sd = datetime.datetime.strptime(period.attrib['{http://www.politicalmashup.nl}from'],'%Y-%m-%d')
                            if "present" in (period.attrib['{http://www.politicalmashup.nl}till']):
                                ed = None
                            else:
                                ed = datetime.datetime.strptime(period.attrib['{http://www.politicalmashup.nl}till'],'%Y-%m-%d')
                                                                
                        if sd in datesDict:
                            datesDict[sd].append(PartyInstance(sd,ed,pn))
                        else:
                            datesDict[sd]=[PartyInstance(sd,ed,pn)]
                            
  
                except KeyError:
                    # this is an old-style file, so we don't need to do anything here
                    pass

                timeline = sorted(list(datesDict.keys()))
                current_party = None
                current_riding = None

                for key_date in timeline:
                    if len(datesDict[key_date])>=2: # there was a party and riding change on this date
                        for date_item in datesDict[key_date]:
                            if "party" in date_item.instance_type():
                                current_party = date_item
                            elif "riding" in date_item.instance_type():
                                current_riding = date_item
                                
                        # now create record for this transition, with the soonest end date of the two

                        if current_riding.get_enddate() is None:
                            if current_party.get_enddate() is None:
                                end = None
                            else:
                                end = current_party.get_enddate()
                        elif current_party.get_enddate() is None:
                            end = current_riding.get_enddate()

                        elif current_riding.get_enddate() <= current_party.get_enddate():
                            end = current_riding.get_enddate()

                        elif current_riding.get_enddate() > current_party.get_enddate():
                            end = current_party.get_enddate()

                        else:
                            raise NameError('Unanticipated ending date error...')

                        c, created = constituency.objects.update_or_create(riding = current_riding.get_riding(),
                                                        province = current_riding.get_province(),
                                                        pid = mpid, # this is still kept from the above politician's processing
                                                        partyid = current_party.get_partyobj(m),
                                                        startdate = key_date,
                                                        enddate = end)

                        
                            

                    else:
                        if "party" in datesDict[key_date][0].instance_type():
                            current_party = datesDict[key_date][0]

                            if current_riding is not None:
                                c, created = constituency.objects.update_or_create(riding = current_riding.get_riding(),
                                                    province = current_riding.get_province(),
                                                    pid = mpid, # this is still kept from the above politician's processing
                                                    partyid = current_party.get_partyobj(m),
                                                    startdate = key_date,
                                                    enddate = current_riding.get_enddate())

                            
                        elif "riding" in datesDict[key_date][0].instance_type():
                            current_riding=datesDict[key_date][0]
                            
                            if current_party is not None:
                                c, created = constituency.objects.update_or_create(riding = current_riding.get_riding(),
                                                        province = current_riding.get_province(),
                                                        pid = mpid,
                                                        partyid = current_party.get_partyobj(m),
                                                        startdate = key_date,
                                                        enddate = current_riding.get_enddate())
                            else:
                                print("No party error for " + m)
                                
                        else:
                            raise NameError('Unanticipated type of date event error...')
       

        path = os.path.join(BASE_DIR, "canada", datadir)
        lst = os.listdir(path)
        lst.sort()
        for file in lst:
            print(file)
            fileLoop(file,path)

