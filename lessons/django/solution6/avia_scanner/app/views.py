from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render

from .forms import SearchTicket
from .models import City


def ticket_page_view(request):
    template = 'app/ticket_page.html'

    context = {
        'form': SearchTicket()
    }

    return render(request, template, context)


def cities_lookup(request):
    """Ajax request предлагающий города для автоподстановки, возвращает JSON"""
    term = request.GET.get('term').lower().strip()

    if 'cities' in cache:
        cities = cache.get('cities')
    else:
        cities = [city['name'] for city in City.objects.values('name')]
        cache.set('cities', cities)

    results = [city for city in cities if city.lower().startswith(term)]

    return JsonResponse(results, safe=False)
