"""F2P tests for event pricing validators."""

from utils.event_pricing_validators import normalize_promo_code, sanitize_event_pricing_request, validate_event_pricing_request


def test_f2p_sanitizes_and_normalizes_payload():
    request = sanitize_event_pricing_request({
        'destination': '  Goa  ',
        'event_type': 'Conference',
        'tier': 'Premium',
        'attendees': '120',
        'days': '3',
        'season': ' peak ',
        'include_meals': 'yes',
        'include_stage_setup': '1',
        'include_photography': 'true',
        'markup_percent': '10',
        'promo_code': ' corp8 ',
    })

    assert request.destination == 'Goa'
    assert request.attendees == 120
    assert request.days == 3
    assert request.season == 'PEAK'
    assert request.include_meals is True
    assert request.include_stage_setup is True
    assert request.include_photography is True
    assert request.markup_percent == 10.0
    assert request.promo_code == 'CORP8'


def test_f2p_rejects_invalid_payload_fields():
    request = sanitize_event_pricing_request({
        'destination': '',
        'event_type': 'Other',
        'tier': 'Ultra',
        'attendees': 1,
        'days': 0,
        'season': 'MID',
        'markup_percent': 99,
    })

    result = validate_event_pricing_request(request)

    assert result.valid is False
    assert 'destination is required' in result.errors
    assert 'event_type must be Conference, Retreat, or Celebration' in result.errors
    assert 'tier must be Basic, Pro, or Premium' in result.errors
    assert 'season must be PEAK, REGULAR, or LOW' in result.errors
    assert 'attendees must be between 5 and 500' in result.errors
    assert 'days must be between 1 and 10' in result.errors
    assert 'markup_percent must be between 0 and 28' in result.errors


def test_f2p_accepts_valid_retreat_payload():
    request = sanitize_event_pricing_request({
        'destination': 'Konkan',
        'event_type': 'Retreat',
        'tier': 'Pro',
        'attendees': 60,
        'days': 4,
        'season': 'LOW',
        'include_meals': True,
        'include_stage_setup': False,
        'include_photography': False,
        'markup_percent': 5,
    })

    result = validate_event_pricing_request(request)
    assert result.valid is True
    assert result.errors == []


def test_f2p_rejects_negative_markup():
    request = sanitize_event_pricing_request({
        'destination': 'Goa',
        'event_type': 'Conference',
        'tier': 'Basic',
        'attendees': 20,
        'days': 2,
        'season': 'REGULAR',
        'markup_percent': -1,
    })

    result = validate_event_pricing_request(request)
    assert result.valid is False
    assert 'markup_percent must be between 0 and 28' in result.errors


def test_f2p_returns_none_for_non_string_promo_code():
    assert normalize_promo_code(10) is None
    assert normalize_promo_code(None) is None
