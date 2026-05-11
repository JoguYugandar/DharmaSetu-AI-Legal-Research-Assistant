"""
streamlit_app.py - DharmaSetu AI Legal Research Assistant
Run with: .venv/Scripts/python.exe -m streamlit run streamlit_app.py
"""

import random
import time
import streamlit as st
from main import (APP_TITLE, APP_SUBTITLE, APP_FOOTER, ROLES, LANGUAGES,
                  GENDERS, RELIGIONS, EXAMPLE_QUERIES, QUERY_SCENARIOS, DEMO_CASES)
from legal_engine import analyze_case, score_analysis
from database import init_db, save_case, get_all_cases, get_case_by_id
from pdf_export import generate_pdf

init_db()

st.set_page_config(
    page_title="DharmaSetu",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* 1. RESET */
*, *::before, *::after { box-sizing: border-box; }
html, body { margin: 0; padding: 0; overflow-x: hidden; }

/* Fix autocomplete browser warning — autocomplete is an HTML attribute,
   not a CSS property. Suppress via JS injection instead (see below). */

/* 2. DARK BACKGROUND */
.stApp, .main, section.main,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background: #0e1117 !important;
    color: #e6edf3 !important;
}

/* 3. SIDEBAR
   CRITICAL: Do NOT set height/overflow on sidebar inner div — breaks toggle.
   Do NOT set min-width:0 — collapses sidebar permanently. */
[data-testid="stSidebar"] {
    background: #161b22 !important;
}
[data-testid="stSidebar"] * { color: #c9d1d9 !important; }
[data-testid="stSidebar"] .stButton > button {
    background: #21262d !important;
    border: 1px solid #30363d !important;
    color: #c9d1d9 !important;
    border-radius: 6px !important;
    font-size: 0.78rem !important;
    padding: 0.28rem 0.55rem !important;
    width: 100% !important;
    text-align: left !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #30363d !important;
    border-color: #58a6ff !important;
}
[data-testid="stSidebar"] hr {
    border-color: #21262d !important;
    margin: 0.3rem 0 !important;
}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0.2rem !important;
}
[data-testid="stSidebarCollapseButton"] {
    visibility: visible !important;
}
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stExpandSidebarButton"] {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 2rem !important;
    height: 2rem !important;
    color: #c9d1d9 !important;
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    opacity: 1 !important;
    visibility: visible !important;
    pointer-events: auto !important;
}
[data-testid="stSidebarCollapseButton"] button:hover,
[data-testid="stExpandSidebarButton"]:hover {
    background: #21262d !important;
    border-color: #58a6ff !important;
}

/* 4. MAIN CONTENT */
.block-container,
[data-testid="block-container"],
.stMainBlockContainer {
    max-width: 820px !important;
    margin: 0 auto !important;
    padding: 0.5rem 1.2rem 5.5rem 1.2rem !important;
    overflow-x: hidden !important;
    background: #0e1117 !important;
}

/* 5. TOPBAR */
.topbar {
    position: sticky;
    top: 0;
    z-index: 100;
    background: #0e1117;
    border-bottom: 1px solid #21262d;
    padding: 0.55rem 0;
    font-size: 0.92rem;
    font-weight: 700;
    color: #e6edf3;
    margin-bottom: 0.5rem;
}

/* 6. CHAT INPUT — style only, never reposition (Streamlit handles placement) */
[data-testid="stBottom"] {
    background: #0e1117 !important;
    border-top: 1px solid #21262d !important;
    padding: 0.5rem 0 0.55rem 0 !important;
}
[data-testid="stBottom"] > div {
    max-width: 820px !important;
    margin: 0 auto !important;
    width: 100% !important;
    padding: 0 !important;
}
[data-testid="stChatInput"] textarea {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 10px !important;
    color: #e6edf3 !important;
    resize: none !important;
    /* suppress autocomplete warning via attribute selector */
}
[data-testid="stChatInput"]:focus-within {
    border-color: #58a6ff !important;
    box-shadow: 0 0 0 3px rgba(88,166,255,0.15) !important;
}

/* 7. CHAT BUBBLES */
[data-testid="stChatMessage"] {
    border-radius: 12px;
    padding: 0.55rem 0.9rem;
    margin-bottom: 0.45rem;
    overflow-wrap: break-word;
    word-break: break-word;
    max-width: 100%;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    flex-direction: row-reverse;
    background: #1c2a3a !important;
    border: 1px solid #1f4068 !important;
    border-radius: 16px 16px 4px 16px;
    margin-left: auto;
    max-width: 80%;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])
    [data-testid="stChatMessageContent"] {
    text-align: right;
    color: #cae8ff;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: #161b22 !important;
    border: 1px solid #21262d !important;
    border-radius: 4px 16px 16px 16px;
    max-width: 92%;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"])
    [data-testid="stChatMessageContent"] { color: #c9d1d9; }

/* 8. MARKDOWN INSIDE BUBBLES */
[data-testid="stChatMessageContent"] { max-width: 100%; }
[data-testid="stChatMessageContent"] p  { margin: 0.18rem 0; line-height: 1.55; }
[data-testid="stChatMessageContent"] h2 {
    font-size: 0.95rem; font-weight: 600; color: #79c0ff;
    margin: 0.7rem 0 0.2rem;
    border-bottom: 1px solid #21262d; padding-bottom: 0.15rem;
}
[data-testid="stChatMessageContent"] h3 {
    font-size: 0.88rem; color: #56d364; margin: 0.45rem 0 0.1rem;
}
[data-testid="stChatMessageContent"] li     { margin: 0.1rem 0; color: #c9d1d9; }
[data-testid="stChatMessageContent"] strong { color: #e6edf3; }
[data-testid="stChatMessageContent"] code {
    background: #0d1117; color: #f0883e;
    padding: 0.1rem 0.3rem; border-radius: 4px; font-size: 0.8rem;
}
[data-testid="stChatMessageContent"] blockquote {
    border-left: 3px solid #30363d; margin: 0.3rem 0;
    padding-left: 0.6rem; color: #8b949e;
    font-style: italic; font-size: 0.82rem;
}

/* 9. SPACING */
[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlockBorderWrapper"] { gap: 0.2rem !important; }
[data-testid="stCaptionContainer"] { margin: 0 !important; padding: 0 !important; }
hr { margin: 0.2rem 0 !important; border-color: #21262d !important; }

/* 10. WELCOME */
.welcome-wrap {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    padding: 3rem 1rem 1.5rem; text-align: center; gap: 0.4rem;
}
.welcome-title { font-size: 1.65rem; font-weight: 700; color: #e6edf3; margin: 0; }
.welcome-sub   { font-size: 0.85rem; color: #8b949e; margin: 0 0 1.2rem; }

/* 11. SCORE STRIP */
.score-strip {
    display: inline-flex; gap: 0.75rem; align-items: center;
    font-size: 0.73rem; color: #8b949e; margin-top: 0.3rem;
    padding: 0.18rem 0.55rem; background: #0d1117;
    border: 1px solid #21262d; border-radius: 6px;
}

/* 12. BUTTONS */
.stDownloadButton > button, .stButton > button {
    background: #21262d !important;
    border: 1px solid #30363d !important;
    color: #c9d1d9 !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
}
.stDownloadButton > button:hover, .stButton > button:hover {
    background: #30363d !important;
    border-color: #58a6ff !important;
    color: #e6edf3 !important;
}

/* 13. MISC */
.history-meta { font-size: 0.7rem; color: #8b949e; margin-bottom: 0.15rem; }
.dharma-footer { text-align: center; color: #30363d; font-size: 0.65rem; padding: 0.35rem 0; }

/* 14. STREAMLIT CHROME
   Keep header visible — Streamlit places the sidebar reopen button there.
   Hide only #MainMenu and footer. */
#MainMenu, footer { visibility: hidden; }
header, [data-testid="stHeader"] {
    background: #0e1117 !important;
    color: #c9d1d9 !important;
}
[data-testid="stSidebarCollapseButton"] {
    visibility: visible !important;
}
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stExpandSidebarButton"] {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 2rem !important;
    height: 2rem !important;
    color: #c9d1d9 !important;
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    opacity: 1 !important;
    visibility: visible !important;
    pointer-events: auto !important;
}
[data-testid="stSidebarCollapseButton"] button:hover,
[data-testid="stExpandSidebarButton"]:hover {
    background: #21262d !important;
    border-color: #58a6ff !important;
}
</style>
""", unsafe_allow_html=True)

# Inject autocomplete="off" on all inputs via JS — CSS cannot set HTML attributes
st.markdown(
    '<script>document.querySelectorAll("input,textarea")'
    '.forEach(el=>el.setAttribute("autocomplete","off"));</script>',
    unsafe_allow_html=True,
)

# ── Session state — safe initialisation ──────────────────────────────────────
_DEFAULTS: dict = {
    "messages":         [],
    "pending_input":    "",
    "followup_pending": "",
    "viewing_case":     None,
    "last_query":       "",
    "last_response":    "",
    "last_role":        "",
    "last_language":    "",
    "demo_preview":     "",
    "_processing":      False,
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# Always reset _processing on page load — prevents permanent freeze
# (st.rerun() after processing sets it False, but a hard refresh skips that)
if st.session_state._processing:
    st.session_state._processing = False


# ── Helpers ───────────────────────────────────────────────────────────────────
def render_score_meter(confidence: int, risk: str) -> None:
    color = {"High": "#f85149", "Medium": "#e3b341"}.get(risk, "#3fb950")
    st.markdown(
        f'<div class="score-strip">'
        f'📊 <strong style="color:#e6edf3">{confidence}%</strong> confidence'
        f' &nbsp;·&nbsp; '
        f'Risk: <strong style="color:{color}">{risk}</strong>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_streaming(content: str) -> None:
    """Batch-stream in 15-word chunks. Double-wrapped for WebSocket safety."""
    if content.startswith(("Warning:", "Error:")):
        st.warning(content)
        return
    try:
        placeholder = st.empty()
        words = content.split(" ")
        displayed = ""
        for i in range(0, len(words), 15):
            displayed += ("" if i == 0 else " ") + " ".join(words[i:i + 15])
            placeholder.markdown(displayed + " |")
            time.sleep(0.055)
        placeholder.markdown(content)
    except Exception:
        # WebSocket dropped mid-stream — fall back to static render
        try:
            st.markdown(content)
        except Exception:
            pass  # connection fully gone


def render_assistant(content: str) -> None:
    if content.startswith(("Warning:", "Error:")):
        st.warning(content)
        return
    st.markdown(content)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚖️ DharmaSetu")
    st.caption(APP_SUBTITLE)

    st.markdown("**⚙️ Settings**")
    role = st.radio("Your Role", list(ROLES.keys()), index=2,
                    help="Changes the tone and depth of the AI response")
    language = st.selectbox("Language", LANGUAGES,
                            help="AI will respond in the selected language")

    st.markdown("**📌 Case Context** *(optional)*")
    st.caption("Helps the AI include relevant personal laws.")
    gender = st.selectbox("Gender of party involved", GENDERS,
                          help="If Female, women-specific laws are highlighted")
    religion = st.selectbox("Religion of party involved", RELIGIONS,
                            help="Relevant personal laws included where applicable")
    gender   = "" if gender   == "Prefer not to say" else gender
    religion = "" if religion == "Prefer not to say" else religion

    st.markdown("**💡 Quick Examples**")
    for i, label in enumerate(EXAMPLE_QUERIES + ["Try Demo Case"]):
        if st.button(label, use_container_width=True, key=f"ex_{i}"):
            if "Demo" in label:
                selected = random.choice(DEMO_CASES)
                st.session_state.pending_input = selected
                st.session_state.demo_preview  = selected
            else:
                st.session_state.pending_input = QUERY_SCENARIOS.get(label, label)
            st.rerun()  # needed so pending_input is picked up immediately

    if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_chat"):
        st.session_state.messages      = []
        st.session_state.last_query    = ""
        st.session_state.last_response = ""
        st.session_state.demo_preview  = ""
        st.session_state.viewing_case  = None
        st.session_state._processing   = False
        st.rerun()

    st.divider()
    st.markdown("**🗂️ Case History**")
    try:
        all_cases = get_all_cases()
    except Exception:
        all_cases = []

    if not all_cases:
        st.caption("No cases saved yet.")
    else:
        search = st.text_input(
            "Search", placeholder="Filter cases...",
            label_visibility="collapsed", key="history_search",
        )
        filtered = (
            [c for c in all_cases if search.lower() in c["user_query"].lower()]
            if search else all_cases
        )
        for case in filtered[:20]:
            is_active = st.session_state.viewing_case == case["case_id"]
            lbl = f"{'▶ ' if is_active else ''}#{case['case_id']} {case['user_query'][:26]}..."
            if st.button(lbl, key=f"case_{case['case_id']}", use_container_width=True,
                         type="primary" if is_active else "secondary"):
                st.session_state.viewing_case = None if is_active else case["case_id"]
                st.rerun()

    st.caption("⚖️ Educational use only. Not legal advice.")


# ── Topbar ────────────────────────────────────────────────────────────────────
st.markdown(f'<div class="topbar">⚖️ {APP_TITLE}</div>', unsafe_allow_html=True)

# ── History view ──────────────────────────────────────────────────────────────
if st.session_state.viewing_case is not None:
    case = None
    try:
        case = get_case_by_id(st.session_state.viewing_case)
    except Exception:
        pass

    if case is None:
        # DB error or deleted case — reset and continue to normal view
        st.session_state.viewing_case = None
        st.rerun()
    else:
        col_meta, col_close = st.columns([6, 1])
        col_meta.markdown(
            f'<div class="history-meta">💬 Case #{case["case_id"]} &nbsp;·&nbsp; '
            f'{case["role"]} &nbsp;·&nbsp; {case["language"]} &nbsp;·&nbsp; '
            f'{case["timestamp"]}</div>',
            unsafe_allow_html=True,
        )
        if col_close.button("✕ Back", key="close_history"):
            st.session_state.viewing_case = None
            st.rerun()
        else:
            # Only render content when NOT closing
            with st.chat_message("user"):
                st.markdown(case["user_query"])
            with st.chat_message("assistant"):
                render_assistant(case["ai_response"])
            try:
                pdf_bytes = generate_pdf(
                    case["user_query"], case["ai_response"],
                    case["role"], case["language"],
                )
                st.download_button(
                    "📄 Download PDF", data=pdf_bytes,
                    file_name=f"dharmasetu_case_{case['case_id']}.pdf",
                    mime="application/pdf", use_container_width=True,
                )
            except Exception as e:
                st.caption(f"PDF unavailable: {e}")

# ── Welcome screen ────────────────────────────────────────────────────────────
elif not st.session_state.messages:
    if st.session_state.demo_preview:
        st.caption(f"📋 Demo queued: _{st.session_state.demo_preview[:90]}_")
    else:
        st.markdown(
            '<div class="welcome-wrap">'
            '<p class="welcome-title">⚖️ DharmaSetu</p>'
            '<p class="welcome-sub">AI-powered legal analysis · Ask anything</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        for i, label in enumerate((EXAMPLE_QUERIES + ["Try Demo Case"])[:4]):
            col   = c1 if i % 2 == 0 else c2
            short = QUERY_SCENARIOS.get(label, label)
            prev  = short[:58] + "…" if len(short) > 58 else short
            if col.button(f"**{label}**\n\n{prev}",
                          use_container_width=True, key=f"card_{i}"):
                if "Demo" in label:
                    selected = random.choice(DEMO_CASES)
                    st.session_state.pending_input = selected
                    st.session_state.demo_preview  = selected
                else:
                    st.session_state.pending_input = QUERY_SCENARIOS.get(label, label)
                st.rerun()

# ── Chat messages ─────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        render_assistant(msg["content"])

# ── Post-chat: PDF + follow-ups ───────────────────────────────────────────────
_last = st.session_state.get("last_response", "")
if _last and not _last.startswith(("Warning:", "Error:")):
    try:
        pdf_bytes = generate_pdf(
            st.session_state.last_query, _last,
            st.session_state.last_role, st.session_state.last_language,
        )
        st.download_button(
            "📄 Download Last Analysis as PDF", data=pdf_bytes,
            file_name="dharmasetu_legal_report.pdf",
            mime="application/pdf", use_container_width=True,
        )
    except Exception as e:
        st.caption(f"PDF unavailable: {e}")

if st.session_state.get("last_query"):
    FOLLOWUPS = {
        "💬 Explain Simply":     "Explain the above case in very simple terms, as if explaining to a common person.",
        "⚠️ Show Risks":         "What are the key legal risks for each party in the above case?",
        "📋 Legal Consequences": "What are the possible legal consequences for each party in the above case?",
    }
    f_cols = st.columns(len(FOLLOWUPS))
    for col, (label, query_text) in zip(f_cols, FOLLOWUPS.items()):
        if col.button(label, use_container_width=True, key=f"fu_{label}"):
            st.session_state.followup_pending = query_text
            st.rerun()

st.markdown(f'<div class="dharma-footer">{APP_FOOTER}</div>', unsafe_allow_html=True)

# ── Chat input ────────────────────────────────────────────────────────────────
# Note: st.chat_input does not support a `disabled` parameter — removed to
# prevent TypeError on all Streamlit versions.
user_input = st.chat_input("💬 Describe your legal query or case scenario...")

# Consume pending inputs — clear BEFORE assigning to prevent rerun loops
if not user_input:
    if st.session_state.followup_pending:
        user_input = st.session_state.followup_pending
        st.session_state.followup_pending = ""
    elif st.session_state.pending_input:
        user_input = st.session_state.pending_input
        st.session_state.pending_input = ""

# ── Process message ───────────────────────────────────────────────────────────
if user_input and user_input.strip() and not st.session_state._processing:
    query            = user_input.strip()
    history_snapshot = list(st.session_state.messages)

    # Guard set BEFORE append — prevents double-append if rerun fires mid-flight
    st.session_state._processing = True
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    response = ""
    with st.chat_message("assistant"):
        with st.spinner("Analysing under Indian law..."):
            try:
                response = analyze_case(
                    query, role, language,
                    history=history_snapshot,
                    gender=gender, religion=religion,
                )
            except Exception as e:
                response = f"Error: Unexpected failure — {e}"

        render_streaming(response)

        if not response.startswith(("Warning:", "Error:")):
            try:
                confidence, risk = score_analysis(response)
                render_score_meter(confidence, risk)
            except Exception:
                pass

    st.session_state.messages.append({"role": "assistant", "content": response})

    if not response.startswith(("Warning:", "Error:")):
        try:
            save_case(query, response, role, language)
        except Exception:
            pass  # DB failure must not crash the app
        st.session_state.last_query    = query
        st.session_state.last_response = response
        st.session_state.last_role     = role
        st.session_state.last_language = language

    st.session_state.demo_preview = ""
    st.session_state._processing  = False
    st.rerun()
