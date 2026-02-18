from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from datetime import date
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from settings.models import Settings
from rest_framework.decorators import action
from .models import Booking, PaxRecord, CustomerDetail, Payment
from .serializers import BookingOverviewSerializer, BookingSerializer
import logging

logger = logging.getLogger(__name__)

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
        try:
            booking_data = request.data.copy()

            # Validate required fields
            if not booking_data.get("trip"):
                return Response(
                    {"error": "Trip ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Extract the user from the request and add it to the booking data
            booking_data["user"] = request.user.id

            # Extract related data from the request
            pax_records_data = booking_data.pop("pax_records", [])
            payments_data = booking_data.pop("payments", [])
            payment_type = request.data.get("payment_type")

            if(payment_type == "full"):
                booking_data['status'] = 'Confirmed'

            # Validate pax_records data
            if not pax_records_data:
                return Response(
                    {"error": "At least one passenger record is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Count customers and rooms before creating anything
            total_customers = 0
            total_rooms = len(pax_records_data)
            
            for i, pax_record_data in enumerate(pax_records_data):
                if not pax_record_data.get("pax") or pax_record_data["pax"] <= 0:
                    return Response(
                        {"error": f"Invalid passenger count in record {i+1}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                customer_details_data = pax_record_data.get("customer_details", [])
                if len(customer_details_data) != pax_record_data["pax"]:
                    return Response(
                        {"error": f"Customer details count mismatch in record {i+1}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                total_customers += len(customer_details_data)

            if total_customers == 0:
                return Response(
                    {"error": "At least one customer is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check seat availability before creating the booking
            from trip.models import Trip as TripModel
            try:
                trip_obj = TripModel.objects.select_for_update().get(id=booking_data.get("trip"))
            except ObjectDoesNotExist:
                return Response(
                    {"error": "Trip not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Validate trip dates
            if trip_obj.start_date < timezone.now().date():
                return Response(
                    {"error": "Cannot book past trips"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if trip_obj.available_seats < total_customers:
                return Response(
                    {"error": f"Not enough available seats. Available: {trip_obj.available_seats}, Required: {total_customers}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if trip_obj.available_rooms < total_rooms:
                return Response(
                    {"error": f"Not enough available rooms. Available: {trip_obj.available_rooms}, Required: {total_rooms}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create the Booking object
            booking_serializer = self.get_serializer(data=booking_data)
            booking_serializer.is_valid(raise_exception=True)
            booking = booking_serializer.save()

            # Create the associated PaxRecords and CustomerDetails
            for pax_record_data in pax_records_data:
                customer_details_data = pax_record_data.pop("customer_details", [])
                pax_record = PaxRecord.objects.create(booking=booking, **pax_record_data)

                for customer_detail_data in customer_details_data:
                    CustomerDetail.objects.create(
                        pax_record=pax_record, **customer_detail_data
                    )

            # Create the associated Payments
            for payment_data in payments_data:
                # Validate payment data
                if not payment_data.get("amount") or payment_data["amount"] <= 0:
                    logger.warning(f"Invalid payment amount: {payment_data}")
                    continue
                Payment.objects.create(booking=booking, **payment_data)

            # Update available seats in the associated Trip
            trip = booking.trip

            # Determine if scuba is included
            settings = Settings.load()
            days_until_trip = (trip.start_date - date.today()).days
            if days_until_trip >= settings.scuba_limit_days:
                booking.scuba_included = True
            else:
                booking.scuba_included = False
            booking.save()

            trip.available_seats -= total_customers
            trip.available_rooms -= total_rooms
            trip.save()

            logger.info(f"Booking created successfully: {booking.id} for user {request.user.id}")

            # Return the full booking with its relationships
            headers = self.get_success_headers(booking_serializer.data)
            return Response(
                booking_serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )

        except ValidationError as e:
            logger.error(f"Validation error in booking creation: {e}")
            return Response(
                {"error": "Validation failed", "details": e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error in booking creation: {e}")
            return Response(
                {"error": "An unexpected error occurred. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @transaction.atomic
    @action(detail=True, methods=['post'], url_path='confirm')
    def confirm_booking(self, request, pk=None):
        booking = self.get_object()

        # Check if the booking is already confirmed
        if booking.status == "Confirmed":
            return Response(
                {"detail": "Booking is already confirmed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Confirm the payment using provided payment details
        payment_data = request.data.get("payment", {})
        if not payment_data:
            return Response(
                {"detail": "Payment data is required to confirm booking."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create a new payment record
        Payment.objects.create(
            booking=booking,
            payment_id=payment_data.get("payment_id"),
            order_id=payment_data.get("order_id"),
            signature=payment_data.get("signature"),
            amount=payment_data.get("amount"),
            payment_method=payment_data.get("payment_method", "Razorpay")
        )

        # Update the booking status and balance amount
        booking.status = "Confirmed"
        booking.balance_amount = 0
        booking.save()

        # Serialize and return the updated booking
        serializer = self.get_serializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)
