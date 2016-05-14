from django.core.management.base import BaseCommand, CommandError
from dilipadsite.models import *
import datetime
import time
import re
import backoff
import urllib2
import simplejson as json

class Command(BaseCommand):
    help = "Checks and updates the current date and yesterday's date (as a doublecheck) Hansard from openparliament API."

    def handle(self, *args, **options): # sorry this is horrible but it has to be ready today, I'll make it cleaner later ok
        today = datetime.datetime.now()
        yesterday = today - datetime.timedelta(days=1)
        yesterday2 = today - datetime.timedelta(days=2)
        yesterday3 = today - datetime.timedelta(days=3)
        
        todayURL = self.checkDate(today)
        time.sleep(5)
        yesterdayURL = self.checkDate(yesterday)
        time.sleep(5)
        yesterday2URL = self.checkDate(yesterday2)
        time.sleep(5)
        yesterday3URL = self.checkDate(yesterday3)
            
        if todayURL != False:
            self.fetchDebates(todayURL)
                    
        time.sleep(5)
            
        if yesterdayURL != False:
            self.fetchDebates(yesterdayURL)

        time.sleep(5)

        if yesterday2URL != False:
            self.fetchDebates(yesterday2URL)

        time.sleep(5)

        if yesterday3URL != False:
            self.fetchDebates(yesterday3URL)
                    
##            
##    @backoff.on_exception(backoff.expo,
##                          urllib2.URLError,
##                          max_value=32)
    
    def url_open(self, url):
        return urllib2.urlopen(url)
            
    def fetchParse(self,purl):
        fetchurl = "http://api.openparliament.ca"+purl+"&format=json"
        req = urllib2.Request(fetchurl)
        resp = self.url_open(req)
        return json.loads(resp.read())

    def fetchPolParse(self,purl):
        fetchurl = "http://api.openparliament.ca"+purl+"?&format=json"
        req = urllib2.Request(fetchurl)
        resp = self.url_open(req)
        return json.loads(resp.read())
    
    def checkDate (self, dateobj):
        '''Returns url of debate if openparliament API has a debate on this day, else False'''
        dateURL = ("http://api.openparliament.ca/debates/"+ str(dateobj.year)+ "/" + str(dateobj.month)+ "/" + str(dateobj.day)+ "/?format=json")
        print ("Checking " + str(dateobj.year)+ "/" + str(dateobj.month)+ "/" + str(dateobj.day))
        req = urllib2.Request(dateURL)
        try:
            resp = self.url_open(req)
        except urllib2.HTTPError as e:
            if e.code==404:
                print ("404 no debate here")
                return False

        print ("Debate found here.")
        
        parse=json.loads(resp.read())
        baseURL = parse.get('related').get('speeches_url')
        print (baseURL +'&limit=100000')
        return (baseURL +'&limit=100000')        
            
    def fetchDebates (self, aurl):
        parse=self.fetchParse(aurl)
        print("Fetching " + aurl)
            
        for speech in parse.get('objects'):
            strdate = (speech.get("time")).split(" ")[0]
            h = 'ca.proc.d.'+strdate+"."+speech.get("source_id")
            b, created = basehansard.objects.get_or_create(hid = h)
            if created is True:
                print(h)
                ss = speech.get("content").get("en")
                b.speechtext=re.sub(re.compile('<[^<]+?>'), '', ss)
                    
                b.speechdate=datetime.datetime.strptime(speech.get('time'),('%Y-%m-%d %H:%M:%S'))
                    
                attribution = speech.get("attribution").get('en')

                if speech.get('politician_url') is None:
                    b.speakername = attribution
                    b.speakerriding=""
                    b.opid = ""
                    b.speakerurl = ""
                    b.speakerid = ""

                    if b.speakername == "":
                        if speech.get("source_id")[0]=="p":
                            b.speakerposition="stagedirection"
                        else:
                            b.speakerposition=""
                    else:
                        b.speakerposition=""
                else:
                    polparse = self.fetchPolParse(speech.get('politician_url'))
                    b.speakername = polparse.get("name")
                    b.speakerurl = polparse.get("links")[0].get("url")
                    memberships = polparse.get("memberships")
                    for membership in memberships:
                        if membership.get("end_date") is None:
                            b.speakerriding = membership.get("riding").get("name").get("en")
                            b.speakerparty=membership.get("party").get("short_name").get("en")
                            b.opid = int(polparse.get("links")[0].get("url").split("/")[-1].split("?")[-1].split("&")[0].split("=")[-1])
                            b.speakerposition = ""
                            b.speakeroldname=attribution

                if "Some" in attribution:
                    if "hon." in attribution:
                        b.speakerposition="intervention"

                elif "An" in attribution:
                    if "hon." in attribution:
                        b.speakerposition="intervention"

                try:
                    b.maintopic = speech.get("h1").get("en")
                except AttributeError:
                    b.maintopic = ""
                try:
                    b.subtopic = speech.get("h2").get("en")
                except AttributeError:
                    b.subtopic = ""
                    
                
                b.pid = None # need to write something to gather these from the existing db opids(?)
                b.save()
                    
            
            
            

