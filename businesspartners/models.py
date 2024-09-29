from django.db import models
from django.contrib.auth.models import User

class BusinessPartnerProfile(models.Model):
    STATUS_CHOICES = [
        ('Requested', 'Requested'),
        ('Active', 'Active'),
        ('Declined', 'Declined'),
        ('Deactivated', 'Deactivated'),
        ('Suspended', 'Suspended'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    pan_no = models.CharField(max_length=10)  
    adhaar_no = models.CharField(max_length=12) 
    address = models.TextField()
    contact_no = models.CharField(max_length=15) 
    whatsapp_no = models.CharField(max_length=15) 
    email = models.EmailField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Requested')

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.status}"
