from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import ContactMessage
from .serializers import ContactMessageSerializer


class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.none()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]
    http_method_names = ["post"]
