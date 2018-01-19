from django.core.management.base import BaseCommand, CommandError
from dilipadsite.models import *
import datetime
import gc

class Command(BaseCommand):
    help = "Links constituencies to member files with new foreign key"

    def handle(self, *args, **options):

        def link(obj):
            the_pid = obj.pid
            fkmember = member.objects.get(pid=the_pid)
            obj.pid_fk = fkmember
            obj.save()

        # dateref = datetime.datetime.now() - datetime.timedelta(days=3) # change this for retroactive fixes
        qs = constituency.objects.all()
        for item in qs:
            link(item)

            
            
