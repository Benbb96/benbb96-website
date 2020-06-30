from django import template
from django.contrib.messages import DEFAULT_LEVELS

register = template.Library()


@register.filter
def color_class(level):
    if level == DEFAULT_LEVELS['DEBUG']:
        return 'primary'
    if level == DEFAULT_LEVELS['INFO']:
        return 'secondary'
    if level == DEFAULT_LEVELS['SUCCESS']:
        return 'success'
    if level == DEFAULT_LEVELS['WARNING']:
        return 'warning'
    if level == DEFAULT_LEVELS['ERROR']:
        return 'danger'


@register.filter
def youtube_id(link):
    return link.split('/')[-1].split('=')[-1]
