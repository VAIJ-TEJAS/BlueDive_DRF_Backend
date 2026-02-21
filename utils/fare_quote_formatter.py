"""Formatting helpers for fare quote display."""

from typing import List
from utils.fare_quote_types import FareQuoteBreakdown


def _inr(amount: float) -> str:
    return f"INR {amount:,.2f}"


def format_fare_quote_breakdown(breakdown: FareQuoteBreakdown) -> List[str]:
    return [
        f"Travel Fare: {_inr(breakdown.travel_fare)}",
        f"Minimum Fare Adjustment: {_inr(breakdown.minimum_adjustment)}",
        f"Luggage Surcharge: {_inr(breakdown.luggage_surcharge)}",
        f"Night Surcharge: {_inr(breakdown.night_surcharge)}",
        f"Surge Surcharge: {_inr(breakdown.surge_surcharge)}",
        f"Subtotal: {_inr(breakdown.subtotal)}",
        f"Discount: {_inr(-breakdown.discount)}",
        f"Service Fee: {_inr(breakdown.service_fee)}",
        f"Total: {_inr(breakdown.total)}",
    ]


def summarize_fare_quote(breakdown: FareQuoteBreakdown) -> str:
    return ' | '.join(format_fare_quote_breakdown(breakdown))
