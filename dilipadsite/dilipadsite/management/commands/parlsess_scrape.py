from django.core.management.base import BaseCommand, CommandError
from dilipadsite.models import *
import datetime
import lxml.html as lh
import urllib2
import re
import string

class Command(BaseCommand):
    help = 'parlsess scrape table from parlinfo'

    def handle(self, *args, **options):
        url='http://www.lop.parl.gc.ca/ParlInfo/compilations/parliament/Sessions.aspx?Language=E'
        doc=lh.parse(urllib2.urlopen(url))
        # first fetch parliament number
        el = doc.xpath("//span[contains(@id, 'lblSectionParliament')]")
        for parl in el:
            ct = parl.attrib['id'].split("_")[-2]
            parltxt = (parl[0].text_content().split(" ")[0].replace("\n", "").replace("\r", "").replace("\t", ""))
            pat = re.compile("^(\d+)")
            parlnum = pat.match(parltxt).group(1)
            sessxpath = "//table[contains(@id, '" + ct+"_grdParliamentSessionsList')]"
            el2 = doc.xpath(sessxpath)
            for sessblock in el2:
                for tr in sessblock:
                    if "GridHeader" in tr.attrib['class']:
                        pass
                    else:
                        datalist = []
                        for td in tr:
                            text = td.text_content().replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")
                            datalist.append(text)
                            
                        sesstxt = datalist[0]
                        sessnum = int(sesstxt[0])
                        startdate = datetime.date(int(datalist[1].split("-")[0].split(".")[0]),
                                                  int(datalist[1].split("-")[0].split(".")[1]),
                                                  int(datalist[1].split("-")[0].split(".")[2]))
                        if datalist[1].split("-")[1]=="":
                            enddate = None
                        else:
                            enddate = datetime.date(int(datalist[1].split("-")[1].split(".")[0]),
                                                      int(datalist[1].split("-")[1].split(".")[1]),
                                                      int(datalist[1].split("-")[1].split(".")[2]))
                        currentid = str(parlnum)+"-"+str(sessnum)
                
                        b, created = parlsess.objects.update_or_create(parlsessid = currentid, defaults={'name': (parltxt + " Parliament, " + sesstxt +" Session"),
                                                                                                      'startdate':startdate,
                                                                                                      'enddate':enddate,
                                                                                                      'parlnum':parlnum,
                                                                                                      'sessnum':sessnum,
                                                                                                      'duration':(int(datalist[2].split('d')[0])),
                                                                                                      'housesittings':(int(datalist[4]))})
                        
                        
                    
                    

        
