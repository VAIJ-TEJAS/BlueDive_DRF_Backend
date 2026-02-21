"""P2P tests for water sport pass pipeline."""

from utils.water_sport_pass_service import WaterSportPassService
from utils.water_sport_pass_formatter import summarize_water_sport_pass


def test_p2p_preserves_singleton_behavior():
    a = WaterSportPassService.get_instance()
    b = WaterSportPassService.get_instance()
    assert a is b


def test_p2p_generates_unique_quote_ids():
    service = WaterSportPassService.get_instance()

    one = service.generate_quote({
        'destination': 'Goa',
        'pass_tier': 'Starter',
        'session_slot': 'Morning',
        'participants': 4,
        'days': 2,
        'include_equipment_insurance': False,
        'include_photo_package': False,
        'include_guide_support': False,
        'markup_percent': 0,
    })

    two = service.generate_quote({
        'destination': 'Goa',
        'pass_tier': 'Starter',
        'session_slot': 'Morning',
        'participants': 4,
        'days': 2,
        'include_equipment_insurance': False,
        'include_photo_package': False,
        'include_guide_support': False,
        'markup_percent': 0,
    })

    assert one['success'] is True
    assert two['success'] is True
    assert one['data'].quote_id != two['data'].quote_id


def test_p2p_keeps_response_contract_stable():
    service = WaterSportPassService.get_instance()

    result = service.generate_quote({
        'destination': 'Tarkarli',
        'pass_tier': 'Pro',
        'session_slot': 'Afternoon',
        'participants': 5,
        'days': 3,
        'include_equipment_insurance': True,
        'include_photo_package': True,
        'include_guide_support': True,
        'markup_percent': 12,
        'promo_code': 'SPLASH5',
    })

    assert isinstance(result, dict)
    assert 'success' in result
    assert 'message' in result

    if result['success']:
        assert hasattr(result['data'], 'request')
        assert hasattr(result['data'], 'breakdown')
        assert hasattr(result['data'].breakdown, 'total')

        summary = summarize_water_sport_pass(result['data'].breakdown)
        assert 'Total:' in summary
        assert len(summary) > 30
