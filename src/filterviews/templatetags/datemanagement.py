from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag(takes_context=True)
def generate_date_hierarchy(context):
    objs = context['object_list']
    request = context['request']
    return mark_safe( """<a href="?bingo=1">Esto no se ve</a>""")