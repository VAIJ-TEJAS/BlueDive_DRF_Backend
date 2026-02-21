"""P2P tests for event pricing pipeline."""

from utils.event_pricing_service import EventPricingService
from utils.event_pricing_formatter import summarize_event_pricing


def test_p2p_preserves_singleton_behavior():
    a = EventPricingService.get_instance()
    b = EventPricingService.get_instance()
    assert a is b


def test_p2p_returns_unique_ids_for_sequential_quotes():
    service = EventPricingService.get_instance()

    one = service.generate_quote({
        'destination': 'Goa',
        'event_type': 'Conference',
        'tier': 'Basic',
        'attendees': 30,
        'days': 2,
        'season': 'REGULAR',
        'include_meals': False,
        'include_stage_setup': False,
        'include_photography': False,
        'markup_percent': 0,
    })

    two = service.generate_quote({
        'destination': 'Goa',
        'event_type': 'Conference',
        'tier': 'Basic',
        'attendees': 30,
        'days': 2,
        'season': 'REGULAR',
        'include_meals': False,
        'include_stage_setup': False,
        'include_photography': False,
        'markup_percent': 0,
    })

    assert one['success'] is True
    assert two['success'] is True
    assert one['data'].quote_id != two['data'].quote_id


def test_p2p_keeps_response_contract_stable():
    service = EventPricingService.get_instance()
    result = service.generate_quote({
        'destination': 'Konkan',
        'event_type': 'Retreat',
        'tier': 'Pro',
        'attendees': 70,
        'days': 4,
        'season': 'LOW',
        'include_meals': True,
        'include_stage_setup': True,
        'include_photography': True,
        'markup_percent': 6,
    })

    assert isinstance(result, dict)
    assert 'success' in result
    assert 'message' in result

    if result['success']:
        assert hasattr(result['data'], 'request')
        assert hasattr(result['data'], 'breakdown')
        assert hasattr(result['data'].breakdown, 'total')
        summary = summarize_event_pricing(result['data'].breakdown)
        assert 'Total:' in summary
        assert len(summary) > 30
