"""F2P tests for group pricing validators."""

from utils.group_pricing_validators import (
    normalize_promo_code,
    sanitize_group_pricing_request,
    validate_group_pricing_request,
)


def test_f2p_sanitizes_and_normalizes_payload():
    request = sanitize_group_pricing_request({
        'destination': '  Goa  ',
        'group_category': 'Corporate',
        'travel_class': 'Premium',
        'travelers': '20',
        'trip_days': '4',
        'include_meals': 'yes',
        'include_transport': '1',
        'include_guide': 'true',
        'season_code': ' peak ',
        'markup_percent': '12',
        'promo_code': ' corp9 ',
    })

    assert request.destination == 'Goa'
    assert request.travelers == 20
    assert request.trip_days == 4
    assert request.include_meals is True
    assert request.include_transport is True
    assert request.include_guide is True
    assert request.season_code == 'PEAK'
    assert request.markup_percent == 12.0
    assert request.promo_code == 'CORP9'


def test_f2p_rejects_invalid_payload_fields():
    request = sanitize_group_pricing_request({
        'destination': '',
        'group_category': 'Other',
        'travel_class': 'Ultra',
        'travelers': 1,
        'trip_days': 0,
        'include_meals': False,
        'include_transport': False,
        'include_guide': False,
        'season_code': 'MID',
        'markup_percent': 99,
    })

    result = validate_group_pricing_request(request)

    assert result.valid is False
    assert 'destination is required' in result.errors
    assert 'group_category must be Corporate, Student, or Family' in result.errors
    assert 'travel_class must be Standard, Premium, or Elite' in result.errors
    assert 'season_code must be PEAK, REGULAR, or LOW' in result.errors
    assert 'travelers must be between 2 and 80' in result.errors
    assert 'trip_days must be between 1 and 20' in result.errors
    assert 'markup_percent must be between 0 and 30' in result.errors


def test_f2p_accepts_valid_student_payload():
    request = sanitize_group_pricing_request({
        'destination': 'Konkan',
        'group_category': 'Student',
        'travel_class': 'Standard',
        'travelers': 30,
        'trip_days': 5,
        'include_meals': True,
        'include_transport': True,
        'include_guide': False,
        'season_code': 'LOW',
        'markup_percent': 5,
    })

    result = validate_group_pricing_request(request)
    assert result.valid is True
    assert result.errors == []


def test_f2p_rejects_markup_below_zero():
    request = sanitize_group_pricing_request({
        'destination': 'Goa',
        'group_category': 'Family',
        'travel_class': 'Standard',
        'travelers': 5,
        'trip_days': 3,
        'include_meals': False,
        'include_transport': False,
        'include_guide': False,
        'season_code': 'REGULAR',
        'markup_percent': -1,
    })

    result = validate_group_pricing_request(request)
    assert result.valid is False
    assert 'markup_percent must be between 0 and 30' in result.errors


def test_f2p_returns_none_for_non_string_promo_code():
    assert normalize_promo_code(10) is None
    assert normalize_promo_code(None) is None
