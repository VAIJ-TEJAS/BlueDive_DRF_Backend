from rest_framework import serializers

from trip.models import Trip
from trip.serializers import TripOverviewSerializer
from .models import Booking, CustomerDetail, PaxRecord, Payment


class CustomerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDetail
        fields = "__all__"
    
    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Name is required")
        return value.strip()
    
    def validate_contact_number(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Contact number is required")
        
        # Remove any non-digit characters for validation
        clean_number = ''.join(filter(str.isdigit, value.strip()))
        
        # Check if it's a valid Indian mobile number (10 digits)
        if len(clean_number) != 10:
            raise serializers.ValidationError("Contact number must be exactly 10 digits")
        
        # Check if it starts with valid Indian mobile prefix (6-9)
        if not clean_number.startswith(('6', '7', '8', '9')):
            raise serializers.ValidationError("Contact number must start with 6, 7, 8, or 9")
        
        return value.strip()


class PaxRecordSerializer(serializers.ModelSerializer):
    customer_details = CustomerDetailSerializer(many=True)

    class Meta:
        model = PaxRecord
        fields = "__all__"
    
    def validate_pax(self, value):
        if not value or value <= 0:
            raise serializers.ValidationError("Pax count must be greater than 0")
        return value


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class BookingSerializer(serializers.ModelSerializer):
    trip = serializers.PrimaryKeyRelatedField(queryset=Trip.objects.all())
    pax_records = PaxRecordSerializer(many=True, read_only=True)
    customer_details = CustomerDetailSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Booking
        fields = "__all__"
    
    def validate_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("Amount cannot be negative")
        return value
    
    def validate_balance_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("Balance amount cannot be negative")
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['trip'] = TripOverviewSerializer(instance.trip).data
        return representation


class BookingOverviewSerializer(serializers.ModelSerializer):
    trip = TripOverviewSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ["id", "trip", "status"]
