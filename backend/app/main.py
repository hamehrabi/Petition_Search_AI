# this is the main file where I set up the API using FastAPI

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.search_engine import PetitionSearchEngine
from app.models import SearchRequest, SearchResponse
from app import config

# create the API app
app = FastAPI(title="Petition Search")

# add CORS so browser can connect - copied this from stackoverflow
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# load the search engine thing
search_engine = PetitionSearchEngine(
    config.CSV_FILE,
    config.MODEL_NAME,
    config.CACHE_FILE
)


# basic endpoints
@app.get("/")
def home():
    return {"message": "Petition search API is working"}

# the main search endpoint
@app.post("/api/search")
async def search(request: SearchRequest):
    results = search_engine.search(request.query, request.limit)
    return SearchResponse(
        query=request.query,
        results=results,
        count=len(results)
    )

# health check endpoint
@app.get("/api/health")
def health():
    return {"status": "healthy"}

# stats endpoint
@app.get("/api/stats")
def stats():
    return {
        "total_petitions": len(search_engine.petitions),
        "open_petitions": len([p for p in search_engine.petitions if p['state'] == 'open']),
        "closed_petitions": len([p for p in search_engine.petitions if p['state'] == 'closed']),
        "rejected_petitions": len([p for p in search_engine.petitions if p['state'] == 'rejected']),
        "total_signatures": sum(p['signatures'] for p in search_engine.petitions),
        "average_signatures": sum(p['signatures'] for p in search_engine.petitions) / len(search_engine.petitions)
    }

# search analytics endpoint
@app.post("/api/search/analytics")
async def search_analytics(request: SearchRequest):
    analytics = search_engine.get_search_analytics(request.query)
    return analytics

# run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)
