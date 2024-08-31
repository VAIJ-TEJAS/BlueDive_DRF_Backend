from rest_framework import serializers
from settings.models import Settings
from .models import Trip
from datetime import date

class TripOverviewSerializer(serializers.ModelSerializer):
    is_scuba_free = serializers.SerializerMethodField()
    is_discount_applicable = serializers.SerializerMethodField()

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