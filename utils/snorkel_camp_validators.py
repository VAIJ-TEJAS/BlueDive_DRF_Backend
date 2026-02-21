"""Validation and sanitization for snorkel camp requests."""

import re
from typing import Any, Dict, Optional
from utils.snorkel_camp_types import SnorkelCampRequest, SnorkelCampValidationResult


_TIERS = {'Starter', 'Adventure', 'Elite'}
_SEASONS = {'LOW', 'REGULAR', 'PEAK'}


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


def sanitize_snorkel_camp_request(payload: Dict[str, Any]) -> SnorkelCampRequest:
    return SnorkelCampRequest(
        destination=_clean_text(payload.get('destination')),
        camp_tier=_clean_text(payload.get('camp_tier')),
        season_band=_clean_text(payload.get('season_band')).upper(),
        participants=_clean_int(payload.get('participants')),
        days=_clean_int(payload.get('days')),
        include_equipment=_clean_bool(payload.get('include_equipment')),
        include_meals=_clean_bool(payload.get('include_meals')),
        include_certification=_clean_bool(payload.get('include_certification')),
        markup_percent=_clean_float(payload.get('markup_percent')),
        promo_code=normalize_promo_code(payload.get('promo_code')),
    )


def validate_snorkel_camp_request(request: SnorkelCampRequest) -> SnorkelCampValidationResult:
    errors = []

    if not request.destination:
        errors.append('destination is required')
    if request.camp_tier not in _TIERS:
        errors.append('camp_tier must be Starter, Adventure, or Elite')
    if request.season_band not in _SEASONS:
        errors.append('season_band must be LOW, REGULAR, or PEAK')
    if request.participants < 1 or request.participants > 60:
        errors.append('participants must be between 1 and 60')
    if request.days < 1 or request.days > 12:
        errors.append('days must be between 1 and 12')
    if request.markup_percent < 0 or request.markup_percent > 25:
        errors.append('markup_percent must be between 0 and 25')

    return SnorkelCampValidationResult(valid=len(errors) == 0, errors=errors)
