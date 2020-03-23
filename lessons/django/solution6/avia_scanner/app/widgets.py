from django.forms.widgets import TextInput, DateInput


class AjaxInputWidget(TextInput):
    template_name = 'widget/ajax_input_widget.html'
    url = ''

    def __init__(self, url, attrs=None):
        """url: путь к ajax API которое будет возвращать список городов для подстановки"""
        super().__init__(attrs)
        self.url = url

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['url'] = self.url
        return context


class DateWidget(DateInput):
    template_name = 'widget/date_widget.html'
