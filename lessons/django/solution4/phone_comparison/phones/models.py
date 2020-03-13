from django.db import models


class Phone(models.Model):

    name = models.CharField(max_length=32)
    price = models.IntegerField()
    os = models.CharField(max_length=32)
    processor = models.CharField(max_length=32)
    ram = models.IntegerField()
    display_size = models.FloatField()
    camera_res = models.IntegerField()
    fast_charge = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name}'


class Samsung(Phone):

    hall_sensor = models.BooleanField(default=False)


class Apple(Phone):

    wireless_charge = models.BooleanField(default=False)
    five_g = models.BooleanField(default=False)


class Honor(Phone):

    radio = models.BooleanField(default=False)



