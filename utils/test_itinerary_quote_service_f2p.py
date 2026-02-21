"""F2P tests for itinerary quote service."""

from utils.itinerary_quote_service import ItineraryQuoteService


def test_f2p_fails_validation_for_incomplete_payload():
    service = ItineraryQuoteService.get_instance()
    result = service.generate_quote({'destination': 'Goa'})

    assert result['success'] is False
    assert result['message'] == 'Validation failed'
    assert isinstance(result['errors'], list)
    assert len(result['errors']) > 0


def test_f2p_generates_valid_quote_with_promo_normalization():
    service = ItineraryQuoteService.get_instance()
    result = service.generate_quote({
        'destination': 'Goa',
        'itinerary_type': 'Family Vacation',
        'travel_month': 'DEC',
        'days': 4,
        'adults': 2,
        'children': 2,
        'hotel_stars': 4,
        'include_breakfast': True,
        'include_transfers': True,
        'promo_code': 'bluedive10',
    })

    assert result['success'] is True
    assert result['data'].quote_id.startswith('ITQ-')
    assert result['data'].currency == 'INR'
    assert result['data'].applied_promo == 'BLUEDIVE10'
    assert result['data'].breakdown.total > 0


def test_f2p_returns_isolated_default_rules_copy():
    service = ItineraryQuoteService.get_instance()
    rules_a = service.get_default_rules()
    rules_b = service.get_default_rules()

    rules_a.promo_discount_by_code['NEW'] = 0.9

    assert rules_b.promo_discount_by_code.get('NEW') is None
    assert rules_b.base_per_day_adult == 2800.0
