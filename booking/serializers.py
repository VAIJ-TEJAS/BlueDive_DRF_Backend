from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re
import logging

from trip.models import Trip
from trip.serializers import TripOverviewSerializer
from .models import Booking, CustomerDetail, PaxRecord, Payment

logger = logging.getLogger(__name__)


class CustomerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDetail
        fields = "__all__"
    
    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError(_("Name is required"))
        
        name = value.strip()
        
        # Validate name length
        if len(name) < 2:
            raise serializers.ValidationError(_("Name must be at least 2 characters long"))
        
        if len(name) > 100:
            raise serializers.ValidationError(_("Name cannot exceed 100 characters"))
        
        # Validate name format (letters, spaces, hyphens, apostrophes only)
        if not re.match(r'^[a-zA-Z\s\'\-]+$', name):
            raise serializers.ValidationError(_("Name can only contain letters, spaces, hyphens, and apostrophes"))
        
        return name
    
    def validate_contact_number(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError(_("Contact number is required"))
        
        contact_number = value.strip()
        
        # Remove any non-digit characters for validation
        clean_number = ''.join(filter(str.isdigit, contact_number))
        
        # Check if it's a valid Indian mobile number (10 digits)
        if len(clean_number) != 10:
            raise serializers.ValidationError(_("Contact number must be exactly 10 digits"))
        
        # Check if it starts with valid Indian mobile prefix (6-9)
        if not clean_number.startswith(('6', '7', '8', '9')):
            raise serializers.ValidationError(_("Contact number must start with 6, 7, 8, or 9"))
        
        # Log validation attempt for security monitoring
        logger.info(f"Contact number validation attempted for: {clean_number[:3]}******")
        
        return contact_number
    
    def validate_pick_up_point(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError(_("Pick up point is required"))
        
        pick_up_point = value.strip()
        
        if len(pick_up_point) < 3:
            raise serializers.ValidationError(_("Pick up point must be at least 3 characters long"))
        
        if len(pick_up_point) > 255:
            raise serializers.ValidationError(_("Pick up point cannot exceed 255 characters"))
        
        return pick_up_point
    
    def validate_meal_option(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError(_("Meal option is required"))
        
        meal_option = value.strip()
        
        if len(meal_option) < 2:
            raise serializers.ValidationError(_("Meal option must be at least 2 characters long"))
        
        return meal_option
    
    def validate_package_cost(self, value):
        if value is None:
            return value
        
        if value < 0:
            raise serializers.ValidationError(_("Package cost cannot be negative"))
        
        if value > 999999.99:
            raise serializers.ValidationError(_("Package cost cannot exceed 999,999"))
        
        return value
    
    def validate_discounted_package_cost(self, value):
        if value is None:
            return value
        
        if value < 0:
            raise serializers.ValidationError(_("Discounted package cost cannot be negative"))
        
        if value > 999999.99:
            raise serializers.ValidationError(_("Discounted package cost cannot exceed 999,999"))
        
        return value


class PaxRecordSerializer(serializers.ModelSerializer):
    customer_details = CustomerDetailSerializer(many=True)

    class Meta:
        model = PaxRecord
        fields = "__all__"
    
    def validate_pax(self, value):
        if value is None:
            raise serializers.ValidationError(_("Pax count is required"))
        
        if not isinstance(value, int):
            raise serializers.ValidationError(_("Pax count must be an integer"))
        
        if value <= 0:
            raise serializers.ValidationError(_("Pax count must be greater than 0"))
        
        if value > 50:
            raise serializers.ValidationError(_("Pax count cannot exceed 50"))
        
        return value


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
    
    def validate_amount(self, value):
        if value is None:
            raise serializers.ValidationError(_("Payment amount is required"))
        
        if not isinstance(value, (int, float)):
            raise serializers.ValidationError(_("Payment amount must be a number"))
        
        if value < 0:
            raise serializers.ValidationError(_("Payment amount cannot be negative"))
        
        if value > 999999.99:
            raise serializers.ValidationError(_("Payment amount cannot exceed 999,999"))
        
        return value
    
    def validate_payment_method(self, value):
        if value is None:
            raise serializers.ValidationError(_("Payment method is required"))
        
        valid_methods = ['cash', 'card', 'upi', 'bank_transfer', 'online']
        if value not in valid_methods:
            raise serializers.ValidationError(_("Invalid payment method"))
        
        return value
    
    def validate_transaction_id(self, value):
        if value is not None:
            # Validate transaction ID format (alphanumeric, length 8-64)
            if not re.match(r'^[a-zA-Z0-9]{8,64}$', value):
                raise serializers.ValidationError(_("Invalid transaction ID format"))
        
        return value


class BookingSerializer(serializers.ModelSerializer):
    trip = serializers.PrimaryKeyRelatedField(queryset=Trip.objects.all())
    pax_records = PaxRecordSerializer(many=True, read_only=True)
    customer_details = CustomerDetailSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Booking
        fields = "__all__"
    
    def validate_amount(self, value):
        if value is None:
            raise serializers.ValidationError(_("Booking amount is required"))
        
        if not isinstance(value, (int, float)):
            raise serializers.ValidationError(_("Booking amount must be a number"))
        
        if value < 0:
            raise serializers.ValidationError(_("Booking amount cannot be negative"))
        
        if value > 999999.99:
            raise serializers.ValidationError(_("Booking amount cannot exceed 999,999"))
        
        return value
    
    def validate_balance_amount(self, value):
        if value is not None:
            if not isinstance(value, (int, float)):
                raise serializers.ValidationError(_("Balance amount must be a number"))
            
            if value < 0:
                raise serializers.ValidationError(_("Balance amount cannot be negative"))
            
            if value > 999999.99:
                raise serializers.ValidationError(_("Balance amount cannot exceed 999,999"))
        
        return value
    
    def validate_status(self, value):
        if value is None:
            raise serializers.ValidationError(_("Booking status is required"))
        
        valid_statuses = ['Pending', 'Confirmed', 'Cancelled', 'Completed', 'Partially Confirmed', 'Rescheduled']
        if value not in valid_statuses:
            raise serializers.ValidationError(_("Invalid booking status"))
        
        return value
    
    def validate_trip(self, value):
        if value is None:
            raise serializers.ValidationError(_("Trip is required"))
        
        # Check if trip exists and is available
        try:
            trip = Trip.objects.get(pk=value)
            if trip.status != 'Scheduled':
                raise serializers.ValidationError(_("Trip is not available for booking"))
        except Trip.DoesNotExist:
            raise serializers.ValidationError(_("Trip not found"))
        
        return value
    
    def validate(self, attrs):
        # Custom validation to ensure customer details match pax count
        pax_records = attrs.get('pax_records', [])
        customer_details = attrs.get('customer_details', [])
        
        if pax_records and customer_details:
            total_pax = sum(pax_record.get('pax', 0) for pax_record in pax_records)
            total_customers = len(customer_details)
            
            if total_pax != total_customers:
                raise serializers.ValidationError(
                    _("Number of customers ({total_customers}) must match total pax count ({total_pax})")
                )
        
        return super().validate(attrs)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['trip'] = TripOverviewSerializer(instance.trip).data
        return representation


class BookingOverviewSerializer(serializers.ModelSerializer):
    trip = TripOverviewSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ["id", "trip", "status"]
