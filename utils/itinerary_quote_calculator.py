"""Calculator logic for itinerary quotes."""

from typing import Optional, Tuple
from utils.itinerary_quote_types import (
    ItineraryQuoteRequest,
    ItineraryQuoteRules,
    ItineraryQuoteBreakdown,
)
from utils.itinerary_quote_rules import merge_itinerary_quote_rules


def _round2(value: float) -> float:
    return round(value + 1e-9, 2)


def _itinerary_multiplier(request: ItineraryQuoteRequest, rules: ItineraryQuoteRules) -> float:
    if request.itinerary_type == 'Adventure Trip':
        return rules.adventure_multiplier
    if request.itinerary_type == 'Family Vacation':
        return rules.family_multiplier
    return rules.weekend_multiplier


def _promo_discount(subtotal: float, promo: Optional[str], rules: ItineraryQuoteRules) -> Tuple[Optional[str], float]:
    if not promo:
        return None, 0.0

    percent = rules.promo_discount_by_code.get(promo, 0.0)
    if percent <= 0:
        return None, 0.0

    return promo, subtotal * percent


def calculate_itinerary_quote_breakdown(
    request: ItineraryQuoteRequest,
    custom_rules: Optional[ItineraryQuoteRules] = None,
):
    rules = merge_itinerary_quote_rules(custom_rules)

    adult_component = request.adults * request.days * rules.base_per_day_adult
    child_component = request.children * request.days * rules.base_per_day_adult * rules.child_multiplier
    base_package = _round2(adult_component + child_component)

    itinerary_adjustment = _round2(base_package * (_itinerary_multiplier(request, rules) - 1.0))

    hotel_surcharge = _round2((rules.star_surcharge_by_hotel.get(request.hotel_stars, 0.0)) * request.days)

    total_people = request.adults + request.children
    breakfast_cost = _round2(total_people * request.days * rules.breakfast_per_person_per_day) if request.include_breakfast else 0.0
    transfer_cost = _round2(rules.transfers_flat_fee) if request.include_transfers else 0.0

    pre_season = _round2(base_package + itinerary_adjustment + hotel_surcharge + breakfast_cost + transfer_cost)

    seasonal_multiplier = rules.seasonal_multiplier_by_month.get(request.travel_month, 1.0)
    seasonal_adjustment = _round2(pre_season * (seasonal_multiplier - 1.0))

    subtotal = _round2(pre_season + seasonal_adjustment)

    applied_promo, discount_amount = _promo_discount(subtotal, request.promo_code, rules)
    discount = _round2(min(subtotal, discount_amount))

    fee_base = _round2(max(0.0, subtotal - discount))
    service_fee = _round2(fee_base * rules.service_fee_percent)
    total = _round2(fee_base + service_fee)

    breakdown = ItineraryQuoteBreakdown(
        base_package=base_package,
        itinerary_adjustment=itinerary_adjustment,
        hotel_surcharge=hotel_surcharge,
        breakfast_cost=breakfast_cost,
        transfer_cost=transfer_cost,
        seasonal_adjustment=seasonal_adjustment,
        subtotal=subtotal,
        discount=discount,
        service_fee=service_fee,
        total=total,
    )

    return breakdown, applied_promo
