"""Service layer for water sport pass pricing."""

from datetime import datetime
from typing import Any, Dict, Optional
from utils.water_sport_pass_types import (
    WaterSportPassResponse,
    WaterSportPassRules,
    WaterSportPassValidationResult,
)
from utils.water_sport_pass_validators import (
    sanitize_water_sport_pass_request,
    validate_water_sport_pass_request,
)
from utils.water_sport_pass_calculator import calculate_water_sport_pass_breakdown
from utils.water_sport_pass_rules import (
    clone_water_sport_pass_rules,
    DEFAULT_WATER_SPORT_PASS_RULES,
)


class WaterSportPassService:
    _instance = None

    def __init__(self):
        self._sequence = 0

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = WaterSportPassService()
        return cls._instance

    def validate(self, payload: Dict[str, Any]) -> WaterSportPassValidationResult:
        request = sanitize_water_sport_pass_request(payload)
        return validate_water_sport_pass_request(request)

    def generate_quote(self, payload: Dict[str, Any], custom_rules: Optional[WaterSportPassRules] = None):
        request = sanitize_water_sport_pass_request(payload)
        validation = validate_water_sport_pass_request(request)

        if not validation.valid:
            return {'success': False, 'message': 'Validation failed', 'errors': validation.errors}

        breakdown, applied = calculate_water_sport_pass_breakdown(request, custom_rules)

        response = WaterSportPassResponse(
            quote_id=self._create_quote_id(),
            generated_at=datetime.utcnow().isoformat() + 'Z',
            currency='INR',
            request=request,
            breakdown=breakdown,
            applied_promo=applied,
        )

        return {'success': True, 'message': 'Water sport pass quote generated', 'data': response}

    def get_default_rules(self) -> WaterSportPassRules:
        return clone_water_sport_pass_rules(DEFAULT_WATER_SPORT_PASS_RULES)

    def _create_quote_id(self) -> str:
        self._sequence += 1
        suffix = str(self._sequence).zfill(4)
        stamp = str(int(datetime.utcnow().timestamp() * 1000))[-6:]
        return f'WSP-{stamp}-{suffix}'
