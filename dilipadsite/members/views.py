from __future__ import absolute_import, division, print_function, unicode_literals

from django.shortcuts import render_to_response, render
from django.contrib import messages
from django.http import HttpResponseRedirect
from data.forms import CSVForm
from dilipadsite.views import streaming_csv
from dilipadsite.models import basehansard
import datetime

def index(request):
    return render(request, 'members/index.html')

def polmap(request):
    return render(request, 'members/map.html')

def record(request):
    return render(request, 'members/member.html')

