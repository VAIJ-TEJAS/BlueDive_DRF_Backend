"""F2P tests for snorkel camp calculator."""

from utils.snorkel_camp_types import SnorkelCampRequest
from utils.snorkel_camp_calculator import calculate_snorkel_camp_breakdown


def test_f2p_calculates_expected_totals_with_addons_and_discount():
    request = SnorkelCampRequest(
        destination='Goa',
        camp_tier='Elite',
        season_band='PEAK',
        participants=6,
        days=2,
        include_equipment=True,
        include_meals=True,
        include_certification=True,
        markup_percent=10,
        promo_code='DEEP10',
    )

    breakdown, applied = calculate_snorkel_camp_breakdown(request)

    assert applied == 'DEEP10'
    assert breakdown.base_camp_cost == 51600.0
    assert breakdown.season_adjustment == 10320.0
    assert breakdown.equipment_cost == 3120.0
    assert breakdown.meals_cost == 3840.0
    assert breakdown.certification_cost == 10800.0
    assert breakdown.markup_amount == 7968.0
    assert breakdown.subtotal == 87648.0
    assert breakdown.discount == 8764.8
    assert breakdown.service_fee == 2366.5
    assert breakdown.total == 81249.7


def test_f2p_calculates_without_optional_addons():
    request = SnorkelCampRequest(
        destination='Konkan',
        camp_tier='Starter',
        season_band='LOW',
        participants=4,
        days=1,
        include_equipment=False,
        include_meals=False,
        include_certification=False,
        markup_percent=0,
        promo_code=None,
    )

    breakdown, applied = calculate_snorkel_camp_breakdown(request)

    assert applied is None
    assert breakdown.base_camp_cost == 8800.0
    assert breakdown.season_adjustment == -880.0
    assert breakdown.subtotal == 7920.0
    assert breakdown.discount == 0.0
    assert breakdown.service_fee == 237.6
    assert breakdown.total == 8157.6


def test_f2p_caps_markup_to_rule_limit():
    request = SnorkelCampRequest(
        destination='Ratnagiri',
        camp_tier='Adventure',
        season_band='REGULAR',
        participants=5,
        days=2,
        include_equipment=True,
        include_meals=False,
        include_certification=False,
        markup_percent=70,
        promo_code=None,
    )

    breakdown, _ = calculate_snorkel_camp_breakdown(request)

    assert breakdown.base_camp_cost == 31000.0
    assert breakdown.equipment_cost == 2600.0
    assert breakdown.markup_amount == 8400.0
    assert breakdown.total == 43260.0
