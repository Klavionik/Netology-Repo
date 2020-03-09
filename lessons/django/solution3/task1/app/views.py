import csv
import os
from django.conf import settings
from django.shortcuts import render


def read_csv(path):
    file = []

    with open(path, encoding='utf8', newline='') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            file.append(row)

    return file


def inflation_view(request):
    template_name = 'inflation.html'
    inflation = read_csv(settings.INFLATION_FILE)
    context = {'head': inflation[0], 'content': inflation[1:]}

    return render(request, template_name,
                  context)
