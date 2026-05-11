"""
translation.py – Language instruction helpers for DharmaSetu.
"""

# Maps language name to a strict instruction injected into both system and user messages.
# The no-mixing rule is the key addition — models tend to slip into English for legal terms
# unless explicitly told not to.
LANGUAGE_INSTRUCTIONS = {
    "English": (
        "Generate the entire response strictly in English. "
        "Do not mix any other language into the response."
    ),
    "Hindi": (
        "Generate the entire response strictly in Hindi using Devanagari script. "
        "Do not mix English or any other language into the response. "
        "Legal terms (like IPC, BNS, FIR) may be written in Hindi transliteration "
        "(e.g., 'आईपीसी', 'एफआईआर') or kept as abbreviations, but all explanations "
        "must be in Hindi only."
    ),
    "Telugu": (
        "Generate the entire response strictly in Telugu script. "
        "Do not mix English or any other language into the response. "
        "Legal abbreviations (IPC, BNS, FIR) may be kept as-is, but all explanations "
        "must be in Telugu only."
    ),
}


def get_language_instruction(language: str) -> str:
    """Return the language instruction string for the given language."""
    return LANGUAGE_INSTRUCTIONS.get(language, LANGUAGE_INSTRUCTIONS["English"])
