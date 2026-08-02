import os
from dotenv import load_dotenv

load_dotenv()

"""Constants for LangGraph agent orchestration."""

DEFAULT_AGENT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
MAX_AGENT_ITERATIONS = 5
DEFAULT_AGENT_VERSION = "v1"
