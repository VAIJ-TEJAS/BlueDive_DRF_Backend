from django.db import models
from package.models import Package

class Trip(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Omitted', 'Omitted'),  
    ]

    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='trips')
    start_date = models.DateField()
    end_date = models.DateField()
    available_seats = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    free_scuba_days_limit = models.PositiveIntegerField(default=30) 
    discount_limit = models.PositiveIntegerField(default=15)

    def __str__(self):
        return f"Trip for {self.package.name} from {self.start_date} to {self.end_date} with {self.available_seats} seats ({self.status})"
