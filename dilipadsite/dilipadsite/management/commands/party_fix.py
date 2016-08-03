from django.core.management.base import BaseCommand, CommandError
from dilipadsite.models import *
import datetime

class Command(BaseCommand):
    help = "Changes party names from openparliament pull to db standard"

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

        def spoonfeed(qs, func, chunk=1000, start=0):
            ''' Chunk up a large queryset and run func on each item.
            Works with automatic primary key fields
            chunk -- how many objects to take on at once
            start -- PK to start from

            >>> spoonfeed(Spam.objects.all(), nom_nom)
            '''
            while start < qs.order_by('pk').last().pk:
                for o in qs.filter(pk__gt=start, pk__lte=start+chunk):
                    func(o)
                start += chunk

        dateref = datetime.datetime.now() - datetime.timedelta(days=4)
        qs = basehansard.objects.filter(speechdate__gte=dateref)
        spoonfeed(qs,clean)

            
            
