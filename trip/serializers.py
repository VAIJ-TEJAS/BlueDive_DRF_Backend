from rest_framework import serializers
from .models import Trip

class TripSerializer(serializers.ModelSerializer):
    package = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = '__all__'

    def get_package(self, obj):
        from package.serializers import PackageSerializer
        package_data = PackageSerializer(obj.package).data

        # Ensure cover_image has a full URL
        cover_image = package_data.get('cover_image')
        if cover_image:
            if not cover_image.startswith('http'):
                package_data['cover_image'] = self.context['request'].build_absolute_uri(cover_image)
        
        return package_data
