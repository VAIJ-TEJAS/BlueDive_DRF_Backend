from django.db import models
from django.contrib.auth.models import User  
from trip.models import Trip

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='bookings')
    advance_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    complete_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ], default='Pending')

    def __str__(self):
        return f"Booking by {self.user.username} for {self.trip.package.name} on {self.booking_date}"

    def get_total_amount(self):
        return self.advance_payment + self.complete_payment
