from django import template

register = template.Library()

@register.filter
def format_price(value):
    """
    Formats the price to include thousand separators with periods.
    Example: 10000.00 -> 10.000
    """
    try:
        formatted_price = "{:,.0f}".format(float(value)).replace(",", ".")
        return formatted_price
    except (ValueError, TypeError):
        return value  # Return the original value if formatting fails