"""
legal_engine.py - Core AI analysis logic for DharmaSetu.
Uses Groq (LLaMA 3.1) with agent-style chain-of-thought prompt engineering.
"""

import os
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
from translation import get_language_instruction

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

# ── Role-specific system personas ─────────────────────────────────────────────
SYSTEM_PERSONAS = {
    "Student": (
        "You are DharmaSetu, a friendly and knowledgeable Indian legal educator. "
        "Your goal is to help law students understand legal concepts clearly. "
        "Use simple language, relatable analogies, and explain legal terms when you use them. "
        "Avoid heavy jargon. Make the student feel confident about understanding the law."
    ),
    "Lawyer": (
        "You are DharmaSetu, a senior Indian legal research assistant with deep expertise "
        "in criminal, civil, and constitutional law. "
        "Provide precise IPC/BNS section references, cite relevant legal principles, "
        "discuss procedural aspects, and use professional legal terminology throughout. "
        "Your analysis should be suitable for use in legal research and case preparation."
    ),
    "Judge": (
        "You are DharmaSetu, a formal legal analysis system designed to assist judicial officers. "
        "Present analysis in a structured, objective, and impartial manner. "
        "Focus on legal principles, precedents, statutory provisions, and the burden of proof. "
        "Maintain strict neutrality. Do not suggest outcomes - only present legal frameworks."
    ),
}

# ── Hidden chain-of-thought reasoning block ───────────────────────────────────
# Instructs the model to reason through 5 agent-style steps INTERNALLY before
# writing the final output. The reasoning is never shown to the user - only the
# structured sections are returned. This is the chain-of-thought technique:
# a hidden scratchpad that significantly improves output depth and accuracy.
AGENT_REASONING = """\
BEFORE writing your final response, silently reason through these 5 steps in your \
mind. Do NOT include this reasoning in your output. It is your internal thinking only.

[INTERNAL REASONING - NOT FOR OUTPUT]
Step 1 - Issue Spotting:
  Read the facts carefully. List every legal problem you can identify.
  Ask: Who did what to whom? What rights were violated? What duties were breached?
  Consider both criminal and civil dimensions.

Step 2 - Law Mapping:
  For each issue from Step 1, map it to the most specific applicable IPC / BNS /
  Indian Evidence Act section. Prefer BNS 2023 over IPC where both apply.
  Ask: What is the exact section number? What is the punishment range?
  Are there any aggravating or mitigating factors that change the applicable section?

Step 3 - Evidence Evaluation:
  Examine every piece of evidence mentioned. Apply the Indian Evidence Act mentally.
  Ask: Is it admissible? Is it primary or secondary evidence?
  Consider: delay in reporting, chain of custody, electronic evidence (Section 65B IEA),
  witness credibility, and whether the evidence is direct or circumstantial.

Step 4 - Risk Calibration:
  For each party, weigh the strength of evidence against their legal exposure.
  Assign a risk level (High / Medium / Low) with a specific reason grounded in facts.
  Ask: Is the offence cognizable? Is bail available? What procedural risks exist?
  Consider: delay in FIR, missing witnesses, contradictory statements.

Step 5 - Role-Adapted Explanation:
  Decide how to present the above based on the user role.
  Student: use analogies, define every legal term used, keep it accessible.
  Lawyer: cite sections precisely, mention procedural steps and court jurisdiction.
  Judge: focus on burden of proof, statutory interpretation, and legal principles only.
[END INTERNAL REASONING]

Now write ONLY the structured output below, informed by your reasoning above.
"""

# ── Structured 7-section output format ────────────────────────────────────────
ANALYSIS_FORMAT = """
Analyze the legal scenario strictly under Indian law. \
Follow this EXACT format with all 7 sections:

---

## 1. Case Scenario
Restate the key facts concisely and objectively in 3-5 sentences.
Do not add assumptions - only state what is given.

## 2. Legal Issues Identified
List every distinct legal issue as a bullet point.
Each issue must name a specific legal concept or right, not a general observation.
- Issue 1
- Issue 2

## 3. Relevant Laws & Sections (IPC / BNS / Other)
For each applicable law provide: section number, title, punishment range, and \
one sentence on why it applies to THIS specific case.
- **BNS/IPC Section [X]** - [Title] ([punishment]): [Why it applies here]
- **Indian Evidence Act Section [Y]** - [Title]: [Why it applies here]
Include at least 3-5 sections. Prefer BNS 2023 sections where applicable.

## 4. Evidence Considerations
For each piece of evidence mentioned, analyse:
- Type: [documentary / oral / electronic / forensic]
- Admissibility: [cite the relevant Evidence Act section]
- Weight: [strong / moderate / weak] and the specific reason
- Challenges: [what could weaken or strengthen this evidence in court]

## 5. Possible Legal Consequences
For each party, list specific consequences:
- Criminal liability: [section, imprisonment range, fine amount]
- Civil liability: [if applicable]
- Procedural: [cognizable/non-cognizable, bailable/non-bailable, which court]
Do NOT state who will win or lose.

## 6. Risk Assessment
For each party provide a calibrated risk rating with a fact-based reason:
- **[Party name/role]:** [High / Medium / Low] - [specific reason tied to evidence and law]
Also note procedural risks: delay in FIR, missing witnesses, chain of custody gaps.

## 7. Advisory Note
Summarise the key legal principles a person in this situation must understand.
Tailor depth and language strictly to the user role.
End with one concrete practical awareness point relevant to the role.

---
> *DharmaSetu is an educational tool only. This analysis does not constitute \
legal advice and no verdict is implied.*
"""

# Max past messages sent as context (8 = 4 exchanges)
MAX_HISTORY = 8


def _build_context_clause(gender: str, religion: str) -> str:
    """
    Build an optional prompt clause for gender/religion context.
    Gender only adjusts legal analysis - never alters the case scenario.
    Religion only adds personal law references where factually relevant.
    """
    lines = []

    if gender == "Female":
        lines.append(
            "GENDER CONTEXT (Legal Analysis Only):\n"
            "The party involved is female. This context affects ONLY the legal analysis, "
            "NOT the case scenario. Do not alter, rewrite, or add facts to the case.\n"
            "Only if the existing facts already involve the following situations, "
            "mention the corresponding law:\n"
            "  - Workplace harassment already described -> Sexual Harassment of Women "
            "at Workplace Act, 2013 (POSH)\n"
            "  - Domestic abuse already described -> Protection of Women from Domestic "
            "Violence Act, 2005\n"
            "  - Physical assault on a woman already described -> BNS Section 74\n"
            "  - Matrimonial dispute already described -> Dowry Prohibition Act, 1961\n"
            "If none of these situations appear in the facts, do not mention these laws. "
            "Do not assume domestic violence or any gender-specific offence "
            "unless the facts explicitly state it."
        )

    personal_law_map = {
        "Hindu": (
            "Hindu Personal Law context: Only if the case involves family, marriage, "
            "inheritance, or succession matters already present in the facts, consider "
            "Hindu Marriage Act 1955, Hindu Succession Act 1956, Hindu Adoption and "
            "Maintenance Act 1956. Do not introduce these if the facts are about "
            "criminal matters only."
        ),
        "Muslim": (
            "Muslim Personal Law context: Only if the case involves family, marriage, "
            "divorce, or inheritance matters already present in the facts, consider "
            "Muslim Personal Law (Shariat) Application Act 1937, Dissolution of Muslim "
            "Marriages Act 1939. Do not introduce these if the facts are about "
            "criminal matters only."
        ),
        "Christian": (
            "Christian Personal Law context: Only if the case involves marriage or "
            "divorce matters already present in the facts, consider Indian Christian "
            "Marriage Act 1872 and Indian Divorce Act 1869. Do not introduce these "
            "if the facts are about criminal matters only."
        ),
        "Sikh": (
            "Sikh Personal Law context: Sikhs are generally governed by Hindu personal "
            "law unless a specific Sikh customary law applies. Only mention if the "
            "facts involve family or matrimonial matters."
        ),
    }
    if religion in personal_law_map:
        lines.append(f"RELIGION CONTEXT (Legal Analysis Only):\n{personal_law_map[religion]}")

    if not lines:
        return ""

    return (
        "\n\nCONTEXT-AWARE LEGAL CONSIDERATIONS:\n"
        "CRITICAL RULE: Do not alter the case scenario based on gender or religion. "
        "Only adjust the legal analysis and mention additional applicable laws "
        "where the facts already support them.\n\n"
        + "\n\n".join(lines)
        + "\n\nAdd this disclaimer at the end of your Advisory Note:\n"
        '"Note: Laws may vary based on personal law systems and case-specific '
        'conditions. This analysis is for educational purposes only."'
    )


def _get_system_prompt(role: str, language: str, has_history: bool,
                       gender: str = "", religion: str = "") -> str:
    """Combine persona + agent reasoning + context clause + ground rules."""
    persona          = SYSTEM_PERSONAS.get(role, SYSTEM_PERSONAS["Student"])
    lang_instruction = get_language_instruction(language)
    context_clause   = _build_context_clause(gender, religion)
    context_rule = (
        "6. This is a continuing conversation. You have the full case context from prior messages. "
        "For follow-up questions: answer ONLY what is asked, keep it short and focused, "
        "do NOT repeat the full 7-section analysis, do NOT restate the case facts unless directly asked, "
        "do NOT regenerate the case scenario unless the user explicitly asks you to. "
        "The case has already been analysed. Build on that analysis."
        if has_history else
        "6. This is the start of a new conversation."
    )
    return (
        f"{persona}\n\n"
        f"{AGENT_REASONING}\n\n"
        f"GROUND RULES YOU MUST FOLLOW:\n"
        f"1. Always cite specific IPC / BNS / Indian Evidence Act sections by number.\n"
        f"2. Never give a final verdict, judgment, or declare anyone guilty/innocent.\n"
        f"3. Always complete all 7 sections on the first query. "
        f"For follow-up questions, answer concisely and reference prior context.\n"
        f"4. {lang_instruction}\n"
        f"5. If the query is not related to law, politely redirect the user.\n"
        f"{context_rule}"
        f"{context_clause}"
    )


def build_messages(query: str, history: list, role: str, language: str,
                   gender: str = "", religion: str = "") -> list:
    """
    Build the full messages list:
      [system] + [last MAX_HISTORY messages] + [current user query]
    The current query is NOT yet in history when this is called.
    """
    has_history = len(history) > 0
    system_msg  = {
        "role": "system",
        "content": _get_system_prompt(role, language, has_history, gender, religion),
    }

    trimmed = history[-MAX_HISTORY:]
    if trimmed and trimmed[0]["role"] == "assistant":
        trimmed = trimmed[1:]

    user_content = (
        f"LANGUAGE REQUIREMENT: {get_language_instruction(language)}\n\n"
        f"Case Scenario:\n{query}\n\n"
        f"User Context:\n"
        f"- Gender of party involved: {gender if gender else 'Not specified'}\n"
        f"- Religion of party involved: {religion if religion else 'Not specified'}\n\n"
        f"Instructions:\n"
        f"1. Identify all legal issues specific to THIS scenario.\n"
        f"2. Apply relevant Indian laws (IPC/BNS) based strictly on the facts given.\n"
        f"3. {'Consider ' + religion + ' personal laws only if the facts involve family/matrimonial matters.' if religion else 'Apply general Indian law.'}\n"
        f"4. {'If the facts involve offences against a female party, mention applicable women protection laws. Do not alter the case scenario or assume gender-specific offences not present in the facts.' if gender == 'Female' else 'Apply laws based on facts only.'}\n"
        f"5. Tailor your explanation to the user role.\n"
        f"6. Generate a unique analysis specific to these exact facts - "
        f"do not produce a generic response.\n"
        f"7. Do not alter the case scenario based on gender or religion context. "
        f"Only adjust the legal analysis.\n"
        f"8. {get_language_instruction(language)}\n\n"
        f"{ANALYSIS_FORMAT}"
        if not has_history else
        f"{get_language_instruction(language)}\n\n"
        f"FOLLOW-UP QUESTION on the case already discussed:\n{query}\n\n"
        f"STRICT RULES FOR THIS FOLLOW-UP:\n"
        f"1. Do NOT repeat or restate the full legal analysis from the previous response.\n"
        f"2. Do NOT output the 7-section format again.\n"
        f"3. Do NOT regenerate the case scenario - it has already been established.\n"
        f"4. Answer ONLY the specific question asked, using the case facts already established.\n"
        f"5. Keep the answer short, focused, and direct (3-8 sentences or bullet points).\n"
        f"6. You may reference section numbers or prior points briefly, but do not re-explain them in full.\n"
        f"7. {get_language_instruction(language)}"
    )
    return [system_msg] + trimmed + [{"role": "user", "content": user_content}]


def score_analysis(response: str) -> tuple:
    """
    Parse the AI response to extract a confidence score (0-100) and risk level.
    Uses keyword signals from the Risk Assessment and Evidence sections.
    Returns (confidence: int, risk: str) where risk is 'Low', 'Medium', or 'High'.
    No extra API call needed - derived from the response text itself.
    """
    text = response.lower()

    # ── Risk level: read from the Risk Assessment section ────────────────────
    # Count High/Medium/Low mentions weighted by position in risk section
    risk_section = ""
    if "risk assessment" in text:
        start = text.find("risk assessment")
        risk_section = text[start:start + 600]

    high_count   = risk_section.count("high")
    medium_count = risk_section.count("medium")
    low_count    = risk_section.count("low")

    if high_count >= medium_count and high_count >= low_count:
        risk = "High"
    elif medium_count >= low_count:
        risk = "Medium"
    else:
        risk = "Low"

    # ── Confidence: based on evidence strength and case clarity signals ───────
    confidence = 60  # baseline

    # Evidence strength signals
    strong_signals  = ["strong evidence", "cctv", "video recording", "medical report",
                       "eyewitness", "documentary evidence", "forensic"]
    weak_signals    = ["weak evidence", "no evidence", "delayed", "contradictory",
                       "missing witness", "chain of custody", "circumstantial"]
    complex_signals = ["complex", "multiple parties", "conflicting", "disputed",
                       "forged", "alleged", "unclear"]

    for s in strong_signals:
        if s in text:
            confidence += 5
    for s in weak_signals:
        if s in text:
            confidence -= 4
    for s in complex_signals:
        if s in text:
            confidence -= 3

    # Risk level also affects confidence
    if risk == "High":
        confidence -= 8
    elif risk == "Low":
        confidence += 8

    confidence = max(30, min(95, confidence))  # clamp to 30-95 range
    return confidence, risk


def analyze_case(query: str, role: str, language: str,
                 history: list = None,
                 gender: str = "", religion: str = "") -> str:
    """
    Send query + history to Groq and return structured legal analysis.
    gender / religion are optional — pass empty string to skip context.
    Returns a user-friendly error string on any failure - never raises.
    """
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key or api_key == "your_actual_api_key_here":
        return "Warning: API key missing. Please configure GROQ_API_KEY in the .env file."

    messages = build_messages(query, history or [], role, language, gender, religion)

    try:
        client   = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.5,   # higher = more varied output for different inputs
            max_tokens=2500,
        )
        return response.choices[0].message.content

    except Exception as e:
        err = str(e)
        if "401" in err or "invalid_api_key" in err.lower():
            return "Warning: Invalid API key. Please check your GROQ_API_KEY in the .env file."
        if "429" in err or "rate_limit" in err.lower():
            return "Warning: Rate limit reached. Please wait a moment and try again."
        if "503" in err or "unavailable" in err.lower():
            return "Warning: Groq service is temporarily unavailable. Please try again shortly."
        return f"Error: Unexpected error: {err}"
