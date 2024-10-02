from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import BusinessPartnerProfile
from .serializers import BusinessPartnerProfileSerializer

class BusinessPartnerProfileViewSet(viewsets.ModelViewSet):
    queryset = BusinessPartnerProfile.objects.all()
    serializer_class = BusinessPartnerProfileSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
