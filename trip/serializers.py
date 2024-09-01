from rest_framework import serializers
from package.models import Package
from settings.models import Settings
from .models import Trip
from datetime import date, timedelta

class TripPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package

class TripOverviewSerializer(serializers.ModelSerializer):
    is_scuba_free = serializers.SerializerMethodField()
    scuba_free_until_date = serializers.SerializerMethodField()
    is_discount_applicable = serializers.SerializerMethodField()
    discount_applicable_until_date = serializers.SerializerMethodField()
    can_do_advance_payment = serializers.SerializerMethodField()
    advance_payment_due_date = serializers.SerializerMethodField()
    package = TripPackageSerializer()
    class Meta:
        model = Trip
        fields = "__all__"  # Include all original fields

    def get_is_scuba_free(self, obj):
        settings = Settings.load()
        days_until_trip = (obj.start_date - date.today()).days
        return days_until_trip >= settings.scuba_limit_days
    
    def get_scuba_free_until_date(self, obj):
        settings = Settings.load()
        if self.get_is_scuba_free(obj):
            return obj.start_date - timedelta(days=settings.scuba_limit_days)
        return None

    def get_is_discount_applicable(self, obj):
        settings = Settings.load()
        days_until_trip = (obj.start_date - date.today()).days
        return days_until_trip >= settings.discount_limit_days
    
    def get_discount_applicable_until_date(self, obj):
        settings = Settings.load()
        if self.get_is_discount_applicable(obj):
            return obj.start_date - timedelta(days=settings.discount_limit_days)
        return None

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