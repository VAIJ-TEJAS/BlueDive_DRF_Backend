"""Calculator for event pricing."""

from typing import Optional, Tuple
from utils.event_pricing_types import EventPricingRequest, EventPricingRules, EventPricingBreakdown
from utils.event_pricing_rules import merge_event_pricing_rules


def _round2(value: float) -> float:
    return round(value + 1e-9, 2)


def _promo_discount(subtotal: float, promo: Optional[str], rules: EventPricingRules) -> Tuple[Optional[str], float]:
    if not promo:
        return None, 0.0
    percent = rules.promo_discount_percent.get(promo, 0.0)
    if percent <= 0:
        return None, 0.0
    return promo, subtotal * percent


def calculate_event_pricing_breakdown(request: EventPricingRequest, custom_rules: Optional[EventPricingRules] = None):
    rules = merge_event_pricing_rules(custom_rules)

    daily = rules.base_per_person_per_day.get(request.tier, 0.0)
    base_cost = _round2(daily * request.attendees * request.days)

    event_adj = _round2(base_cost * (rules.event_multiplier.get(request.event_type, 1.0) - 1.0))
    season_adj = _round2((base_cost + event_adj) * (rules.season_multiplier.get(request.season, 1.0) - 1.0))

    meals_cost = _round2(request.attendees * request.days * rules.meals_per_person_per_day) if request.include_meals else 0.0
    stage_cost = _round2(request.days * rules.stage_setup_per_day) if request.include_stage_setup else 0.0
    photo_cost = _round2(request.days * rules.photography_per_day) if request.include_photography else 0.0

    pre_markup = _round2(base_cost + event_adj + season_adj + meals_cost + stage_cost + photo_cost)
    markup = max(0.0, min(request.markup_percent, rules.max_markup_percent))
    markup_amount = _round2(pre_markup * markup / 100.0)

    subtotal = _round2(pre_markup + markup_amount)

    applied_promo, raw_discount = _promo_discount(subtotal, request.promo_code, rules)
    discount = _round2(min(subtotal, raw_discount))

    fee_base = _round2(max(0.0, subtotal - discount))
    service_charge = _round2(fee_base * rules.service_charge_percent)
    total = _round2(fee_base + service_charge)

    breakdown = EventPricingBreakdown(
        base_cost=base_cost,
        event_adjustment=event_adj,
        season_adjustment=season_adj,
        meals_cost=meals_cost,
        stage_setup_cost=stage_cost,
        photography_cost=photo_cost,
        markup_amount=markup_amount,
        subtotal=subtotal,
        discount=discount,
        service_charge=service_charge,
        total=total,
    )

    return breakdown, applied_promo
