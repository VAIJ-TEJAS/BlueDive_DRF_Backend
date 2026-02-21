"""Rules and helpers for fare quote calculations."""

from copy import deepcopy
from typing import Optional
from utils.fare_quote_types import FareQuoteRules


DEFAULT_FARE_QUOTE_RULES = FareQuoteRules(
    per_km_rate=19.0,
    round_trip_multiplier=1.8,
    hourly_rate=350.0,
    minimum_fare=500.0,
    luggage_surcharge_per_unit=45.0,
    service_fee_percent=0.04,
    night_surcharge_percent=0.2,
    night_start_hour=22,
    night_end_hour=5,
    surge_multiplier=1.0,
    coupon_discounts={
        'WELCOME10': 0.10,
        'SAVE15': 0.15,
        'FAMILY5': 0.05,
    },
)


def clone_fare_quote_rules(rules: FareQuoteRules) -> FareQuoteRules:
    return FareQuoteRules(
        per_km_rate=rules.per_km_rate,
        round_trip_multiplier=rules.round_trip_multiplier,
        hourly_rate=rules.hourly_rate,
        minimum_fare=rules.minimum_fare,
        luggage_surcharge_per_unit=rules.luggage_surcharge_per_unit,
        service_fee_percent=rules.service_fee_percent,
        night_surcharge_percent=rules.night_surcharge_percent,
        night_start_hour=rules.night_start_hour,
        night_end_hour=rules.night_end_hour,
        surge_multiplier=rules.surge_multiplier,
        coupon_discounts=deepcopy(rules.coupon_discounts),
    )


def merge_fare_quote_rules(overrides: Optional[FareQuoteRules] = None) -> FareQuoteRules:
    if overrides is None:
        return clone_fare_quote_rules(DEFAULT_FARE_QUOTE_RULES)

    merged = clone_fare_quote_rules(DEFAULT_FARE_QUOTE_RULES)
    merged.per_km_rate = overrides.per_km_rate
    merged.round_trip_multiplier = overrides.round_trip_multiplier
    merged.hourly_rate = overrides.hourly_rate
    merged.minimum_fare = overrides.minimum_fare
    merged.luggage_surcharge_per_unit = overrides.luggage_surcharge_per_unit
    merged.service_fee_percent = overrides.service_fee_percent
    merged.night_surcharge_percent = overrides.night_surcharge_percent
    merged.night_start_hour = overrides.night_start_hour
    merged.night_end_hour = overrides.night_end_hour
    merged.surge_multiplier = overrides.surge_multiplier
    merged.coupon_discounts.update(overrides.coupon_discounts)
    return merged
