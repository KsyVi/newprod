from pydantic import BaseModel
from typing import List

class SearchResult(BaseModel):
    games: List[int] = []
    providers: List[int] = []

