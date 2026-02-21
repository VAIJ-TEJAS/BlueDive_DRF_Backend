"""F2P tests for event pricing service."""

from utils.event_pricing_service import EventPricingService


def test_f2p_fails_validation_for_incomplete_payload():
    service = EventPricingService.get_instance()
    result = service.generate_quote({'destination': 'Goa'})

    assert result['success'] is False
    assert result['message'] == 'Validation failed'
    assert isinstance(result['errors'], list)
    assert len(result['errors']) > 0


def test_f2p_generates_valid_quote_for_complete_payload():
    service = EventPricingService.get_instance()
    result = service.generate_quote({
        'destination': 'Goa',
        'event_type': 'Conference',
        'tier': 'Premium',
        'attendees': 120,
        'days': 3,
        'season': 'PEAK',
        'include_meals': True,
        'include_stage_setup': True,
        'include_photography': True,
        'markup_percent': 10,
        'promo_code': 'corp8',
    })

    assert result['success'] is True
    assert result['data'].quote_id.startswith('EPQ-')
    assert result['data'].currency == 'INR'
    assert result['data'].applied_promo == 'CORP8'
    assert result['data'].breakdown.total > 0


def test_f2p_returns_independent_default_rules_copy():
    service = EventPricingService.get_instance()
    a = service.get_default_rules()
    b = service.get_default_rules()

    a.promo_discount_percent['NEW'] = 0.4

    assert b.promo_discount_percent.get('NEW') is None
    assert b.base_per_person_per_day['Basic'] == 1500.0
