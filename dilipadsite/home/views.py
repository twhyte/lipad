from django.contrib.messages import success
from django.shortcuts import render, redirect
from django.template import Context
from home.forms import ContactForm
from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from andablog.models import Entry

def index(request):
    b = Entry.objects.last()
    return render(request, 'home/index.html',
                  {'blog': b})

def front_search(request):
    return render(request, 'search/search.html')



