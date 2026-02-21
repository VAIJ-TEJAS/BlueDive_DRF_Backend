"""Types for fare quote processing."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Literal

TripType = Literal['One-Way Trip', 'Round Trip', 'Hourly Rental']


@dataclass
class FareQuoteRequest:
    source_city: str
    destination_city: str
    trip_type: TripType
    pickup_time: str
    travellers: int
    luggage_units: int
    distance_km: Optional[float] = None
    rental_hours: Optional[float] = None
    coupon_code: Optional[str] = None


@dataclass
class FareQuoteRules:
    per_km_rate: float
    round_trip_multiplier: float
    hourly_rate: float
    minimum_fare: float
    luggage_surcharge_per_unit: float
    service_fee_percent: float
    night_surcharge_percent: float
    night_start_hour: int
    night_end_hour: int
    surge_multiplier: float
    coupon_discounts: Dict[str, float]


@dataclass
class FareQuoteBreakdown:
    travel_fare: float
    minimum_adjustment: float
    luggage_surcharge: float
    night_surcharge: float
    surge_surcharge: float
    subtotal: float
    discount: float
    service_fee: float
    total: float


@dataclass
class FareQuoteResponse:
    quote_id: str
    currency: str
    generated_at: str
    request: FareQuoteRequest
    breakdown: FareQuoteBreakdown
    applied_coupon: Optional[str] = None


@dataclass
class FareQuoteValidationResult:
    valid: bool
    errors: List[str]
