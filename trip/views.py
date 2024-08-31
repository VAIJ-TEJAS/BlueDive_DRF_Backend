from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Trip
from .serializers import TripOverviewSerializer

class TripViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Trip.objects.filter(status='Scheduled')
    serializer_class = TripOverviewSerializer
    permission_classes = [AllowAny]
