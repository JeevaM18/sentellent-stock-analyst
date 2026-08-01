import time
import logging
from typing import Any
from sqlalchemy.orm import Session

from app.investor_memory.builder import MemoryBuilder
from app.investor_memory.service import InvestorMemoryService
from app.tools.base import BaseAgentTool

logger = logging.getLogger(__name__)


class MemoryTool(BaseAgentTool):
    """
    Memory Tool supporting multi-action management (READ, WRITE, DELETE, REFRESH)
    over user investor profile memory.
    """

    name = "memory"
    description = "Manages user investor memory profile (read, write, delete, refresh from chat history)."

    def run(
        self,
        db: Session | None = None,
        user_id: Any = None,
        action: str = "READ",
        update_data: dict[str, Any] | None = None,
        chat_history: str = "",
        **kwargs: Any,
    ) -> dict[str, Any]:
        start_time = time.perf_counter()
        action_upper = action.upper().strip()

        if not db or not user_id:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return self.format_output(
                tool_name=self.name,
                status="empty",
                execution_ms=duration_ms,
                formatted_context="User investor memory is unavailable without an active authenticated user session.",
                data={"action": action_upper, "has_profile": False},
            )

        if action_upper == "DELETE":
            success = InvestorMemoryService.delete_memory(db, user_id)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return self.format_output(
                tool_name=self.name,
                status="success" if success else "not_found",
                execution_ms=duration_ms,
                formatted_context="Investor memory profile cleared successfully." if success else "No existing profile found to delete.",
                data={"action": "DELETE", "deleted": success},
            )

        elif action_upper == "WRITE":
            memory = InvestorMemoryService.update_memory(db, user_id, update_data or {})
            ctx = MemoryBuilder.build(memory)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return self.format_output(
                tool_name=self.name,
                status="success",
                execution_ms=duration_ms,
                formatted_context=ctx.prompt_context,
                data={"action": "WRITE", "confidence": memory.confidence_score},
            )

        elif action_upper == "REFRESH":
            memory = InvestorMemoryService.refresh_memory_from_history(db, user_id, chat_history)
            ctx = MemoryBuilder.build(memory)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return self.format_output(
                tool_name=self.name,
                status="success" if memory else "not_found",
                execution_ms=duration_ms,
                formatted_context=ctx.prompt_context if ctx.has_profile else "No investor preferences detected from chat history.",
                data={"action": "REFRESH", "has_profile": ctx.has_profile},
            )

        else:  # Default READ
            memory = InvestorMemoryService.get_memory(db, user_id)
            ctx = MemoryBuilder.build(memory)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return self.format_output(
                tool_name=self.name,
                status="success" if ctx.has_profile else "empty",
                execution_ms=duration_ms,
                formatted_context=ctx.prompt_context if ctx.has_profile else "No stored investor profile memory found.",
                data={"action": "READ", "has_profile": ctx.has_profile, "confidence": ctx.confidence},
            )
