from django.urls import path, register_converter

from .converters import DateConverter
from .views import file_list, file_content

register_converter(DateConverter, 'date')

urlpatterns = [
    path('', file_list, name='file_list'),
    path('<date:date>/', file_list, name='file_list'),
    path('file/<name>/', file_content, name='file_content'),
]
