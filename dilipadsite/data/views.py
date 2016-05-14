from __future__ import absolute_import, division, print_function, unicode_literals

from django.shortcuts import render_to_response, render
from django.contrib import messages
from django.http import HttpResponseRedirect
from data.forms import CSVForm
from dilipadsite.views import streaming_csv
from dilipadsite.models import basehansard
import datetime

def index(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CSVForm(data=request.POST)
        # check whether it's valid:
        if form.is_valid():
            qs = basehansard.objects.filter(speechdate__gte=form.cleaned_data['sd']).filter(speechdate__lte=form.cleaned_data['ed']).order_by('basepk').all()
            filename = "proceedings"+ form.cleaned_data['sd'].strftime("%Y%m%d")+"_"+form.cleaned_data['ed'].strftime("%Y%m%d")
            messages.success(request, 'Export successful! Please wait for your file to begin downloading.')
            return streaming_csv(request, qs, filename)
    else:
        form = CSVForm()
        return render(request, 'data/index.html', {'form': form})

