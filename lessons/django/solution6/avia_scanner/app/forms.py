from django import forms
from django.urls import reverse_lazy

from .models import City
from .widgets import AjaxInputWidget
from .widgets import DateWidget


class SearchTicket(forms.Form):
    departure = forms.CharField(
        widget=AjaxInputWidget(url=reverse_lazy('cities')),
        label='Город отправления')

    arrival = forms.ModelChoiceField(
        queryset=City.objects.all(),
        label='Город прибытия')

    date = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=DateWidget(), label='Дата вылета')
