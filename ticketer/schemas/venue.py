"""Venue schemas."""

from pydantic import BaseModel


class VenueCreate(BaseModel):
    """Schema for creating a venue."""

    name: str
    address: str


class VenueResponse(BaseModel):
    """Schema for venue response."""

    id: int
    name: str
    address: str

    model_config = {"from_attributes": True}

