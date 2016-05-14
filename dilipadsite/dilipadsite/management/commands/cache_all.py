from django.core.management.base import BaseCommand, CommandError
from dilipadsite.models import *
from digg_paginator import DiggPaginator

class Command(BaseCommand):
    help = 'Iterates through all basehansard queries to filesystem cache them'

    def handle(self, *args, **options):

        datelist = datenav.objects.values_list('hansarddate', flat=True)
        for date in datelist:
            qs = basehansard.objects.filter(speechdate=date).order_by('basepk').all()
            count = 0
            pagecount = 0
            for obj in qs:
                count +=1

            print("%s: %s objects." % (date,count))

                
                
                
