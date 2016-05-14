from __future__ import absolute_import, division, print_function, unicode_literals

from django.conf import settings
from django.core.paginator import InvalidPage, Paginator
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.template import RequestContext
from dilipadsite.models import basehansard, datenav, datePickle
from dilipadsite.views import streaming_csv
from natsort import natsorted
import datetime, operator
import calendar
import unicodecsv as csv
from django.utils.six.moves import range
from django.http import StreamingHttpResponse
from django.template import Context, loader
from django.http import HttpResponse, Http404
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist as DoesNotExist
from digg_paginator import DiggPaginator

# most recent hansard

# explore by year

def index(request):
    timeline = datePickle.objects.all()[0].fullmap
            
    return render_to_response('full/index.html', 
              {'timeline':timeline.items})

def year_view(request, year):

    def get_next_year_link(y):
        if y+1 < 2017: 
           n = y+1
           return ("/full/"+str(n)+"/")
        else:
            return ""

    def get_previous_year_link(y):
        if y-1 > 1900:
            n = y-1
            return ("/full/"+str(n)+"/")
        else:
            return ""

    def monthFix(n):
        m = str(n)
        if len(m)<=1:
            m="0"+m
        return (m)

        
    qs = datenav.objects.filter(hansarddate__year=year).order_by('hansarddate').values('month').distinct()
    monthSet = set()
    for result in qs:
        monthSet.add(result['month'])
    x = list(monthSet)
    monthList = []
    for m in x:
        monthList.append((monthFix(m),calendar.month_name[m]))
        
    context = {'year':year, 'dates':monthList, 'next':get_next_year_link(int(year)), 'previous':get_previous_year_link(int(year))}
    return render_to_response('full/year.html', context)

def month_view(request, year, month):
    qs = datenav.objects.filter(hansarddate__year=year).filter(hansarddate__month=month).order_by('hansarddate').distinct().values_list('hansarddate')

    first = qs[0]
    last = qs.reverse()[0]
    lastdatenav = datenav.objects.get(hansarddate=last[0])
    firstdatenav = datenav.objects.get(hansarddate=first[0])

    try:
        nextdatenav = lastdatenav.get_next_by_hansarddate()

    except DoesNotExist:
        nextdatenav = ""

    try:
        prevdatenav = firstdatenav.get_previous_by_hansarddate()

    except DoesNotExist:
        prevdatenav = ""

    def yieldURL(datenav, currentnavobj):

        datenavobj = datenav

        if datenavobj == "":
            datenavobj = currentnavobj

        y = str(datenavobj.year)
        m = str(datenavobj.month)

        if len(m)<=1:
            m="0"+m

        return ("/full/"+y+"/"+m+"/")

    nextnav = yieldURL(nextdatenav, lastdatenav)
    prevnav = yieldURL(prevdatenav, firstdatenav)
                                      
    context = {'year':year, 'month': month, 'monthname':calendar.month_name[int(month)], 'dates':qs, 'next':nextnav, 'previous':prevnav}
    return render_to_response('full/month.html', context)

def hansard_view(request, year, month, day, pageno):
    y=int(year)
    m=int(month)
    d=int(day)
    dateobj = datetime.date(y,m,d)
    
    qs = basehansard.objects.filter(speechdate=dateobj).order_by('basepk').all()
    
    paginator = DiggPaginator(qs, 20, body=5, tail=2, padding=2)
    thisday = qs[1].speechdate
    
    datenavobject = datenav.objects.get(hansarddate=thisday)
    
    storage = messages.get_messages(request)

    baseurl=("/full/"+str(year)+"/"+str(month)+"/"+str(day)+"/")
    if len(storage) == 0:

        try:
            context = {'year':year, 'baseurl':baseurl, 'month':month, 'day':day, 'hansard':qs, 'next':datenavobject.get_next_day_link(), 'paginator': paginator, 'page':paginator.page(pageno), 'pageno':pageno, 'previous':datenavobject.get_previous_day_link()}
        except InvalidPage:
            raise Http404("Page does not exist")

    else:
        refer_pk = None
        for m in storage:
            refer_pk = m.message
            break
        try:
            context = {'year':year, 'month':month, 'baseurl':baseurl, 'day':day, 'hansard':qs, 'next':datenavobject.get_next_day_link(), 'paginator': paginator, 'page':paginator.page(pageno), 'pageno':pageno, 'previous':datenavobject.get_previous_day_link(), 'refer_pk':refer_pk}
        except InvalidPage:
            raise Http404("Page does not exist")
        
    return render_to_response('full/hansard.html', context, context_instance=RequestContext(request))

def hansard_day_redirect(request, year, month, day):
    '''Redirects a plain old date to first page'''
    y=str(year)
    m=str(month)
    d=str(day)
    return redirect("/full/"+y+"/"+m+"/"+d+"/1/")

def hansard_full_view_redirect(request, year, month, day, pk):
    y=int(year)
    m=int(month)
    d=int(day)
    dateobj = datetime.date(y,m,d)
    qs = basehansard.objects.filter(speechdate=dateobj).order_by('basepk').all()
    firstpk = int(qs[0].basepk)

    intpk = int(pk)

    pageNo = ((intpk-firstpk)//20)+1

    # request.session['refer_pk'] = pk  alternate way of storing refer_pk
    messages.add_message(request, messages.INFO, pk)

    return redirect("/full/"+year+"/"+month+"/"+day+"/"+str(pageNo)+"#"+str(intpk))

def full_csv_export_view(request, year, month, day):
    y=int(year)
    m=int(month)
    d=int(day)
    dateobj = datetime.date(y,m,d)
    qs = basehansard.objects.filter(speechdate=dateobj).order_by('basepk').all()
    filename = "proceedings"+str(year)+"_"+str(month)+"_"+str(day)
    return streaming_csv(request, qs, filename)

def permalink_view(request, pk):
    """Permalink to basepk"""
    qs = basehansard.objects.get(basepk=pk)
    return render_to_response('full/perma.html', 
              {'obj':qs})



