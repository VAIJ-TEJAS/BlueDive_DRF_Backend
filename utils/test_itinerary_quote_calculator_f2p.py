"""F2P tests for itinerary quote calculator."""

from utils.itinerary_quote_calculator import calculate_itinerary_quote_breakdown
from utils.itinerary_quote_types import ItineraryQuoteRequest


def test_f2p_computes_weekend_quote_with_breakfast_and_transfer():
    request = ItineraryQuoteRequest(
        destination='Goa',
        itinerary_type='Weekend Getaway',
        travel_month='APR',
        days=3,
        adults=2,
        children=1,
        hotel_stars=3,
        include_breakfast=True,
        include_transfers=True,
    )

    breakdown, _ = calculate_itinerary_quote_breakdown(request)

    assert breakdown.base_package == 21420.0
    assert breakdown.itinerary_adjustment == 1713.6
    assert breakdown.breakfast_cost == 1980.0
    assert breakdown.transfer_cost == 1800.0
    assert breakdown.total == 27855.58


def test_f2p_applies_seasonal_adjustment_and_promo_discount():
    request = ItineraryQuoteRequest(
        destination='Goa',
        itinerary_type='Family Vacation',
        travel_month='DEC',
        days=4,
        adults=2,
        children=2,
        hotel_stars=4,
        include_breakfast=True,
        include_transfers=True,
        promo_code='BLUEDIVE10',
    )

    breakdown, applied_promo = calculate_itinerary_quote_breakdown(request)

    assert breakdown.seasonal_adjustment > 0
    assert applied_promo == 'BLUEDIVE10'
    assert breakdown.discount > 0
    assert breakdown.total == 49379.93


def test_f2p_computes_adventure_quote_without_extras():
    request = ItineraryQuoteRequest(
        destination='Ladakh',
        itinerary_type='Adventure Trip',
        travel_month='JUN',
        days=5,
        adults=3,
        children=0,
        hotel_stars=5,
        include_breakfast=False,
        include_transfers=False,
    )

    breakdown, _ = calculate_itinerary_quote_breakdown(request)

    assert breakdown.hotel_surcharge == 7000.0
    assert breakdown.breakfast_cost == 0.0
    assert breakdown.transfer_cost == 0.0
    assert breakdown.total == 53856.43


def test_f2p_ignores_unknown_promo_codes():
    request = ItineraryQuoteRequest(
        destination='Goa',
        itinerary_type='Weekend Getaway',
        travel_month='APR',
        days=2,
        adults=2,
        children=0,
        hotel_stars=3,
        include_breakfast=False,
        include_transfers=False,
        promo_code='UNKNOWN',
    )

    breakdown, applied_promo = calculate_itinerary_quote_breakdown(request)

    assert applied_promo is None
    assert breakdown.discount == 0.0
