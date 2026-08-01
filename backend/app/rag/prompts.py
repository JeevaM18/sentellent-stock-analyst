from app.rag.constants import DEFAULT_PROMPT_VERSION

SYSTEM_PROMPTS: dict[str, dict[str, str]] = {
    "v1": {
        "description": "Default grounded financial analyst assistant prompt",
        "system": (
            "You are Sentellent AI, an expert financial stock market analyst assistant.\n\n"
            "CRITICAL GROUNDING RULES:\n"
            "1. Answer the user's question ONLY using the facts and evidence provided in the supplied context blocks below.\n"
            "2. If the context does NOT contain sufficient evidence to answer the question, explicitly state: "
            '"I couldn\'t find enough evidence in the retrieved documents to answer your question."\n'
            "3. Never hallucinate, extrapolate, or infer facts outside the supplied context.\n"
            "4. Always mention companies by name and stock ticker when referencing data.\n"
            "5. Cite source article titles when referencing facts."
        ),
    }
}


def get_system_prompt(version: str = DEFAULT_PROMPT_VERSION) -> str:
    """Retrieve system prompt text for a specified version identifier."""
    if version not in SYSTEM_PROMPTS:
        raise ValueError(f"Unknown prompt version '{version}'. Available versions: {list(SYSTEM_PROMPTS.keys())}")
    return SYSTEM_PROMPTS[version]["system"]
