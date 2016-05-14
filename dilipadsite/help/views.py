from __future__ import absolute_import, division, print_function, unicode_literals

from django.conf import settings
from django.core.paginator import InvalidPage, Paginator
from django.shortcuts import get_object_or_404, render, render_to_response
from dilipadsite.models import basehansard
from natsort import natsorted
import datetime, operator

# most recent hansard

# explore by year

def index(request):
    return render_to_response('help/index.html')


