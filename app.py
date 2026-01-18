import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime
from urllib.parse import urlparse
from typing import List

from src.clients.yellowcake import YellowcakeClient
from src.clients.gemini import GeminiClient
from src.services.verifier import VerificationEngine
from src.schemas.models import ESGClaim, GreenwashReport
from src.ui.components import render_claim_card, render_risk_badge
from src.ui.charts import render_truth_meter

load_dotenv()

st.set_page_config(
    page_title="PurePath | Greenwashing Monitor",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Forest Green Eco-Friendly Design System
st.markdown("""
<style>
    /* Import clean, modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

    /* CSS Variables - Forest Green Palette */
    :root {
        --forest-dark: #1B4332;
        --forest-primary: #2D6A4F;
        --forest-medium: #40916C;
        --forest-light: #52B788;
        --forest-pale: #74C69D;
        --forest-mist: #95D5B2;
        --forest-frost: #B7E4C7;
        --forest-snow: #D8F3DC;
        --earth-brown: #5C4033;
        --bark-brown: #8B7355;
        --cream: #FEFAE0;
        --soft-white: #F8FAF7;
        --text-primary: #1B4332;
        --text-secondary: #40916C;
        --text-muted: #6B7B6E;
    }

    /* Global Styles */
    .stApp {
        background: linear-gradient(165deg, #F8FAF7 0%, #D8F3DC 50%, #B7E4C7 100%);
    }

    /* Main Header */
    .main-header {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 2.8rem;
        font-weight: 700;
        color: var(--forest-dark);
        margin-bottom: 0.25rem;
        letter-spacing: -0.5px;
    }

    .sub-header {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-secondary);
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 2rem;
        letter-spacing: 0.2px;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--forest-dark) 0%, var(--forest-primary) 100%);
    }

    [data-testid="stSidebar"] * {
        color: var(--soft-white) !important;
    }

    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: var(--forest-frost) !important;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.2);
    }

    /* Input Fields - Complete override */
    .stTextInput,
    .stTextInput > div,
    .stTextInput > div > div,
    .stTextInput > label,
    .stTextInput [data-baseweb="base-input"],
    .stTextInput [data-baseweb="input"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }

    .stTextInput > div > div > input {
        background-color: #FFFFFF !important;
        color: #1B4332 !important;
        border: 2px solid #95D5B2 !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
        outline: none !important;
        box-shadow: none !important;
        -webkit-appearance: none !important;
        -moz-appearance: none !important;
        appearance: none !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #6B7B6E !important;
        opacity: 0.8 !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #2D6A4F !important;
        box-shadow: none !important;
        outline: none !important;
        color: #1B4332 !important;
    }

    /* Primary Button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--forest-primary) 0%, var(--forest-medium) 100%);
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        letter-spacing: 0.3px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(45, 106, 79, 0.3);
    }

    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, var(--forest-dark) 0%, var(--forest-primary) 100%);
        box-shadow: 0 6px 20px rgba(27, 67, 50, 0.4);
        transform: translateY(-2px);
    }

    /* Section Headers */
    .stMarkdown h2, .stMarkdown h3 {
        font-family: 'Inter', sans-serif;
        color: var(--forest-dark);
        font-weight: 600;
    }

    /* Dividers */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--forest-mist), transparent);
        margin: 1.5rem 0;
    }

    /* Status Messages */
    .stSuccess {
        background-color: rgba(82, 183, 136, 0.15);
        border-left: 4px solid var(--forest-light);
    }

    .stError {
        background-color: rgba(220, 53, 69, 0.1);
        border-left: 4px solid #dc3545;
    }

    .stWarning {
        background-color: rgba(255, 193, 7, 0.15);
        border-left: 4px solid #ffc107;
    }

    .stInfo {
        background-color: rgba(45, 106, 79, 0.1);
        border-left: 4px solid var(--forest-primary);
    }

    /* Progress Bar */
    .stProgress .st-bo {
        background-color: var(--forest-light);
    }

    /* Organic leaf decoration */
    .leaf-decoration {
        position: relative;
    }

    .leaf-decoration::before {
        content: "🌿";
        position: absolute;
        left: -30px;
        opacity: 0.6;
    }

    /* Card-like containers */
    .eco-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid var(--forest-frost);
        box-shadow: 0 4px 20px rgba(27, 67, 50, 0.08);
        margin-bottom: 1rem;
    }

    /* Metric Cards */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.9);
        padding: 1rem;
        border-radius: 12px;
        border-left: 4px solid var(--forest-medium);
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--forest-snow);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--forest-mist);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--forest-medium);
    }
</style>
""", unsafe_allow_html=True)


def check_api_keys() -> dict:
    """Check if required API keys are configured."""
    return {
        "yellowcake": bool(os.getenv("YELLOWCAKE_API_KEY")),
        "gemini": bool(os.getenv("GEMINI_API_KEY"))
    }


def extract_company_name(url: str) -> str:
    """Extract company name from URL."""
    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")
    return domain.split(".")[0].title()


def run_analysis(url: str):
    """Run the complete greenwashing analysis pipeline."""
    yellowcake = YellowcakeClient(api_key=os.getenv("YELLOWCAKE_API_KEY"))
    gemini = GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))
    verifier = VerificationEngine(gemini)

    company_name = extract_company_name(url)
    claims: List[ESGClaim] = []

    col_status, col_results = st.columns([1, 2])

    with col_status:
        st.subheader("Status Feed")

        with st.status("Analyzing website...", expanded=True) as status:
            st.write(f"Connecting to {url}...")
            claims_placeholder = st.empty()

            try:
                claim_count = 0

                for chunk in yellowcake.extract_stream(url, render_js=True):
                    if isinstance(chunk, dict):
                        if "data" in chunk and isinstance(chunk["data"], list):
                            for item in chunk["data"]:
                                try:
                                    claim = ESGClaim(**item)
                                    claims.append(claim)
                                    claim_count += 1
                                    claims_placeholder.write(
                                        f"Found {claim_count} claims..."
                                    )
                                except Exception:
                                    pass

                        elif "category" in chunk and "statement" in chunk:
                            try:
                                claim = ESGClaim(**chunk)
                                claims.append(claim)
                                claim_count += 1
                                claims_placeholder.write(
                                    f"Found {claim_count} claims..."
                                )
                            except Exception:
                                pass

                        elif isinstance(chunk, list):
                            for item in chunk:
                                if isinstance(item, dict) and "category" in item:
                                    try:
                                        claim = ESGClaim(**item)
                                        claims.append(claim)
                                        claim_count += 1
                                        claims_placeholder.write(
                                            f"Found {claim_count} claims..."
                                        )
                                    except Exception:
                                        pass

                st.write(f"Extracted {len(claims)} ESG claims")

                if claims:
                    st.write("Verifying claims with AI...")
                    risk_score, red_flags, summary = verifier.verify_claims(
                        claims=claims,
                        company_name=company_name
                    )
                else:
                    risk_score = 0
                    red_flags = []
                    summary = "No ESG claims were found on this page."

                status.update(label="Analysis complete!", state="complete")

            except Exception as e:
                status.update(label="Analysis failed", state="error")
                st.error(f"Error: {str(e)}")
                return

    report = GreenwashReport(
        company_name=company_name,
        company_url=url,
        claims=claims,
        risk_score=risk_score,
        conflicting_evidence=red_flags,
        analysis_summary=summary,
        timestamp=datetime.now().isoformat()
    )

    st.session_state.report = report

    with col_results:
        display_results(report)


def display_results(report: GreenwashReport):
    """Display analysis results."""
    # Results header
    st.markdown(f'''
    <div style="
        background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%);
        color: white;
        padding: 1.25rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    ">
        <h2 style="margin: 0; color: white; font-family: 'Playfair Display', serif;">
            📊 Analysis Results
        </h2>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1.1rem;">
            {report.company_name}
        </p>
    </div>
    ''', unsafe_allow_html=True)

    col_gauge, col_summary = st.columns([1, 2])

    with col_gauge:
        render_truth_meter(report.risk_score)

    with col_summary:
        st.markdown('''
        <h3 style="color: #1B4332; font-family: Inter, sans-serif; margin-bottom: 1rem;">
            Risk Assessment
        </h3>
        ''', unsafe_allow_html=True)
        render_risk_badge(report.risk_score)
        st.write("")

        if report.analysis_summary:
            st.markdown(f'''
            <div class="eco-card" style="margin-top: 1rem;">
                <p style="color: #2D6A4F; line-height: 1.7; margin: 0;">
                    {report.analysis_summary}
                </p>
            </div>
            ''', unsafe_allow_html=True)

    st.markdown("---")

    if report.claims:
        st.markdown(f'''
        <h3 style="color: #1B4332; font-family: Inter, sans-serif; margin-bottom: 1rem;">
            🌱 ESG Claims Detected <span style="
                background: #40916C;
                color: white;
                padding: 0.2rem 0.6rem;
                border-radius: 12px;
                font-size: 0.9rem;
                margin-left: 0.5rem;
            ">{len(report.claims)}</span>
        </h3>
        ''', unsafe_allow_html=True)
        for claim in report.claims:
            render_claim_card(claim)
    else:
        st.info("No ESG claims were found on this page.")

    if report.conflicting_evidence:
        st.markdown('''
        <h3 style="color: #c0392b; font-family: Inter, sans-serif; margin: 1.5rem 0 1rem 0;">
            ⚠️ Red Flags & Concerns
        </h3>
        ''', unsafe_allow_html=True)
        for flag in report.conflicting_evidence:
            st.markdown(f'''
            <div style="
                background: rgba(192, 57, 43, 0.08);
                border-left: 3px solid #e74c3c;
                padding: 0.75rem 1rem;
                margin-bottom: 0.5rem;
                border-radius: 0 8px 8px 0;
            ">
                <span style="color: #c0392b;">⚡</span> {flag}
            </div>
            ''', unsafe_allow_html=True)


def main():
    # Hero Header with organic styling
    st.markdown('''
    <div style="text-align: center; padding: 1rem 0 0.5rem 0;">
        <p style="font-size: 3rem; margin-bottom: 0;">🌲</p>
        <p class="main-header">PurePath</p>
        <p class="sub-header">Real-Time Greenwashing Detection & ESG Verification</p>
    </div>
    ''', unsafe_allow_html=True)

    with st.sidebar:
        # Sidebar branding
        st.markdown('''
        <div style="text-align: center; padding: 1rem 0; margin-bottom: 1rem;">
            <span style="font-size: 2rem;">🌿</span>
            <h2 style="margin: 0.5rem 0 0 0; font-size: 1.3rem;">PurePath</h2>
            <p style="font-size: 0.8rem; opacity: 0.8; margin-top: 0.25rem;">Sustainable Intelligence</p>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### System Status")
        api_status = check_api_keys()

        if api_status["yellowcake"]:
            st.success("Yellowcake API: Connected")
        else:
            st.error("Yellowcake API: Not configured")

        if api_status["gemini"]:
            st.success("Gemini API: Connected")
        else:
            st.error("Gemini API: Not configured")

        if not api_status["yellowcake"] or not api_status["gemini"]:
            st.markdown('''
            <div style="background: rgba(255,193,7,0.2); padding: 0.75rem; border-radius: 8px; margin-top: 0.5rem;">
                <small>Add missing API keys to your .env file to enable analysis.</small>
            </div>
            ''', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### How It Works")
        st.markdown("""
        <div style="font-size: 0.9rem; line-height: 1.6;">
            <p><strong>1.</strong> Extract ESG claims from corporate websites</p>
            <p><strong>2.</strong> Analyze claim specificity & quality</p>
            <p><strong>3.</strong> Identify potential red flags</p>
            <p><strong>4.</strong> Calculate greenwashing risk score</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('''
        <div style="text-align: center; font-size: 0.75rem; opacity: 0.7; padding-top: 1rem;">
            Built with 💚 for a sustainable future
        </div>
        ''', unsafe_allow_html=True)

    # Search Section with eco-card styling
    st.markdown('''
    <div class="eco-card" style="margin-top: 1rem;">
        <h4 style="color: #1B4332; margin-bottom: 0.5rem; font-family: Inter, sans-serif;">
            🔍 Analyze a Company
        </h4>
        <p style="color: #6B7B6E; font-size: 0.9rem; margin-bottom: 1rem;">
            Enter a corporate sustainability or ESG page URL to detect potential greenwashing
        </p>
    </div>
    ''', unsafe_allow_html=True)

    col1, col2 = st.columns([4, 1])

    with col1:
        company_url = st.text_input(
            "Website URL",
            placeholder="https://company.com/sustainability",
            help="Enter the full URL of a company's sustainability, ESG, or environmental page",
            label_visibility="collapsed"
        )

    with col2:
        analyze_btn = st.button(
            "🌿 Analyze",
            type="primary",
            use_container_width=True,
            disabled=not (check_api_keys()["yellowcake"] and check_api_keys()["gemini"])
        )

    if analyze_btn and company_url:
        if not company_url.startswith(("http://", "https://")):
            company_url = "https://" + company_url
        run_analysis(company_url)

    elif "report" in st.session_state:
        col_status, col_results = st.columns([1, 2])
        with col_results:
            display_results(st.session_state.report)


if __name__ == "__main__":
    main()
