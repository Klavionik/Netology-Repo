from django.contrib import admin

from .forms import ReviewAdminForm
from .models import Car, Review


class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'review_count')
    list_filter = ('brand', 'model')
    ordering = ('brand',)

    def review_count(self, obj):
        return obj.review_count()
    review_count.short_description = 'Количество обзоров'


class ReviewAdmin(admin.ModelAdmin):
    form = ReviewAdminForm
    list_display = ('car', 'title')
    search_fields = ('car__model', 'title')
    ordering = ('-id',)


admin.site.register(Car, CarAdmin)
admin.site.register(Review, ReviewAdmin)
