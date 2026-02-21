"""Types for itinerary quote processing."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Literal

ItineraryType = Literal['Weekend Getaway', 'Adventure Trip', 'Family Vacation']


@dataclass
class ItineraryQuoteRequest:
    destination: str
    itinerary_type: ItineraryType
    travel_month: str
    days: int
    adults: int
    children: int
    hotel_stars: int
    include_breakfast: bool
    include_transfers: bool
    promo_code: Optional[str] = None


@dataclass
class ItineraryQuoteRules:
    base_per_day_adult: float
    child_multiplier: float
    weekend_multiplier: float
    adventure_multiplier: float
    family_multiplier: float
    star_surcharge_by_hotel: Dict[int, float]
    breakfast_per_person_per_day: float
    transfers_flat_fee: float
    seasonal_multiplier_by_month: Dict[str, float]
    service_fee_percent: float
    promo_discount_by_code: Dict[str, float]


@dataclass
class ItineraryQuoteBreakdown:
    base_package: float
    itinerary_adjustment: float
    hotel_surcharge: float
    breakfast_cost: float
    transfer_cost: float
    seasonal_adjustment: float
    subtotal: float
    discount: float
    service_fee: float
    total: float


@dataclass
class ItineraryQuoteResponse:
    quote_id: str
    generated_at: str
    currency: str
    request: ItineraryQuoteRequest
    breakdown: ItineraryQuoteBreakdown
    applied_promo: Optional[str] = None


@dataclass
class ItineraryValidationResult:
    valid: bool
    errors: List[str]
