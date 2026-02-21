"""Service layer for event pricing."""

from datetime import datetime
from typing import Any, Dict, Optional
from utils.event_pricing_types import EventPricingResponse, EventPricingRules, EventPricingValidationResult
from utils.event_pricing_validators import sanitize_event_pricing_request, validate_event_pricing_request
from utils.event_pricing_calculator import calculate_event_pricing_breakdown
from utils.event_pricing_rules import clone_event_pricing_rules, DEFAULT_EVENT_PRICING_RULES


class EventPricingService:
    _instance = None

    def __init__(self):
        self._sequence = 0

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = EventPricingService()
        return cls._instance

    def validate(self, payload: Dict[str, Any]) -> EventPricingValidationResult:
        request = sanitize_event_pricing_request(payload)
        return validate_event_pricing_request(request)

    def generate_quote(self, payload: Dict[str, Any], custom_rules: Optional[EventPricingRules] = None):
        request = sanitize_event_pricing_request(payload)
        validation = validate_event_pricing_request(request)

        if not validation.valid:
            return {'success': False, 'message': 'Validation failed', 'errors': validation.errors}

        breakdown, applied_promo = calculate_event_pricing_breakdown(request, custom_rules)
        response = EventPricingResponse(
            quote_id=self._create_quote_id(),
            generated_at=datetime.utcnow().isoformat() + 'Z',
            currency='INR',
            request=request,
            breakdown=breakdown,
            applied_promo=applied_promo,
        )

        return {'success': True, 'message': 'Event pricing quote generated', 'data': response}

    def get_default_rules(self) -> EventPricingRules:
        return clone_event_pricing_rules(DEFAULT_EVENT_PRICING_RULES)

    def _create_quote_id(self) -> str:
        self._sequence += 1
        suffix = str(self._sequence).zfill(4)
        stamp = str(int(datetime.utcnow().timestamp() * 1000))[-6:]
        return f'EPQ-{stamp}-{suffix}'
