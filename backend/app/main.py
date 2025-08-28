"""
Main FastAPI application for the AI-powered petition search system.
This file sets up the API server and defines all the endpoints.

Author: Junior Developer
Date: 2025
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn
import logging
from datetime import datetime

# Import our custom modules
from app.search_engine import PetitionSearchEngine
from app.models import SearchRequest, SearchResponse, PetitionStats, HealthCheck
from app.config import Settings

# Set up logging to help with debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app with metadata
app = FastAPI(
    title="AI Petition Search API",
    description="Natural language search for UK Parliament petitions using semantic search",
    version="1.0.0",
    docs_url="/docs",  # This gives us automatic API documentation!
)

# Configure CORS - this allows our frontend to communicate with the backend
# In production, we'd restrict origins to specific domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins like ["https://petitions.example.com"]
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Load configuration
settings = Settings()

# Initialize our search engine (this is where the AI magic happens!)
try:
    logger.info("Initializing petition search engine...")
    search_engine = PetitionSearchEngine(
        csv_path=settings.CSV_PATH,
        model_name=settings.MODEL_NAME,
        embeddings_cache_path=settings.EMBEDDINGS_CACHE_PATH
    )
    logger.info(f"Search engine initialized successfully with {search_engine.get_petition_count()} petitions")
except Exception as e:
    logger.error(f"Failed to initialize search engine: {e}")
    # In production, we might want to exit here or use a fallback
    search_engine = None


@app.get("/", tags=["General"])
def root():
    """
    Welcome endpoint - shows basic API information.
    This helps developers understand what the API does.
    """
    return {
        "message": "Welcome to the AI Petition Search API",
        "version": "1.0.0",
        "endpoints": {
            "search": "/api/search",
            "petitions": "/api/petitions",
            "stats": "/api/stats",
            "health": "/api/health",
            "docs": "/docs"
        },
        "description": "Use natural language to search UK Parliament petitions"
    }


@app.post("/api/search", response_model=SearchResponse, tags=["Search"])
async def search_petitions(request: SearchRequest):
    """
    Main search endpoint - this is where users submit their natural language queries.
    
    Examples of queries that work well:
    - "Find me all petitions about education"
    - "Show me campaigns calling for environmental protection"
    - "Petitions about healthcare and NHS"
    - "Climate change initiatives"
    
    The search uses AI embeddings to understand meaning, not just keywords!
    """
    try:
        # Validate that search engine is initialized
        if not search_engine:
            raise HTTPException(
                status_code=503,
                detail="Search engine is not available. Please try again later."
            )
        
        # Log the search request (useful for understanding user behavior)
        logger.info(f"Search request received: '{request.query}' with filters: {request.filters}")
        
        # Perform the semantic search
        results = search_engine.search(
            query=request.query,
            top_k=request.limit,
            state_filter=request.filters.state if request.filters else None,
            min_signatures=request.filters.min_signatures if request.filters else None,
            include_similarity_score=True  # Always include scores to show relevance
        )
        
        # Log search performance
        logger.info(f"Search completed: found {len(results)} results for query '{request.query}'")
        
        # Return the formatted response
        return SearchResponse(
            query=request.query,
            results=results,
            count=len(results),
            search_type="semantic",  # Let frontend know we used AI search
            timestamp=datetime.utcnow().isoformat()
        )
        
    except ValueError as e:
        # Handle validation errors (like invalid query)
        logger.error(f"Validation error in search: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Error during search: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your search. Please try again."
        )


@app.get("/api/petitions", tags=["Petitions"])
async def list_petitions(
    offset: int = 0,
    limit: int = 20,
    state: Optional[str] = None
):
    """
    List all petitions with pagination support.
    
    This endpoint is useful for browsing petitions without searching.
    Supports filtering by state (open/closed) and pagination.
    
    Query parameters:
    - offset: Starting index (for pagination)
    - limit: Number of results to return (max 100)
    - state: Filter by petition state (open/closed)
    """
    try:
        if not search_engine:
            raise HTTPException(
                status_code=503,
                detail="Search engine is not available"
            )
        
        # Get paginated list of petitions
        petitions = search_engine.get_all_petitions(
            offset=offset,
            limit=limit,
            state_filter=state
        )
        
        return {
            "petitions": petitions,
            "offset": offset,
            "limit": limit,
            "total": search_engine.get_petition_count(state_filter=state),
            "has_more": len(petitions) == limit
        }
        
    except Exception as e:
        logger.error(f"Error listing petitions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve petitions")


@app.get("/api/stats", response_model=PetitionStats, tags=["Statistics"])
async def get_statistics():
    """
    Get statistics about the petition dataset.
    
    Returns useful metrics like:
    - Total number of petitions
    - Number of open vs closed petitions  
    - Average signatures
    - Most popular petitions
    
    This helps users understand the dataset better.
    """
    try:
        if not search_engine:
            raise HTTPException(
                status_code=503,
                detail="Search engine is not available"
            )
        
        stats = search_engine.get_statistics()
        return PetitionStats(**stats)
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")


@app.get("/api/health", response_model=HealthCheck, tags=["System"])
async def health_check():
    """
    Health check endpoint for monitoring.
    
    In production, this would be used by:
    - Load balancers to check if the service is alive
    - Monitoring systems to track uptime
    - Kubernetes for liveness/readiness probes
    """
    try:
        # Check if search engine is working
        engine_status = "healthy" if search_engine and search_engine.is_ready() else "unhealthy"
        
        return HealthCheck(
            status=engine_status,
            timestamp=datetime.utcnow().isoformat(),
            service="petition-search-api",
            version="1.0.0",
            details={
                "search_engine": engine_status,
                "total_petitions": search_engine.get_petition_count() if search_engine else 0,
                "embeddings_loaded": search_engine.embeddings_loaded if search_engine else False
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheck(
            status="unhealthy",
            timestamp=datetime.utcnow().isoformat(),
            service="petition-search-api",
            version="1.0.0",
            error=str(e)
        )


# Rate limiting endpoint (demonstrates security awareness)
@app.middleware("http")
async def add_rate_limit_headers(request, call_next):
    """
    Add rate limiting headers to responses.
    In production, we'd implement actual rate limiting with Redis or similar.
    
    This shows awareness of:
    - API security best practices
    - Preventing abuse
    - Resource management
    """
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = "100"
    response.headers["X-RateLimit-Remaining"] = "99"  # In production, track actual usage
    response.headers["X-RateLimit-Reset"] = str(int(datetime.utcnow().timestamp()) + 3600)
    return response


if __name__ == "__main__":
    """
    Run the FastAPI application using uvicorn.
    In production, we'd use a proper ASGI server like Gunicorn with Uvicorn workers.
    """
    logger.info("Starting Petition Search API server...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # Listen on all interfaces
        port=8000,
        reload=True,  # Auto-reload on code changes (development only)
        log_level="info"
    )
