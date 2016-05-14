from django.core.management.base import BaseCommand, CommandError
from dilipadsite.models import *

class Command(BaseCommand):
    help = 'populates a model datenav containing a date list of all hansarddays, creates the full dictionary, and pickles'

    def handle(self, *args, **options):
        basehansard.objects.filter(opid__isnull=True,pid__isnull=True,
                                   speakeroldname__isnull=True,speakerposition__isnull=True,
                                   maintopic__isnull=True,subtopic__isnull=True,
                                   speechtext__isnull=True,speakerparty__isnull=True,
                                   speakerriding__isnull=True,speakername__isnull=True).delete()
        
