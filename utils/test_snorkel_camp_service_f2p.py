"""F2P tests for snorkel camp service."""

from utils.snorkel_camp_service import SnorkelCampService


def test_f2p_generate_quote_rejects_invalid_payload():
    service = SnorkelCampService.get_instance()

    result = service.generate_quote({
        'destination': '',
        'camp_tier': 'Starter',
        'season_band': 'LOW',
        'participants': 0,
        'days': 0,
        'include_equipment': False,
        'include_meals': False,
        'include_certification': False,
        'markup_percent': 0,
    })

    assert result['success'] is False
    assert result['message'] == 'Validation failed'
    assert len(result['errors']) > 0


def test_f2p_generate_quote_returns_contract_for_valid_payload():
    service = SnorkelCampService.get_instance()

    result = service.generate_quote({
        'destination': 'Goa',
        'camp_tier': 'Adventure',
        'season_band': 'PEAK',
        'participants': 7,
        'days': 2,
        'include_equipment': True,
        'include_meals': True,
        'include_certification': True,
        'markup_percent': 12,
        'promo_code': 'REEF8',
    })

    assert result['success'] is True
    assert result['data'].currency == 'INR'
    assert result['data'].quote_id.startswith('SCQ-')
    assert result['data'].breakdown.total > 0
    assert result['data'].applied_promo == 'REEF8'


def test_f2p_get_default_rules_returns_clone_instances():
    service = SnorkelCampService.get_instance()
    a = service.get_default_rules()
    b = service.get_default_rules()

    assert a is not b
    assert a.base_per_participant_per_day is not b.base_per_participant_per_day
    assert a.max_markup_percent == 25.0
