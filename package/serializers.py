from rest_framework import serializers

from trip.serializers import TripSerializer
from .models import (
    Option, Event, Day, EventRecord, DayRecord, Package,
    Meal, PaxOptions, MealRecords, Vehicle, VehicleImage,
    Accommodation, AccommodationImage
)

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = '__all__'

class EventRecordSerializer(serializers.ModelSerializer):
    event = EventSerializer()
    day = serializers.StringRelatedField()

    class Meta:
        model = EventRecord
        fields = '__all__'

class DaySerializer(serializers.ModelSerializer):
    event_records = EventRecordSerializer(many=True, read_only=True)

    class Meta:
        model = Day
        fields = '__all__'

class DayRecordSerializer(serializers.ModelSerializer):
    day = DaySerializer()

    class Meta:
        model = DayRecord
        fields = '__all__'

class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = '__all__'

class PaxOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaxOptions
        fields = '__all__'

class MealRecordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealRecords
        fields = '__all__'

class VehicleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImage
        fields = '__all__'

class VehicleSerializer(serializers.ModelSerializer):
    images = VehicleImageSerializer(many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = '__all__'

class AccommodationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccommodationImage
        fields = '__all__'

class AccommodationSerializer(serializers.ModelSerializer):
    images = AccommodationImageSerializer(many=True, read_only=True)

    class Meta:
        model = Accommodation
        fields = '__all__'

class PackageSerializer(serializers.ModelSerializer):
    day_records = DayRecordSerializer(many=True, read_only=True)
    meals = MealSerializer(many=True, read_only=True)
    pax_options = PaxOptionsSerializer(many=True, read_only=True)
    meal_records = MealRecordsSerializer(many=True, read_only=True)
    vehicle = VehicleSerializer(read_only=True)
    accommodation = AccommodationSerializer(read_only=True)

    class Meta:
        model = Package
        fields = '__all__'

class PackageOverviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = '__all__'

class PackageTripsSerializer(serializers.ModelSerializer):
    trips = TripSerializer(many=True, read_only=True)
    class Meta:
        model = Package
        fields = '__all__'