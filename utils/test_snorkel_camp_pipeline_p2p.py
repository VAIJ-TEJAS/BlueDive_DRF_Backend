"""P2P tests for snorkel camp pipeline."""

from utils.snorkel_camp_service import SnorkelCampService
from utils.snorkel_camp_formatter import summarize_snorkel_camp


def test_p2p_preserves_singleton_behavior():
    a = SnorkelCampService.get_instance()
    b = SnorkelCampService.get_instance()
    assert a is b


def test_p2p_generates_unique_quote_ids():
    service = SnorkelCampService.get_instance()

    one = service.generate_quote({
        'destination': 'Goa',
        'camp_tier': 'Starter',
        'season_band': 'REGULAR',
        'participants': 4,
        'days': 2,
        'include_equipment': False,
        'include_meals': False,
        'include_certification': False,
        'markup_percent': 0,
    })

    two = service.generate_quote({
        'destination': 'Goa',
        'camp_tier': 'Starter',
        'season_band': 'REGULAR',
        'participants': 4,
        'days': 2,
        'include_equipment': False,
        'include_meals': False,
        'include_certification': False,
        'markup_percent': 0,
    })

    assert one['success'] is True
    assert two['success'] is True
    assert one['data'].quote_id != two['data'].quote_id


def test_p2p_keeps_response_contract_stable():
    service = SnorkelCampService.get_instance()

    result = service.generate_quote({
        'destination': 'Tarkarli',
        'camp_tier': 'Elite',
        'season_band': 'LOW',
        'participants': 5,
        'days': 3,
        'include_equipment': True,
        'include_meals': True,
        'include_certification': True,
        'markup_percent': 11,
        'promo_code': 'CAMP5',
    })

    assert isinstance(result, dict)
    assert 'success' in result
    assert 'message' in result

    if result['success']:
        assert hasattr(result['data'], 'request')
        assert hasattr(result['data'], 'breakdown')
        assert hasattr(result['data'].breakdown, 'total')

        summary = summarize_snorkel_camp(result['data'].breakdown)
        assert 'Total:' in summary
        assert len(summary) > 30
