"""Rules and defaults for itinerary quote calculation."""

from typing import Optional
from utils.itinerary_quote_types import ItineraryQuoteRules


DEFAULT_ITINERARY_QUOTE_RULES = ItineraryQuoteRules(
    base_per_day_adult=2800.0,
    child_multiplier=0.55,
    weekend_multiplier=1.08,
    adventure_multiplier=1.18,
    family_multiplier=1.05,
    star_surcharge_by_hotel={
        3: 0.0,
        4: 600.0,
        5: 1400.0,
    },
    breakfast_per_person_per_day=220.0,
    transfers_flat_fee=1800.0,
    seasonal_multiplier_by_month={
        'JAN': 1.15,
        'FEB': 1.10,
        'MAR': 1.05,
        'APR': 1.00,
        'MAY': 0.96,
        'JUN': 0.92,
        'JUL': 0.90,
        'AUG': 0.90,
        'SEP': 0.95,
        'OCT': 1.05,
        'NOV': 1.10,
        'DEC': 1.20,
    },
    service_fee_percent=0.035,
    promo_discount_by_code={
        'BLUEDIVE10': 0.10,
        'FAMILY7': 0.07,
        'GETAWAY5': 0.05,
    },
)


def clone_itinerary_quote_rules(rules: ItineraryQuoteRules) -> ItineraryQuoteRules:
    return ItineraryQuoteRules(
        base_per_day_adult=rules.base_per_day_adult,
        child_multiplier=rules.child_multiplier,
        weekend_multiplier=rules.weekend_multiplier,
        adventure_multiplier=rules.adventure_multiplier,
        family_multiplier=rules.family_multiplier,
        star_surcharge_by_hotel=dict(rules.star_surcharge_by_hotel),
        breakfast_per_person_per_day=rules.breakfast_per_person_per_day,
        transfers_flat_fee=rules.transfers_flat_fee,
        seasonal_multiplier_by_month=dict(rules.seasonal_multiplier_by_month),
        service_fee_percent=rules.service_fee_percent,
        promo_discount_by_code=dict(rules.promo_discount_by_code),
    )


def merge_itinerary_quote_rules(overrides: Optional[ItineraryQuoteRules] = None) -> ItineraryQuoteRules:
    if overrides is None:
        return clone_itinerary_quote_rules(DEFAULT_ITINERARY_QUOTE_RULES)

    merged = clone_itinerary_quote_rules(DEFAULT_ITINERARY_QUOTE_RULES)
    merged.base_per_day_adult = overrides.base_per_day_adult
    merged.child_multiplier = overrides.child_multiplier
    merged.weekend_multiplier = overrides.weekend_multiplier
    merged.adventure_multiplier = overrides.adventure_multiplier
    merged.family_multiplier = overrides.family_multiplier
    merged.star_surcharge_by_hotel.update(overrides.star_surcharge_by_hotel)
    merged.breakfast_per_person_per_day = overrides.breakfast_per_person_per_day
    merged.transfers_flat_fee = overrides.transfers_flat_fee
    merged.seasonal_multiplier_by_month.update(overrides.seasonal_multiplier_by_month)
    merged.service_fee_percent = overrides.service_fee_percent
    merged.promo_discount_by_code.update(overrides.promo_discount_by_code)
    return merged
