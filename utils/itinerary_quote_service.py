"""Service layer for itinerary quote generation."""

from datetime import datetime
from typing import Dict, Any, Optional
from utils.itinerary_quote_types import (
    ItineraryValidationResult,
    ItineraryQuoteResponse,
    ItineraryQuoteRules,
)
from utils.itinerary_quote_validators import (
    sanitize_itinerary_quote_request,
    validate_itinerary_quote_request,
)
from utils.itinerary_quote_calculator import calculate_itinerary_quote_breakdown
from utils.itinerary_quote_rules import clone_itinerary_quote_rules, DEFAULT_ITINERARY_QUOTE_RULES


class ItineraryQuoteService:
    _instance = None

    def __init__(self):
        self._sequence = 0

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ItineraryQuoteService()
        return cls._instance

    def validate(self, payload: Dict[str, Any]) -> ItineraryValidationResult:
        request = sanitize_itinerary_quote_request(payload)
        return validate_itinerary_quote_request(request)

    def generate_quote(self, payload: Dict[str, Any], custom_rules: Optional[ItineraryQuoteRules] = None):
        request = sanitize_itinerary_quote_request(payload)
        validation = validate_itinerary_quote_request(request)

        if not validation.valid:
            return {
                'success': False,
                'message': 'Validation failed',
                'errors': validation.errors,
            }

        breakdown, applied_promo = calculate_itinerary_quote_breakdown(request, custom_rules)

        response = ItineraryQuoteResponse(
            quote_id=self._create_quote_id(),
            generated_at=datetime.utcnow().isoformat() + 'Z',
            currency='INR',
            request=request,
            breakdown=breakdown,
            applied_promo=applied_promo,
        )

        return {
            'success': True,
            'message': 'Itinerary quote generated',
            'data': response,
        }

    def get_default_rules(self) -> ItineraryQuoteRules:
        return clone_itinerary_quote_rules(DEFAULT_ITINERARY_QUOTE_RULES)

    def _create_quote_id(self) -> str:
        self._sequence += 1
        suffix = str(self._sequence).zfill(4)
        stamp = str(int(datetime.utcnow().timestamp() * 1000))[-6:]
        return f'ITQ-{stamp}-{suffix}'
