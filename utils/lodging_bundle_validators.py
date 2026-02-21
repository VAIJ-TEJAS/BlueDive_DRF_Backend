"""Validation and sanitization for lodging bundle requests."""

import re
from typing import Any, Dict, Optional
from utils.lodging_bundle_types import LodgingBundleRequest, LodgingBundleValidationResult


_BUNDLE_TYPES = {'Business', 'Leisure', 'Honeymoon'}
_ROOM_TYPES = {'Standard', 'Deluxe', 'Suite'}
_SEASONS = {'PEAK', 'REGULAR', 'LOW'}


def _clean_text(value: Any) -> str:
    if value is None:
        return ''
    return re.sub(r'\s+', ' ', str(value).strip())


def _clean_int(value: Any, fallback: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return fallback


def _clean_float(value: Any, fallback: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _clean_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {'true', '1', 'yes'}
    return False


def normalize_promo_code(value: Any) -> Optional[str]:
    if not isinstance(value, str):
        return None
    cleaned = value.strip().upper()
    return cleaned if cleaned else None


def sanitize_lodging_bundle_request(payload: Dict[str, Any]) -> LodgingBundleRequest:
    return LodgingBundleRequest(
        destination=_clean_text(payload.get('destination')),
        bundle_type=_clean_text(payload.get('bundle_type')),
        room_type=_clean_text(payload.get('room_type')),
        nights=_clean_int(payload.get('nights')),
        rooms=_clean_int(payload.get('rooms')),
        guests=_clean_int(payload.get('guests')),
        include_breakfast=_clean_bool(payload.get('include_breakfast')),
        include_airport_pickup=_clean_bool(payload.get('include_airport_pickup')),
        include_sightseeing=_clean_bool(payload.get('include_sightseeing')),
        season_code=_clean_text(payload.get('season_code')).upper(),
        markup_percent=_clean_float(payload.get('markup_percent')),
        promo_code=normalize_promo_code(payload.get('promo_code')),
    )


def validate_lodging_bundle_request(request: LodgingBundleRequest) -> LodgingBundleValidationResult:
    errors = []
    if not request.destination:
        errors.append('destination is required')
    if request.bundle_type not in _BUNDLE_TYPES:
        errors.append('bundle_type must be Business, Leisure, or Honeymoon')
    if request.room_type not in _ROOM_TYPES:
        errors.append('room_type must be Standard, Deluxe, or Suite')
    if request.season_code not in _SEASONS:
        errors.append('season_code must be PEAK, REGULAR, or LOW')
    if request.nights < 1 or request.nights > 15:
        errors.append('nights must be between 1 and 15')
    if request.rooms < 1 or request.rooms > 40:
        errors.append('rooms must be between 1 and 40')
    if request.guests < 1 or request.guests > 120:
        errors.append('guests must be between 1 and 120')
    if request.markup_percent < 0 or request.markup_percent > 26:
        errors.append('markup_percent must be between 0 and 26')
    return LodgingBundleValidationResult(valid=len(errors) == 0, errors=errors)
