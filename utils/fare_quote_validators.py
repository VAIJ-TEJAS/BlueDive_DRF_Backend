"""Validation and sanitization for fare quote requests."""

import re
from typing import Any, Dict, Optional
from utils.fare_quote_types import FareQuoteRequest, FareQuoteValidationResult


_TRIP_TYPES = {'One-Way Trip', 'Round Trip', 'Hourly Rental'}


def _clean_text(value: Any) -> str:
    if value is None:
        return ''
    return re.sub(r'\s+', ' ', str(value).strip())


def _clean_int(value: Any) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _clean_float(value: Any) -> Optional[float]:
    if value is None or value == '':
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_coupon(value: Any) -> Optional[str]:
    if not isinstance(value, str):
        return None
    cleaned = value.strip().upper()
    return cleaned if cleaned else None


def sanitize_fare_quote_request(payload: Dict[str, Any]) -> FareQuoteRequest:
    return FareQuoteRequest(
        source_city=_clean_text(payload.get('source_city')),
        destination_city=_clean_text(payload.get('destination_city')),
        trip_type=_clean_text(payload.get('trip_type')) or 'One-Way Trip',
        pickup_time=_clean_text(payload.get('pickup_time')),
        travellers=_clean_int(payload.get('travellers')),
        luggage_units=_clean_int(payload.get('luggage_units')),
        distance_km=_clean_float(payload.get('distance_km')),
        rental_hours=_clean_float(payload.get('rental_hours')),
        coupon_code=normalize_coupon(payload.get('coupon_code')),
    )


def validate_fare_quote_request(request: FareQuoteRequest) -> FareQuoteValidationResult:
    errors = []

    if not request.source_city:
        errors.append('source_city is required')

    if not request.destination_city:
        errors.append('destination_city is required')

    if request.trip_type == 'One-Way Trip' and request.source_city == request.destination_city:
        errors.append('source_city and destination_city must differ for one-way trip')

    if request.trip_type not in _TRIP_TYPES:
        errors.append('trip_type is invalid')

    if not re.match(r'^([01]\d|2[0-3]):[0-5]\d$', request.pickup_time):
        errors.append('pickup_time must be HH:MM in 24-hour format')

    if request.travellers < 1 or request.travellers > 12:
        errors.append('travellers must be an integer between 1 and 12')

    if request.luggage_units < 0 or request.luggage_units > 20:
        errors.append('luggage_units must be an integer between 0 and 20')

    if request.trip_type == 'Hourly Rental':
        if request.rental_hours is None or request.rental_hours <= 0:
            errors.append('rental_hours must be greater than 0 for hourly rental')
        elif request.rental_hours > 24:
            errors.append('rental_hours cannot exceed 24')
    else:
        if request.distance_km is None or request.distance_km <= 0:
            errors.append('distance_km must be greater than 0 for trip type')
        elif request.distance_km > 3000:
            errors.append('distance_km cannot exceed 3000')

    return FareQuoteValidationResult(valid=len(errors) == 0, errors=errors)
