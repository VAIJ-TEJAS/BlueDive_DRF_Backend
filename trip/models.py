from django.db import models
from package.models import Package


class Trip(models.Model):
    STATUS_CHOICES = [
        ("Scheduled", "Scheduled"),
        ("Ongoing", "Ongoing"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
        ("Omitted", "Omitted"),
    ]

    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name="trips")
    start_date = models.DateField()
    end_date = models.DateField()
    available_seats = models.PositiveIntegerField(default=18)
    available_rooms = models.PositiveIntegerField(default=6)  
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="Scheduled"
    )

    def clean(self):
        from django.core.exceptions import ValidationError
        from datetime import date
        
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError('Start date cannot be after end date')
            if self.start_date < date.today():
                raise ValidationError('Start date cannot be in the past')
        
        if self.available_seats < 0:
            raise ValidationError('Available seats cannot be negative')
        if self.available_rooms < 0:
            raise ValidationError('Available rooms cannot be negative')

    def __str__(self):
        return f"Trip for {self.package.name} from {self.start_date} to {self.end_date} with {self.available_seats} seats and {self.available_rooms} rooms ({self.status})"
