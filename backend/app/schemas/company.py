from uuid import UUID
from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)


class PaginatedCompanyResponse(BaseModel):
    total: int
    page: int
    limit: int
    companies: list[CompanyResponse]
