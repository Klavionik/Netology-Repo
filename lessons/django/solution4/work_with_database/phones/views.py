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
    context = {'phones': []}
    for phone in catalog:
        context['phones'].append(
            {'name': phone.name,
             'price': phone.price,
             'image': phone.image,
             "slug": phone.slug
             })

    return render(request, template, context)


def show_product(request, slug):
    template = 'product.html'

    phone = Phone.objects.get(slug=slug)
    context = {'phone': {
        'name': phone.name,
        'price': phone.price,
        'image': phone.image,
        'release_date': phone.release_date,
        'lte': 'Да' if phone.lte_exists else 'Нет'
    }}
    return render(request, template, context)
