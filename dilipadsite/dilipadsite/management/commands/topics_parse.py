from django.core.management.base import BaseCommand, CommandError
from dilipadsite.models import *
import datetime
import re
import string
import os
import csv
import io
import difflib
from lxml import etree

class Command(BaseCommand):
    help = "Writes html diff files for daily topics (dataset vs. new parse)"

    def handle(self, *args, **options):
        self.datadir = "stage_2"
        self.path = os.path.join(os.getcwd(), "canada", self.datadir)
        self.lst = os.listdir(self.path)
        self.lst.sort()
        for file in self.lst:
            namestr = file[5:-4]
            thedate = datetime.datetime.strptime(namestr, "%B_%d_%Y").date()
            
            # reads chronological topic (+sub +subsub) list from stage_2 output files
            # this is a list of strings with no location info
            
            parsedtopics = self.readTopics(file,self.path)

            # gets chronological topic (+..) list from db query
            # these will have already been converted to uppercase
            
            datatopics = self.loadExistingTopics(thedate)

            if not parsedtopics == datatopics:

                d = difflib.HtmlDiff()
                result = d.make_file(datatopics, parsedtopics, "Data", "New Parse")
                writepath = os.path.join(os.getcwd(), "canada", "diff")
                f = open(os.path.join(writepath, (thedate.strftime("%Y_%m_%d")+".html")), 'w')
                f.write(result)
                f.close()
                print("Wrote diff file for %s" % (thedate.strftime("%Y_%m_%d")))

    def stringify_children(self,node):
        '''workaround for bug in lxml'''
        s = node.text
        if s is None:
            s = ''
        for child in node:
            s += etree.tostring(child, encoding='unicode')
        return s

    def readTopics(self, file, path):

        topicslist = []

        with open (os.path.join(path, file), 'rb') as xmlfile:

            doc = etree.parse(xmlfile)
            root =  doc.getroot()

            for element in root.iter():
                try:
                    title = element.get("title")
                    if title == "UNKNOWN TOPIC":
                        pass
                    else:
                        topicslist.append(title)
                except:
                    pass

        return(filter(None,topicslist))

    def loadExistingTopics(self, hdate):
        qs = basehansard.objects.filter(speechdate=hdate).order_by('basepk')
        wtopic = ""
        wsubtopic = ""
        wsubsubtopic = ""

        topicslist = []
        
        for hobject in qs:
            if hobject.speakerposition=="topic":
                wtopic = hobject.maintopic
                wsubtopic = ""
                wsubsubtopic = ""
                topicslist.append(hobject.maintopic)
            elif hobject.speakerposition=="subtopic":
                wsubtopic = hobject.subtopic
                wsubsubtopic = ""
                topicslist.append(hobject.subtopic)
            else:
                if wsubsubtopic == hobject.subsubtopic:
                    pass # nothing has changed; proceed
                else:
                    # the subsubtopic has changed, but not the sub or topic
                    wsubsubtopic = hobject.subsubtopic
                    topicslist.append(hobject.subsubtopic)

        return(filter(None,topicslist))
                    
            
            
            





        

