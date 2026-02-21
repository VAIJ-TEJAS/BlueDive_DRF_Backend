"""Rule helpers for snorkel camp pricing."""

from typing import Optional
from utils.snorkel_camp_types import SnorkelCampRules


DEFAULT_SNORKEL_CAMP_RULES = SnorkelCampRules(
    base_per_participant_per_day={'Starter': 2200.0, 'Adventure': 3100.0, 'Elite': 4300.0},
    season_multiplier={'LOW': 0.9, 'REGULAR': 1.0, 'PEAK': 1.2},
    equipment_per_participant_per_day=260.0,
    meals_per_participant_per_day=320.0,
    certification_per_participant=1800.0,
    service_fee_percent=0.03,
    max_markup_percent=25.0,
    promo_discount_percent={'CAMP5': 0.05, 'REEF8': 0.08, 'DEEP10': 0.10},
)


def clone_snorkel_camp_rules(rules: SnorkelCampRules) -> SnorkelCampRules:
    return SnorkelCampRules(
        base_per_participant_per_day=dict(rules.base_per_participant_per_day),
        season_multiplier=dict(rules.season_multiplier),
        equipment_per_participant_per_day=rules.equipment_per_participant_per_day,
        meals_per_participant_per_day=rules.meals_per_participant_per_day,
        certification_per_participant=rules.certification_per_participant,
        service_fee_percent=rules.service_fee_percent,
        max_markup_percent=rules.max_markup_percent,
        promo_discount_percent=dict(rules.promo_discount_percent),
    )


def merge_snorkel_camp_rules(overrides: Optional[SnorkelCampRules] = None) -> SnorkelCampRules:
    if overrides is None:
        return clone_snorkel_camp_rules(DEFAULT_SNORKEL_CAMP_RULES)

    merged = clone_snorkel_camp_rules(DEFAULT_SNORKEL_CAMP_RULES)
    merged.base_per_participant_per_day.update(overrides.base_per_participant_per_day)
    merged.season_multiplier.update(overrides.season_multiplier)
    merged.equipment_per_participant_per_day = overrides.equipment_per_participant_per_day
    merged.meals_per_participant_per_day = overrides.meals_per_participant_per_day
    merged.certification_per_participant = overrides.certification_per_participant
    merged.service_fee_percent = overrides.service_fee_percent
    merged.max_markup_percent = overrides.max_markup_percent
    merged.promo_discount_percent.update(overrides.promo_discount_percent)
    return merged
