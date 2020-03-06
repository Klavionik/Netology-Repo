from datetime import datetime


class DateConverter:
    regex = r'\d{4}-\d{2}-\d{2}'

    def to_python(self, date):
        return datetime.strptime(date, '%Y-%m-%d').date()

    def to_url(self, date):
        return date.strftime('%Y-%m-%d')
