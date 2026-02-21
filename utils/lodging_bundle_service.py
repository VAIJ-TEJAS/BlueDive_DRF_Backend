"""Service layer for lodging bundle pricing."""

from datetime import datetime
from typing import Any, Dict, Optional
from utils.lodging_bundle_types import LodgingBundleResponse, LodgingBundleRules, LodgingBundleValidationResult
from utils.lodging_bundle_validators import sanitize_lodging_bundle_request, validate_lodging_bundle_request
from utils.lodging_bundle_calculator import calculate_lodging_bundle_breakdown
from utils.lodging_bundle_rules import clone_lodging_bundle_rules, DEFAULT_LODGING_BUNDLE_RULES


class LodgingBundleService:
    _instance = None

    def __init__(self):
        self._sequence = 0

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = LodgingBundleService()
        return cls._instance

    def validate(self, payload: Dict[str, Any]) -> LodgingBundleValidationResult:
        request = sanitize_lodging_bundle_request(payload)
        return validate_lodging_bundle_request(request)

    def generate_quote(self, payload: Dict[str, Any], custom_rules: Optional[LodgingBundleRules] = None):
        request = sanitize_lodging_bundle_request(payload)
        validation = validate_lodging_bundle_request(request)

        if not validation.valid:
            return {'success': False, 'message': 'Validation failed', 'errors': validation.errors}

        breakdown, applied = calculate_lodging_bundle_breakdown(request, custom_rules)
        response = LodgingBundleResponse(
            quote_id=self._create_quote_id(),
            generated_at=datetime.utcnow().isoformat() + 'Z',
            currency='INR',
            request=request,
            breakdown=breakdown,
            applied_promo=applied,
        )

        return {'success': True, 'message': 'Lodging bundle quote generated', 'data': response}

    def get_default_rules(self) -> LodgingBundleRules:
        return clone_lodging_bundle_rules(DEFAULT_LODGING_BUNDLE_RULES)

    def _create_quote_id(self) -> str:
        self._sequence += 1
        suffix = str(self._sequence).zfill(4)
        stamp = str(int(datetime.utcnow().timestamp() * 1000))[-6:]
        return f'LBQ-{stamp}-{suffix}'
