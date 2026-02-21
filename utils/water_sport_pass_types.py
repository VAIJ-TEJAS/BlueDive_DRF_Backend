"""Types for water sport pass pricing."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Literal

PassTier = Literal['Starter', 'Explorer', 'Pro']
SessionSlot = Literal['Morning', 'Afternoon', 'Sunset']


@dataclass
class WaterSportPassRequest:
    destination: str
    pass_tier: PassTier
    session_slot: SessionSlot
    participants: int
    days: int
    include_equipment_insurance: bool
    include_photo_package: bool
    include_guide_support: bool
    markup_percent: float = 0.0
    promo_code: Optional[str] = None


@dataclass
class WaterSportPassRules:
    base_per_participant_per_day: Dict[PassTier, float]
    slot_multiplier: Dict[SessionSlot, float]
    equipment_insurance_per_participant_per_day: float
    photo_package_per_participant: float
    guide_support_per_day: float
    service_fee_percent: float
    max_markup_percent: float
    promo_discount_percent: Dict[str, float]


@dataclass
class WaterSportPassBreakdown:
    base_pass_cost: float
    slot_adjustment: float
    equipment_insurance_cost: float
    photo_package_cost: float
    guide_support_cost: float
    markup_amount: float
    subtotal: float
    discount: float
    service_fee: float
    total: float


@dataclass
class WaterSportPassResponse:
    quote_id: str
    generated_at: str
    currency: str
    request: WaterSportPassRequest
    breakdown: WaterSportPassBreakdown
    applied_promo: Optional[str] = None


@dataclass
class WaterSportPassValidationResult:
    valid: bool
    errors: List[str]
