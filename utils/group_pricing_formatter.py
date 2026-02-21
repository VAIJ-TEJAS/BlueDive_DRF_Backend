"""Formatter helpers for group pricing."""

from typing import List
from utils.group_pricing_types import GroupPricingBreakdown


def _inr(value: float) -> str:
    return f"INR {value:,.2f}"


def format_group_pricing_breakdown(breakdown: GroupPricingBreakdown) -> List[str]:
    return [
        f"Base Cost: {_inr(breakdown.base_cost)}",
        f"Category Adjustment: {_inr(breakdown.category_adjustment)}",
        f"Season Adjustment: {_inr(breakdown.season_adjustment)}",
        f"Meals Cost: {_inr(breakdown.meals_cost)}",
        f"Transport Cost: {_inr(breakdown.transport_cost)}",
        f"Guide Cost: {_inr(breakdown.guide_cost)}",
        f"Markup Amount: {_inr(breakdown.markup_amount)}",
        f"Subtotal: {_inr(breakdown.subtotal)}",
        f"Discount: {_inr(-breakdown.discount)}",
        f"Service Charge: {_inr(breakdown.service_charge)}",
        f"Total: {_inr(breakdown.total)}",
    ]


def summarize_group_pricing(breakdown: GroupPricingBreakdown) -> str:
    return ' | '.join(format_group_pricing_breakdown(breakdown))
