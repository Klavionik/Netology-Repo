from django.shortcuts import render, redirect

from .models import Phone


def ordering(param):
    orders = {'name': 'name',
              'min_price': 'price',
              'max_price': '-price'}
    return orders[param]


def index(request):
    return redirect(show_catalog)


def show_catalog(request):
    template = 'catalog.html'
    sort_param = request.GET.get('sort')

    if not sort_param:
        sort_param = 'name'

    catalog = Phone.objects.order_by(ordering(sort_param))
    context = {'phones': catalog}

    return render(request, template, context)


def show_product(request, slug):
    template = 'product.html'

    phone = Phone.objects.get(slug=slug)
    context = {'phone': phone}
    return render(request, template, context)
