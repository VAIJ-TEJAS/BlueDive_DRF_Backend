"""Calculator for water sport pass quotes."""

from typing import Optional, Tuple
from utils.water_sport_pass_types import WaterSportPassRequest, WaterSportPassRules, WaterSportPassBreakdown
from utils.water_sport_pass_rules import merge_water_sport_pass_rules


def _round2(value: float) -> float:
    return round(value + 1e-9, 2)


def _promo_discount(subtotal: float, promo: Optional[str], rules: WaterSportPassRules) -> Tuple[Optional[str], float]:
    if not promo:
        return None, 0.0
    percent = rules.promo_discount_percent.get(promo, 0.0)
    if percent <= 0:
        return None, 0.0
    return promo, subtotal * percent


def calculate_water_sport_pass_breakdown(
    request: WaterSportPassRequest,
    custom_rules: Optional[WaterSportPassRules] = None,
):
    rules = merge_water_sport_pass_rules(custom_rules)

    base_daily = rules.base_per_participant_per_day.get(request.pass_tier, 0.0)
    base_pass_cost = _round2(base_daily * request.participants * request.days)

    slot_adjustment = _round2(
        base_pass_cost * (rules.slot_multiplier.get(request.session_slot, 1.0) - 1.0)
    )

    equipment_insurance_cost = (
        _round2(request.participants * request.days * rules.equipment_insurance_per_participant_per_day)
        if request.include_equipment_insurance
        else 0.0
    )
    photo_package_cost = (
        _round2(request.participants * rules.photo_package_per_participant)
        if request.include_photo_package
        else 0.0
    )
    guide_support_cost = _round2(request.days * rules.guide_support_per_day) if request.include_guide_support else 0.0

    pre_markup = _round2(
        base_pass_cost
        + slot_adjustment
        + equipment_insurance_cost
        + photo_package_cost
        + guide_support_cost
    )

    markup = max(0.0, min(request.markup_percent, rules.max_markup_percent))
    markup_amount = _round2(pre_markup * markup / 100.0)

    subtotal = _round2(pre_markup + markup_amount)

    applied_promo, raw_discount = _promo_discount(subtotal, request.promo_code, rules)
    discount = _round2(min(subtotal, raw_discount))

    fee_base = _round2(max(0.0, subtotal - discount))
    service_fee = _round2(fee_base * rules.service_fee_percent)
    total = _round2(fee_base + service_fee)

    breakdown = WaterSportPassBreakdown(
        base_pass_cost=base_pass_cost,
        slot_adjustment=slot_adjustment,
        equipment_insurance_cost=equipment_insurance_cost,
        photo_package_cost=photo_package_cost,
        guide_support_cost=guide_support_cost,
        markup_amount=markup_amount,
        subtotal=subtotal,
        discount=discount,
        service_fee=service_fee,
        total=total,
    )

    return breakdown, applied_promo
