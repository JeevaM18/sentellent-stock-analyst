import logging
from typing import Any
from app.tools.base import BaseAgentTool

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Central registry for managing, dependency-injecting, and executing agentic tools.
    """

    def __init__(self) -> None:
        self._tools: dict[str, BaseAgentTool] = {}

    def register(self, tool: BaseAgentTool) -> None:
        """Register a tool instance."""
        self._tools[tool.name] = tool
        logger.info("ToolRegistry registered tool: %s", tool.name)

    def get(self, name: str) -> BaseAgentTool | None:
        """Retrieve registered tool by name."""
        return self._tools.get(name)

    def execute(self, name: str, **kwargs: Any) -> dict[str, Any]:
        """Execute a registered tool by name with provided arguments."""
        tool = self.get(name)
        if not tool:
            logger.warning("ToolRegistry tool '%s' not registered", name)
            return BaseAgentTool.format_output(
                tool_name=name,
                status="error",
                execution_ms=0.0,
                formatted_context=f"Tool '{name}' is not registered in ToolRegistry.",
                data={"error": f"Unregistered tool '{name}'"},
            )
        return tool.run(**kwargs)

    def list_tools(self) -> list[str]:
        """Return list of registered tool names."""
        return list(self._tools.keys())
