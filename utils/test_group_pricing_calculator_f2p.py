"""F2P tests for group pricing calculator."""

from utils.group_pricing_calculator import calculate_group_pricing_breakdown
from utils.group_pricing_types import GroupPricingRequest


def test_f2p_computes_corporate_premium_with_all_addons():
    request = GroupPricingRequest(
        destination='Goa',
        group_category='Corporate',
        travel_class='Premium',
        travelers=20,
        trip_days=4,
        include_meals=True,
        include_transport=True,
        include_guide=True,
        season_code='PEAK',
        markup_percent=12,
    )

    breakdown, _ = calculate_group_pricing_breakdown(request)

    assert breakdown.base_cost == 248000.0
    assert breakdown.category_adjustment == 29760.0
    assert breakdown.season_adjustment == 61107.2
    assert breakdown.meals_cost == 28000.0
    assert breakdown.total == 442598.48


def test_f2p_applies_promo_discount_correctly():
    request = GroupPricingRequest(
        destination='Goa',
        group_category='Family',
        travel_class='Elite',
        travelers=12,
        trip_days=5,
        include_meals=True,
        include_transport=True,
        include_guide=True,
        season_code='PEAK',
        markup_percent=8,
        promo_code='GROUP7',
    )

    breakdown, applied_promo = calculate_group_pricing_breakdown(request)

    assert applied_promo == 'GROUP7'
    assert breakdown.discount > 0
    assert breakdown.total == 437234.61


def test_f2p_computes_low_season_student_standard_without_addons():
    request = GroupPricingRequest(
        destination='Konkan',
        group_category='Student',
        travel_class='Standard',
        travelers=30,
        trip_days=5,
        include_meals=False,
        include_transport=False,
        include_guide=False,
        season_code='LOW',
        markup_percent=0,
    )

    breakdown, _ = calculate_group_pricing_breakdown(request)

    assert breakdown.meals_cost == 0.0
    assert breakdown.transport_cost == 0.0
    assert breakdown.guide_cost == 0.0
    assert breakdown.total == 203291.1


def test_f2p_ignores_unknown_promo():
    request = GroupPricingRequest(
        destination='Goa',
        group_category='Family',
        travel_class='Standard',
        travelers=10,
        trip_days=3,
        include_meals=False,
        include_transport=False,
        include_guide=False,
        season_code='REGULAR',
        markup_percent=0,
        promo_code='UNKNOWN',
    )

    breakdown, applied = calculate_group_pricing_breakdown(request)
    assert applied is None
    assert breakdown.discount == 0.0
