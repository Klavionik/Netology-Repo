import os
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render, reverse


def home_view(request):
    template_name = 'app/home.html'
    pages = {
        'Главная страница': reverse('home'),
        'Показать текущее время': reverse('time'),
        'Показать содержимое рабочей директории': reverse('workdir')
    }
    context = {
        'pages': pages
    }
    return render(request, template_name, context)


def time_view(request):
    datetime.now()
    current_time = datetime.strftime(datetime.now(), '%X')
    msg = f'Current server time: {current_time}'
    return HttpResponse(msg)


def workdir_view(request):
    msg = f"Current working directory contains: {', '.join(os.listdir('.'))}"
    return HttpResponse(msg)
