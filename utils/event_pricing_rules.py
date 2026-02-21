"""Rule helpers for event pricing."""

from typing import Optional
from utils.event_pricing_types import EventPricingRules


DEFAULT_EVENT_PRICING_RULES = EventPricingRules(
    base_per_person_per_day={'Basic': 1500.0, 'Pro': 2600.0, 'Premium': 4300.0},
    event_multiplier={'Conference': 1.15, 'Retreat': 1.05, 'Celebration': 1.22},
    season_multiplier={'PEAK': 1.20, 'REGULAR': 1.00, 'LOW': 0.86},
    meals_per_person_per_day=420.0,
    stage_setup_per_day=4800.0,
    photography_per_day=2600.0,
    service_charge_percent=0.03,
    max_markup_percent=28.0,
    promo_discount_percent={'EVENT6': 0.06, 'CORP8': 0.08, 'FEST10': 0.10},
)


def clone_event_pricing_rules(rules: EventPricingRules) -> EventPricingRules:
    return EventPricingRules(
        base_per_person_per_day=dict(rules.base_per_person_per_day),
        event_multiplier=dict(rules.event_multiplier),
        season_multiplier=dict(rules.season_multiplier),
        meals_per_person_per_day=rules.meals_per_person_per_day,
        stage_setup_per_day=rules.stage_setup_per_day,
        photography_per_day=rules.photography_per_day,
        service_charge_percent=rules.service_charge_percent,
        max_markup_percent=rules.max_markup_percent,
        promo_discount_percent=dict(rules.promo_discount_percent),
    )


def merge_event_pricing_rules(overrides: Optional[EventPricingRules] = None) -> EventPricingRules:
    if overrides is None:
        return clone_event_pricing_rules(DEFAULT_EVENT_PRICING_RULES)

    merged = clone_event_pricing_rules(DEFAULT_EVENT_PRICING_RULES)
    merged.base_per_person_per_day.update(overrides.base_per_person_per_day)
    merged.event_multiplier.update(overrides.event_multiplier)
    merged.season_multiplier.update(overrides.season_multiplier)
    merged.meals_per_person_per_day = overrides.meals_per_person_per_day
    merged.stage_setup_per_day = overrides.stage_setup_per_day
    merged.photography_per_day = overrides.photography_per_day
    merged.service_charge_percent = overrides.service_charge_percent
    merged.max_markup_percent = overrides.max_markup_percent
    merged.promo_discount_percent.update(overrides.promo_discount_percent)
    return merged
