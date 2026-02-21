"""Validation and sanitization for itinerary quote requests."""

import re
from typing import Any, Dict, Optional
from utils.itinerary_quote_types import ItineraryQuoteRequest, ItineraryValidationResult


_ITINERARY_TYPES = {'Weekend Getaway', 'Adventure Trip', 'Family Vacation'}
_VALID_MONTHS = {'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'}


def _clean_text(value: Any) -> str:
    if value is None:
        return ''
    return re.sub(r'\s+', ' ', str(value).strip())


def _clean_int(value: Any, fallback: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return fallback


def _clean_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        return lowered in {'true', '1', 'yes'}
    return False


def normalize_promo_code(value: Any) -> Optional[str]:
    if not isinstance(value, str):
        return None
    normalized = value.strip().upper()
    return normalized if normalized else None


def sanitize_itinerary_quote_request(payload: Dict[str, Any]) -> ItineraryQuoteRequest:
    return ItineraryQuoteRequest(
        destination=_clean_text(payload.get('destination')),
        itinerary_type=_clean_text(payload.get('itinerary_type')) or 'Weekend Getaway',
        travel_month=_clean_text(payload.get('travel_month')).upper(),
        days=_clean_int(payload.get('days')),
        adults=_clean_int(payload.get('adults')),
        children=_clean_int(payload.get('children')),
        hotel_stars=_clean_int(payload.get('hotel_stars')),
        include_breakfast=_clean_bool(payload.get('include_breakfast')),
        include_transfers=_clean_bool(payload.get('include_transfers')),
        promo_code=normalize_promo_code(payload.get('promo_code')),
    )


def validate_itinerary_quote_request(request: ItineraryQuoteRequest) -> ItineraryValidationResult:
    errors = []

    if not request.destination:
        errors.append('destination is required')

    if request.itinerary_type not in _ITINERARY_TYPES:
        errors.append('itinerary_type must be Weekend Getaway, Adventure Trip, or Family Vacation')

    if request.travel_month not in _VALID_MONTHS:
        errors.append('travel_month must be a valid 3-letter month code')

    if request.days < 1 or request.days > 15:
        errors.append('days must be an integer between 1 and 15')

    if request.adults < 1 or request.adults > 8:
        errors.append('adults must be an integer between 1 and 8')

    if request.children < 0 or request.children > 6:
        errors.append('children must be an integer between 0 and 6')

    if request.hotel_stars not in {3, 4, 5}:
        errors.append('hotel_stars must be one of: 3, 4, 5')

    if request.adults + request.children > 10:
        errors.append('total travelers cannot exceed 10')

    return ItineraryValidationResult(valid=len(errors) == 0, errors=errors)
