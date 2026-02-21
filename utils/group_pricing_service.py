"""Service API for group pricing calculations."""

from datetime import datetime
from typing import Any, Dict, Optional
from utils.group_pricing_types import (
    GroupPricingResponse,
    GroupPricingRules,
    GroupPricingValidationResult,
)
from utils.group_pricing_validators import (
    sanitize_group_pricing_request,
    validate_group_pricing_request,
)
from utils.group_pricing_calculator import calculate_group_pricing_breakdown
from utils.group_pricing_rules import clone_group_pricing_rules, DEFAULT_GROUP_PRICING_RULES


class GroupPricingService:
    _instance = None

    def __init__(self):
        self._sequence = 0

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = GroupPricingService()
        return cls._instance

    def validate(self, payload: Dict[str, Any]) -> GroupPricingValidationResult:
        request = sanitize_group_pricing_request(payload)
        return validate_group_pricing_request(request)

    def generate_quote(self, payload: Dict[str, Any], custom_rules: Optional[GroupPricingRules] = None):
        request = sanitize_group_pricing_request(payload)
        validation = validate_group_pricing_request(request)

        if not validation.valid:
            return {
                'success': False,
                'message': 'Validation failed',
                'errors': validation.errors,
            }

        breakdown, applied_promo = calculate_group_pricing_breakdown(request, custom_rules)

        response = GroupPricingResponse(
            quote_id=self._create_quote_id(),
            generated_at=datetime.utcnow().isoformat() + 'Z',
            currency='INR',
            request=request,
            breakdown=breakdown,
            applied_promo=applied_promo,
        )

        return {
            'success': True,
            'message': 'Group pricing quote generated',
            'data': response,
        }

    def get_default_rules(self) -> GroupPricingRules:
        return clone_group_pricing_rules(DEFAULT_GROUP_PRICING_RULES)

    def _create_quote_id(self) -> str:
        self._sequence += 1
        suffix = str(self._sequence).zfill(4)
        stamp = str(int(datetime.utcnow().timestamp() * 1000))[-6:]
        return f'GPQ-{stamp}-{suffix}'
