"""Rule helpers for water sport pass pricing."""

from typing import Optional
from utils.water_sport_pass_types import WaterSportPassRules


DEFAULT_WATER_SPORT_PASS_RULES = WaterSportPassRules(
    base_per_participant_per_day={'Starter': 1800.0, 'Explorer': 2600.0, 'Pro': 3400.0},
    slot_multiplier={'Morning': 1.00, 'Afternoon': 1.08, 'Sunset': 1.15},
    equipment_insurance_per_participant_per_day=220.0,
    photo_package_per_participant=350.0,
    guide_support_per_day=1200.0,
    service_fee_percent=0.03,
    max_markup_percent=24.0,
    promo_discount_percent={'SPLASH5': 0.05, 'WAVE7': 0.07, 'CREW9': 0.09},
)


def clone_water_sport_pass_rules(rules: WaterSportPassRules) -> WaterSportPassRules:
    return WaterSportPassRules(
        base_per_participant_per_day=dict(rules.base_per_participant_per_day),
        slot_multiplier=dict(rules.slot_multiplier),
        equipment_insurance_per_participant_per_day=rules.equipment_insurance_per_participant_per_day,
        photo_package_per_participant=rules.photo_package_per_participant,
        guide_support_per_day=rules.guide_support_per_day,
        service_fee_percent=rules.service_fee_percent,
        max_markup_percent=rules.max_markup_percent,
        promo_discount_percent=dict(rules.promo_discount_percent),
    )


def merge_water_sport_pass_rules(overrides: Optional[WaterSportPassRules] = None) -> WaterSportPassRules:
    if overrides is None:
        return clone_water_sport_pass_rules(DEFAULT_WATER_SPORT_PASS_RULES)

    merged = clone_water_sport_pass_rules(DEFAULT_WATER_SPORT_PASS_RULES)
    merged.base_per_participant_per_day.update(overrides.base_per_participant_per_day)
    merged.slot_multiplier.update(overrides.slot_multiplier)
    merged.equipment_insurance_per_participant_per_day = overrides.equipment_insurance_per_participant_per_day
    merged.photo_package_per_participant = overrides.photo_package_per_participant
    merged.guide_support_per_day = overrides.guide_support_per_day
    merged.service_fee_percent = overrides.service_fee_percent
    merged.max_markup_percent = overrides.max_markup_percent
    merged.promo_discount_percent.update(overrides.promo_discount_percent)
    return merged
