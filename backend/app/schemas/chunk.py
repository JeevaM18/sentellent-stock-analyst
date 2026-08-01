from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ChunkBase(BaseModel):
    chunk_index: int
    content: str
    chunk_hash: str
    token_count: int
    character_count: int
    start_char: int | None = None
    end_char: int | None = None
    status: str = "NEW"
    embedding_model: str | None = None


class ChunkResponse(ChunkBase):
    id: UUID
    document_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
