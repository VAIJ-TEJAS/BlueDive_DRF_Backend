"""Rule helpers for lodging bundle pricing."""

from typing import Optional
from utils.lodging_bundle_types import LodgingBundleRules


DEFAULT_LODGING_BUNDLE_RULES = LodgingBundleRules(
    base_room_per_night={'Standard': 2600.0, 'Deluxe': 4200.0, 'Suite': 6900.0},
    bundle_multiplier={'Business': 1.14, 'Leisure': 1.00, 'Honeymoon': 1.20},
    season_multiplier={'PEAK': 1.24, 'REGULAR': 1.00, 'LOW': 0.87},
    breakfast_per_guest_per_day=280.0,
    airport_pickup_flat=3200.0,
    sightseeing_per_guest=950.0,
    service_fee_percent=0.03,
    max_markup_percent=26.0,
    promo_discount_percent={'BUNDLE6': 0.06, 'ROMANCE8': 0.08, 'STAY5': 0.05},
)


def clone_lodging_bundle_rules(rules: LodgingBundleRules) -> LodgingBundleRules:
    return LodgingBundleRules(
        base_room_per_night=dict(rules.base_room_per_night),
        bundle_multiplier=dict(rules.bundle_multiplier),
        season_multiplier=dict(rules.season_multiplier),
        breakfast_per_guest_per_day=rules.breakfast_per_guest_per_day,
        airport_pickup_flat=rules.airport_pickup_flat,
        sightseeing_per_guest=rules.sightseeing_per_guest,
        service_fee_percent=rules.service_fee_percent,
        max_markup_percent=rules.max_markup_percent,
        promo_discount_percent=dict(rules.promo_discount_percent),
    )


def merge_lodging_bundle_rules(overrides: Optional[LodgingBundleRules] = None) -> LodgingBundleRules:
    if overrides is None:
        return clone_lodging_bundle_rules(DEFAULT_LODGING_BUNDLE_RULES)

    merged = clone_lodging_bundle_rules(DEFAULT_LODGING_BUNDLE_RULES)
    merged.base_room_per_night.update(overrides.base_room_per_night)
    merged.bundle_multiplier.update(overrides.bundle_multiplier)
    merged.season_multiplier.update(overrides.season_multiplier)
    merged.breakfast_per_guest_per_day = overrides.breakfast_per_guest_per_day
    merged.airport_pickup_flat = overrides.airport_pickup_flat
    merged.sightseeing_per_guest = overrides.sightseeing_per_guest
    merged.service_fee_percent = overrides.service_fee_percent
    merged.max_markup_percent = overrides.max_markup_percent
    merged.promo_discount_percent.update(overrides.promo_discount_percent)
    return merged
