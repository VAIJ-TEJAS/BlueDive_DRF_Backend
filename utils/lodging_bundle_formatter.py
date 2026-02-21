"""Formatting helpers for lodging bundle pricing."""

from typing import List
from utils.lodging_bundle_types import LodgingBundleBreakdown


def _inr(value: float) -> str:
    return f"INR {value:,.2f}"


def format_lodging_bundle_breakdown(breakdown: LodgingBundleBreakdown) -> List[str]:
    return [
        f"Base Room Cost: {_inr(breakdown.base_room_cost)}",
        f"Bundle Adjustment: {_inr(breakdown.bundle_adjustment)}",
        f"Season Adjustment: {_inr(breakdown.season_adjustment)}",
        f"Breakfast Cost: {_inr(breakdown.breakfast_cost)}",
        f"Pickup Cost: {_inr(breakdown.pickup_cost)}",
        f"Sightseeing Cost: {_inr(breakdown.sightseeing_cost)}",
        f"Markup Amount: {_inr(breakdown.markup_amount)}",
        f"Subtotal: {_inr(breakdown.subtotal)}",
        f"Discount: {_inr(-breakdown.discount)}",
        f"Service Fee: {_inr(breakdown.service_fee)}",
        f"Total: {_inr(breakdown.total)}",
    ]


def summarize_lodging_bundle(breakdown: LodgingBundleBreakdown) -> str:
    return ' | '.join(format_lodging_bundle_breakdown(breakdown))
