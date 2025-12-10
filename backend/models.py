from pydantic import BaseModel, Field
from typing import Optional, Any, List


class LeadRow(BaseModel):
    """Represents a single row/lead from the CSV."""
    name: Optional[str] = Field("", description="Lead name")
    email: Optional[str] = Field("", description="Email address")
    phone: Optional[str] = Field("", description="Phone number")
    property_type: Optional[str] = Field("", description="e.g., apartment, villa")
    budget: Optional[Any] = Field("", description="Budget (string or numeric)")
    location_preference: Optional[str] = Field("", description="Location preference")
    timeframe_to_move: Optional[str] = Field("", description="Desired timeframe")
    message: Optional[str] = Field("", description="Lead message")
    source: Optional[str] = Field("", description="Lead source, e.g., Facebook, Website")


class LeadOut(LeadRow):
    """Output model returned by the backend for each processed lead."""
    qualification_score: int
    tier: str
    recommended_action: str
    reasons: List[str]
    intent_label: str
    short_reason: str
