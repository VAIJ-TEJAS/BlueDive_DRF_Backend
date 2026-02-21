"""Validation utilities for event pricing."""

import re
from typing import Any, Dict, Optional
from utils.event_pricing_types import EventPricingRequest, EventPricingValidationResult

_EVENT_TYPES = {'Conference', 'Retreat', 'Celebration'}
_TIERS = {'Basic', 'Pro', 'Premium'}
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


def sanitize_event_pricing_request(payload: Dict[str, Any]) -> EventPricingRequest:
    return EventPricingRequest(
        destination=_clean_text(payload.get('destination')),
        event_type=_clean_text(payload.get('event_type')),
        tier=_clean_text(payload.get('tier')),
        attendees=_clean_int(payload.get('attendees')),
        days=_clean_int(payload.get('days')),
        season=_clean_text(payload.get('season')).upper(),
        include_meals=_clean_bool(payload.get('include_meals')),
        include_stage_setup=_clean_bool(payload.get('include_stage_setup')),
        include_photography=_clean_bool(payload.get('include_photography')),
        markup_percent=_clean_float(payload.get('markup_percent')),
        promo_code=normalize_promo_code(payload.get('promo_code')),
    )


def validate_event_pricing_request(request: EventPricingRequest) -> EventPricingValidationResult:
    errors = []
    if not request.destination:
        errors.append('destination is required')
    if request.event_type not in _EVENT_TYPES:
        errors.append('event_type must be Conference, Retreat, or Celebration')
    if request.tier not in _TIERS:
        errors.append('tier must be Basic, Pro, or Premium')
    if request.season not in _SEASONS:
        errors.append('season must be PEAK, REGULAR, or LOW')
    if request.attendees < 5 or request.attendees > 500:
        errors.append('attendees must be between 5 and 500')
    if request.days < 1 or request.days > 10:
        errors.append('days must be between 1 and 10')
    if request.markup_percent < 0 or request.markup_percent > 28:
        errors.append('markup_percent must be between 0 and 28')

    return EventPricingValidationResult(valid=len(errors) == 0, errors=errors)
