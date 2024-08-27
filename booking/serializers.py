from rest_framework import serializers

from trip.serializers import TripSerializer
from .models import Booking

class BookingSerializer(serializers.ModelSerializer):
    trip = TripSerializer()
    class Meta:
        model = Booking
        fields = '__all__'

class BookingOverviewSerializer(serializers.ModelSerializer):
    trip = TripSerializer()
    class Meta:
        model = Booking
        fields = ['id', 'trip', 'status']

