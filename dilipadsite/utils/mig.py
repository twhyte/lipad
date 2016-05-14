## mig:  helper code for organizing and migrating data from old db, run me from django shell
##
## 1) migrateToWeb() migration from base DB to web DB
## 2) textClean () fixes a few issues such as lion.
## 3) opImport() import from openparliament 1994- data dump csv, query as follows:
##### "SELECT s.sequence, s.document_id, s.time, s.who_en, p.name, s.content_en, a.name, r.name
##### FROM hansards_statement s
##### LEFT JOIN core_electedmember c ON s.member_id = c.id
##### LEFT JOIN core_politician p ON s.politician_id = p.id
##### LEFT JOIN core_party a ON c.party_id = a.id
##### LEFT JOIN core_riding r ON c.riding_id = r.id
##### WHERE (urlcache LIKE '%debates%') AND (urlcache NOT LIKE '%speaker%');"


import datetime, re, io, unicodecsv, gc
from dilipadsite.models import HansardP, HansardSpeechelement, MemberMember, MemberAffiliation, MemberParty, MemberMembership, BaseHansard
# import pdb

class migrateToWeb(object):
    
    def __init__(self):
        for line in HansardSpeechelement.objects.all().iterator():
            h = line.hid
            b, created = BaseHansard.objects.get_or_create(hid = h)
            if created is True:
                t = self.prepare_speech(line)
                d = self.prepare_speechdate(line)
                n = self.prepare_speakername(line)
                r = self.prepare_speakerriding(line)
                p = self.prepare_speakerparty(line)
                b.speechtext=t
                b.speechdate=d
                b.speakername=n
                b.speakerriding=r
                b.speakerparty=p
                b.save()
            elif b.speechdate is None:
                d = self.prepare_speechdate(line)
                if d is not None:
                    b.speechdate = d
                b.save()
            else:
                pass

    def get_model(self):
        return HansardSpeechelement

    def prepare_speech(self, obj):
        prep = ""
        queryset=HansardP.objects.filter(speechid=obj.hid).order_by('hid').values_list('ptext')
        for line in queryset:
            prep = prep + " " + line[0]
        return(prep)

    def prepare_speechdate(self,obj):
        currenthid = obj.hid
        # pdb.set_trace()
        if currenthid is None:
            return(None)
        else:
            result = re.findall(re.compile("\d{4}[-]\d{1,}[-]\d{1,}"),currenthid)
            if len(result)==0:
                return(None)
            else:
                return(datetime.datetime.strptime(result[0], "%Y-%m-%d").date())

    def prepare_speakername(self,obj):
        currenthid = obj.hid
        if currenthid is None:
            return(None)
        elif obj.speakerid is None:
            if obj.meta is None:
                return(None)
            else:
                currentmeta = obj.meta
                st = currentmeta.replace("speaker-name=","")
                currentmeta = st.replace(";speaker-link-result=intervention-or-unparseable;","")
                st = currentmeta
                if "moved :" in currentmeta:
                    st = currentmeta.replace("moved: ","")
                if ";speaker-link-result=unmatched;" in currentmeta:
                    st = currentmeta.replace(";speaker-link-result=unmatched;","")
                return (st)

        elif obj.speakerid is not None:
            return ("%s %s" % (obj.speakerid.firstname, obj.speakerid.lastname))


    def prepare_speakerparty(self,obj):
        currenthid = obj.hid
        if currenthid is None:
            return(None)
        else:
            result = re.findall(re.compile("\d{4}[-]\d{1,}[-]\d{1,}"),currenthid)
            if len(result)==0:
                return(None)
            else:
                objectdate = datetime.datetime.strptime(result[0], "%Y-%m-%d").date()

                queryset = MemberAffiliation.objects.filter(memberid=obj.speakerid).values_list('from_field','to','partyref')

                for line in queryset:
                    if len(line) <3:
                        return(None)
                    else:
                        if objectdate < line[0]:
                            pass
                        elif line[1]=="" or line[1] is None: # this is a current party and this guy is in it
                            currentpartyref = line[2]
                            a = MemberParty.objects.get(ref=currentpartyref)
                            return(a.partyname)
                        elif objectdate >= line[0]:
                            if objectdate <= line[1]:
                                currentpartyref = line[2]
                                a = MemberParty.objects.get(ref=currentpartyref)
                                return(a.partyname)

    def prepare_speakerriding(self,obj):  # yes this duplicate code should be cleaned up.  you caught me. todo.
        currenthid = obj.hid
        if currenthid is None:
            return(None)
        else:
            result = re.findall(re.compile("\d{4}[-]\d{1,}[-]\d{1,}"),currenthid)
            if len(result)==0:
                return(None)
            else:
                objectdate = datetime.datetime.strptime(result[0], "%Y-%m-%d").date()

                queryset = MemberMembership.objects.filter(memberid=obj.speakerid).values_list('from_field','to','district')

                for line in queryset:
                    if len(line) <3:
                        return(None)
                    else:
                        if objectdate < line[0]:
                            pass
                        elif line[1]=="" or line[1] is None: # this is a current district and this guy is in it
                            currentdistrict = line[2]
                            return(currentdistrict)
                        elif objectdate >= line[0]:
                            if objectdate <= line[1]:
                                district = line[2]
                                return(district)



class opImport(object):


    '''sequence,document_id,time,who_en,pol_name,content_en,end_date,start_date,party_name,riding_name'''


    def __init__(self):
        with io.open('opdump.csv','rb') as csvfile:
            reader = unicodecsv.DictReader(csvfile)
            for row in reader:
                h = self.prepare_hid(row)
                b, created = BaseHansard.objects.get_or_create(hid = h)
                if created is True:
                    t = self.prepare_speech(row)
                    d = self.prepare_date(row)
                    n = self.prepare_speakername(row)
                    r = row['riding_name']
                    p = self.prepare_speakerparty(row)
                    b.speechtext=t
                    b.speechdate=d
                    b.speakername=n
                    b.speakerriding=r
                    b.speakerparty=p
                    b.save()
                else:
                    if b.speakername == row['pol_name']:
                        pass
                    elif b.speakername == "" or b.speakername is None:
                        b.speakername = row['who_en']
                        b.save()

                

    def prepare_speech(self,dictline):
        '''strips html'''
        string = dictline['content_en']
        speech = re.sub(re.compile('<[^<]+?>'), '', string)
        return(speech)

    def prepare_date(self,dictline):
        time = (dictline['time'])[:-3]
        datetimeobject = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        return(datetimeobject)
        
    def prepare_hid(self,dictline):
        '''formats date, sequence, and document_id into a unique id in pseudo-dilipad style, eg. ca.proc.d.2004-8-11.document_id.sequence'''
        strdate = (self.prepare_date(dictline)).strftime('%Y-%m-%d')
        hid = 'ca.proc.d.'+strdate+"."+str(dictline['document_id'])+"."+str(dictline['sequence'])
        return(hid)

    def prepare_speakername(self,dictline):
        '''name field combine to include non-politicians'''
        if dictline['pol_name'] == "" or dictline['pol_name'] is None:
            return(dictline['who_en'])
        else:
            return(dictline['pol_name'])

    def prepare_speakerparty(self, dictline):
        '''parties into standard dilipad party names for 94-'''
        party = ""
        
        if dictline['party_name'] is None:
            party = None
        elif "Conservative Party of Canada" in dictline['party_name']:
            party = "Conservative"
        elif "Liberal Party of Canada" in dictline['party_name']:
            party = "Liberal"
        elif "Green Party of Canada" in dictline['party_name']:
            party = "Green"
        elif "Reform Party of Canada" in dictline['party_name']:
            party = "Reform"
        else:
            party = dictline['party_name']
            
        return(party)
                       



def queryset_iterator(queryset, chunksize=1000):
    '''''
    Iterate over a Django Queryset ordered by the primary key

    This method loads a maximum of chunksize (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator does not support ordered query sets.
    '''
    
    pk = 'ca.proc.d.1901-2-11.1.1'
    last_pk = queryset.order_by('-pk')[0].pk
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunksize]:
            pk = row.pk
            yield row
        gc.collect()


class textClean(object):
    
    def __init__(self):
        for b in queryset_iterator(BaseHansard.objects.all()):
            if " lion. " in b.speechtext:
                n = (b.speechtext).replace(" lion. ", " hon. ")
                b.speechtext = n
                b.save()
