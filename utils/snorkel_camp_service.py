"""Service layer for snorkel camp quote pipeline."""

from datetime import datetime
from typing import Any, Dict, Optional
from utils.snorkel_camp_types import SnorkelCampResponse, SnorkelCampRules, SnorkelCampValidationResult
from utils.snorkel_camp_validators import sanitize_snorkel_camp_request, validate_snorkel_camp_request
from utils.snorkel_camp_calculator import calculate_snorkel_camp_breakdown
from utils.snorkel_camp_rules import clone_snorkel_camp_rules, DEFAULT_SNORKEL_CAMP_RULES


class SnorkelCampService:
    _instance = None

    def __init__(self):
        self._sequence = 0

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = SnorkelCampService()
        return cls._instance

    def validate(self, payload: Dict[str, Any]) -> SnorkelCampValidationResult:
        request = sanitize_snorkel_camp_request(payload)
        return validate_snorkel_camp_request(request)

    def generate_quote(self, payload: Dict[str, Any], custom_rules: Optional[SnorkelCampRules] = None):
        request = sanitize_snorkel_camp_request(payload)
        validation = validate_snorkel_camp_request(request)

        if not validation.valid:
            return {'success': False, 'message': 'Validation failed', 'errors': validation.errors}

        breakdown, applied = calculate_snorkel_camp_breakdown(request, custom_rules)
        response = SnorkelCampResponse(
            quote_id=self._create_quote_id(),
            generated_at=datetime.utcnow().isoformat() + 'Z',
            currency='INR',
            request=request,
            breakdown=breakdown,
            applied_promo=applied,
        )

        return {'success': True, 'message': 'Snorkel camp quote generated', 'data': response}

    def get_default_rules(self) -> SnorkelCampRules:
        return clone_snorkel_camp_rules(DEFAULT_SNORKEL_CAMP_RULES)

    def _create_quote_id(self) -> str:
        self._sequence += 1
        suffix = str(self._sequence).zfill(4)
        stamp = str(int(datetime.utcnow().timestamp() * 1000))[-6:]
        return f'SCQ-{stamp}-{suffix}'
