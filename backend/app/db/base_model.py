from app.db.base import Base

# Import all models so they are registered with Base.metadata for Alembic discovery
from app.models import *

target_metadata = Base.metadata
