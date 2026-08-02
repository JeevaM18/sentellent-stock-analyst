from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CompanyFundamentalsResponse(BaseModel):
    id: UUID
    company_id: UUID
    current_price: float | None = None
    market_cap: int | None = None
    shares_outstanding: int | None = None
    pe_ratio: float | None = None
    eps: float | None = None
    roe: float | None = None
    debt_to_equity: float | None = None
    dividend_yield: float | None = None
    book_value: float | None = None
    price_to_book: float | None = None
    beta: float | None = None
    fifty_two_week_high: float | None = None
    fifty_two_week_low: float | None = None
    currency: str = "INR"
    last_updated: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class CompanyBase(BaseModel):
    ticker: str
    company_name: str
    exchange: str
    nse_symbol: str | None = None
    bse_symbol: str | None = None
    isin: str | None = None
    sector: str | None = None
    industry: str | None = None
    is_active: bool = True


class CompanyResponse(CompanyBase):
    id: UUID
    fundamentals: CompanyFundamentalsResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedCompanyResponse(BaseModel):
    total: int
    page: int
    limit: int
    companies: list[CompanyResponse]
