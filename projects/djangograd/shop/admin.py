from django.contrib import admin

from shop import models
from shop.forms import ArticleForm


class OrderProducts(admin.TabularInline):
    model = models.OrderProducts


class Articles(admin.TabularInline):
    model = models.Article.products.through


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = (Articles,)
    prepopulated_fields = {'slug': ['title']}


@admin.register(models.Article)
class ArticleAdmin(admin.ModelAdmin):
    inlines = (Articles,)
    exclude = ('products',)
    prepopulated_fields = {'slug': ['title']}
    form = ArticleForm


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['title']}


@admin.register(models.Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['title']}


@admin.register(models.Feedback)
class ReviewAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        OrderProducts
    ]
