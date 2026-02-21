"""P2P tests for fare quote pipeline stability."""

from utils.fare_quote_service import FareQuoteService
from utils.fare_quote_formatter import summarize_fare_quote


def test_p2p_preserves_singleton_behavior():
    a = FareQuoteService.get_instance()
    b = FareQuoteService.get_instance()

    assert a is b


def test_p2p_emits_distinct_quote_ids_for_sequential_requests():
    service = FareQuoteService.get_instance()

    first = service.generate_quote({
        'source_city': 'Mumbai',
        'destination_city': 'Pune',
        'trip_type': 'One-Way Trip',
        'pickup_time': '09:00',
        'distance_km': 160,
        'travellers': 2,
        'luggage_units': 1,
    })

    second = service.generate_quote({
        'source_city': 'Mumbai',
        'destination_city': 'Pune',
        'trip_type': 'One-Way Trip',
        'pickup_time': '09:05',
        'distance_km': 161,
        'travellers': 2,
        'luggage_units': 1,
    })

    assert first['success'] is True
    assert second['success'] is True
    assert first['data'].quote_id != second['data'].quote_id


def test_p2p_keeps_response_shape_stable_for_valid_quote():
    service = FareQuoteService.get_instance()
    result = service.generate_quote({
        'source_city': 'Mumbai',
        'destination_city': 'Goa',
        'trip_type': 'Round Trip',
        'pickup_time': '07:20',
        'distance_km': 580,
        'travellers': 6,
        'luggage_units': 4,
    })

    assert isinstance(result, dict)
    assert 'success' in result
    assert 'message' in result

    if result['success']:
        assert hasattr(result['data'], 'request')
        assert hasattr(result['data'], 'breakdown')
        assert hasattr(result['data'].breakdown, 'total')

        summary = summarize_fare_quote(result['data'].breakdown)
        assert 'Total:' in summary
        assert len(summary) > 20
