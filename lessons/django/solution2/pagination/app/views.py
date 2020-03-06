import csv
from urllib.parse import urlencode

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render, redirect
from django.urls import reverse

stations = settings.BUS_STATION_CSV


def next_page_url(page):
    try:
        next_page = page.next_page_number()
    except EmptyPage:
        return None

    base_url = reverse(bus_stations)
    params = urlencode({"page": next_page})
    url = f'{base_url}?{params}'

    return url


def prev_page_url(page):
    try:
        prev_page = page.previous_page_number()
    except EmptyPage:
        return None

    base_url = reverse(bus_stations)
    params = urlencode({"page": prev_page})
    url = f'{base_url}?{params}'

    return url


def read_csv(path):
    file = []

    with open(path, encoding='cp1251', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            file.append({'Name': row['Name'],
                         "Street": row['Street'],
                         'District': row['District']
                         })

    return file


def index(request):
    return redirect(reverse(bus_stations))


def bus_stations(request):
    data = read_csv(stations)
    paginator = Paginator(data, 10)

    current_page_number = request.GET.get('page', 1)
    page = paginator.page(current_page_number)

    page_content = []
    for row in page.object_list:
        page_content.append(row)

    return render(request, 'index.html', context={
        'bus_stations': page_content,
        'current_page': current_page_number,
        'prev_page_url': prev_page_url(page),
        'next_page_url': next_page_url(page),
    })
