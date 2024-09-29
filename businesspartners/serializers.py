from rest_framework import serializers
from .models import BusinessPartnerProfile

class BusinessPartnerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessPartnerProfile
        fields = '__all__'  # You can specify specific fields if needed
