from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
import re


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    def clean(self):
        # Validate phone number format
        if self.phone_number:
            if not re.match(r'^\+?1?\d{9,15}$', self.phone_number):
                raise ValidationError('Please enter a valid phone number')
        
        # Validate date of birth is not in future
        if self.date_of_birth and self.date_of_birth > timezone.now().date():
            raise ValidationError('Date of birth cannot be in the future')
    
    def __str__(self):
        return f"{self.user.username}'s Profile"