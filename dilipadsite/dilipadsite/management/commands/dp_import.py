from django.core.management.base import BaseCommand, CommandError
from dilipadsite.models import *
import datetime
import re
import string
import os
import csv
import io
from lxml import etree

####################
# Note that this import has not been updated to also parse subsubtopics

class WeirdXMLError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Command(BaseCommand):
    help = 'Imports all hansard data to 1993 from the dilipad XML data dump, no args needed; replaces a bunch of old migration utilities.'

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
            self.importProc(datadir)
            self.stdout.write('Successfully imported "%s"' % datadir)

    def stringify_children(self,node):
        '''workaround for bug in lxml'''
        s = node.text
        if s is None:
            s = ''
        for child in node:
            s += etree.tostring(child, encoding='unicode')
        return s

    def the_lion_clean(self,inputstr):
        '''Everyone's favourite OCR error gets nuked here'''
        
        contentstr = inputstr
        contentstr = contentstr.replace("The lion,", "The hon.")
        contentstr = contentstr.replace("My lion,", "My hon.")
        contentstr = contentstr.replace("my lion,", "my hon.")
        contentstr = contentstr.replace("the lion,", "the hon.")

        leading = re.compile("^\.\s{1}[A-Z]")

        if re.match(leading, contentstr) is not None:
            contentstr = contentstr[2:]
        
        return contentstr
    
    def importProc(self, datadir):
        '''imports ca-proc files to database basehansard objects.  There's a lot of repetition but given
        our xml or db standard may change in the future I think it's worth keeping verbose'''

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
                    self.stdout.write('Importing "%s"' % date)   # date is the same whatever type of event this is, so we just keep it

                    
                # collects and creates stagedirection events
                
                for child in root.findall('pm:proceedings//pm:topic//pm:stage-direction//pm:p',root.nsmap):
                    content = self.stringify_children(child)
                    h = child.attrib['{http://www.politicalmashup.nl}id'] 
                    
                    try:
                        pid = child.attrib['{http://www.politicalmashup.nl}speaker-id']
                    except KeyError:
                        pid = ""
                         
                    speakerposition = 'stagedirection'

                    try:
                        opid = child.attrib['{http://www.politicalmashup.nl}member-ref']
                    except KeyError:
                        opid = ""

                    try:
                        speakeroldname = child.attrib['{http://dilipad.history.ac.uk}speaker-old']
                    except KeyError:
                        speakeroldname = ''

                    try:
                        speakername = child.attrib['{http://www.politicalmashup.nl}speaker']
                    except:
                        speakername = ""

                    b, created = basehansard.objects.update_or_create(hid = h, defaults = {'speechtext':content,
                                                                   'speechdate':date,
                                                                   'speakeroldname':speakeroldname,
                                                                    'speakerurl':'',
                                                                    'speakername':speakername,
                                                                   'speakerposition':speakerposition,
                                                                   'pid':pid,
                                                                   'opid':opid,'maintopic':'','subtopic':'', 'speakerparty':'', 'speakerriding':'','basepk' :0})

                # in newer OP files there are stage directions within scenes as well, so handle these
                # NOTE stagedirections are ALLLLL messed up in the new files so this is commented out

                # instead just use own opdump rather than the pm conversion
##                
##                for child in root.findall('pm:proceedings//pm:topic//pm:scene//pm:stage-direction//pm:p',root.nsmap):
##                    content = self.stringify_children(child)
##                    h = child.attrib['{http://www.politicalmashup.nl}id'] 
##                    
##                    try:
##                        pid = child.attrib['{http://www.politicalmashup.nl}speaker-id']
##                    except KeyError:
##                        pid = ""
##                         
##                    speakerposition = 'stagedirection'
##
##                    try:
##                        opid = child.attrib['{http://www.politicalmashup.nl}member-ref']
##                    except KeyError:
##                        opid = ""
##
##                    try:
##                        speakeroldname = child.attrib['{http://dilipad.history.ac.uk}speaker-old']
##                    except KeyError:
##                        speakeroldname = ''
##
##                    try:
##                        speakername = child.attrib['{http://www.politicalmashup.nl}speaker']
##                    except:
##                        speakername = ""
##
##                    b, created = basehansard.objects.update_or_create(hid = h, defaults = {'speechtext':content,
##                                                                   'speechdate':date,
##                                                                   'speakeroldname':speakeroldname,
##                                                                    'speakername':speakername,
##                                                                   'speakerposition':speakerposition,
##                                                                   'pid':pid,
##                                                                   'opid':opid,'maintopic':'','subtopic':'', 'speakerparty':''})
##


                # collects and creates main topic events

                maintopic = ""
                subtopic = ""

                for child in root.findall('pm:proceedings//pm:topic',root.nsmap):
                    maintopic = child.attrib['{http://www.politicalmashup.nl}title']
                    content = ''
                    
                    h = child.attrib['{http://www.politicalmashup.nl}id']
                    
                    try:
                        pid = child.attrib['{http://www.politicalmashup.nl}speaker-id']
                    except:
                        pid = ""

                    try:
                        speakername = child.attrib['{http://www.politicalmashup.nl}speaker']
                    except:
                        speakername = ""
                    
                    speakerposition = 'topic'

                    try:
                        speakeroldname = child.attrib['{http://dilipad.history.ac.uk}speaker-old']
                    except KeyError:
                        speakeroldname = ''

                    try:
                        opid = child.attrib['{http://www.politicalmashup.nl}member-ref']
                    except KeyError:
                        opid = ''

                    b, created = basehansard.objects.update_or_create(hid = h, defaults = {'speechtext':content,
                                           'speechdate':date,
                                           'speakeroldname':speakeroldname,
                                           'speakerposition':speakerposition,
                                               'speakerurl':'',                                            
                                           'pid':pid,
                                            'opid':opid,'maintopic':maintopic,'subtopic':'', 'speakerparty':'', 'speakerriding':'','speakername':speakername, 'basepk' :0})

                    for speechchild in child.getiterator(tag='{http://www.politicalmashup.nl}speech'):
                        # some speeches don't have a scene due to ocr errors--handle these here.
                        # make sure they have a topic but no subtopic.

                        content = []
                        speakerold = ""
                        opid = ''
                        h = speechchild.attrib['{http://www.politicalmashup.nl}id']
                        try:
                            pid = speechchild.attrib['{http://dilipad.history.ac.uk}speaker-id']
                        except KeyError:
                            pid = ''

                        try:
                            opid = speechchild.attrib['{http://www.politicalmashup.nl}member-ref']
                        except KeyError:
                            opid = ''

                        try:
                            speakerposition = speechchild.attrib['{http://www.politicalmashup.nl}function']
                        except KeyError:
                            speakerposition = ''

                        try:
                            speakerparty = speechchild.attrib['{http://www.politicalmashup.nl}party']
                        except KeyError:
                            speakerparty = ''
                            
                        try:
                            speakeroldname = speechchild.attrib['{http://dilipad.history.ac.uk}speaker-old']
                        except KeyError:
                            speakeroldname = ''

                        try:
                            speakername = speechchild.attrib['{http://www.politicalmashup.nl}speaker']
                        except:
                            speakername = ""
                        
                        for item in speechchild.findall('pm:p', root.nsmap):
                            content.append(self.stringify_children(item))

                        contentstr = ""
                
                        for p in content:
                            if type(p) is str:
                                contentstr = contentstr + p + "\n\n"

                        contentstr = self.the_lion_clean(contentstr)

                        # adding in the url

                        pattern = re.compile(".{8}-.{4}-.{4}-.{4}-.{12}")

                        if re.match(pattern, pid) is not None:
                            speakerurl= ("http://www.parl.gc.ca/parlinfo/Files/Parliamentarian.aspx?Item="+pid+"&Language=E&Section=ALL")
                        elif re.match(pattern, opid) is not None:
                            speakerurl= ("http://www.parl.gc.ca/parlinfo/Files/Parliamentarian.aspx?Item="+opid+"&Language=E&Section=ALL")
                        else:
                            speakerurl = ""
                            
                        b, created = basehansard.objects.update_or_create(hid = h, defaults = {'speechtext':contentstr,
                                                                                               'speechdate':date,
                                                                                               'speakeroldname':speakeroldname,
                                                                                               'speakerposition':speakerposition,
                                                                                               'speakerurl':speakerurl,
                                                                                               'pid':pid,
                                                                                               'opid':opid,
                                                                                               'maintopic':maintopic,
                                                                                               'subtopic':'', 'basepk': 0,'speakerparty':speakerparty,'speakerriding':'', 'speakername':speakername})
                    
                    for subtopicchild in child.getiterator(tag='{http://www.politicalmashup.nl}scene'):
                        # collects and creates sub topic events
                        #  -- this is new and may not cover every case properly yet hence WeirdXMLError
                        # old loop was for child in root.findall('pm:proceedings//pm:topic//pm:scene',root.nsmap):

                        h = subtopicchild.attrib['{http://www.politicalmashup.nl}id']

                        try:
                            subtopic = subtopicchild.attrib['{http://www.politicalmashup.nl}title']
                            content = ''

                        except KeyError: # this is a speech... maybe?

                            if subtopicchild.tag=='{http://www.politicalmashup.nl}speech':
                                
                                raise WeirdXMLError('A speech without a subtopic broke stuff here at "%s"' % h) 
                            
                                #for speechchild in subtopicchild.getiterator(tag='{http://www.politicalmashup.nl}speech'):
                            
                            else:
                                subtopic = ""
                                # these look to be old scene "topics" with no real topic.. a political mashup standardization thing maybe?
                                # should be find with a blank subtopic for the time being.
                                
                                # raise WeirdXMLError('Something unidentified in the XML broke stuff at "%s"' % h)
                            

                        try:
                            pid = subtopicchild.attrib['{http://www.politicalmashup.nl}speaker-id']
                        except:
                            pid = ""
                        
                        speakerposition = 'subtopic'

                        try:
                            speakeroldname = subtopicchild.attrib['{http://dilipad.history.ac.uk}speaker-old']
                        except KeyError:
                            speakeroldname = ''

                        try:
                            speakername = subtopicchild.attrib['{http://www.politicalmashup.nl}speaker']
                        except:
                            speakername = ""

                        try:
                            opid = subtopicchild.attrib['{http://www.politicalmashup.nl}member-ref']
                        except KeyError:
                            opid = ''

                        b, created = basehansard.objects.update_or_create(hid = h, defaults = {'speechtext':content,
                           'speechdate':date,
                           'speakeroldname':speakeroldname,
                           'speakerposition':speakerposition,
                           'pid':pid, "speakerurl":"",'opid':opid,'maintopic':maintopic,'speakerriding':'','subtopic':subtopic,'speakername':speakername,'speakerparty':'', 'basepk':0})


                        # while we're in this subtopic, collect and create hansard events
                        # this now takes place within the subtopic loop so that every speech has an attached topic and subtopic!
                        # again here's the old loop just in case:
                        # for child in root.findall('pm:proceedings//pm:topic//pm:scene//pm:speech', root.nsmap):

                        for speechchild in subtopicchild.getiterator(tag='{http://www.politicalmashup.nl}speech'):

                            content = []
                            speakerold = ""
                            opid = ''
                            h = speechchild.attrib['{http://www.politicalmashup.nl}id']
                            try:
                                pid = speechchild.attrib['{http://dilipad.history.ac.uk}speaker-id']
                            except KeyError:
                                pid = ''

                            try:
                                opid = speechchild.attrib['{http://www.politicalmashup.nl}member-ref']
                            except KeyError:
                                opid = ''

                            try:
                                speakerposition = speechchild.attrib['{http://www.politicalmashup.nl}function']
                            except KeyError:
                                speakerposition = ''

                            try:
                                speakerparty = speechchild.attrib['{http://www.politicalmashup.nl}party']
                            except KeyError:
                                speakerparty = ''

                            try:
                                speakername = speechchild.attrib['{http://www.politicalmashup.nl}speaker']
                            except:
                                speakername = ""
                                
                            try:
                                speakeroldname = speechchild.attrib['{http://dilipad.history.ac.uk}speaker-old']
                            except KeyError:
                                speakeroldname = ''
                            
                            for item in speechchild.findall('pm:p', root.nsmap):
                                content.append(self.stringify_children(item))

                            contentstr = ""
                    
                            for p in content:
                                if type(p) is str:
                                    contentstr = contentstr + p + "\n\n"

                            contentstr = self.the_lion_clean(contentstr)

                            pattern = re.compile(".{8}-.{4}-.{4}-.{4}-.{12}")

                            if re.match(pattern, pid) is not None:
                                speakerurl= ("http://www.parl.gc.ca/parlinfo/Files/Parliamentarian.aspx?Item="+pid+"&Language=E&Section=ALL")
                            elif re.match(pattern, opid) is not None:
                                speakerurl= ("http://www.parl.gc.ca/parlinfo/Files/Parliamentarian.aspx?Item="+opid+"&Language=E&Section=ALL")
                            else:
                                speakerurl = ""

                            # parsing and preprocessing complete!  Now write speech to DB.

                            b, created = basehansard.objects.update_or_create(hid = h, defaults = {'speechtext':contentstr,
                                                                                                   'speechdate':date,
                                                                                                   'speakeroldname':speakeroldname,
                                                                                                   'speakername':speakername,
                                                                                                   'speakerposition':speakerposition,
                                                                                                   'speakerurl':speakerurl,
                                                                                                   'pid':pid,
                                                                                                   'opid':opid,
                                                                                                   'maintopic':maintopic,
                                                                                                   'subtopic':subtopic,'speakerparty':speakerparty,'speakerriding':'', 'basepk' : 0})

        path = os.path.join(os.getcwd(), "canada", "ca-proc-updated-10-03-2016")
        lst = os.listdir(path)
        lst.sort()
        for file in lst:
            fileLoop(file,path)
