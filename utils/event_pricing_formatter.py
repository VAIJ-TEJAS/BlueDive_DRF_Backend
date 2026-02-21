"""Formatter helpers for event pricing."""

from typing import List
from utils.event_pricing_types import EventPricingBreakdown


def _inr(value: float) -> str:
    return f"INR {value:,.2f}"


def format_event_pricing_breakdown(breakdown: EventPricingBreakdown) -> List[str]:
    return [
        f"Base Cost: {_inr(breakdown.base_cost)}",
        f"Event Adjustment: {_inr(breakdown.event_adjustment)}",
        f"Season Adjustment: {_inr(breakdown.season_adjustment)}",
        f"Meals Cost: {_inr(breakdown.meals_cost)}",
        f"Stage Setup Cost: {_inr(breakdown.stage_setup_cost)}",
        f"Photography Cost: {_inr(breakdown.photography_cost)}",
        f"Markup Amount: {_inr(breakdown.markup_amount)}",
        f"Subtotal: {_inr(breakdown.subtotal)}",
        f"Discount: {_inr(-breakdown.discount)}",
        f"Service Charge: {_inr(breakdown.service_charge)}",
        f"Total: {_inr(breakdown.total)}",
    ]


def summarize_event_pricing(breakdown: EventPricingBreakdown) -> str:
    return ' | '.join(format_event_pricing_breakdown(breakdown))
