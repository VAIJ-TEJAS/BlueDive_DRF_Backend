from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from .models import BusinessPartnerProfile
from .serializers import BusinessPartnerProfileSerializer

class BusinessPartnerProfileViewSet(viewsets.ModelViewSet):
    queryset = BusinessPartnerProfile.objects.all()
    serializer_class = BusinessPartnerProfileSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
