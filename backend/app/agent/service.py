import logging
import time
from typing import Any
from uuid import UUID
from sqlalchemy.orm import Session

from app.agent.constants import DEFAULT_AGENT_MODEL
from app.agent.graph import AgentGraph
from app.agent.state import AgentState
from app.chat.history import build_chat_history
from app.constants.chat import ROLE_ASSISTANT, ROLE_USER
from app.llm.service import GenerationService
from app.retrieval.service import RetrieverService
from app.services.conversation_service import ConversationService

logger = logging.getLogger(__name__)


class AgentService:
    """Service orchestrating conversation history persistence and LangGraph agent workflow execution."""

    @classmethod
    def run(
        cls,
        *,
        db: Session,
        question: str,
        user_id: UUID | None = None,
        conversation_id: UUID | None = None,
        retriever_service: RetrieverService | None = None,
        generation_service: GenerationService | None = None,
    ) -> dict[str, Any]:
        """
        Execute end-to-end agentic workflow over LangGraph graph and return state execution payload.
        """
        start_total = time.perf_counter()

        # Step 1: Manage Conversation Session
        if conversation_id:
            conversation = ConversationService.get_conversation(db, conversation_id, user_id=user_id)
            if not conversation:
                conversation = ConversationService.create_conversation(db, user_id=user_id)
        else:
            conversation = ConversationService.create_conversation(db, user_id=user_id)

        conv_id = conversation.id

        # Step 2: Fetch history context before appending current query
        prior_messages = ConversationService.get_messages(db, conv_id)
        chat_history_str = build_chat_history(prior_messages)

        # Step 3: Save USER message to database
        ConversationService.append_message(
            db,
            conversation_id=conv_id,
            role=ROLE_USER,
            content=question,
        )

        # Step 4: Prepare initial AgentState with services mapping for reliable node access
        retriever = retriever_service or RetrieverService()
        gen_service = generation_service or GenerationService()

        initial_state: AgentState = {
            "user_id": user_id,
            "conversation_id": conv_id,
            "question": question,
            "chat_history": chat_history_str,
            "retrieved_context": "",
            "tool_results": {},
            "final_answer": "",
            "citations": [],
            "metadata": {
                "agent_version": AgentGraph.version,
                "model": DEFAULT_AGENT_MODEL,
                "tools_used": [],
            },
            "iteration": 0,
            "services": {
                "db": db,
                "retriever": retriever,
                "generation_service": gen_service,
            },
        }

        # Step 5: Invoke LangGraph Graph
        config = {
            "configurable": {
                "db": db,
                "retriever": retriever,
                "generation_service": gen_service,
            }
        }

        final_state = AgentGraph.graph.invoke(initial_state, config=config)

        total_time_ms = round((time.perf_counter() - start_total) * 1000, 2)
        metadata = dict(final_state.get("metadata", {}))
        metadata["execution_time_ms"] = total_time_ms
        final_state["metadata"] = metadata

        # Step 6: Save ASSISTANT message to database
        ConversationService.append_message(
            db,
            conversation_id=conv_id,
            role=ROLE_ASSISTANT,
            content=final_state.get("final_answer", ""),
        )

        # Step 7: Update default conversation title
        ConversationService.update_conversation_title_if_default(db, conversation, question)

        logger.info(
            "Agent execution for conversation %s completed in %.2f ms (tools: %s)",
            conv_id,
            total_time_ms,
            metadata.get("tools_used"),
        )

        return final_state
