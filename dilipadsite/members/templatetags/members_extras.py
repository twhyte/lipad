from django import template
import ast

register = template.Library()

# Formatting for profession list

@register.filter
def prof_fix(string):
    l = ast.literal_eval(string)
    l = [i.strip() for i in l]
    return (', '.join(l))

