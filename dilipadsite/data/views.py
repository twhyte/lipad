from __future__ import absolute_import, division, print_function, unicode_literals

from django.shortcuts import render_to_response, render
from django.contrib import messages
from django.http import StreamingHttpResponse
from data.forms import CSVForm
import unicodecsv as csv
from dilipadsite.models import basehansard
import datetime
import calendar

class Echo(object):
    """An object that implements just the write method of the file-like interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

def index(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CSVForm(data=request.POST)
        # check whether it's valid:
        if form.is_valid():
            d = form.cleaned_data['d']
            ed = d.replace(day=calendar.monthrange(d.year, d.month)[1])
            qs = basehansard.objects.filter(speechdate__gte=d).filter(speechdate__lte=ed).order_by('basepk')
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

            filename = "proceedings"+ form.cleaned_data['d'].strftime("%Y-%m")

            response['Content-Disposition'] = ('attachment;filename=%s.csv' % filename)
            #messages.success(request, 'Export successful! Please wait for your file to begin downloading.')
            return (response)
        else:
            form = CSVForm()
            return render(request, 'data/index.html', {'form': form})
    else:
        form = CSVForm()
        return render(request, 'data/index.html', {'form': form})

