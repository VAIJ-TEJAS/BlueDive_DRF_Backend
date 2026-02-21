"""F2P tests for lodging bundle validators."""

from utils.lodging_bundle_validators import normalize_promo_code, sanitize_lodging_bundle_request, validate_lodging_bundle_request


def test_f2p_sanitizes_and_normalizes_payload():
    request = sanitize_lodging_bundle_request({
        'destination': '  Goa  ',
        'bundle_type': 'Business',
        'room_type': 'Deluxe',
        'nights': '4',
        'rooms': '10',
        'guests': '25',
        'include_breakfast': 'yes',
        'include_airport_pickup': '1',
        'include_sightseeing': 'true',
        'season_code': ' peak ',
        'markup_percent': '12',
        'promo_code': ' bundle6 ',
    })

    assert request.destination == 'Goa'
    assert request.nights == 4
    assert request.rooms == 10
    assert request.guests == 25
    assert request.season_code == 'PEAK'
    assert request.markup_percent == 12.0
    assert request.promo_code == 'BUNDLE6'


def test_f2p_rejects_invalid_payload_fields():
    request = sanitize_lodging_bundle_request({
        'destination': '',
        'bundle_type': 'Other',
        'room_type': 'Ultra',
        'nights': 0,
        'rooms': 0,
        'guests': 0,
        'season_code': 'MID',
        'markup_percent': 99,
    })

    result = validate_lodging_bundle_request(request)

    assert result.valid is False
    assert 'destination is required' in result.errors
    assert 'bundle_type must be Business, Leisure, or Honeymoon' in result.errors
    assert 'room_type must be Standard, Deluxe, or Suite' in result.errors
    assert 'season_code must be PEAK, REGULAR, or LOW' in result.errors
    assert 'nights must be between 1 and 15' in result.errors
    assert 'rooms must be between 1 and 40' in result.errors
    assert 'guests must be between 1 and 120' in result.errors
    assert 'markup_percent must be between 0 and 26' in result.errors


def test_f2p_accepts_valid_payload():
    request = sanitize_lodging_bundle_request({
        'destination': 'Konkan',
        'bundle_type': 'Leisure',
        'room_type': 'Standard',
        'nights': 5,
        'rooms': 6,
        'guests': 12,
        'include_breakfast': True,
        'include_airport_pickup': True,
        'include_sightseeing': False,
        'season_code': 'LOW',
        'markup_percent': 8,
    })

    result = validate_lodging_bundle_request(request)
    assert result.valid is True
    assert result.errors == []


def test_f2p_rejects_negative_markup():
    request = sanitize_lodging_bundle_request({
        'destination': 'Goa',
        'bundle_type': 'Business',
        'room_type': 'Standard',
        'nights': 2,
        'rooms': 2,
        'guests': 4,
        'season_code': 'REGULAR',
        'markup_percent': -1,
    })

    result = validate_lodging_bundle_request(request)
    assert result.valid is False
    assert 'markup_percent must be between 0 and 26' in result.errors


def test_f2p_returns_none_for_non_string_promo():
    assert normalize_promo_code(10) is None
    assert normalize_promo_code(None) is None
