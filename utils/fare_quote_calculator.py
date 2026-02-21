"""Fare quote calculation logic."""

from typing import Optional
from utils.fare_quote_types import FareQuoteRequest, FareQuoteRules, FareQuoteBreakdown
from utils.fare_quote_rules import merge_fare_quote_rules


def _round2(value: float) -> float:
    return round(value + 1e-9, 2)


def _parse_hour(pickup_time: str) -> Optional[int]:
    try:
        return int(pickup_time.split(':')[0])
    except (ValueError, IndexError):
        return None


def is_night_pickup(pickup_time: str, rules: FareQuoteRules) -> bool:
    hour = _parse_hour(pickup_time)
    if hour is None:
        return False

    if rules.night_start_hour > rules.night_end_hour:
        return hour >= rules.night_start_hour or hour < rules.night_end_hour

    return rules.night_start_hour <= hour < rules.night_end_hour


def _compute_travel_fare(request: FareQuoteRequest, rules: FareQuoteRules) -> float:
    if request.trip_type == 'Hourly Rental':
        return (request.rental_hours or 0.0) * rules.hourly_rate

    base = (request.distance_km or 0.0) * rules.per_km_rate
    if request.trip_type == 'Round Trip':
        return base * rules.round_trip_multiplier

    return base


def _compute_discount(subtotal: float, coupon_code: Optional[str], rules: FareQuoteRules):
    if not coupon_code:
        return None, 0.0

    percent = rules.coupon_discounts.get(coupon_code, 0.0)
    if percent <= 0:
        return None, 0.0

    return coupon_code, subtotal * percent


def compute_fare_quote_breakdown(request: FareQuoteRequest, custom_rules: Optional[FareQuoteRules] = None):
    rules = merge_fare_quote_rules(custom_rules)

    raw_travel_fare = _compute_travel_fare(request, rules)
    travel_fare = max(raw_travel_fare, rules.minimum_fare)
    minimum_adjustment = _round2(travel_fare - raw_travel_fare)

    luggage_surcharge = _round2(request.luggage_units * rules.luggage_surcharge_per_unit)

    if is_night_pickup(request.pickup_time, rules):
        night_surcharge = _round2((travel_fare + luggage_surcharge) * rules.night_surcharge_percent)
    else:
        night_surcharge = 0.0

    surge_surcharge = _round2(
        (travel_fare + luggage_surcharge + night_surcharge) * (rules.surge_multiplier - 1)
    )

    subtotal = _round2(travel_fare + luggage_surcharge + night_surcharge + surge_surcharge)

    applied_coupon, raw_discount = _compute_discount(subtotal, request.coupon_code, rules)
    discount = _round2(min(subtotal, raw_discount))

    discounted_subtotal = _round2(max(0.0, subtotal - discount))
    service_fee = _round2(discounted_subtotal * rules.service_fee_percent)
    total = _round2(discounted_subtotal + service_fee)

    breakdown = FareQuoteBreakdown(
        travel_fare=_round2(travel_fare),
        minimum_adjustment=minimum_adjustment,
        luggage_surcharge=luggage_surcharge,
        night_surcharge=night_surcharge,
        surge_surcharge=surge_surcharge,
        subtotal=subtotal,
        discount=discount,
        service_fee=service_fee,
        total=total,
    )

    return breakdown, applied_coupon
