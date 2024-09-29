from rest_framework import viewsets
from .models import BusinessPartnerProfile
from .serializers import BusinessPartnerProfileSerializer

class BusinessPartnerProfileViewSet(viewsets.ModelViewSet):
    queryset = BusinessPartnerProfile.objects.all()
    serializer_class = BusinessPartnerProfileSerializer