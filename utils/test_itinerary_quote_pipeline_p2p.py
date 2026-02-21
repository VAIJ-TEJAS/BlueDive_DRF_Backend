"""P2P tests for itinerary quote pipeline."""

from utils.itinerary_quote_service import ItineraryQuoteService
from utils.itinerary_quote_formatter import summarize_itinerary_quote


def test_p2p_preserves_singleton_instance_behavior():
    a = ItineraryQuoteService.get_instance()
    b = ItineraryQuoteService.get_instance()
    assert a is b


def test_p2p_returns_unique_quote_ids_for_sequential_calls():
    service = ItineraryQuoteService.get_instance()

    one = service.generate_quote({
        'destination': 'Goa',
        'itinerary_type': 'Weekend Getaway',
        'travel_month': 'APR',
        'days': 2,
        'adults': 2,
        'children': 0,
        'hotel_stars': 3,
        'include_breakfast': False,
        'include_transfers': False,
    })

    two = service.generate_quote({
        'destination': 'Goa',
        'itinerary_type': 'Weekend Getaway',
        'travel_month': 'APR',
        'days': 2,
        'adults': 2,
        'children': 0,
        'hotel_stars': 3,
        'include_breakfast': False,
        'include_transfers': False,
    })

    assert one['success'] is True
    assert two['success'] is True
    assert one['data'].quote_id != two['data'].quote_id


def test_p2p_keeps_response_contract_stable():
    service = ItineraryQuoteService.get_instance()

    result = service.generate_quote({
        'destination': 'Ladakh',
        'itinerary_type': 'Adventure Trip',
        'travel_month': 'OCT',
        'days': 5,
        'adults': 3,
        'children': 0,
        'hotel_stars': 4,
        'include_breakfast': True,
        'include_transfers': True,
    })

    assert isinstance(result, dict)
    assert 'success' in result
    assert 'message' in result

    if result['success']:
        assert hasattr(result['data'], 'request')
        assert hasattr(result['data'], 'breakdown')
        assert hasattr(result['data'].breakdown, 'total')
        summary = summarize_itinerary_quote(result['data'].breakdown)
        assert 'Total:' in summary
        assert len(summary) > 30
