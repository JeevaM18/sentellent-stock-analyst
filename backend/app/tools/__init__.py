"""Tools package for LangGraph financial agent execution."""

from app.tools.base import BaseAgentTool
from app.tools.fundamentals import FundamentalsTool
from app.tools.memory_tool import MemoryTool
from app.tools.registry import ToolRegistry
from app.tools.retrieval_tool import RetrievalTool
from app.tools.watchlist import WatchlistIntelligenceTool

def create_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(FundamentalsTool())
    registry.register(WatchlistIntelligenceTool())
    registry.register(RetrievalTool())
    registry.register(MemoryTool())
    return registry

default_tool_registry = create_default_registry()

__all__ = [
    "BaseAgentTool",
    "FundamentalsTool",
    "WatchlistIntelligenceTool",
    "RetrievalTool",
    "MemoryTool",
    "ToolRegistry",
    "default_tool_registry",
]
