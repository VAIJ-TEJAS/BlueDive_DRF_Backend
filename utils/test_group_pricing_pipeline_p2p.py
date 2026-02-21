"""P2P tests for group pricing pipeline."""

from utils.group_pricing_service import GroupPricingService
from utils.group_pricing_formatter import summarize_group_pricing


def test_p2p_preserves_singleton_instance_behavior():
    a = GroupPricingService.get_instance()
    b = GroupPricingService.get_instance()
    assert a is b


def test_p2p_returns_unique_quote_ids_for_sequential_calls():
    service = GroupPricingService.get_instance()

    one = service.generate_quote({
        'destination': 'Goa',
        'group_category': 'Family',
        'travel_class': 'Standard',
        'travelers': 10,
        'trip_days': 3,
        'include_meals': False,
        'include_transport': False,
        'include_guide': False,
        'season_code': 'REGULAR',
        'markup_percent': 0,
    })

    two = service.generate_quote({
        'destination': 'Goa',
        'group_category': 'Family',
        'travel_class': 'Standard',
        'travelers': 10,
        'trip_days': 3,
        'include_meals': False,
        'include_transport': False,
        'include_guide': False,
        'season_code': 'REGULAR',
        'markup_percent': 0,
    })

    assert one['success'] is True
    assert two['success'] is True
    assert one['data'].quote_id != two['data'].quote_id


def test_p2p_keeps_response_contract_stable():
    service = GroupPricingService.get_instance()

    result = service.generate_quote({
        'destination': 'Konkan',
        'group_category': 'Student',
        'travel_class': 'Premium',
        'travelers': 25,
        'trip_days': 4,
        'include_meals': True,
        'include_transport': True,
        'include_guide': True,
        'season_code': 'LOW',
        'markup_percent': 5,
    })

    assert isinstance(result, dict)
    assert 'success' in result
    assert 'message' in result

    if result['success']:
        assert hasattr(result['data'], 'request')
        assert hasattr(result['data'], 'breakdown')
        assert hasattr(result['data'].breakdown, 'total')
        summary = summarize_group_pricing(result['data'].breakdown)
        assert 'Total:' in summary
        assert len(summary) > 30
