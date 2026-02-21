"""Formatting helpers for itinerary quote outputs."""

from typing import List
from utils.itinerary_quote_types import ItineraryQuoteBreakdown


def _inr(value: float) -> str:
    return f"INR {value:,.2f}"


def format_itinerary_quote_breakdown(breakdown: ItineraryQuoteBreakdown) -> List[str]:
    return [
        f"Base Package: {_inr(breakdown.base_package)}",
        f"Itinerary Adjustment: {_inr(breakdown.itinerary_adjustment)}",
        f"Hotel Surcharge: {_inr(breakdown.hotel_surcharge)}",
        f"Breakfast Cost: {_inr(breakdown.breakfast_cost)}",
        f"Transfer Cost: {_inr(breakdown.transfer_cost)}",
        f"Seasonal Adjustment: {_inr(breakdown.seasonal_adjustment)}",
        f"Subtotal: {_inr(breakdown.subtotal)}",
        f"Discount: {_inr(-breakdown.discount)}",
        f"Service Fee: {_inr(breakdown.service_fee)}",
        f"Total: {_inr(breakdown.total)}",
    ]


def summarize_itinerary_quote(breakdown: ItineraryQuoteBreakdown) -> str:
    return ' | '.join(format_itinerary_quote_breakdown(breakdown))
