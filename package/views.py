from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Package
from .serializers import PackageSerializer

class PackageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [AllowAny]
