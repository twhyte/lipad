from django.core.management.base import BaseCommand, CommandError
from dilipadsite.models import *
import datetime
import time
import re
import backoff
import urllib2
import simplejson as json

class Command(BaseCommand):
    help = "DANGER: Nukes and repulls all entries from last extant date in the database to a specified start date --startdate (default 2016-5-1)."
    def add_arguments(self, parser):
        parser.add_argument(
            '--startdate',
            type=str,
            action='store',
            dest='startdate',
            default='2016-5-1',
        )
        
    def handle(self, *args, **options):
        startdate = datetime.date(2016, 5, 1)
        if options['startdate']:
            startdate = datetime.datetime.strptime(options['startdate'], "%Y-%m-%d")
        enddate = basehansard.objects.latest('speechdate').speechdate
        if enddate is None:
            qs = basehansard.objects.order_by('-speechdate')
            enddate = qs[1].speechdate

        days_past_value = (startdate.date()-enddate).days
        
        self.nukeDebates(startdate, enddate)
        print ("Debates between %s and %s deleted. Refetching...") % (startdate.isoformat(), enddate.isoformat())
        
        for td in range(days_past_value):
            hansard_date = startdate + datetime.timedelta(days=td)
            hansard_url = self.checkDate(hansard_date)
            while hansard_url is not None:
                time.sleep(5)
                hansard_url=self.fetchDebates(hansard_url)      

##            
##    @backoff.on_exception(backoff.expo,
##                          urllib2.URLError,
##                          max_value=32)
    
    def url_open(self, url):
        return urllib2.urlopen(url)
            
    def fetchParse(self,purl):
        fetchurl = "http://api.openparliament.ca"+purl+"&format=json"
        req = urllib2.Request(fetchurl, headers={ 'User-Agent': 'tanya.whyte@mail.utoronto.ca' })
        resp = self.url_open(req)
        return json.loads(resp.read())

    def nukeDebates(self, startdate, enddate):
        basehansard.objects.filter(speechdate__range=[startdate, enddate]).delete()
        
    def fetchPolParse(self,purl):
        fetchurl = "http://api.openparliament.ca"+purl+"?&format=json"
        req = urllib2.Request(fetchurl, headers={ 'User-Agent': 'tanya.whyte@mail.utoronto.ca' })
        resp = self.url_open(req)
        return json.loads(resp.read())
    
    def checkDate (self, dateobj):
        '''Returns url of debate if openparliament API has a debate on this day, else False'''
        dateURL = ("http://api.openparliament.ca/debates/"+ str(dateobj.year)+ "/" + str(dateobj.month)+ "/" + str(dateobj.day)+ "/?format=json")
        print ("Checking " + str(dateobj.year)+ "/" + str(dateobj.month)+ "/" + str(dateobj.day))
        req = urllib2.Request(dateURL, headers={ 'User-Agent': 'tanya.whyte@mail.utoronto.ca' })
        try:
            resp = self.url_open(req)
        except urllib2.HTTPError as e:
            if e.code==404:
                print ("404 no debate here")
                return None

        print ("Debate found here.")
        
        parse=json.loads(resp.read())
        baseURL = parse.get('related').get('speeches_url')
        print (baseURL +'&limit=500')
        return (baseURL +'&limit=500')        
            
    def fetchDebates (self, aurl):
        parse=self.fetchParse(aurl)
        print("Fetching " + aurl)
            
        for speech in parse.get('objects'):
            strdate = (speech.get("time")).split(" ")[0]
            h = 'ca.proc.d.'+strdate+"."+speech.get("source_id")
            b, created = basehansard.objects.get_or_create(hid = h)
            if created is True:
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
                    # lookup pid from members table
                    slug = polparse.get("url")
                    try:
                        memobj = member.objects.get(op_slug=(slug[:-1]))
                    except:
                        print ("member lookup failed for "+polparse.get("name")+" at url " + slug)
                    b.pid = memobj.pid
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
                    
                b.save()
                
        print("Finished offset.")
        next_url = parse.get('pagination').get('next_url')
        return next_url
                    
            
            
            

