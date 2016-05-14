from django.core.management.base import BaseCommand, CommandError
from dilipadsite.models import *
import datetime
import re
import string
from natsort import natsorted
import os
import csv
import io
from lxml import etree

class WeirdXMLError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Command(BaseCommand):
    help = 'writes basepk final primary key'

    def handle(self, *args, **options):
        '''Creates an int PK to replace the dilipad-style PK, so that we can avoid naturalsort problems later.'''
        viewlist = basehansard.objects.values_list('hid', flat=True)
        order = natsorted(viewlist)
        newpk = 1
        for h in order:
            basehansard.objects.update_or_create(hid = h, defaults = {'basepk':newpk})
            newpk+=1
        
