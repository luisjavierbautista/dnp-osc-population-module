"""Pydantic schemas for API requests and responses."""
from .population import (
    PopulationAgeRequest,
    PopulationCompareRequest,
    PopulationAgeResponse,
    UrbanRuralResponse,
    GrowthResponse,
    PyramidResponse,
    CompareResponse,
    ErrorResponse,
)

__all__ = [
    "PopulationAgeRequest",
    "PopulationCompareRequest",
    "PopulationAgeResponse",
    "UrbanRuralResponse",
    "GrowthResponse",
    "PyramidResponse",
    "CompareResponse",
    "ErrorResponse",
]
