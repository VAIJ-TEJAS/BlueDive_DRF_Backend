"""Types for snorkel camp quote pipeline."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Literal

CampTier = Literal['Starter', 'Adventure', 'Elite']
SeasonBand = Literal['LOW', 'REGULAR', 'PEAK']


@dataclass
class SnorkelCampRequest:
    destination: str
    camp_tier: CampTier
    season_band: SeasonBand
    participants: int
    days: int
    include_equipment: bool
    include_meals: bool
    include_certification: bool
    markup_percent: float = 0.0
    promo_code: Optional[str] = None


@dataclass
class SnorkelCampRules:
    base_per_participant_per_day: Dict[CampTier, float]
    season_multiplier: Dict[SeasonBand, float]
    equipment_per_participant_per_day: float
    meals_per_participant_per_day: float
    certification_per_participant: float
    service_fee_percent: float
    max_markup_percent: float
    promo_discount_percent: Dict[str, float]


@dataclass
class SnorkelCampBreakdown:
    base_camp_cost: float
    season_adjustment: float
    equipment_cost: float
    meals_cost: float
    certification_cost: float
    markup_amount: float
    subtotal: float
    discount: float
    service_fee: float
    total: float


@dataclass
class SnorkelCampResponse:
    quote_id: str
    generated_at: str
    currency: str
    request: SnorkelCampRequest
    breakdown: SnorkelCampBreakdown
    applied_promo: Optional[str] = None


@dataclass
class SnorkelCampValidationResult:
    valid: bool
    errors: List[str]
