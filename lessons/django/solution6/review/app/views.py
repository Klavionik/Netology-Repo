from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import View, ListView

from .forms import ReviewForm
from .models import Product, Review


class ProductList(ListView):
    template_name = 'app/product_list.html'
    model = Product


class ProductDetail(View):
    template = 'app/product_detail.html'
    form = ReviewForm

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.pk = kwargs.get('pk')
        self.product = get_object_or_404(Product, id=self.pk)
        self.reviewed_products = request.session.get('reviewed_products', [])
        self.review_exists = self.pk in self.reviewed_products

    def get(self, request, *args, **kwargs):
        reviews = Review.objects.filter(product=self.product)
        context = {
            'form': self.form,
            'product': self.product,
            'reviews': reviews,
            'is_review_exist': self.review_exists
        }

        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        if not self.review_exists:
            bound_form = self.form(request.POST)
            if bound_form.is_valid():
                Review.objects.create(
                    text=bound_form.cleaned_data['text'],
                    product=self.product)
                self.reviewed_products.append(self.pk)
                request.session['reviewed_products'] = self.reviewed_products

        return redirect('product_detail', pk=self.pk)
