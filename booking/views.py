from django.db import transaction
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response

from package.models import MealRecords
from .models import Booking, PaxRecord, CustomerDetail, Payment
from .serializers import BookingSerializer

import razorpay
import time
import os

client = razorpay.Client(auth=(os.getenv("KEY_ID"), os.getenv("KEY_SECRET")))


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    @action(detail=False, methods=["post"], url_path="calculate")
    def calculate_booking(self, request):
        pax_records = request.data.get("pax_records", [])
        if not pax_records:
            return Response(
                {"error": "No pax records provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total_cost = 0

        for pax_record in pax_records:
            for customer_detail in pax_record.get("customer_details", []):
                meal_option_id = customer_detail.get("meal_option_id")
                try:
                    meal_record = MealRecords.objects.get(id=meal_option_id)
                    total_cost += (
                        meal_record.discounted_price
                        if meal_record.discounted_price
                        else meal_record.price
                    )
                except MealRecords.DoesNotExist:
                    return Response(
                        {"error": f"Meal option with id {meal_option_id} not found."},
                        status=status.HTTP_404_NOT_FOUND,
                    )

        # Return the calculated amount in paise (for Razorpay)
        order_amount = total_cost * 100

        # Create an order with Razorpay
        order_currency = "INR"
        order_receipt = f"receipt_{int(time.time())}"
        notes = {}

        razorpay_order = client.order.create(
            dict(
                amount=order_amount,
                currency=order_currency,
                receipt=order_receipt,
                notes=notes,
            )
        )

        return Response(
            {
                "order_id": razorpay_order["id"],
                "razorpay_key_id": os.getenv("KEY_ID"),
                "amount": order_amount,
            },
            status=status.HTTP_200_OK,
        )

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        booking_data = request.data

        # Extract the user from the request and add it to the booking data
        booking_data["user"] = request.user.id

        # Extract related data from the request
        pax_records_data = booking_data.pop("pax_records", [])
        payments_data = booking_data.pop("payments", [])

        # Create the Booking object
        booking_serializer = self.get_serializer(data=booking_data)
        booking_serializer.is_valid(raise_exception=True)
        booking = booking_serializer.save()

        total_customers = 0

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
        trip = booking.trip
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
