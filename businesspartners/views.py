from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from .models import BusinessPartnerProfile
from .serializers import BusinessPartnerProfileSerializer

class BusinessPartnerProfileViewSet(viewsets.ModelViewSet):
    queryset = BusinessPartnerProfile.objects.all()
    serializer_class = BusinessPartnerProfileSerializer

    def create(self, request, *args, **kwargs):
        partner_data = request.data.copy() 
        partner_data["user"] = request.user.id 

        serializer = self.get_serializer(data=partner_data)
        serializer.is_valid(raise_exception=True)

        # Save the new BusinessPartnerProfile
        partner_profile = serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
