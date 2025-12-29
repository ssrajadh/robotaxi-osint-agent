"""
Data models for the Robotaxi OSINT Agent.
"""
from datetime import datetime, UTC
from typing import Optional, List
from pydantic import BaseModel, Field, field_serializer, field_validator
import re


class ExtractedData(BaseModel):
    """Structured data extracted from a sighting."""
    license_plate: Optional[str] = None
    vehicle_type: Optional[str] = None
    vehicle_color: Optional[str] = None
    location: Optional[str] = None
    coordinates_approx: Optional[List[float]] = None
    
    @field_validator('vehicle_type', mode='before')
    @classmethod
    def normalize_vehicle_type(cls, v):
        """
        Normalize and validate vehicle type.
        Only accepts 'cybercab' or 'model y' (case-insensitive).
        Invalid values are set to None.
        """
        if v is None:
            return None
        v_lower = str(v).lower().strip()
        # Normalize to standard forms (case-insensitive matching)
        if v_lower in ['cybercab', 'cyber cab']:
            return 'cybercab'
        elif v_lower in ['model y', 'modely', 'model-y']:
            return 'model y'
        else:
            # Invalid vehicle type - set to None
            return None
    
    @field_validator('location', mode='before')
    @classmethod
    def validate_location_format(cls, v):
        """
        Validate location is in 'city, state' format.
        Requires at least one comma to separate city and state.
        Invalid formats are set to None.
        """
        if v is None:
            return None
        v_str = str(v).strip()
        # Pattern: requires comma to separate city and state
        # Allows flexible formats like "Palo Alto, CA" or "New York, NY, USA"
        pattern = r'^.+,\s*.+$'
        if re.match(pattern, v_str):
            return v_str
        else:
            # Invalid location format (missing comma) - set to None
            return None


class MediaData(BaseModel):
    """Media attachments from a post."""
    image_url: Optional[str] = None


class SightingCandidate(BaseModel):
    """A candidate robotaxi sighting."""
    source_id: str
    source_url: str
    timestamp_detected: datetime = Field(default_factory=lambda: datetime.now(UTC))
    confidence_score: float = 0.0
    extracted_data: ExtractedData = Field(default_factory=ExtractedData)
    media: MediaData = Field(default_factory=MediaData)
    status: str = "PENDING_REVIEW"
    raw_text: str = ""
    
    @field_serializer('timestamp_detected')
    def serialize_datetime(self, dt: datetime, _info) -> str:
        """Serialize datetime to ISO format with Z suffix."""
        return dt.isoformat() + "Z"
