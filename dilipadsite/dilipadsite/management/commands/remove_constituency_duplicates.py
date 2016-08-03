from django.core.management.base import BaseCommand, CommandError
from dilipadsite.models import *

class Command(BaseCommand):
    help = 'clears duplicated constituency entries'

    def handle(self, *args, **options):
        qs = constituency.objects.filter(enddate='2015-08-02').filter(startdate='2011-05-02')
        for row in qs:
            if qs.filter(riding=row.riding).count() > 1:
                row.delete()

        
