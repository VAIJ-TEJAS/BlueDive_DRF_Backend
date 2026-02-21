"""Rules and defaults for group pricing."""

from typing import Optional
from utils.group_pricing_types import GroupPricingRules


DEFAULT_GROUP_PRICING_RULES = GroupPricingRules(
    base_daily_per_person={
        'Standard': 1800.0,
        'Premium': 3100.0,
        'Elite': 5200.0,
    },
    category_multiplier={
        'Corporate': 1.12,
        'Student': 0.86,
        'Family': 1.00,
    },
    season_multiplier={
        'PEAK': 1.22,
        'REGULAR': 1.00,
        'LOW': 0.85,
    },
    meals_per_person_per_day=350.0,
    transport_per_day=2400.0,
    guide_per_day=1800.0,
    service_charge_percent=0.03,
    max_markup_percent=30.0,
    promo_discount_percent={
        'GROUP7': 0.07,
        'CORP9': 0.09,
        'STUDENT5': 0.05,
    },
)


def clone_group_pricing_rules(rules: GroupPricingRules) -> GroupPricingRules:
    return GroupPricingRules(
        base_daily_per_person=dict(rules.base_daily_per_person),
        category_multiplier=dict(rules.category_multiplier),
        season_multiplier=dict(rules.season_multiplier),
        meals_per_person_per_day=rules.meals_per_person_per_day,
        transport_per_day=rules.transport_per_day,
        guide_per_day=rules.guide_per_day,
        service_charge_percent=rules.service_charge_percent,
        max_markup_percent=rules.max_markup_percent,
        promo_discount_percent=dict(rules.promo_discount_percent),
    )


def merge_group_pricing_rules(overrides: Optional[GroupPricingRules] = None) -> GroupPricingRules:
    if overrides is None:
        return clone_group_pricing_rules(DEFAULT_GROUP_PRICING_RULES)

    merged = clone_group_pricing_rules(DEFAULT_GROUP_PRICING_RULES)
    merged.base_daily_per_person.update(overrides.base_daily_per_person)
    merged.category_multiplier.update(overrides.category_multiplier)
    merged.season_multiplier.update(overrides.season_multiplier)
    merged.meals_per_person_per_day = overrides.meals_per_person_per_day
    merged.transport_per_day = overrides.transport_per_day
    merged.guide_per_day = overrides.guide_per_day
    merged.service_charge_percent = overrides.service_charge_percent
    merged.max_markup_percent = overrides.max_markup_percent
    merged.promo_discount_percent.update(overrides.promo_discount_percent)
    return merged
