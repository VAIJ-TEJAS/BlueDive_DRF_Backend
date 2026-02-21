"""F2P tests for group pricing service."""

from utils.group_pricing_service import GroupPricingService


def test_f2p_fails_validation_for_incomplete_payload():
    service = GroupPricingService.get_instance()
    result = service.generate_quote({'destination': 'Goa'})

    assert result['success'] is False
    assert result['message'] == 'Validation failed'
    assert isinstance(result['errors'], list)
    assert len(result['errors']) > 0


def test_f2p_generates_valid_quote_for_complete_payload():
    service = GroupPricingService.get_instance()
    result = service.generate_quote({
        'destination': 'Goa',
        'group_category': 'Corporate',
        'travel_class': 'Premium',
        'travelers': 20,
        'trip_days': 4,
        'include_meals': True,
        'include_transport': True,
        'include_guide': True,
        'season_code': 'PEAK',
        'markup_percent': 12,
        'promo_code': 'corp9',
    })

    assert result['success'] is True
    assert result['data'].quote_id.startswith('GPQ-')
    assert result['data'].currency == 'INR'
    assert result['data'].applied_promo == 'CORP9'
    assert result['data'].breakdown.total > 0


def test_f2p_returns_independent_default_rules_copy():
    service = GroupPricingService.get_instance()
    rules_a = service.get_default_rules()
    rules_b = service.get_default_rules()

    rules_a.promo_discount_percent['NEW'] = 0.4

    assert rules_b.promo_discount_percent.get('NEW') is None
    assert rules_b.base_daily_per_person['Standard'] == 1800.0
