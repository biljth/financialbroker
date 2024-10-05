from django import template

register = template.Library()

@register.filter
def format_thousands(value):
    if value is not None:
        return "{:,.0f}".format(value).replace(",", ".")
    return value