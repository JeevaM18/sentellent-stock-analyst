import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.tools.base import BaseAgentTool
from app.tools.registry import ToolRegistry


class SampleMockTool(BaseAgentTool):
    name = "mock_tool"
    description = "Mock testing tool"

    def run(self, query: str = "", **kwargs):
        return self.format_output(
            tool_name=self.name,
            status="success",
            execution_ms=5.0,
            formatted_context=f"Processed query: {query}",
            data={"echo": query},
        )


def test_tool_registry_registration_and_execution():
    registry = ToolRegistry()
    tool = SampleMockTool()

    registry.register(tool)
    assert "mock_tool" in registry.list_tools()
    assert registry.get("mock_tool") == tool

    res = registry.execute("mock_tool", query="Test Query")
    assert res["status"] == "success"
    assert res["tool"] == "mock_tool"
    assert res["data"]["echo"] == "Test Query"
    assert "Processed query: Test Query" in res["formatted_context"]


def test_tool_registry_unregistered_tool():
    registry = ToolRegistry()
    res = registry.execute("non_existent_tool")
    assert res["status"] == "error"
    assert "not registered" in res["formatted_context"]
