import os
from dotenv import load_dotenv

load_dotenv()

"""Constants for LLM response generation and Gemini provider settings."""

AVAILABLE_MODELS = [
    os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
    "gemini-3.6-flash-lite",
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-1.5-flash",
]

DEFAULT_MODEL = AVAILABLE_MODELS[0]
FALLBACK_MODELS = AVAILABLE_MODELS
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_OUTPUT_TOKENS = 1024
DEFAULT_PROVIDER = "google"
