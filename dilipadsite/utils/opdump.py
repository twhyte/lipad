import psycopg2
import datetime
import re
import string
import os, sys
import unicodecsv as csv
import io
from dilipadsite.models import basehansard
from django.db import DataError
from natsort import natsorted

DB_NAME = ""
DB_USER = ""
DB_PASS = ""


conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASS)
cursor = conn.cursor()

##SELECT s.sequence, s.document_id, s.politician_id, s.slug, s.h1_en, s.h2_en, s.time, s.who_en, p.name, s.procedural, s.statement_type, s.content_en, a.name, r.name, i.value 
##FROM hansards_statement s 
##LEFT JOIN core_electedmember c ON s.member_id = c.id 
##LEFT JOIN core_politician p ON s.politician_id = p.id 
##LEFT JOIN core_party a ON c.party_id = a.id 
##LEFT JOIN core_riding r ON c.riding_id = r.id 
##LEFT JOIN core_politicianinfo i ON c.politician_id = i.politician_id AND i.schema LIKE 'parlinfo_id' 
##WHERE (urlcache LIKE '%debates%');

def opQuery():
    cursor.execute("SELECT s.sequence, s.document_id, s.time, s.who_en, p.name, s.content_en, a.name, r.name, i.value, s.politician_id, s.slug, s.h1_en, s.h2_en, s.procedural, s.statement_type FROM hansards_statement s LEFT JOIN core_electedmember c ON s.member_id = c.id LEFT JOIN core_politician p ON s.politician_id = p.id LEFT JOIN core_party a ON c.party_id = a.id LEFT JOIN core_riding r ON c.riding_id = r.id LEFT JOIN core_politicianinfo i ON c.politician_id = i.politician_id AND i.schema LIKE 'parlinfo_id' WHERE (urlcache LIKE '%debates%');")

class queryIterator(object):
    def __init__(self):
        pass
    
    def __iter__(self):
        return(self)

    def __next__(self):
        res = cursor.fetchone()
        cleaned = []
        if res == None:
            raise StopIteration
        else:
            result = res
            # formats date, sequence, and document_id into a unique id in pseudo-dilipad style, eg. ca.proc.d.2004-8-11.document_id.sequence
            d = result[2]
            strdate = d.strftime('%Y-%m-%d')
            hid = 'ca.proc.d.'+strdate+"."+str(result[1])+"."+str(result[0])

            cleaned.append(hid)
            print(hid)
            cleaned.append(result[2]) # speechdate
            
            # name field combine to include non-politicians
            if result[4] is "" or result[4] is None:
                cleaned.append(result[3])
                cleaned.append("")
            else:
                cleaned.append(result[4])
                cleaned.append(result[3])

            # parties into standard dilipad party names for 94-
            party = ""

            if result[6] is None:
                party = None
            elif "Conservative Party of Canada" in result[6]:
                party = "Conservative"
            elif "Liberal Party of Canada" in result[6]:
                party = "Liberal"
            elif "Green Party of Canada" in result[6]:
                party = "Green"
            elif "Reform Party of Canada" in result[6]:
                party = "Reform"
            else:
                party = result[6]
                
            cleaned.append(party)

            # strips any html from speech
            ss = result[5]
            speech = re.sub(re.compile('<[^<]+?>'), '', ss)
            cleaned.append(speech)
            cleaned.append(result[7])
            cleaned.append(result[8])
            cleaned.append(result[9])
            cleaned.append(result[10])
            cleaned.append(result[11])
            cleaned.append(result[12])
            cleaned.append(result[13])
            cleaned.append(result[14])


            # s.politician_id, s.slug, s.h1_en, s.h2_en, s.procedural, s.statement_type
            
        return(cleaned)

def djangoqueryset_iterator(queryset, chunksize=1000):
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

def opDumpToFile():
    '''Dumps openparliament db query to a csv to import on another server'''
    with open('opdump', 'wb') as csvfile:
        wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        wr.writerow(['hid', 'speechdate','speakername','speakeroldname','speakerparty','speechtext','speakerriding','speakerid', 'politician_id', 'slug', 'h1_en', 'h2_en', 'procedural', 'statement_type'])
        opQuery()
        q = queryIterator()
        while q:
            wr.writerow(q.__next__())
        cursor.close()
        conn.close()

def opAppend():
    with io.open('opdump','rb') as csvfile:
        reader = unicodecsv.DictReader(csvfile)
        for row in reader:
            h = row['hid']
            b, created = basehansard.objects.get_or_create(hid = h)
            if created is True:
                b.speechtext=row['speechtext']
                b.speechdate=datetime.datetime.strptime(row['speechdate'][:19],('%Y-%m-%d %H:%M:%S'))
                b.speakername=row['speakername']
                b.speakerriding=row['speakerriding']
                b.speakerparty=row['speakerparty']
                b.speakerid =row['speakerid']
                b.save()
            else:
                b.speakerid = str(row['speakerid'])
                b.save()

def masterPK():
    '''Creates an int PK to replace the dilipad-style PK, so that we can avoid naturalsort problems later.'''
    viewlist = basehansard.objects.values_list('hid', flat=True)
    order = natsorted(viewlist)
    newpk = 1
    for h in order:
        basehansard.objects.update_or_create(hid = h, defaults = {'basepk':newpk})
        newpk+=1

def pmAppend():
    ''' for political mashup data converted via pmmigrate
    ['hid','date','pid', 'opid', 'speaker','speakeroldname', 'speakerposition', 'speakerparty','speakerriding','content']'''


    maxInt = sys.maxsize
    decrement = True

    while decrement:
        # decrease the maxInt value by factor 10 
        # as long as the OverflowError occurs.

        decrement = False
        try:
            unicodecsv.field_size_limit(maxInt)
        except OverflowError:
            maxInt = int(maxInt/10)
            decrement = True
    
    with io.open('pmdump.csv','rb') as csvfile:
        reader = unicodecsv.DictReader(csvfile)
        for row in reader:
            h = row['hid']
            b, created = basehansard.objects.update_or_create(hid = h, defaults = {'speechtext':row['content'], 'speechdate':row['date'], 'speakername':row['speaker'],
                'speakeroldname':row['speakeroldname'], 'speakerposition':row['speakerposition'], 'speakerriding':row['speakerriding'], 'speakerparty':row['speakerparty'],
                'pid':row['pid'], 'opid':row['opid']})
##            except DataError:
##                print("Skipped")
##                print (row)

        



      
        
    


    


            
