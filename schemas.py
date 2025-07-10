from typing import List, Optional

from pydantic import BaseModel


class SearchResult(BaseModel):
    games: List[int] = []
    providers: List[int] = []
    cache: Optional[bool] = False

