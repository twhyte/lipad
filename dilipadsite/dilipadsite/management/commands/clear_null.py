from django.core.management.base import BaseCommand, CommandError
from dilipadsite.models import *

class Command(BaseCommand):
    help = 'clears rows with no content created by openparliament scrape'

    def handle(self, *args, **options):
        basehansard.objects.filter(opid__isnull=True,pid__isnull=True,
                                   speakeroldname__isnull=True,speakerposition__isnull=True,
                                   maintopic__isnull=True,subtopic__isnull=True,
                                   speechtext__isnull=True,speakerparty__isnull=True,
                                   speakerriding__isnull=True,speakername__isnull=True).delete()
        
