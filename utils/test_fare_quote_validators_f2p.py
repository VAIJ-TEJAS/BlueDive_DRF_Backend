"""F2P tests for fare quote validators."""

from utils.fare_quote_validators import (
    normalize_coupon,
    sanitize_fare_quote_request,
    validate_fare_quote_request,
)


def test_f2p_sanitizes_fields_and_normalizes_coupon():
    request = sanitize_fare_quote_request({
        'source_city': '  Mumbai ',
        'destination_city': ' Pune  ',
        'trip_type': 'One-Way Trip',
        'pickup_time': ' 09:45 ',
        'distance_km': '145.5',
        'travellers': '3',
        'luggage_units': '2',
        'coupon_code': ' welcome10 ',
    })

    assert request.source_city == 'Mumbai'
    assert request.destination_city == 'Pune'
    assert request.distance_km == 145.5
    assert request.travellers == 3
    assert request.luggage_units == 2
    assert request.coupon_code == 'WELCOME10'


def test_f2p_rejects_invalid_one_way_payload():
    request = sanitize_fare_quote_request({
        'source_city': 'Mumbai',
        'destination_city': 'Mumbai',
        'trip_type': 'One-Way Trip',
        'pickup_time': '29:99',
        'distance_km': -30,
        'travellers': 0,
        'luggage_units': 25,
    })

    result = validate_fare_quote_request(request)

    assert result.valid is False
    assert 'source_city and destination_city must differ for one-way trip' in result.errors
    assert 'pickup_time must be HH:MM in 24-hour format' in result.errors
    assert 'distance_km must be greater than 0 for trip type' in result.errors
    assert 'travellers must be an integer between 1 and 12' in result.errors
    assert 'luggage_units must be an integer between 0 and 20' in result.errors


def test_f2p_requires_rental_hours_for_hourly_rental():
    request = sanitize_fare_quote_request({
        'source_city': 'Mumbai',
        'destination_city': 'Mumbai',
        'trip_type': 'Hourly Rental',
        'pickup_time': '12:30',
        'travellers': 2,
        'luggage_units': 1,
    })

    result = validate_fare_quote_request(request)
    assert result.valid is False
    assert 'rental_hours must be greater than 0 for hourly rental' in result.errors


def test_f2p_accepts_valid_round_trip_payload():
    request = sanitize_fare_quote_request({
        'source_city': 'Mumbai',
        'destination_city': 'Goa',
        'trip_type': 'Round Trip',
        'pickup_time': '06:10',
        'distance_km': 590,
        'travellers': 5,
        'luggage_units': 4,
    })

    result = validate_fare_quote_request(request)
    assert result.valid is True
    assert result.errors == []


def test_f2p_returns_none_for_non_string_coupon():
    assert normalize_coupon(0) is None
    assert normalize_coupon(None) is None
