from rest_framework import serializers
from .models import Trip

class TripSerializer(serializers.ModelSerializer):
    package = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = '__all__'

    def get_package(self, obj):
        from package.serializers import PackageSerializer 
        return PackageSerializer(obj.package).data
