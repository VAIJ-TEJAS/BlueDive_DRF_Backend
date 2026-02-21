"""F2P tests for water sport pass validators."""

from utils.water_sport_pass_validators import (
    sanitize_water_sport_pass_request,
    validate_water_sport_pass_request,
)


def test_f2p_sanitizes_payload_values():
    request = sanitize_water_sport_pass_request({
        'destination': '  Goa  ',
        'pass_tier': ' Explorer ',
        'session_slot': ' Sunset ',
        'participants': '6',
        'days': '3',
        'include_equipment_insurance': 'yes',
        'include_photo_package': 'true',
        'include_guide_support': '1',
        'markup_percent': '9.5',
        'promo_code': ' splash5 ',
    })

    assert request.destination == 'Goa'
    assert request.pass_tier == 'Explorer'
    assert request.session_slot == 'Sunset'
    assert request.participants == 6
    assert request.days == 3
    assert request.include_equipment_insurance is True
    assert request.include_photo_package is True
    assert request.include_guide_support is True
    assert request.markup_percent == 9.5
    assert request.promo_code == 'SPLASH5'


def test_f2p_validates_happy_path():
    request = sanitize_water_sport_pass_request({
        'destination': 'Tarkarli',
        'pass_tier': 'Pro',
        'session_slot': 'Afternoon',
        'participants': 8,
        'days': 2,
        'include_equipment_insurance': True,
        'include_photo_package': False,
        'include_guide_support': True,
        'markup_percent': 10,
    })

    validation = validate_water_sport_pass_request(request)
    assert validation.valid is True
    assert validation.errors == []


def test_f2p_rejects_out_of_range_values():
    request = sanitize_water_sport_pass_request({
        'destination': '',
        'pass_tier': 'Invalid',
        'session_slot': 'Night',
        'participants': 0,
        'days': 0,
        'include_equipment_insurance': False,
        'include_photo_package': False,
        'include_guide_support': False,
        'markup_percent': 99,
    })

    validation = validate_water_sport_pass_request(request)
    assert validation.valid is False
    assert 'destination is required' in validation.errors
    assert 'pass_tier must be Starter, Explorer, or Pro' in validation.errors
    assert 'session_slot must be Morning, Afternoon, or Sunset' in validation.errors
    assert 'participants must be between 1 and 80' in validation.errors
    assert 'days must be between 1 and 10' in validation.errors
    assert 'markup_percent must be between 0 and 24' in validation.errors
