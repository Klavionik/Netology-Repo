from datetime import datetime

from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def format_date(value):
    datetime_obj = datetime.fromtimestamp(value, tz=timezone.get_current_timezone())
    now = timezone.localtime()
    delta = now - datetime_obj
    if delta.seconds < 600:
        return 'Только что'
    if delta.seconds < 86400:
        hour = int(delta.seconds / 60 / 60)
        if hour % 10 == 1:
            return f'{hour} час назад'
        elif 2 <= hour % 10 <= 4:
            return f'{hour} часа назад'
        else:
            return f'{hour} часов назад'
    else:
        return f'{datetime_obj.year}-{datetime_obj.month}-{datetime_obj.day}'


@register.filter
def format_score(value):
    if value < -5:
        return "Все плохо"
    if -5 <= value <= 5:
        return "Нейтрально"
    if value > 5:
        return "Хорошо"


@register.filter
def format_num_comments(value):
    if value == 0:
        return "Оставьте комментарий"
    if 0 <= value <= 50:
        return value
    if value > 50:
        return "50+"
    return value


@register.filter
def format_selftext(value, count=None):
    if not count:
        return value

    words = value.split()
    beginning = ' '.join(words[:count])
    end = ' '.join(words[len(words) - count:])
    return f'{beginning} ... {end}'
