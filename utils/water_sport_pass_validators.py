"""Validation and sanitization for water sport pass requests."""

import re
from typing import Any, Dict, Optional
from utils.water_sport_pass_types import WaterSportPassRequest, WaterSportPassValidationResult


_PASS_TIERS = {'Starter', 'Explorer', 'Pro'}
_SESSION_SLOTS = {'Morning', 'Afternoon', 'Sunset'}


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


def sanitize_water_sport_pass_request(payload: Dict[str, Any]) -> WaterSportPassRequest:
    return WaterSportPassRequest(
        destination=_clean_text(payload.get('destination')),
        pass_tier=_clean_text(payload.get('pass_tier')),
        session_slot=_clean_text(payload.get('session_slot')),
        participants=_clean_int(payload.get('participants')),
        days=_clean_int(payload.get('days')),
        include_equipment_insurance=_clean_bool(payload.get('include_equipment_insurance')),
        include_photo_package=_clean_bool(payload.get('include_photo_package')),
        include_guide_support=_clean_bool(payload.get('include_guide_support')),
        markup_percent=_clean_float(payload.get('markup_percent')),
        promo_code=normalize_promo_code(payload.get('promo_code')),
    )


def validate_water_sport_pass_request(request: WaterSportPassRequest) -> WaterSportPassValidationResult:
    errors = []

    if not request.destination:
        errors.append('destination is required')
    if request.pass_tier not in _PASS_TIERS:
        errors.append('pass_tier must be Starter, Explorer, or Pro')
    if request.session_slot not in _SESSION_SLOTS:
        errors.append('session_slot must be Morning, Afternoon, or Sunset')
    if request.participants < 1 or request.participants > 80:
        errors.append('participants must be between 1 and 80')
    if request.days < 1 or request.days > 10:
        errors.append('days must be between 1 and 10')
    if request.markup_percent < 0 or request.markup_percent > 24:
        errors.append('markup_percent must be between 0 and 24')

    return WaterSportPassValidationResult(valid=len(errors) == 0, errors=errors)
