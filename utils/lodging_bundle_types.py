"""Types for lodging bundle pricing."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Literal

BundleType = Literal['Business', 'Leisure', 'Honeymoon']
RoomType = Literal['Standard', 'Deluxe', 'Suite']


@dataclass
class LodgingBundleRequest:
    destination: str
    bundle_type: BundleType
    room_type: RoomType
    nights: int
    rooms: int
    guests: int
    include_breakfast: bool
    include_airport_pickup: bool
    include_sightseeing: bool
    season_code: str
    markup_percent: float = 0.0
    promo_code: Optional[str] = None


@dataclass
class LodgingBundleRules:
    base_room_per_night: Dict[RoomType, float]
    bundle_multiplier: Dict[BundleType, float]
    season_multiplier: Dict[str, float]
    breakfast_per_guest_per_day: float
    airport_pickup_flat: float
    sightseeing_per_guest: float
    service_fee_percent: float
    max_markup_percent: float
    promo_discount_percent: Dict[str, float]


@dataclass
class LodgingBundleBreakdown:
    base_room_cost: float
    bundle_adjustment: float
    season_adjustment: float
    breakfast_cost: float
    pickup_cost: float
    sightseeing_cost: float
    markup_amount: float
    subtotal: float
    discount: float
    service_fee: float
    total: float


@dataclass
class LodgingBundleResponse:
    quote_id: str
    generated_at: str
    currency: str
    request: LodgingBundleRequest
    breakdown: LodgingBundleBreakdown
    applied_promo: Optional[str] = None


@dataclass
class LodgingBundleValidationResult:
    valid: bool
    errors: List[str]
