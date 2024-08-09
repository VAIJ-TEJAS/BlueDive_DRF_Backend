from django.db import models

class Accommodation(models.Model):
    name = models.CharField(max_length=200)
    details = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class Vehicle(models.Model):
    name = models.CharField(max_length=200)
    details = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class Package(models.Model):
    code = models.CharField(max_length=100, null=True, blank=True)
    cover_image = models.ImageField(upload_to='package_cover_images/', null=True, blank=True)
    duration = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    display_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, related_name='packages', null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='packages', null=True, blank=True)

    def __str__(self):
        return self.name

class Day(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='days', null=True, blank=True)

    def __str__(self):
        return f"{self.name} in Package {self.package.name if self.package else 'No Package'}"

class Event(models.Model):
    name = models.CharField(max_length=200)
    standard_option = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='events', null=True, blank=True)

    def __str__(self):
        return f"Standard Option: {self.standard_option if self.standard_option else 'None'} - {self.name} in Package {self.package.code if self.package else 'No Package Code'}"

class Option(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='options', null=True, blank=True)

    def __str__(self):
        return self.name

class EventRecord(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_records')
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='event_records')

    def __str__(self):
        return f"EventRecord for Event {self.event.name} on {self.day}"

class DayRecord(models.Model):
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='day_records')
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='day_records')

    def __str__(self):
        return f"DayRecord for {self.day}"

class Meal(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class PaxOptions(models.Model):
    pax = models.IntegerField()
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='pax_options', null=True, blank=True)

    def __str__(self):
        return f"PaxOptions for Package {self.package.name if self.package else 'No Package'}"

class MealRecords(models.Model):
    pax_option = models.ForeignKey(PaxOptions, on_delete=models.CASCADE, related_name='meal_records')
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='meal_records')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"MealRecord for {self.meal.name} in PaxOption {self.pax_option.id}"

class VehicleImage(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='vehicle_images/')

    def __str__(self):
        return f"Image for {self.vehicle.name}"

class AccommodationImage(models.Model):
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='accommodation_images/')

    def __str__(self):
        return f"Image for {self.accommodation.name}"

class PackageImages(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='package_images/')

    def __str__(self):
        return f"Image for Package {self.package.name}"