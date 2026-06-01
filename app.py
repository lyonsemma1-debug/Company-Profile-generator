import streamlit as st
import subprocess
import sys
from functools import lru_cache

from generate_profiles import generate_profiles_from_csv_bytes

st.set_page_config(page_title="Company Profile Generator", layout="wide")

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;700&family=Geist+Mono:wght@400;500;700&display=swap');

:root {
    --bg: #060a0a;
    --panel: #0a1111;
    --line: #1b2c2c;
    --text: #c9c9c9;
    --text-strong: #ececec;
    --accent: #ff5a1f;
}

.stApp {
    font-family: 'Geist Mono', monospace;
    color: var(--text);
    background-color: var(--bg);
    background-image:
        linear-gradient(to right, rgba(255, 255, 255, 0.03) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(255, 255, 255, 0.03) 1px, transparent 1px),
        repeating-linear-gradient(-45deg, rgba(255, 255, 255, 0.015) 0 2px, transparent 2px 8px);
    background-size: 40px 40px, 40px 40px, 10px 10px;
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stAppViewContainer"] > .main {
    background: transparent;
}

[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid var(--line);
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.015) 0%, rgba(0, 0, 0, 0.2) 100%);
}

h1, h2, h3, p, label, div, span {
    font-family: 'Geist Mono', monospace !important;
}

/* Keep Streamlit/Material icon ligatures rendered as icons, not plain text. */
span[class*="material-symbol"],
i[class*="material-symbol"],
[data-testid="stFileUploader"] button span:first-child {
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined' !important;
    text-transform: none !important;
    letter-spacing: normal !important;
}

.brief-hero {
    border: 1px solid var(--line);
    background:
        radial-gradient(120% 80% at 0% 0%, rgba(255, 90, 31, 0.10) 0%, transparent 55%),
        linear-gradient(180deg, rgba(255, 255, 255, 0.02), rgba(0, 0, 0, 0.35));
    padding: 22px 24px;
    margin-bottom: 16px;
}

.brief-kicker {
    color: var(--accent);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-size: 12px;
    margin-bottom: 10px;
}

.brief-title {
    color: var(--text-strong);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-size: clamp(30px, 4vw, 48px);
    font-weight: 700;
    line-height: 1;
    margin: 0;
}

.brief-title-accent {
    color: var(--accent);
}

.brief-sub {
    margin-top: 12px;
    color: #9ca1a1;
    max-width: 860px;
    font-size: 13px;
    line-height: 1.5;
}

.spec-note {
    border: 1px dashed #2f3f3f;
    background: rgba(6, 10, 10, 0.65);
    color: #8f9595;
    padding: 10px 12px;
    margin-bottom: 12px;
    font-size: 12px;
    line-height: 1.6;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

[data-testid="stFileUploader"] {
    border: 1px solid var(--accent);
    background: rgba(10, 17, 17, 0.9);
    padding: 14px;
}

[data-testid="stBaseButton-secondary"] {
    padding: 14px !important
}

[data-testid="stFileUploader"] section {
    border: 1px dashed #495757;
    background: repeating-linear-gradient(
        -45deg,
        rgba(255, 255, 255, 0.015),
        rgba(255, 255, 255, 0.015) 3px,
        rgba(0, 0, 0, 0.0) 3px,
        rgba(0, 0, 0, 0.0) 9px
    );
    padding: 34px;
}

[data-testid="stFileUploader"] small {
    color: #8d9292 !important;
}

div[data-testid="stButton"] > button,
div[data-testid="stDownloadButton"] > button {
    border: 1px solid var(--accent);
    color: var(--text-strong);
    background: linear-gradient(180deg, rgba(255, 90, 31, 0.14) 0%, rgba(255, 90, 31, 0.05) 100%);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 12px;
    border-radius: 0;
}

div[data-testid="stButton"] > button:hover,
div[data-testid="stDownloadButton"] > button:hover {
    background: linear-gradient(180deg, rgba(255, 90, 31, 0.2) 0%, rgba(255, 90, 31, 0.08) 100%);
    border-color: #ff7546;
    color: #ffffff;
}

[data-testid="stFileUploader"] button {
    font-family: 'Geist', sans-serif !important;
    text-transform: none !important;
    letter-spacing: normal !important;
    font-size: 20px;
    line-height: 1.2;
    white-space: nowrap;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 38px;
    padding: 0 14px;
}

[data-testid="stFileUploader"] button span {
    display: inline-block;
    line-height: 1.2;
}

[data-testid="stSuccess"] {
    border: 1px solid #2f4f41;
    background: rgba(6, 22, 14, 0.65);
}

[data-testid="stInfo"] {
    border: 1px solid #33484a;
    background: rgba(9, 15, 17, 0.75);
}

h3 {
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-strong);
}

[data-testid="stToolbar"] {
    right: 0.75rem;
}
</style>
"""

st.markdown(THEME_CSS, unsafe_allow_html=True)
st.markdown(
    """
    <div class="brief-hero">
      <div class="brief-kicker">// COMPANY PROFILE GENERATOR</div>
      <h1 class="brief-title">COMPANY PROFILES<span class="brief-title-accent">_</span></h1>
      <p class="brief-sub">Drop one CSV to generate the full profile deck as HTML and A4 PDF with layout-accurate rendering.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

def html_to_pdf_bytes(compiled_html):
    """Convert compiled HTML into an A4 PDF with no margins and background graphics."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Playwright is not installed. Run: pip install playwright; playwright install chromium"
        ) from exc

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
            )
        except Exception as exc:
            # Streamlit Cloud often has playwright package but no installed browser binary.
            if "executable doesn't exist" in str(exc).lower():
                ensure_chromium_installed()
                browser = p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
                )
            else:
                raise

        page = browser.new_page(viewport={"width": 595, "height": 842})
        page.set_content(compiled_html, wait_until="networkidle")
        pdf_bytes = page.pdf(
            format="A4",
            print_background=True,
            prefer_css_page_size=True,
            margin={"top": "0mm", "right": "0mm", "bottom": "0mm", "left": "0mm"},
        )
        browser.close()

    return pdf_bytes


@lru_cache(maxsize=1)
def ensure_chromium_installed():
    """Install Playwright Chromium once per process when missing in hosted environments."""
    proc = subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        stderr = proc.stderr.strip() or proc.stdout.strip()
        raise RuntimeError(f"Failed to install Chromium for Playwright: {stderr}")

st.caption("Upload your CSV below.")
st.caption("In-memory flow only: files are generated for download and not saved into this repository.")

uploaded_csv = st.file_uploader("Drag and drop CSV here", type=["csv"])

if uploaded_csv is not None:
    file_signature = (uploaded_csv.name, uploaded_csv.size)
    if st.session_state.get("uploaded_file_signature") != file_signature:
        st.session_state["uploaded_file_signature"] = file_signature
        st.session_state.pop("pdf_error", None)
        with st.spinner("Generating profiles and PDF..."):
            compiled_html, profile_count = generate_profiles_from_csv_bytes(uploaded_csv.getvalue())
            st.session_state["compiled_html"] = compiled_html
            st.session_state["profile_count"] = profile_count
            try:
                st.session_state["pdf_bytes"] = html_to_pdf_bytes(compiled_html)
            except Exception as exc:
                st.session_state.pop("pdf_bytes", None)
                st.session_state["pdf_error"] = str(exc)

    compiled_html = st.session_state.get("compiled_html", "")
    profile_count = st.session_state.get("profile_count", 0)

    st.success(f"Generated {profile_count} profiles ({profile_count * 2} pages).")

    if "compiled_html" in st.session_state:
        st.download_button(
            label="Download HTML",
            data=st.session_state["compiled_html"].encode("utf-8"),
            file_name="profiles-output.html",
            mime="text/html",
        )

    if "pdf_bytes" in st.session_state:
        st.download_button(
            label="Download A4 PDF",
            data=st.session_state["pdf_bytes"],
            file_name="profiles-output.pdf",
            mime="application/pdf",
        )
    elif "pdf_error" in st.session_state:
        st.warning(
            "PDF export failed in this environment. "
            "HTML export is still available. "
            f"Details: {st.session_state['pdf_error']}"
        )

    st.subheader("Preview")
    st.components.v1.html(compiled_html, height=700, scrolling=True)
