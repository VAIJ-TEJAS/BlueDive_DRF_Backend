from rest_framework import serializers
from settings.models import Settings
from .models import Trip
from datetime import date, timedelta

class TripOverviewSerializer(serializers.ModelSerializer):
    is_scuba_free = serializers.SerializerMethodField()
    is_discount_applicable = serializers.SerializerMethodField()
    can_do_advance_payment = serializers.SerializerMethodField()
    advance_payment_due_date = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = "__all__"  # Include all original fields

    def get_is_scuba_free(self, obj):
        settings = Settings.load()
        days_until_trip = (obj.start_date - date.today()).days
        return days_until_trip >= settings.scuba_limit_days

    def get_is_discount_applicable(self, obj):
        settings = Settings.load()
        days_until_trip = (obj.start_date - date.today()).days
        return days_until_trip >= settings.discount_limit_days

    def get_can_do_advance_payment(self, obj):
        settings = Settings.load()
        days_until_trip = (obj.start_date - date.today()).days
        return days_until_trip > settings.balance_payment_limit_days

    def get_advance_payment_due_date(self, obj):
        settings = Settings.load()
        days_until_trip = (obj.start_date - date.today()).days
        if days_until_trip >= settings.balance_payment_limit_days:
            return obj.start_date - timedelta(days=settings.balance_payment_limit_days)
        return None