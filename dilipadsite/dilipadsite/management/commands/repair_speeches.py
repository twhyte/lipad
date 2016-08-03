from django.core.management.base import BaseCommand, CommandError
from dilipadsite.models import *
import datetime
import re
import string
from natsort import natsorted
import os
import csv
import StringIO

class Command(BaseCommand):
    help = "Uses Ludovic's speech repair code to fix linebreak issues in all speechtexts."

    def handle(self, *args, **options):

        def clean(obj):
            text = obj.speechtext
            # The following replaces lines ending with hyphenation, with no spacing.
            text = text.replace('-\n','')
            # Remove double linebreaks
            # text = text.replace('\n\n','\n')
            # Yet another lion clean.
            text = text.replace('right lion,','right hon.')
            text = text.replace('hou. member','hon. member')
            # Removes long sequences of spacing left during parsing and encodes.						
            text = re.sub('\s{2,}', ' ',text)
            # Again removes redundant spacing that may have been introduced in previous steps.
            text = re.sub('\s{2,}', ' ', text)
            # Removes punctuation at the beginning of the speech.
            if text.startswith(": ") or text.startswith(", ") or text.startswith("; ") or text.startswith(". "):
                text = text[2:]
            obj.speechtext = text
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
                
        qs = basehansard.objects.all()
        spoonfeed(qs,clean)


        
