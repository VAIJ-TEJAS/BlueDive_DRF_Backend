from rest_framework import serializers

from package.models import Package
from .models import Trip

class TripPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = '__all__'


class TripSerializer(serializers.ModelSerializer):
    package = TripPackageSerializer()

    class Meta:
        model = Trip
        fields = '__all__'
