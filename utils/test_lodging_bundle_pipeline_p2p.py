"""P2P tests for lodging bundle pipeline."""

from utils.lodging_bundle_service import LodgingBundleService
from utils.lodging_bundle_formatter import summarize_lodging_bundle


def test_p2p_preserves_singleton_behavior():
    a = LodgingBundleService.get_instance()
    b = LodgingBundleService.get_instance()
    assert a is b


def test_p2p_generates_unique_quote_ids():
    service = LodgingBundleService.get_instance()

    one = service.generate_quote({
        'destination': 'Goa',
        'bundle_type': 'Leisure',
        'room_type': 'Standard',
        'nights': 2,
        'rooms': 2,
        'guests': 4,
        'include_breakfast': False,
        'include_airport_pickup': False,
        'include_sightseeing': False,
        'season_code': 'REGULAR',
        'markup_percent': 0,
    })

    two = service.generate_quote({
        'destination': 'Goa',
        'bundle_type': 'Leisure',
        'room_type': 'Standard',
        'nights': 2,
        'rooms': 2,
        'guests': 4,
        'include_breakfast': False,
        'include_airport_pickup': False,
        'include_sightseeing': False,
        'season_code': 'REGULAR',
        'markup_percent': 0,
    })

    assert one['success'] is True
    assert two['success'] is True
    assert one['data'].quote_id != two['data'].quote_id


def test_p2p_keeps_response_contract_stable():
    service = LodgingBundleService.get_instance()

    result = service.generate_quote({
        'destination': 'Konkan',
        'bundle_type': 'Honeymoon',
        'room_type': 'Suite',
        'nights': 3,
        'rooms': 2,
        'guests': 4,
        'include_breakfast': True,
        'include_airport_pickup': True,
        'include_sightseeing': True,
        'season_code': 'PEAK',
        'markup_percent': 10,
    })

    assert isinstance(result, dict)
    assert 'success' in result
    assert 'message' in result

    if result['success']:
        assert hasattr(result['data'], 'request')
        assert hasattr(result['data'], 'breakdown')
        assert hasattr(result['data'].breakdown, 'total')
        summary = summarize_lodging_bundle(result['data'].breakdown)
        assert 'Total:' in summary
        assert len(summary) > 30
