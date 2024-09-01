from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from datetime import date, timedelta
from settings.models import Settings
from trip.models import Trip

from .models import Booking, PaxRecord, CustomerDetail, Payment
from .serializers import BookingOverviewSerializer, BookingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return BookingOverviewSerializer
        return BookingSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        booking_data = request.data

        # Extract the user from the request and add it to the booking data
        booking_data["user"] = request.user.id

        # Extract related data from the request
        pax_records_data = booking_data.pop("pax_records", [])
        payments_data = booking_data.pop("payments", [])
        trip_id = booking_data.get("trip", None)

        # Create the Booking object
        booking_serializer = self.get_serializer(data=booking_data)
        booking_serializer.is_valid(raise_exception=True)
        booking = booking_serializer.save()

        total_customers = 0

        # Fetch the Trip instance using the trip ID
        try:
            trip = Trip.objects.filter(id=trip_id).first() 
        except Trip.DoesNotExist:
            return Response(
                {"detail": "Trip not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Determine if scuba is included
        settings = Settings.load()
        days_until_trip = (trip.start_date - date.today()).days
        if days_until_trip >= settings.scuba_limit_days:
            booking.scuba_included = True
        else:
            booking.scuba_included = False
        booking.save()

        # Create the associated PaxRecords and CustomerDetails
        for pax_record_data in pax_records_data:
            customer_details_data = pax_record_data.pop("customer_details", [])
            pax_record = PaxRecord.objects.create(booking=booking, **pax_record_data)

            total_customers += len(customer_details_data)
            for customer_detail_data in customer_details_data:
                CustomerDetail.objects.create(
                    pax_record=pax_record, **customer_detail_data
                )

        # Create the associated Payments
        for payment_data in payments_data:
            Payment.objects.create(booking=booking, **payment_data)

        # Update available seats in the associated Trip
        if trip.available_seats < total_customers:
            return Response(
                {"detail": "Not enough available seats."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        trip.available_seats -= total_customers
        trip.save()

        # Return the full booking with its relationships
        headers = self.get_success_headers(booking_serializer.data)
        return Response(
            booking_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
