"""F2P tests for water sport pass calculator."""

from utils.water_sport_pass_types import WaterSportPassRequest
from utils.water_sport_pass_calculator import calculate_water_sport_pass_breakdown


def test_f2p_calculates_expected_total_with_addons_and_discount():
    request = WaterSportPassRequest(
        destination='Goa',
        pass_tier='Pro',
        session_slot='Sunset',
        participants=6,
        days=2,
        include_equipment_insurance=True,
        include_photo_package=True,
        include_guide_support=True,
        markup_percent=10,
        promo_code='CREW9',
    )

    breakdown, applied = calculate_water_sport_pass_breakdown(request)

    assert applied == 'CREW9'
    assert breakdown.base_pass_cost == 40800.0
    assert breakdown.slot_adjustment == 6120.0
    assert breakdown.equipment_insurance_cost == 2640.0
    assert breakdown.photo_package_cost == 2100.0
    assert breakdown.guide_support_cost == 2400.0
    assert breakdown.markup_amount == 5406.0
    assert breakdown.subtotal == 59466.0
    assert breakdown.discount == 5351.94
    assert breakdown.service_fee == 1623.42
    assert breakdown.total == 55737.48


def test_f2p_calculates_without_optional_addons():
    request = WaterSportPassRequest(
        destination='Konkan',
        pass_tier='Starter',
        session_slot='Morning',
        participants=4,
        days=1,
        include_equipment_insurance=False,
        include_photo_package=False,
        include_guide_support=False,
        markup_percent=0,
        promo_code=None,
    )

    breakdown, applied = calculate_water_sport_pass_breakdown(request)

    assert applied is None
    assert breakdown.base_pass_cost == 7200.0
    assert breakdown.slot_adjustment == 0.0
    assert breakdown.subtotal == 7200.0
    assert breakdown.discount == 0.0
    assert breakdown.service_fee == 216.0
    assert breakdown.total == 7416.0


def test_f2p_caps_markup_at_rule_limit():
    request = WaterSportPassRequest(
        destination='Ratnagiri',
        pass_tier='Explorer',
        session_slot='Afternoon',
        participants=5,
        days=2,
        include_equipment_insurance=True,
        include_photo_package=False,
        include_guide_support=False,
        markup_percent=80,
        promo_code=None,
    )

    breakdown, _ = calculate_water_sport_pass_breakdown(request)

    assert breakdown.base_pass_cost == 26000.0
    assert breakdown.slot_adjustment == 2080.0
    assert breakdown.equipment_insurance_cost == 2200.0
    assert breakdown.markup_amount == 7267.2
    assert breakdown.total == 38673.62
