import logging
from app.constants.chat import MAX_HISTORY_EXCHANGES, ROLE_ASSISTANT, ROLE_USER
from app.models.chat_message import ChatMessage

logger = logging.getLogger(__name__)


def build_chat_history(messages: list[ChatMessage], max_exchanges: int = MAX_HISTORY_EXCHANGES) -> str:
    """
    Format prior ChatMessages into structured dialogue exchanges for LLM prompt context.
    Groups messages into USER/ASSISTANT pairs and preserves up to max_exchanges (10 exchanges).
    """
    if not messages:
        return ""

    # Group into exchanges
    exchanges: list[tuple[str, str]] = []
    current_user_msg: str | None = None

    for msg in messages:
        if msg.role == ROLE_USER:
            current_user_msg = msg.content.strip()
        elif msg.role == ROLE_ASSISTANT and current_user_msg:
            exchanges.append((current_user_msg, msg.content.strip()))
            current_user_msg = None

    # Keep last max_exchanges
    selected_exchanges = exchanges[-max_exchanges:] if len(exchanges) > max_exchanges else exchanges

    formatted_lines: list[str] = []
    for user_text, assistant_text in selected_exchanges:
        formatted_lines.append(f"USER: {user_text}")
        formatted_lines.append(f"ASSISTANT: {assistant_text}")

    return "\n".join(formatted_lines)
