from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def urlize_target_blank(text):
    return text.replace('<a ', '<a target="_blank" ')


urlize_target_blank = register.filter(urlize_target_blank, is_safe=True)