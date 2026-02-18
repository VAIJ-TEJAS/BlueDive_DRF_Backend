from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, RegexValidator, MaxLengthValidator


class Meal(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


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


class PickupPoint(models.Model):
    name = models.CharField(max_length=200)
    location = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name


class WaterSportOption(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Package(models.Model):
    code = models.CharField(max_length=100, null=True, blank=True, validators=[
        RegexValidator(r'^[A-Z0-9-]+$', message='Package code can only contain uppercase letters, numbers, and hyphens')
    ])
    cover_image = models.ImageField(
        upload_to="package_cover_images/", null=True, blank=True
    )
    name = models.CharField(max_length=200, validators=[
        MinLengthValidator(3, message='Package name must be at least 3 characters long'),
        RegexValidator(r'^[a-zA-Z0-9\s\-]+$', message='Package name can only contain letters, numbers, spaces, and hyphens')
    ])
    duration = models.CharField(max_length=200, validators=[
        MinLengthValidator(2, message='Duration must be at least 2 characters long'),
        RegexValidator(r'^\d+\s+(days|day|hours|hour)$', message='Duration must be in format like "3 days" or "2 hours"')
    ])
    description = models.TextField(null=True, blank=True, validators=[
        MaxLengthValidator(2000, message='Description cannot exceed 2000 characters')
    ])
    display_price = models.IntegerField(null=True, blank=True, validators=[
        MinValueValidator(0, message='Display price cannot be negative'),
        MaxValueValidator(999999, message='Display price cannot exceed 999,999')
    ])
    display_discount_percentage = models.IntegerField(null=True, blank=True, validators=[
        MinValueValidator(0, message='Discount percentage cannot be negative'),
        MaxValueValidator(100, message='Discount percentage cannot exceed 100')
    ])
    accommodation = models.ForeignKey(
        Accommodation,
        on_delete=models.SET_NULL,
        related_name="packages",
        null=True,
        blank=True,
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        related_name="packages",
        null=True,
        blank=True,
    )
    pickup_points = models.ManyToManyField(
        PickupPoint, related_name="packages", blank=True
    )
    water_sport_options = models.ManyToManyField(
        WaterSportOption, related_name="packages", blank=True
    )
    default_meal_option = models.ForeignKey(
        Meal,
        on_delete=models.SET_NULL,
        related_name="default_meal_packages",
        null=True,
        blank=True,
    )

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.display_price and self.display_price < 0:
            raise ValidationError('Display price cannot be negative')
        if self.display_discount_percentage and self.display_discount_percentage < 0:
            raise ValidationError('Display discount percentage cannot be negative')

    def __str__(self):
        return self.name


class Day(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name="days", null=True, blank=True
    )

    def __str__(self):
        return f"{self.name} in Package {self.package.name if self.package else 'No Package'}"


class Event(models.Model):
    name = models.CharField(max_length=200)
    standard_option = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name="events", null=True, blank=True
    )

    def __str__(self):
        return f"{self.package.name if self.package else 'None'} - {self.name}"


class Option(models.Model):
    name = models.CharField(max_length=200)
    price = models.IntegerField(null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="options", null=True, blank=True
    )

    def __str__(self):
        return self.name


class EventRecord(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="event_records"
    )
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name="event_records")

    def __str__(self):
        return f"EventRecord for Event {self.event.name} on {self.day}"


class DayRecord(models.Model):
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name="day_records")
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name="day_records"
    )

    def __str__(self):
        return f"DayRecord for {self.day}"


class PaxOptions(models.Model):
    pax = models.IntegerField()
    discount = models.IntegerField(null=True, blank=True)
    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        related_name="pax_options",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"PaxOptions for Package {self.package.name if self.package else 'No Package'}"


class MealRecords(models.Model):
    pax_option = models.ForeignKey(
        PaxOptions, on_delete=models.CASCADE, related_name="meal_records"
    )
    meal = models.ForeignKey(
        Meal, on_delete=models.CASCADE, related_name="meal_records"
    )
    price = models.IntegerField(null=True, blank=True)
    discounted_price = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"MealRecord for {self.meal.name} in PaxOption {self.pax_option.id}"


class VehicleImage(models.Model):
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="vehicle_images/")

    def __str__(self):
        return f"Image for {self.vehicle.name}"


class AccommodationImage(models.Model):
    accommodation = models.ForeignKey(
        Accommodation, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="accommodation_images/")

    def __str__(self):
        return f"Image for {self.accommodation.name}"


class PackageImages(models.Model):
    package = models.ForeignKey(
        Package, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="package_images/")

    def __str__(self):
        return f"Image for Package {self.package.name}"


class FoodOption(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class FoodRecord(models.Model):
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name="food_records")
    meal = models.ForeignKey(
        Meal, on_delete=models.CASCADE, related_name="food_records"
    )

    def __str__(self):
        return f"FoodRecord for Day {self.day.name}"


class MealFoodRecord(models.Model):
    food_record = models.ForeignKey(
        FoodRecord, on_delete=models.CASCADE, related_name="meal_food_records"
    )
    food_options = models.ManyToManyField(FoodOption, related_name="meal_food_records")
    meal_type = models.CharField(
        max_length=10, choices=[("lunch", "Lunch"), ("dinner", "Dinner")]
    )

    def __str__(self):
        return f"MealFoodRecord with {self.food_options.count()} options"
