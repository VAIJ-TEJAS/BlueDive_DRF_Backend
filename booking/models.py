from django.db import models
from django.contrib.auth.models import User
from trip.models import Trip

class Booking(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='bookings')
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='bookings')
    advance_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    complete_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('Partially Confirmed', 'Partially Confirmed'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ], default='Pending')
    scuba_included = models.BooleanField(default=False)

    def __str__(self):
        return f"Booking by {self.user.username} for {self.trip.package.name} on {self.booking_date}"

class PaxRecord(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='pax_records')
    pax = models.IntegerField()

    def __str__(self):
        return f"Pax record for booking {self.booking}"

class CustomerDetail(models.Model):
    pax_record = models.ForeignKey(PaxRecord, on_delete=models.CASCADE, related_name='customer_details')
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    pick_up_point = models.CharField(max_length=255)
    meal_option = models.CharField(max_length=50)
    meal_option_id = models.IntegerField(null=True, blank=True)
    watersports_option = models.CharField(max_length=50)
    package_cost = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_package_cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.pax_record.booking.trip.package.name}"

class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    payment_id = models.CharField(max_length=100)
    order_id = models.CharField(max_length=100)
    signature = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[
        ('Created', 'Created'),
        ('Authorized', 'Authorized'),
        ('Captured', 'Captured'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded')
    ], default='Created')
    payment_method = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.payment_id} for booking {self.booking.id}"