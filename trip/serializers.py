from rest_framework import serializers

from package.models import Package
from .models import Trip


class TripPackageOverviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = "__all__"


class TripOverviewSerializer(serializers.ModelSerializer):
    # package = TripPackageOverviewSerializer()

    class Meta:
        model = Trip
        fields = "__all__"
