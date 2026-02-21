"""Calculator for lodging bundle quotes."""

from typing import Optional, Tuple
from utils.lodging_bundle_types import LodgingBundleRequest, LodgingBundleRules, LodgingBundleBreakdown
from utils.lodging_bundle_rules import merge_lodging_bundle_rules


def _round2(value: float) -> float:
    return round(value + 1e-9, 2)


def _promo_discount(subtotal: float, promo: Optional[str], rules: LodgingBundleRules) -> Tuple[Optional[str], float]:
    if not promo:
        return None, 0.0
    percent = rules.promo_discount_percent.get(promo, 0.0)
    if percent <= 0:
        return None, 0.0
    return promo, subtotal * percent


def calculate_lodging_bundle_breakdown(request: LodgingBundleRequest, custom_rules: Optional[LodgingBundleRules] = None):
    rules = merge_lodging_bundle_rules(custom_rules)

    nightly = rules.base_room_per_night.get(request.room_type, 0.0)
    base_room_cost = _round2(nightly * request.rooms * request.nights)

    bundle_adjustment = _round2(base_room_cost * (rules.bundle_multiplier.get(request.bundle_type, 1.0) - 1.0))
    season_adjustment = _round2((base_room_cost + bundle_adjustment) * (rules.season_multiplier.get(request.season_code, 1.0) - 1.0))

    breakfast_cost = _round2(request.guests * request.nights * rules.breakfast_per_guest_per_day) if request.include_breakfast else 0.0
    pickup_cost = _round2(rules.airport_pickup_flat) if request.include_airport_pickup else 0.0
    sightseeing_cost = _round2(request.guests * rules.sightseeing_per_guest) if request.include_sightseeing else 0.0

    pre_markup = _round2(base_room_cost + bundle_adjustment + season_adjustment + breakfast_cost + pickup_cost + sightseeing_cost)
    markup = max(0.0, min(request.markup_percent, rules.max_markup_percent))
    markup_amount = _round2(pre_markup * markup / 100.0)

    subtotal = _round2(pre_markup + markup_amount)

    applied_promo, raw_discount = _promo_discount(subtotal, request.promo_code, rules)
    discount = _round2(min(subtotal, raw_discount))

    fee_base = _round2(max(0.0, subtotal - discount))
    service_fee = _round2(fee_base * rules.service_fee_percent)
    total = _round2(fee_base + service_fee)

    breakdown = LodgingBundleBreakdown(
        base_room_cost=base_room_cost,
        bundle_adjustment=bundle_adjustment,
        season_adjustment=season_adjustment,
        breakfast_cost=breakfast_cost,
        pickup_cost=pickup_cost,
        sightseeing_cost=sightseeing_cost,
        markup_amount=markup_amount,
        subtotal=subtotal,
        discount=discount,
        service_fee=service_fee,
        total=total,
    )
    return breakdown, applied_promo
