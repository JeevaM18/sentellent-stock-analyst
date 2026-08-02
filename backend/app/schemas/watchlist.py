from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.schemas.company import CompanyResponse


class FollowCompanyRequest(BaseModel):
    company_id: UUID


class WatchlistItemResponse(BaseModel):
    company_id: UUID
    ticker: str
    company_name: str
    exchange: str
    sector: str | None = None
    followed_at: datetime
    following: bool = True
    company: CompanyResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class WatchlistResponse(BaseModel):
    items: list[WatchlistItemResponse]


class WatchlistCountResponse(BaseModel):
    count: int


class FollowCompanyResponse(BaseModel):
    message: str
    watchlist_item: WatchlistItemResponse


class UnfollowCompanyResponse(BaseModel):
    message: str


class WatchlistCheckResponse(BaseModel):
    following: bool
