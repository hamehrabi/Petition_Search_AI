# models for the API - using pydantic because tutorial said it's good for APIs

from pydantic import BaseModel
from typing import List

# what the user sends when searching
class SearchRequest(BaseModel):
    query: str
    limit: int = 10

# single petition result
class PetitionResult(BaseModel):
    title: str
    url: str
    state: str
    signatures: int

# what we send back after search
class SearchResponse(BaseModel):
    query: str
    results: List[PetitionResult]
    count: int
