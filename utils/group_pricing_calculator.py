"""Core calculator for group pricing."""

from typing import Optional, Tuple
from utils.group_pricing_types import (
    GroupPricingRequest,
    GroupPricingRules,
    GroupPricingBreakdown,
)
from utils.group_pricing_rules import merge_group_pricing_rules


def _round2(value: float) -> float:
    return round(value + 1e-9, 2)


def _promo_discount(subtotal: float, promo: Optional[str], rules: GroupPricingRules) -> Tuple[Optional[str], float]:
    if not promo:
        return None, 0.0

    percent = rules.promo_discount_percent.get(promo, 0.0)
    if percent <= 0:
        return None, 0.0

    return promo, subtotal * percent


def calculate_group_pricing_breakdown(
    request: GroupPricingRequest,
    custom_rules: Optional[GroupPricingRules] = None,
):
    rules = merge_group_pricing_rules(custom_rules)

    daily = rules.base_daily_per_person.get(request.travel_class, 0.0)
    base_cost = _round2(daily * request.travelers * request.trip_days)

    category_factor = rules.category_multiplier.get(request.group_category, 1.0)
    category_adjustment = _round2(base_cost * (category_factor - 1.0))

    season_factor = rules.season_multiplier.get(request.season_code, 1.0)
    season_adjustment = _round2((base_cost + category_adjustment) * (season_factor - 1.0))

    meals_cost = _round2(request.travelers * request.trip_days * rules.meals_per_person_per_day) if request.include_meals else 0.0
    transport_cost = _round2(request.trip_days * rules.transport_per_day) if request.include_transport else 0.0
    guide_cost = _round2(request.trip_days * rules.guide_per_day) if request.include_guide else 0.0

    pre_markup = _round2(base_cost + category_adjustment + season_adjustment + meals_cost + transport_cost + guide_cost)

    markup = max(0.0, min(request.markup_percent, rules.max_markup_percent))
    markup_amount = _round2(pre_markup * (markup / 100.0))

    subtotal = _round2(pre_markup + markup_amount)

    applied_promo, raw_discount = _promo_discount(subtotal, request.promo_code, rules)
    discount = _round2(min(subtotal, raw_discount))

    fee_base = _round2(max(0.0, subtotal - discount))
    service_charge = _round2(fee_base * rules.service_charge_percent)
    total = _round2(fee_base + service_charge)

    breakdown = GroupPricingBreakdown(
        base_cost=base_cost,
        category_adjustment=category_adjustment,
        season_adjustment=season_adjustment,
        meals_cost=meals_cost,
        transport_cost=transport_cost,
        guide_cost=guide_cost,
        markup_amount=markup_amount,
        subtotal=subtotal,
        discount=discount,
        service_charge=service_charge,
        total=total,
    )

    return breakdown, applied_promo
