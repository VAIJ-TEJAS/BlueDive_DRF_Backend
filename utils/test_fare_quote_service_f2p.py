"""F2P tests for fare quote service."""

from utils.fare_quote_service import FareQuoteService


def test_f2p_fails_for_incomplete_payload():
    service = FareQuoteService.get_instance()
    result = service.generate_quote({'source_city': 'Mumbai'})

    assert result['success'] is False
    assert result['message'] == 'Validation failed'
    assert isinstance(result['errors'], list)
    assert len(result['errors']) > 0


def test_f2p_generates_valid_quote_with_normalized_coupon():
    service = FareQuoteService.get_instance()
    result = service.generate_quote({
        'source_city': 'Mumbai',
        'destination_city': 'Nashik',
        'trip_type': 'One-Way Trip',
        'pickup_time': '10:20',
        'distance_km': 170,
        'travellers': 4,
        'luggage_units': 3,
        'coupon_code': 'save15',
    })

    assert result['success'] is True
    assert result['data'] is not None
    assert result['data'].quote_id.startswith('BDQ-')
    assert result['data'].currency == 'INR'
    assert result['data'].applied_coupon == 'SAVE15'
    assert result['data'].breakdown.total > 0


def test_f2p_returns_cloned_default_rules():
    service = FareQuoteService.get_instance()
    rules_a = service.get_default_rules()
    rules_b = service.get_default_rules()

    rules_a.coupon_discounts['NEWCODE'] = 0.5

    assert rules_b.coupon_discounts.get('NEWCODE') is None
    assert rules_b.minimum_fare == 500.0
