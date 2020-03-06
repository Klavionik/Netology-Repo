import os
from datetime import datetime

from django.conf import settings
from django.shortcuts import render

files = settings.FILES_PATH


def file_info(file):
    return file.name, \
           datetime.fromtimestamp(file.stat().st_ctime).date(), \
           datetime.fromtimestamp(file.stat().st_mtime).date()


def file_list(request, date=None):
    template_name = 'index.html'
    context = {'files': [], 'date': date}

    with os.scandir(files) as catalog:
        for entry in catalog:
            if entry.is_file():
                filename, ctime, mtime = file_info(entry)
                if date and (date == ctime):
                    context['files'].append({
                        'name': filename,
                        'ctime': ctime,
                        'mtime': mtime
                    })
                elif not date:
                    context['files'].append({
                        'name': filename,
                        'ctime': ctime,
                        'mtime': mtime
                    })

    return render(request, template_name, context)


def file_content(request, name):
    template_name = 'file_content.html'
    context = {'file_name': 'File Not Found', 'file_content': 'File Not Found'}

    if name in os.listdir(files):
        path = os.path.join(files, name)
        with open(path) as f:
            content = f.read()
            context = {'file_name': name, 'file_content': content}

    return render(
        request,
        template_name,
        context
    )
