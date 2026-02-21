"""F2P tests for water sport pass service."""

from utils.water_sport_pass_service import WaterSportPassService


def test_f2p_generate_quote_rejects_invalid_payload():
    service = WaterSportPassService.get_instance()

    result = service.generate_quote({
        'destination': '',
        'pass_tier': 'Pro',
        'session_slot': 'Morning',
        'participants': 0,
        'days': 0,
        'include_equipment_insurance': False,
        'include_photo_package': False,
        'include_guide_support': False,
        'markup_percent': 0,
    })

    assert result['success'] is False
    assert result['message'] == 'Validation failed'
    assert len(result['errors']) > 0


def test_f2p_generate_quote_returns_response_contract():
    service = WaterSportPassService.get_instance()

    result = service.generate_quote({
        'destination': 'Goa',
        'pass_tier': 'Explorer',
        'session_slot': 'Sunset',
        'participants': 7,
        'days': 2,
        'include_equipment_insurance': True,
        'include_photo_package': True,
        'include_guide_support': True,
        'markup_percent': 11,
        'promo_code': 'WAVE7',
    })

    assert result['success'] is True
    assert result['data'].currency == 'INR'
    assert result['data'].quote_id.startswith('WSP-')
    assert result['data'].breakdown.total > 0
    assert result['data'].applied_promo == 'WAVE7'


def test_f2p_get_default_rules_returns_clone_instances():
    service = WaterSportPassService.get_instance()
    rules_a = service.get_default_rules()
    rules_b = service.get_default_rules()

    assert rules_a is not rules_b
    assert rules_a.base_per_participant_per_day is not rules_b.base_per_participant_per_day
    assert rules_a.max_markup_percent == 24.0
