"""Service layer for fare quote generation."""

from datetime import datetime
from typing import Any, Dict, Optional
from utils.fare_quote_types import FareQuoteValidationResult, FareQuoteResponse, FareQuoteRules
from utils.fare_quote_validators import sanitize_fare_quote_request, validate_fare_quote_request
from utils.fare_quote_calculator import compute_fare_quote_breakdown
from utils.fare_quote_rules import clone_fare_quote_rules, DEFAULT_FARE_QUOTE_RULES


class FareQuoteService:
    _instance = None

    def __init__(self):
        self._sequence = 0

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = FareQuoteService()
        return cls._instance

    def validate(self, payload: Dict[str, Any]) -> FareQuoteValidationResult:
        request = sanitize_fare_quote_request(payload)
        return validate_fare_quote_request(request)

    def generate_quote(self, payload: Dict[str, Any], custom_rules: Optional[FareQuoteRules] = None):
        request = sanitize_fare_quote_request(payload)
        validation = validate_fare_quote_request(request)

        if not validation.valid:
            return {
                'success': False,
                'message': 'Validation failed',
                'errors': validation.errors,
            }

        breakdown, applied_coupon = compute_fare_quote_breakdown(request, custom_rules)

        response = FareQuoteResponse(
            quote_id=self._create_quote_id(),
            currency='INR',
            generated_at=datetime.utcnow().isoformat() + 'Z',
            request=request,
            breakdown=breakdown,
            applied_coupon=applied_coupon,
        )

        return {
            'success': True,
            'message': 'Fare quote generated',
            'data': response,
        }

    def get_default_rules(self) -> FareQuoteRules:
        return clone_fare_quote_rules(DEFAULT_FARE_QUOTE_RULES)

    def _create_quote_id(self) -> str:
        self._sequence += 1
        suffix = str(self._sequence).zfill(4)
        stamp = str(int(datetime.utcnow().timestamp() * 1000))[-6:]
        return f'BDQ-{stamp}-{suffix}'
