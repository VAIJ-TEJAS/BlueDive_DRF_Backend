from rest_framework import viewsets, status
from rest_framework.response import Response

from booking.models import Booking
from booking.serializers import BookingSerializer
from package.models import MealRecords

import razorpay
import time
import os

client = razorpay.Client(auth=(os.getenv("KEY_ID"), os.getenv("KEY_SECRET")))


class PaymentViewset(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        pax_records = request.data.get("pax_records", [])

        print("KEY_ID:", os.getenv("KEY_ID"))
        print("KEY_SECRET:", os.getenv("KEY_SECRET"))


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

        print(razorpay_order)

        return Response(
            {
                "order_id": razorpay_order["id"],
                "razorpay_key_id": os.getenv("KEY_ID"),
                "amount": order_amount,
            },
            status=status.HTTP_200_OK,
        )
