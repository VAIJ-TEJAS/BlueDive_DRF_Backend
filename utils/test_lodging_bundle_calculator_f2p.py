"""F2P tests for lodging bundle calculator."""

from utils.lodging_bundle_calculator import calculate_lodging_bundle_breakdown
from utils.lodging_bundle_types import LodgingBundleRequest


def test_f2p_computes_peak_business_deluxe_with_all_addons():
    request = LodgingBundleRequest(
        destination='Goa',
        bundle_type='Business',
        room_type='Deluxe',
        nights=4,
        rooms=10,
        guests=25,
        include_breakfast=True,
        include_airport_pickup=True,
        include_sightseeing=True,
        season_code='PEAK',
        markup_percent=12,
    )

    breakdown, _ = calculate_lodging_bundle_breakdown(request)

    assert breakdown.base_room_cost == 168000.0
    assert breakdown.bundle_adjustment == 23520.0
    assert breakdown.season_adjustment == 45964.8
    assert breakdown.breakfast_cost == 28000.0
    assert breakdown.total == 337352.79


def test_f2p_applies_promo_discount():
    request = LodgingBundleRequest(
        destination='Goa',
        bundle_type='Honeymoon',
        room_type='Suite',
        nights=3,
        rooms=3,
        guests=6,
        include_breakfast=True,
        include_airport_pickup=True,
        include_sightseeing=True,
        season_code='PEAK',
        markup_percent=10,
        promo_code='ROMANCE8',
    )

    breakdown, applied = calculate_lodging_bundle_breakdown(request)

    assert applied == 'ROMANCE8'
    assert breakdown.discount > 0
    assert breakdown.total == 110849.57


def test_f2p_computes_low_leisure_standard_without_optional_addons():
    request = LodgingBundleRequest(
        destination='Konkan',
        bundle_type='Leisure',
        room_type='Standard',
        nights=5,
        rooms=6,
        guests=12,
        include_breakfast=False,
        include_airport_pickup=False,
        include_sightseeing=False,
        season_code='LOW',
        markup_percent=0,
    )

    breakdown, _ = calculate_lodging_bundle_breakdown(request)

    assert breakdown.breakfast_cost == 0.0
    assert breakdown.pickup_cost == 0.0
    assert breakdown.sightseeing_cost == 0.0
    assert breakdown.total == 69895.8


def test_f2p_ignores_unknown_promo_code():
    request = LodgingBundleRequest(
        destination='Goa',
        bundle_type='Leisure',
        room_type='Standard',
        nights=2,
        rooms=2,
        guests=4,
        include_breakfast=False,
        include_airport_pickup=False,
        include_sightseeing=False,
        season_code='REGULAR',
        markup_percent=0,
        promo_code='UNKNOWN',
    )

    breakdown, applied = calculate_lodging_bundle_breakdown(request)
    assert applied is None
    assert breakdown.discount == 0.0
