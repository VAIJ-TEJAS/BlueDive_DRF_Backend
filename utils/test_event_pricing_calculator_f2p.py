"""F2P tests for event pricing calculator."""

from utils.event_pricing_calculator import calculate_event_pricing_breakdown
from utils.event_pricing_types import EventPricingRequest


def test_f2p_computes_peak_conference_premium_with_addons():
    request = EventPricingRequest(
        destination='Goa',
        event_type='Conference',
        tier='Premium',
        attendees=120,
        days=3,
        season='PEAK',
        include_meals=True,
        include_stage_setup=True,
        include_photography=True,
        markup_percent=10,
    )

    breakdown, _ = calculate_event_pricing_breakdown(request)

    assert breakdown.base_cost == 1548000.0
    assert breakdown.event_adjustment == 232200.0
    assert breakdown.season_adjustment == 356040.0
    assert breakdown.meals_cost == 151200.0
    assert breakdown.total == 2616822.12


def test_f2p_applies_promo_discount_correctly():
    request = EventPricingRequest(
        destination='Goa',
        event_type='Celebration',
        tier='Pro',
        attendees=80,
        days=2,
        season='PEAK',
        include_meals=True,
        include_stage_setup=True,
        include_photography=False,
        markup_percent=8,
        promo_code='EVENT6',
    )

    breakdown, applied = calculate_event_pricing_breakdown(request)

    assert applied == 'EVENT6'
    assert breakdown.discount > 0
    assert breakdown.total == 717135.98


def test_f2p_computes_low_retreat_basic_without_addons():
    request = EventPricingRequest(
        destination='Konkan',
        event_type='Retreat',
        tier='Basic',
        attendees=60,
        days=4,
        season='LOW',
        include_meals=False,
        include_stage_setup=False,
        include_photography=False,
        markup_percent=0,
    )

    breakdown, _ = calculate_event_pricing_breakdown(request)

    assert breakdown.meals_cost == 0.0
    assert breakdown.stage_setup_cost == 0.0
    assert breakdown.photography_cost == 0.0
    assert breakdown.total == 334832.4


def test_f2p_ignores_unknown_promo_code():
    request = EventPricingRequest(
        destination='Goa',
        event_type='Conference',
        tier='Basic',
        attendees=30,
        days=2,
        season='REGULAR',
        include_meals=False,
        include_stage_setup=False,
        include_photography=False,
        markup_percent=0,
        promo_code='UNKNOWN',
    )

    breakdown, applied = calculate_event_pricing_breakdown(request)

    assert applied is None
    assert breakdown.discount == 0.0
