from rest_framework import serializers

from trip.models import Trip
from trip.serializers import TripOverviewSerializer
from .models import Booking, CustomerDetail, PaxRecord, Payment


class CustomerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDetail
        fields = "__all__"


class PaxRecordSerializer(serializers.ModelSerializer):
    customer_details = CustomerDetailSerializer(many=True)

    class Meta:
        model = PaxRecord
        fields = "__all__"


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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Replace the trip ID with the trip object
        representation['trip'] = TripOverviewSerializer(instance.trip).data
        return representation


class BookingOverviewSerializer(serializers.ModelSerializer):
    trip = TripOverviewSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ["id", "trip", "status"]
