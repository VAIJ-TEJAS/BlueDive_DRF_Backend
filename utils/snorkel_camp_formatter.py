"""Formatting helpers for snorkel camp quote pipeline."""

from typing import List
from utils.snorkel_camp_types import SnorkelCampBreakdown


def _inr(value: float) -> str:
    return f"INR {value:,.2f}"


def format_snorkel_camp_breakdown(breakdown: SnorkelCampBreakdown) -> List[str]:
    return [
        f"Base Camp Cost: {_inr(breakdown.base_camp_cost)}",
        f"Season Adjustment: {_inr(breakdown.season_adjustment)}",
        f"Equipment Cost: {_inr(breakdown.equipment_cost)}",
        f"Meals Cost: {_inr(breakdown.meals_cost)}",
        f"Certification Cost: {_inr(breakdown.certification_cost)}",
        f"Markup Amount: {_inr(breakdown.markup_amount)}",
        f"Subtotal: {_inr(breakdown.subtotal)}",
        f"Discount: {_inr(-breakdown.discount)}",
        f"Service Fee: {_inr(breakdown.service_fee)}",
        f"Total: {_inr(breakdown.total)}",
    ]


def summarize_snorkel_camp(breakdown: SnorkelCampBreakdown) -> str:
    return ' | '.join(format_snorkel_camp_breakdown(breakdown))
