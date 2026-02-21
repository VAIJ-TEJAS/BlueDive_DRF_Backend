"""F2P tests for itinerary quote validators."""

from utils.itinerary_quote_validators import (
    normalize_promo_code,
    sanitize_itinerary_quote_request,
    validate_itinerary_quote_request,
)


def test_f2p_sanitizes_fields_and_normalizes_promo_code():
    request = sanitize_itinerary_quote_request({
        'destination': '  Goa  ',
        'itinerary_type': 'Family Vacation',
        'travel_month': ' dec ',
        'days': '4',
        'adults': '2',
        'children': '1',
        'hotel_stars': '4',
        'include_breakfast': 'yes',
        'include_transfers': '1',
        'promo_code': ' bluedive10 ',
    })

    assert request.destination == 'Goa'
    assert request.travel_month == 'DEC'
    assert request.days == 4
    assert request.adults == 2
    assert request.children == 1
    assert request.promo_code == 'BLUEDIVE10'
    assert request.include_breakfast is True
    assert request.include_transfers is True


def test_f2p_rejects_invalid_payload():
    request = sanitize_itinerary_quote_request({
        'destination': '',
        'itinerary_type': 'Random',
        'travel_month': 'XYZ',
        'days': 0,
        'adults': 0,
        'children': 9,
        'hotel_stars': 2,
        'include_breakfast': False,
        'include_transfers': False,
    })

    result = validate_itinerary_quote_request(request)

    assert result.valid is False
    assert 'destination is required' in result.errors
    assert 'itinerary_type must be Weekend Getaway, Adventure Trip, or Family Vacation' in result.errors
    assert 'travel_month must be a valid 3-letter month code' in result.errors
    assert 'days must be an integer between 1 and 15' in result.errors
    assert 'adults must be an integer between 1 and 8' in result.errors
    assert 'children must be an integer between 0 and 6' in result.errors
    assert 'hotel_stars must be one of: 3, 4, 5' in result.errors


def test_f2p_rejects_travelers_over_cap():
    request = sanitize_itinerary_quote_request({
        'destination': 'Goa',
        'itinerary_type': 'Weekend Getaway',
        'travel_month': 'JAN',
        'days': 3,
        'adults': 8,
        'children': 3,
        'hotel_stars': 3,
        'include_breakfast': False,
        'include_transfers': False,
    })

    result = validate_itinerary_quote_request(request)
    assert result.valid is False
    assert 'total travelers cannot exceed 10' in result.errors


def test_f2p_accepts_valid_adventure_trip_payload():
    request = sanitize_itinerary_quote_request({
        'destination': 'Ladakh',
        'itinerary_type': 'Adventure Trip',
        'travel_month': 'JUN',
        'days': 6,
        'adults': 3,
        'children': 0,
        'hotel_stars': 3,
        'include_breakfast': True,
        'include_transfers': True,
    })

    result = validate_itinerary_quote_request(request)
    assert result.valid is True
    assert result.errors == []


def test_f2p_returns_none_for_non_string_promo_code():
    assert normalize_promo_code(5) is None
    assert normalize_promo_code(None) is None
