"""
Data models for the petition search API.
These Pydantic models define the structure of our API requests and responses.

Pydantic gives us:
- Automatic validation
- Type hints
- API documentation
- JSON serialization

Author: Junior Developer
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class SearchFilters(BaseModel):
    """
    Filters that can be applied to search results.
    This allows users to narrow down their search.
    """
    state: Optional[str] = Field(
        None, 
        description="Filter by petition state: 'open' or 'closed'"
    )
    min_signatures: Optional[int] = Field(
        None, 
        ge=0,
        description="Minimum number of signatures required"
    )
    max_signatures: Optional[int] = Field(
        None,
        ge=0,
        description="Maximum number of signatures"
    )


class SearchRequest(BaseModel):
    """
    Request model for the search endpoint.
    This is what users send to search for petitions.
    """
    query: str = Field(
        ...,  # ... means this field is required
        min_length=1,
        max_length=500,
        description="Natural language search query",
        example="Find me all petitions about education"
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of results to return"
    )
    filters: Optional[SearchFilters] = Field(
        None,
        description="Optional filters to apply to results"
    )
    
    class Config:
        # This creates example data for our API docs
        schema_extra = {
            "example": {
                "query": "petitions about climate change",
                "limit": 10,
                "filters": {
                    "state": "open",
                    "min_signatures": 1000
                }
            }
        }


class PetitionResult(BaseModel):
    """
    Model for a single petition in search results.
    Contains all the information users need to see about a petition.
    """
    title: str = Field(
        ...,
        description="The petition title or text"
    )
    url: str = Field(
        ...,
        description="Link to the petition on parliament website"
    )
    state: str = Field(
        ...,
        description="Current state of the petition (open/closed)"
    )
    signatures: int = Field(
        ...,
        description="Number of signatures the petition has received"
    )
    similarity_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Similarity score between query and petition (0-1)"
    )
    rank: Optional[int] = Field(
        None,
        description="Position in search results"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "title": "Increase funding for renewable energy research",
                "url": "https://petition.parliament.uk/petitions/123456",
                "state": "open",
                "signatures": 15234,
                "similarity_score": 0.85,
                "rank": 1
            }
        }


class SearchResponse(BaseModel):
    """
    Response model for the search endpoint.
    This is what we send back to users after a search.
    """
    query: str = Field(
        ...,
        description="The original search query"
    )
    results: List[PetitionResult] = Field(
        ...,
        description="List of matching petitions"
    )
    count: int = Field(
        ...,
        description="Number of results returned"
    )
    search_type: str = Field(
        default="semantic",
        description="Type of search performed (semantic/keyword)"
    )
    timestamp: str = Field(
        ...,
        description="When the search was performed"
    )
    processing_time_ms: Optional[float] = Field(
        None,
        description="Time taken to process the search in milliseconds"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "query": "environmental protection",
                "results": [
                    {
                        "title": "Ban single-use plastics in all UK supermarkets",
                        "url": "https://petition.parliament.uk/petitions/234567",
                        "state": "open",
                        "signatures": 45678,
                        "similarity_score": 0.92,
                        "rank": 1
                    }
                ],
                "count": 1,
                "search_type": "semantic",
                "timestamp": "2025-01-15T10:30:00Z",
                "processing_time_ms": 125.5
            }
        }


class PetitionStats(BaseModel):
    """
    Statistics about the petition dataset.
    Helps users understand what data is available.
    """
    total_petitions: int = Field(
        ...,
        description="Total number of petitions in the system"
    )
    open_petitions: int = Field(
        ...,
        description="Number of currently open petitions"
    )
    closed_petitions: int = Field(
        ...,
        description="Number of closed petitions"
    )
    total_signatures: int = Field(
        ...,
        description="Total signatures across all petitions"
    )
    average_signatures: float = Field(
        ...,
        description="Average number of signatures per petition"
    )
    most_signed: Optional[PetitionResult] = Field(
        None,
        description="The petition with the most signatures"
    )
    recently_opened: Optional[List[PetitionResult]] = Field(
        None,
        description="Recently opened petitions"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "total_petitions": 1500,
                "open_petitions": 234,
                "closed_petitions": 1266,
                "total_signatures": 5678900,
                "average_signatures": 3785.9,
                "most_signed": {
                    "title": "Cancel Brexit",
                    "url": "https://petition.parliament.uk/petitions/241584",
                    "state": "closed",
                    "signatures": 6103056
                }
            }
        }


class HealthCheck(BaseModel):
    """
    Health check response model.
    Used for monitoring the API status.
    """
    status: str = Field(
        ...,
        description="Service health status"
    )
    timestamp: str = Field(
        ...,
        description="Current server time"
    )
    service: str = Field(
        ...,
        description="Service name"
    )
    version: str = Field(
        ...,
        description="API version"
    )
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional health details"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if unhealthy"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-01-15T10:30:00Z",
                "service": "petition-search-api",
                "version": "1.0.0",
                "details": {
                    "search_engine": "healthy",
                    "total_petitions": 1500,
                    "embeddings_loaded": True
                }
            }
        }


class ErrorResponse(BaseModel):
    """
    Standard error response format.
    Consistent error handling makes debugging easier.
    """
    error: str = Field(
        ...,
        description="Error type"
    )
    message: str = Field(
        ...,
        description="Human-readable error message"
    )
    detail: Optional[str] = Field(
        None,
        description="Additional error details"
    )
    timestamp: str = Field(
        ...,
        description="When the error occurred"
    )
    path: Optional[str] = Field(
        None,
        description="API path that caused the error"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Query cannot be empty",
                "detail": "The 'query' field is required and must contain at least 1 character",
                "timestamp": "2025-01-15T10:30:00Z",
                "path": "/api/search"
            }
        }
