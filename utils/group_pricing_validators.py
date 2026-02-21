"""Validators and sanitizer for group pricing requests."""

import re
from typing import Any, Dict, Optional
from utils.group_pricing_types import GroupPricingRequest, GroupPricingValidationResult


_GROUP_CATEGORIES = {'Corporate', 'Student', 'Family'}
_TRAVEL_CLASSES = {'Standard', 'Premium', 'Elite'}
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
    normalized = value.strip().upper()
    return normalized if normalized else None


def sanitize_group_pricing_request(payload: Dict[str, Any]) -> GroupPricingRequest:
    return GroupPricingRequest(
        destination=_clean_text(payload.get('destination')),
        group_category=_clean_text(payload.get('group_category')),
        travel_class=_clean_text(payload.get('travel_class')),
        travelers=_clean_int(payload.get('travelers')),
        trip_days=_clean_int(payload.get('trip_days')),
        include_meals=_clean_bool(payload.get('include_meals')),
        include_transport=_clean_bool(payload.get('include_transport')),
        include_guide=_clean_bool(payload.get('include_guide')),
        season_code=_clean_text(payload.get('season_code')).upper(),
        markup_percent=_clean_float(payload.get('markup_percent')),
        promo_code=normalize_promo_code(payload.get('promo_code')),
    )


def validate_group_pricing_request(request: GroupPricingRequest) -> GroupPricingValidationResult:
    errors = []

    if not request.destination:
        errors.append('destination is required')

    if request.group_category not in _GROUP_CATEGORIES:
        errors.append('group_category must be Corporate, Student, or Family')

    if request.travel_class not in _TRAVEL_CLASSES:
        errors.append('travel_class must be Standard, Premium, or Elite')

    if request.season_code not in _SEASONS:
        errors.append('season_code must be PEAK, REGULAR, or LOW')

    if request.travelers < 2 or request.travelers > 80:
        errors.append('travelers must be between 2 and 80')

    if request.trip_days < 1 or request.trip_days > 20:
        errors.append('trip_days must be between 1 and 20')

    if request.markup_percent < 0 or request.markup_percent > 30:
        errors.append('markup_percent must be between 0 and 30')

    return GroupPricingValidationResult(valid=len(errors) == 0, errors=errors)
