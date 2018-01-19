from django import template
import calendar
from django.template import Library, Node
from django.template.defaultfilters import stringfilter
import re

register = template.Library()

# Friendlier date display helpers

@register.filter
def month_name(month_number):
    return calendar.month_name[month_number]

@register.simple_tag
def url_replace(request, field, value):

    dict_ = request.GET.copy()

    dict_[field] = value

    return dict_.urlencode()

@register.filter
@stringfilter
def paragraphs(value):
    """
    Turns paragraphs delineated with newline characters into
    paragraphs wrapped in <p> and </p> HTML tags.
    """
    paras = re.split(r'[\r\n]+', value)
    paras = ['<p>%s</p>' % p.strip() for p in paras]
    return '\n'.join(paras)
