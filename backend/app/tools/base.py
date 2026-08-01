from abc import ABC, abstractmethod
from typing import Any


class BaseAgentTool(ABC):
    """Abstract base class for all agentic financial tools."""

    name: str = "base_tool"
    description: str = "Base tool interface"

    @abstractmethod
    def run(self, **kwargs: Any) -> dict[str, Any]:
        """Execute tool operation and return standardized output payload."""
        pass

    @classmethod
    def format_output(
        cls,
        tool_name: str,
        status: str,
        execution_ms: float,
        formatted_context: str,
        data: dict[str, Any] | None = None,
        citations: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Standardized output structure for all tools in the system."""
        return {
            "status": status,
            "tool": tool_name,
            "execution_ms": execution_ms,
            "formatted_context": formatted_context,
            "data": data or {},
            "citations": citations or [],
        }
