from django.core.management.base import BaseCommand, CommandError
from dilipadsite.models import *
import datetime
import gc

class Command(BaseCommand):
    help = "Changes party names from openparliament pull to db standard"
    # also handles David Sweet, for some reason he's broken in the pull

    def handle(self, *args, **options):

        def clean(obj):
            if obj.speakerparty == "Green":
                obj.speakerparty = "Green Party"
                obj.save()
            elif obj.speakerparty == "NDP":
                obj.speakerparty = "New Democratic Party"
                obj.save()
            elif obj.speakerparty == "Bloc":
                obj.speakerparty = u'Bloc Qu\xe9b\xe9cois'
                obj.save()
            if obj.speakername == "David Sweet":
                obj.pid="cad621a1-daf5-4d48-b500-1fc5344b5646"
                obj.save()
            elif obj.speakername == "Glen Motz":
                obj.pid="AD6E8838-A6D5-4D6D-94F7-25180A163C59"
                obj.save()

        dateref = datetime.datetime.now() - datetime.timedelta(days=3) # could change this for retroactive fixes as needed
        qs = queryset_iterator(basehansard.objects.filter(speechdate__gte=dateref))
        for item in qs:
            clean(item)


def queryset_iterator(queryset, chunksize=1000):
    '''''
    Iterate over a Django Queryset ordered by the primary key

    This method loads a maximum of chunksize (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator does not support ordered query sets.
    '''
    pk = 0
    last_pk = queryset.order_by('-basepk')[0].basepk
    queryset = queryset.order_by('basepk')
    while pk < last_pk:
        for row in queryset.filter(basepk__gt=pk)[:chunksize]:
            pk = row.basepk
            yield row
        gc.collect()
            
            
