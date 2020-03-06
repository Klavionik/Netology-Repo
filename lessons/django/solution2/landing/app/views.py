from collections import Counter

from django.shortcuts import render

counter_show = Counter()
counter_click = Counter()


def index(request):
    if (arg := request.GET.get('from-landing')) == 'test':
        counter_click['test'] += 1
    elif arg == 'original':
        counter_click['original'] += 1
    return render(request, 'index.html')


def landing(request):
    if (arg := request.GET.get('ab-test-arg')) == 'test':
        counter_show['test'] += 1
        return render(request, 'landing_alternate.html')
    elif arg == 'original':
        counter_show['original'] += 1
        return render(request, 'landing.html')
    return render(request, 'landing.html')


def stats(request):
    try:
        test_conv = counter_click['test'] / counter_show['test']
    except ZeroDivisionError:
        test_conv = 0
    try:
        original_conv = counter_click['original'] / counter_show['original']
    except ZeroDivisionError:
        original_conv = 0
    return render(request, 'stats.html', context={
        'test_conversion': test_conv,
        'original_conversion': original_conv,
    })
