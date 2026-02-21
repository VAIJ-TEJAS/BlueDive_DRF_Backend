"""F2P tests for fare quote calculator."""

from utils.fare_quote_calculator import compute_fare_quote_breakdown, is_night_pickup
from utils.fare_quote_rules import DEFAULT_FARE_QUOTE_RULES
from utils.fare_quote_types import FareQuoteRequest


def test_f2p_applies_minimum_fare_for_short_one_way_trip():
    request = FareQuoteRequest(
        source_city='Mumbai',
        destination_city='Thane',
        trip_type='One-Way Trip',
        pickup_time='14:00',
        distance_km=8,
        travellers=2,
        luggage_units=1,
    )

    breakdown, _ = compute_fare_quote_breakdown(request)

    assert breakdown.travel_fare == 500.0
    assert breakdown.minimum_adjustment == 348.0
    assert breakdown.luggage_surcharge == 45.0
    assert breakdown.total == 566.8


def test_f2p_applies_night_surcharge_and_coupon_discount():
    request = FareQuoteRequest(
        source_city='Mumbai',
        destination_city='Pune',
        trip_type='One-Way Trip',
        pickup_time='23:00',
        distance_km=180,
        travellers=3,
        luggage_units=2,
        coupon_code='WELCOME10',
    )

    breakdown, applied_coupon = compute_fare_quote_breakdown(request)

    assert breakdown.travel_fare == 3420.0
    assert breakdown.night_surcharge == 702.0
    assert applied_coupon == 'WELCOME10'
    assert breakdown.discount == 421.2
    assert breakdown.total == 3942.43


def test_f2p_computes_hourly_rental_fare_path():
    request = FareQuoteRequest(
        source_city='Mumbai',
        destination_city='Mumbai',
        trip_type='Hourly Rental',
        pickup_time='11:30',
        rental_hours=4,
        travellers=2,
        luggage_units=0,
    )

    breakdown, _ = compute_fare_quote_breakdown(request)

    assert breakdown.travel_fare == 1400.0
    assert breakdown.minimum_adjustment == 0.0
    assert breakdown.subtotal == 1400.0
    assert breakdown.total == 1456.0


def test_f2p_detects_night_window_over_midnight():
    assert is_night_pickup('23:30', DEFAULT_FARE_QUOTE_RULES) is True
    assert is_night_pickup('04:15', DEFAULT_FARE_QUOTE_RULES) is True
    assert is_night_pickup('15:15', DEFAULT_FARE_QUOTE_RULES) is False
