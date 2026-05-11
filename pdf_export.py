"""
pdf_export.py - PDF generation for DharmaSetu legal analysis reports.
Uses fpdf2 (pip install fpdf2). All text is sanitised to ASCII before
writing so standard Helvetica/Arial fonts never encounter Unicode errors.
"""

import re
from datetime import datetime, timezone
from fpdf import FPDF
from fpdf.enums import XPos, YPos


# ── Text sanitisation ─────────────────────────────────────────────────────────

def _strip_non_ascii(text: str) -> str:
    """
    Remove every character that cannot be encoded in latin-1 (the encoding
    used by FPDF's built-in fonts).  This covers all emojis, Devanagari,
    Telugu, and any other multi-byte Unicode codepoints.
    """
    return text.encode("latin-1", errors="ignore").decode("latin-1")


def _clean_markdown(text: str) -> str:
    """Strip markdown syntax, then remove non-ASCII characters."""
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)          # **bold**
    text = re.sub(r"\*(.*?)\*",     r"\1", text)           # *italic*
    text = re.sub(r"`(.*?)`",       r"\1", text)           # `code`
    text = re.sub(r"^#{1,6}\s*",    "",    text, flags=re.MULTILINE)  # headings
    text = re.sub(r"^>\s*",         "",    text, flags=re.MULTILINE)  # blockquotes
    text = re.sub(r"-{3,}",         "",    text)           # horizontal rules
    return _strip_non_ascii(text.strip())


# ── Custom FPDF subclass ──────────────────────────────────────────────────────

class _PDF(FPDF):
    """FPDF subclass with branded header and page-number footer."""

    def header(self):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(30, 60, 120)
        self.cell(0, 10, "DharmaSetu - AI Legal Research Assistant", align="L",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(120, 120, 120)
        # Use UTC-aware datetime to avoid naive-datetime warnings
        now = datetime.now(timezone.utc).strftime("%d %b %Y  %H:%M UTC")
        self.cell(0, 10, now, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(4)
        self.set_draw_color(30, 60, 120)
        self.set_line_width(0.4)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(
            0, 10,
            f"For educational purposes only. Not legal advice.  |  Page {self.page_no()}",
            align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT,
        )


# ── PDF section renderers ─────────────────────────────────────────────────────

def _render_query_box(pdf: _PDF, query: str, role: str, language: str) -> None:
    """Render the user query in a shaded box with meta info."""
    W = pdf.w - 28

    pdf.set_fill_color(235, 240, 255)
    pdf.set_draw_color(180, 190, 220)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(30, 60, 120)
    pdf.cell(0, 7, f"  Query / Case  |  Role: {role}  |  Language: {language}",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True, border=1)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(30, 30, 30)
    pdf.set_fill_color(248, 250, 255)
    pdf.multi_cell(W, 6, _clean_markdown(query), border=1, fill=True)
    pdf.ln(5)


def _render_analysis_sections(pdf: _PDF, analysis: str) -> None:
    """Split analysis on H2 headings and render each as a coloured section."""
    W = pdf.w - 28
    heading_colors = [(20, 40, 100), (10, 90, 90)]

    sections = re.split(r"(?=^## )", analysis, flags=re.MULTILINE)
    sections = [s.strip() for s in sections if s.strip()]

    for idx, section in enumerate(sections):
        lines = section.splitlines()
        if not lines:
            continue

        # Section heading
        r, g, b = heading_colors[idx % 2]
        pdf.set_fill_color(r, g, b)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 8, f"  {_clean_markdown(lines[0])}",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)

        # Section body
        pdf.set_text_color(30, 30, 30)
        pdf.set_font("Helvetica", "", 10)

        for line in lines[1:]:
            stripped = line.strip()
            if not stripped or stripped == "---":
                pdf.ln(2)
                continue
            if stripped.startswith(("- ", "* ", chr(8226) + " ")):
                pdf.set_x(18)
                pdf.cell(4, 6, "-")
                pdf.multi_cell(W - 8, 6, _clean_markdown(stripped[2:]))
            else:
                pdf.multi_cell(W, 6, _clean_markdown(stripped))

        pdf.ln(3)


def _render_disclaimer(pdf: _PDF) -> None:
    """Render the disclaimer block at the end of the report."""
    W = pdf.w - 28
    pdf.set_fill_color(255, 245, 220)
    pdf.set_draw_color(200, 160, 60)
    pdf.set_text_color(100, 70, 0)
    pdf.set_font("Helvetica", "I", 9)
    pdf.multi_cell(
        W, 6,
        "Disclaimer: This report is generated by DharmaSetu for educational purposes only. "
        "It does not constitute legal advice and no verdict is implied. "
        "Consult a qualified lawyer for actual legal guidance.",
        border=1, fill=True,
    )


# ── Public API ────────────────────────────────────────────────────────────────

def generate_pdf(query: str, analysis: str, role: str, language: str) -> bytes:
    """
    Build a formatted A4 PDF from the legal analysis and return raw bytes.
    All text is sanitised to ASCII/latin-1 before writing, so emojis and
    Unicode characters are safely removed without raising FPDF errors.
    Compatible with st.download_button(data=...).
    """
    pdf = _PDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(14, 14, 14)
    pdf.add_page()

    # Report title
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(20, 40, 100)
    pdf.cell(0, 10, "Legal Analysis Report",
             align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    _render_query_box(pdf, query, role, language)
    _render_analysis_sections(pdf, analysis)
    _render_disclaimer(pdf)

    return bytes(pdf.output())
