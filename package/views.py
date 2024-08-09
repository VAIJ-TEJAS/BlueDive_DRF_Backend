from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Package
from .serializers import PackageOverviewSerializer, PackageSerializer

class PackageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [AllowAny]

class PackageOverviewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageOverviewSerializer
    permission_classes = [AllowAny]