"""Types for event pricing pipeline."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Literal

EventType = Literal['Conference', 'Retreat', 'Celebration']
TierType = Literal['Basic', 'Pro', 'Premium']


@dataclass
class EventPricingRequest:
    destination: str
    event_type: EventType
    tier: TierType
    attendees: int
    days: int
    season: str
    include_meals: bool
    include_stage_setup: bool
    include_photography: bool
    markup_percent: float = 0.0
    promo_code: Optional[str] = None


@dataclass
class EventPricingRules:
    base_per_person_per_day: Dict[TierType, float]
    event_multiplier: Dict[EventType, float]
    season_multiplier: Dict[str, float]
    meals_per_person_per_day: float
    stage_setup_per_day: float
    photography_per_day: float
    service_charge_percent: float
    max_markup_percent: float
    promo_discount_percent: Dict[str, float]


@dataclass
class EventPricingBreakdown:
    base_cost: float
    event_adjustment: float
    season_adjustment: float
    meals_cost: float
    stage_setup_cost: float
    photography_cost: float
    markup_amount: float
    subtotal: float
    discount: float
    service_charge: float
    total: float


@dataclass
class EventPricingResponse:
    quote_id: str
    generated_at: str
    currency: str
    request: EventPricingRequest
    breakdown: EventPricingBreakdown
    applied_promo: Optional[str] = None


@dataclass
class EventPricingValidationResult:
    valid: bool
    errors: List[str]
