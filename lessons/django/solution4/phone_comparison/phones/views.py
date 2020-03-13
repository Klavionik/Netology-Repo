from django.shortcuts import render
from phones.models import Phone


def show_catalog(request):
    for_comparison = Phone.objects.all()
    template = 'catalog.html'
    context = {'phones': for_comparison}
    return render(
        request,
        template,
        context
    )
