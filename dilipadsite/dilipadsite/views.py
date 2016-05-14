import unicodecsv as csv
from dilipadsite.models import basehansard
from django.http import StreamingHttpResponse, HttpResponse
from django.utils.encoding import smart_str
import codecs

class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

def get_model_fields(model):
    return model._meta.fields

##def streaming_csv_old(request, qs, filename):
##    '''This doesn't actually stream--but it works. Pre-generates the .csv
##    Keeping this method around as a backup'''
##    opts = qs.model._meta
##    model = qs.model
##    response = HttpResponse(content_type='text/csv')
##    # force download.
##    response['Content-Disposition'] = ('attachment;filename=%s.csv' % filename)
##    # the csv writer
##    writer = csv.writer(response)
##    field_names = [field.name for field in opts.fields]
##    # Write a first row with header information
##    writer.writerow(field_names)
##    # Write data rows
##    for obj in qs:
##        writer.writerow([getattr(obj, field) for field in field_names])
##    return response

def stream_response_generator(qs):
    """Streaming function to return data iteratively """
    opts = qs.model._meta
    model = qs.model
    field_names = [field.name for field in opts.fields]
    yield (field_names)
    for obj in qs:
        yield([getattr(obj, field) for field in field_names])

def streaming_csv(request, qs, filename):
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(row) for row in stream_response_generator(qs)),
                                     content_type="text/csv")
    response['Content-Disposition'] = ('attachment;filename=%s.csv' % filename)
    return response
