from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from booking.models import Booking
from booking.serializers import BookingSerializer
from package.models import MealRecords

import razorpay
import time
import os

import hmac
import hashlib
import json
import logging

from settings.models import Settings

logger = logging.getLogger(__name__)
from trip.models import Trip
from trip.serializers import TripOverviewSerializer

client = razorpay.Client(auth=(os.getenv("KEY_ID"), os.getenv("KEY_SECRET")))

class PaymentWebhookViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"], url_path="payment-success")
    def payment_successful_webhook(self, request, *args, **kwargs):
        # Step 1: Log request details for debugging
        logger.debug("Webhook headers: %s", request.headers)
        logger.debug("Webhook payload: %s", request.data)

        # Step 2: Get the Signature from the Header (replace with actual header name if different)
        signature = request.headers.get("X-Razorpay-Signature")
        if not signature:
            return Response({"error": "Signature missing"}, status=status.HTTP_400_BAD_REQUEST)

        # Step 3: Verify the signature using the secret
        webhook_secret = os.getenv("WEBHOOK_SECRET")
        if not webhook_secret:
            logger.error("WEBHOOK_SECRET environment variable is not set")
            return Response({"error": "Server configuration error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        payload = json.dumps(request.data, separators=(',', ':'))  # Convert payload to JSON string
        expected_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # Step 4: Compare the computed signature with the one from the header
        if hmac.compare_digest(expected_signature, signature):
            # If valid, process the webhook event
            logger.info("Webhook signature verified successfully")
        else:
            # If invalid, reject the request
            return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

        # Step 5: Respond with a simple acknowledgment
        return Response({"status": "received"}, status=status.HTTP_200_OK)

class BookingPaymentViewset(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        pax_records = request.data.get("pax_records", [])
        trip_id = request.data.get("trip")
        payment_type = request.data.get("payment_type")

        if not pax_records:
            return Response(
                {"error": "No pax records provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )


        # Load the trip object
        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            return Response(
                {"error": "Trip not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Serialize the trip object to check for limits
        trip_serializer = TripOverviewSerializer(trip)
        is_discount_applicable = trip_serializer.data.get("is_discount_applicable")

        total_cost = 0
        advance_cost = 0
        balance_amount = 0

        # Get advance payment amount from settings
        settings_instance = Settings.load()
        # advance_amount_per_pax = settings_instance.advance_payment_amount
        
        for pax_record in pax_records:
            for customer_detail in pax_record.get("customer_details", []):
                meal_option_id = customer_detail.get("meal_option_id")

                try:
                    meal_record = MealRecords.objects.get(id=meal_option_id)

                    # Use discounted price if discount is applicable, otherwise use regular price
                    if is_discount_applicable and meal_record.discounted_price:
                        total_cost += meal_record.discounted_price
                    else:
                        total_cost += meal_record.price

                except MealRecords.DoesNotExist:
                    return Response(
                        {"error": f"Meal option with id {meal_option_id} not found."},
                        status=status.HTTP_404_NOT_FOUND,
                    )
      
        for pax_record in pax_records:
            pax_count = pax_record.get('pax') or 0
            advance_cost += pax_count * 2500
        

        # Return the calculated amount in paise (for Razorpay)
        order_amount = 0
        if(payment_type == 'advance'):
            order_amount = advance_cost * 100
            balance_amount = total_cost - advance_cost
        elif(payment_type == 'full'):
            order_amount = total_cost * 100 
        else:
            return Response(
                {"error": "Invalid payment type provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
                "balance_amount": balance_amount
            },
            status=status.HTTP_200_OK,
        )

class BalancePaymentViewset(viewsets.ViewSet):

    def create(self, request, *args, **kwargs):
        booking_id = request.data.get("booking_id")

        if not booking_id:
            return Response(
                {"error": "Booking ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fetch the booking object
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Calculate the balance amount (in this case, it is assumed to be stored in the booking)
        balance_amount = booking.balance_amount

        if balance_amount <= 0:
            return Response(
                {"error": "No balance amount available for this booking."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create an order with Razorpay
        order_currency = "INR"
        order_receipt = f"receipt_{int(time.time())}"
        notes = {"booking_id": booking_id}

        razorpay_order = client.order.create(
            dict(
                amount=int(balance_amount * 100),  # amount in paise
                currency=order_currency,
                receipt=order_receipt,
                notes=notes,
            )
        )

        # Return the Razorpay order ID and other details
        return Response(
            {
                "order_id": razorpay_order["id"],
                "razorpay_key_id": os.getenv("KEY_ID"),
                "amount": balance_amount * 100,  # returning amount in paise
                "currency": order_currency,
                "booking_id": booking_id,
            },
            status=status.HTTP_200_OK,
        )