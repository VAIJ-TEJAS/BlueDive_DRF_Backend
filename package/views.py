from rest_framework import viewsets
from .models import Option, Event, Day, EventRecord, DayRecord, Package
from .serializers import OptionSerializer, EventSerializer, DaySerializer, EventRecordSerializer, DayRecordSerializer, PackageSerializer

class OptionViewSet(viewsets.ModelViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class DayViewSet(viewsets.ModelViewSet):
    queryset = Day.objects.all()
    serializer_class = DaySerializer

class EventRecordViewSet(viewsets.ModelViewSet):
    queryset = EventRecord.objects.all()
    serializer_class = EventRecordSerializer

class DayRecordViewSet(viewsets.ModelViewSet):
    queryset = DayRecord.objects.all()
    serializer_class = DayRecordSerializer

class PackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
