"""F2P tests for lodging bundle service."""

from utils.lodging_bundle_service import LodgingBundleService


def test_f2p_fails_validation_for_incomplete_payload():
    service = LodgingBundleService.get_instance()
    result = service.generate_quote({'destination': 'Goa'})

    assert result['success'] is False
    assert result['message'] == 'Validation failed'
    assert isinstance(result['errors'], list)
    assert len(result['errors']) > 0


def test_f2p_generates_valid_quote_for_complete_payload():
    service = LodgingBundleService.get_instance()
    result = service.generate_quote({
        'destination': 'Goa',
        'bundle_type': 'Business',
        'room_type': 'Deluxe',
        'nights': 4,
        'rooms': 10,
        'guests': 25,
        'include_breakfast': True,
        'include_airport_pickup': True,
        'include_sightseeing': True,
        'season_code': 'PEAK',
        'markup_percent': 12,
        'promo_code': 'bundle6',
    })

    assert result['success'] is True
    assert result['data'].quote_id.startswith('LBQ-')
    assert result['data'].currency == 'INR'
    assert result['data'].applied_promo == 'BUNDLE6'
    assert result['data'].breakdown.total > 0


def test_f2p_returns_independent_rules_copy():
    service = LodgingBundleService.get_instance()
    a = service.get_default_rules()
    b = service.get_default_rules()

    a.promo_discount_percent['NEW'] = 0.4

    assert b.promo_discount_percent.get('NEW') is None
    assert b.base_room_per_night['Standard'] == 2600.0
