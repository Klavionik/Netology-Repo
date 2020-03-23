from django import forms

from .models import City
from .widgets import AjaxInputWidget
from .widgets import DateWidget


class SearchTicket(forms.Form):
    departure = forms.CharField(
        widget=AjaxInputWidget(url='http://localhost:8000/api/city_ajax/'),
        label='Город отправления')

    arrival = forms.ModelChoiceField(
        queryset=City.objects.all(),
        label='Город прибытия')

    date = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=DateWidget(), label='Дата вылета')
