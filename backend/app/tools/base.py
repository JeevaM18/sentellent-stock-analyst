from abc import ABC, abstractmethod
from typing import Any


class BaseAgentTool(ABC):
    """Abstract base class for financial agent tools."""

    name: str
    description: str

    @abstractmethod
    def run(self, **kwargs: Any) -> dict[str, Any]:
        """Execute the tool action and return structured result payload."""
        pass
