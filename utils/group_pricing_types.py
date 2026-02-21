"""Types for group pricing calculations."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Literal

GroupCategory = Literal['Corporate', 'Student', 'Family']
TravelClass = Literal['Standard', 'Premium', 'Elite']


@dataclass
class GroupPricingRequest:
    destination: str
    group_category: GroupCategory
    travel_class: TravelClass
    travelers: int
    trip_days: int
    include_meals: bool
    include_transport: bool
    include_guide: bool
    season_code: str
    markup_percent: float = 0.0
    promo_code: Optional[str] = None


@dataclass
class GroupPricingRules:
    base_daily_per_person: Dict[TravelClass, float]
    category_multiplier: Dict[GroupCategory, float]
    season_multiplier: Dict[str, float]
    meals_per_person_per_day: float
    transport_per_day: float
    guide_per_day: float
    service_charge_percent: float
    max_markup_percent: float
    promo_discount_percent: Dict[str, float]


@dataclass
class GroupPricingBreakdown:
    base_cost: float
    category_adjustment: float
    season_adjustment: float
    meals_cost: float
    transport_cost: float
    guide_cost: float
    markup_amount: float
    subtotal: float
    discount: float
    service_charge: float
    total: float


@dataclass
class GroupPricingResponse:
    quote_id: str
    generated_at: str
    currency: str
    request: GroupPricingRequest
    breakdown: GroupPricingBreakdown
    applied_promo: Optional[str] = None


@dataclass
class GroupPricingValidationResult:
    valid: bool
    errors: List[str]
