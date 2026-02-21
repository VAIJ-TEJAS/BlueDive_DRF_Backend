"""Formatting helpers for water sport pass pricing."""

from typing import List
from utils.water_sport_pass_types import WaterSportPassBreakdown


def _inr(value: float) -> str:
    return f"INR {value:,.2f}"


def format_water_sport_pass_breakdown(breakdown: WaterSportPassBreakdown) -> List[str]:
    return [
        f"Base Pass Cost: {_inr(breakdown.base_pass_cost)}",
        f"Slot Adjustment: {_inr(breakdown.slot_adjustment)}",
        f"Equipment Insurance Cost: {_inr(breakdown.equipment_insurance_cost)}",
        f"Photo Package Cost: {_inr(breakdown.photo_package_cost)}",
        f"Guide Support Cost: {_inr(breakdown.guide_support_cost)}",
        f"Markup Amount: {_inr(breakdown.markup_amount)}",
        f"Subtotal: {_inr(breakdown.subtotal)}",
        f"Discount: {_inr(-breakdown.discount)}",
        f"Service Fee: {_inr(breakdown.service_fee)}",
        f"Total: {_inr(breakdown.total)}",
    ]


def summarize_water_sport_pass(breakdown: WaterSportPassBreakdown) -> str:
    return ' | '.join(format_water_sport_pass_breakdown(breakdown))
