from django.core import validators
from django.db import models


class Phone(models.Model):

    name = models.CharField(max_length=64)
    image = models.TextField()
    price = models.IntegerField()
    release_date = models.DateField()
    lte_exists = models.BooleanField()
    slug = models.CharField(max_length=64, validators=[validators.validate_slug])

    def __str__(self):
        return f'{self.id} {self.name}'
