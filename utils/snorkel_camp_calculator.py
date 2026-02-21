"""Calculator for snorkel camp quote pipeline."""

from typing import Optional, Tuple
from utils.snorkel_camp_types import SnorkelCampRequest, SnorkelCampRules, SnorkelCampBreakdown
from utils.snorkel_camp_rules import merge_snorkel_camp_rules


def _round2(value: float) -> float:
    return round(value + 1e-9, 2)


def _promo_discount(subtotal: float, promo: Optional[str], rules: SnorkelCampRules) -> Tuple[Optional[str], float]:
    if not promo:
        return None, 0.0
    percent = rules.promo_discount_percent.get(promo, 0.0)
    if percent <= 0:
        return None, 0.0
    return promo, subtotal * percent


def calculate_snorkel_camp_breakdown(request: SnorkelCampRequest, custom_rules: Optional[SnorkelCampRules] = None):
    rules = merge_snorkel_camp_rules(custom_rules)

    base_daily = rules.base_per_participant_per_day.get(request.camp_tier, 0.0)
    base_camp_cost = _round2(base_daily * request.participants * request.days)

    season_factor = rules.season_multiplier.get(request.season_band, 1.0)
    season_adjustment = _round2(base_camp_cost * (season_factor - 1.0))

    equipment_cost = (
        _round2(request.participants * request.days * rules.equipment_per_participant_per_day)
        if request.include_equipment
        else 0.0
    )
    meals_cost = (
        _round2(request.participants * request.days * rules.meals_per_participant_per_day)
        if request.include_meals
        else 0.0
    )
    certification_cost = (
        _round2(request.participants * rules.certification_per_participant)
        if request.include_certification
        else 0.0
    )

    pre_markup = _round2(base_camp_cost + season_adjustment + equipment_cost + meals_cost + certification_cost)
    markup = max(0.0, min(request.markup_percent, rules.max_markup_percent))
    markup_amount = _round2(pre_markup * markup / 100.0)

    subtotal = _round2(pre_markup + markup_amount)

    applied_promo, raw_discount = _promo_discount(subtotal, request.promo_code, rules)
    discount = _round2(min(subtotal, raw_discount))

    fee_base = _round2(max(0.0, subtotal - discount))
    service_fee = _round2(fee_base * rules.service_fee_percent)
    total = _round2(fee_base + service_fee)

    breakdown = SnorkelCampBreakdown(
        base_camp_cost=base_camp_cost,
        season_adjustment=season_adjustment,
        equipment_cost=equipment_cost,
        meals_cost=meals_cost,
        certification_cost=certification_cost,
        markup_amount=markup_amount,
        subtotal=subtotal,
        discount=discount,
        service_fee=service_fee,
        total=total,
    )

    return breakdown, applied_promo
