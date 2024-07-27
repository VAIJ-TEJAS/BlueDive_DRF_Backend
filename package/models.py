from django.db import models

class BreakFastOption(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class LunchOption(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class DinnerOption(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class RoomSharingOption(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class WaterSportOption(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Package(models.Model):
    name = models.CharField(max_length=200)
    display_price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField()
    breakfast_options = models.ManyToManyField('BreakFastOption', related_name='packages')
    lunch_options = models.ManyToManyField('LunchOption', related_name='packages')
    dinner_options = models.ManyToManyField('DinnerOption', related_name='packages')
    room_sharing_options = models.ManyToManyField('RoomSharingOption', related_name='packages')
    water_sport_options = models.ManyToManyField('WaterSportOption', related_name='packages')

    def __str__(self):
        return self.name
    
class Amenity(models.Model):
    name = models.CharField(max_length=200)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='amenities')

    def __str__(self):
        return self.name
