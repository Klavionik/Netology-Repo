from django import template

register = template.Library()


@register.filter
def color_class(value):
    try:
        value = float(value)
    except ValueError:
        return ""

    if value < 0:
        return "green darken-1"
    elif 2 > value >= 1:
        return "red lighten-3"
    elif 5 > value >= 2:
        return "red lighten-1"
    elif value >= 5:
        return "red darken-1"
