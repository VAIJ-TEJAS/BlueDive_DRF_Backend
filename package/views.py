from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Package
from .serializers import PackageOverviewSerializer, PackageSerializer, PackageTripsSerializer

class PackageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [AllowAny]

class PackageOverviewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageOverviewSerializer
    permission_classes = [AllowAny]

class PackageTripsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PackageTripsSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        package_name = self.request.query_params.get('name')
        if package_name:
            return Package.objects.filter(name=package_name)
        return Package.objects.all()