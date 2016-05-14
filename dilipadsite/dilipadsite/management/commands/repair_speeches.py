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
        idlist = basehansard.objects.all()
        for obj in idlist:
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
        
