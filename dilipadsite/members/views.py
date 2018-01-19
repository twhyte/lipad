from django.shortcuts import render_to_response, render
from dilipadsite.models import *
from django.http import Http404
import datetime
from digg_paginator import DiggPaginator
import unicodecsv as csv
from django.http import StreamingHttpResponse

def index(request):
    return render(request, 'members/index.html')

def polmap(request):
    return render(request, 'members/map.html')

class Echo(object):
    """An object that implements just the write method of the file-like interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

def record(request, memberpid, pageno):
    try:
        q = member.objects.get(pid=memberpid)
    except member.DoesNotExist:
        raise Http404("Member does not exist.")
    qs = basehansard.objects.filter(pid=memberpid).order_by('-speechdate').all()
    paginator = DiggPaginator(qs, 5, body=5, tail=2, padding=2)
    thedate = datetime.datetime.now().date()
    baseurl = "/members/record/"+memberpid+'/'
    ridings = constituency.objects.filter(pid=memberpid).order_by('startdate').distinct() # this handles duplicates (for now) which need to be culled properly
    ridings_reverse = constituency.objects.filter(pid=memberpid).order_by('-startdate').all()
    try:
        lastparty = ridings_reverse[0].partyid
    except:
        lastparty = party.objects.get(partyid=31)
    try:
        lastconstituency = ridings_reverse[0]
    except:
        lastconstituency = None
    return render_to_response('members/member.html', 
              {'member':q, 'latest':qs, 'ridings':ridings, 'lastparty':lastparty, 'baseurl':baseurl,'paginator': paginator, 'page':paginator.page(pageno), 'pageno':pageno, 'lastconstituency':lastconstituency})

def record_csv_export_view(request, memberpid):
    qs = basehansard.objects.filter(pid=memberpid).order_by('-speechdate').all()
    q = member.objects.get(pid=memberpid)
    filename = "speeches_"+q.lastname
    model_fields = qs.model._meta.fields
    headers = [field.name for field in model_fields]

    def get_row(obj):
        row = []
        for field in model_fields:
            val = getattr(obj, field.name)
            row.append(val)
        return(row)

    def stream(headers,data):
        if headers:
            yield headers
        for obj in data:
            yield get_row(obj)

    pseudo_buffer = Echo()
    writer=csv.writer(pseudo_buffer)
    response = StreamingHttpResponse(
    (writer.writerow(row) for row in stream(headers, qs)),
    content_type="text/csv")
    response['Content-Disposition'] = ('attachment;filename=%s.csv' % filename)
    return (response)
