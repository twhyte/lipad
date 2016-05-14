from django import template
import calendar

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
