from typing import List

from pydantic import BaseModel


class SearchResult(BaseModel):
    games: List[int] = []
    providers: List[int] = []

