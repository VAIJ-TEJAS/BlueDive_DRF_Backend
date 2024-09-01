from rest_framework import viewsets, status
from rest_framework.response import Response

from booking.models import Booking
from booking.serializers import BookingSerializer
from package.models import MealRecords

import razorpay
import time
import os

from settings.models import Settings
from trip.models import Trip
from trip.serializers import TripOverviewSerializer

# client = razorpay.Client(auth=("rzp_test_RX98n2GyvgDl78", "mFUsAztsl4YJ2L7OAQJjni20"))
client = razorpay.Client(auth=(os.getenv("KEY_ID"), os.getenv("KEY_SECRET")))


class PaymentViewset(viewsets.ModelViewSet):
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
            advance_cost += pax_record.get('pax') * 1000
        

        # Return the calculated amount in paise (for Razorpay)
        order_amount = 0
        if(payment_type == 'advance'):
            order_amount = advance_cost * 100
            balance_amount = total_cost - order_amount
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
