"""F2P tests for snorkel camp validators."""

from utils.snorkel_camp_validators import sanitize_snorkel_camp_request, validate_snorkel_camp_request


def test_f2p_sanitizes_input_payload():
    request = sanitize_snorkel_camp_request({
        'destination': '  Goa  ',
        'camp_tier': ' Adventure ',
        'season_band': ' peak ',
        'participants': '8',
        'days': '3',
        'include_equipment': 'yes',
        'include_meals': 'true',
        'include_certification': '1',
        'markup_percent': '9.5',
        'promo_code': ' reef8 ',
    })

    assert request.destination == 'Goa'
    assert request.camp_tier == 'Adventure'
    assert request.season_band == 'PEAK'
    assert request.participants == 8
    assert request.days == 3
    assert request.include_equipment is True
    assert request.include_meals is True
    assert request.include_certification is True
    assert request.markup_percent == 9.5
    assert request.promo_code == 'REEF8'


def test_f2p_validates_happy_path():
    request = sanitize_snorkel_camp_request({
        'destination': 'Tarkarli',
        'camp_tier': 'Elite',
        'season_band': 'REGULAR',
        'participants': 10,
        'days': 2,
        'include_equipment': True,
        'include_meals': True,
        'include_certification': False,
        'markup_percent': 10,
    })

    result = validate_snorkel_camp_request(request)
    assert result.valid is True
    assert result.errors == []


def test_f2p_rejects_out_of_range_values():
    request = sanitize_snorkel_camp_request({
        'destination': '',
        'camp_tier': 'Invalid',
        'season_band': 'HOT',
        'participants': 0,
        'days': 0,
        'include_equipment': False,
        'include_meals': False,
        'include_certification': False,
        'markup_percent': 80,
    })

    result = validate_snorkel_camp_request(request)
    assert result.valid is False
    assert 'destination is required' in result.errors
    assert 'camp_tier must be Starter, Adventure, or Elite' in result.errors
    assert 'season_band must be LOW, REGULAR, or PEAK' in result.errors
    assert 'participants must be between 1 and 60' in result.errors
    assert 'days must be between 1 and 12' in result.errors
    assert 'markup_percent must be between 0 and 25' in result.errors
