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
    page_title="Greenwashing Monitor",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stProgress .st-bo { background-color: #00ff00; }
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        color: gray;
        margin-bottom: 2rem;
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
    st.subheader(f"Analysis: {report.company_name}")

    col_gauge, col_summary = st.columns([1, 2])

    with col_gauge:
        render_truth_meter(report.risk_score)

    with col_summary:
        st.markdown("### Risk Assessment")
        render_risk_badge(report.risk_score)
        st.write("")

        if report.analysis_summary:
            st.markdown(report.analysis_summary)

    st.markdown("---")

    if report.claims:
        st.markdown(f"### ESG Claims Found ({len(report.claims)})")
        for claim in report.claims:
            render_claim_card(claim)
    else:
        st.info("No ESG claims were found on this page.")

    if report.conflicting_evidence:
        st.markdown("### Red Flags / Concerns")
        for flag in report.conflicting_evidence:
            st.markdown(f"- {flag}")


def main():
    st.markdown('<p class="main-header">Real-Time Greenwashing Monitor</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Analyze ESG claims and detect potential greenwashing</p>',
                unsafe_allow_html=True)

    with st.sidebar:
        st.header("Configuration")
        api_status = check_api_keys()

        st.markdown("**API Status:**")
        if api_status["yellowcake"]:
            st.success("Yellowcake API: Connected")
        else:
            st.error("Yellowcake API: Missing key")

        if api_status["gemini"]:
            st.success("Gemini API: Connected")
        else:
            st.error("Gemini API: Missing key")

        if not api_status["yellowcake"] or not api_status["gemini"]:
            st.warning("Add missing API keys to your .env file")

        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This tool analyzes corporate sustainability pages
        to detect potential greenwashing by:

        1. Extracting ESG claims from websites
        2. Analyzing claim quality and specificity
        3. Identifying red flags and concerns
        4. Computing a greenwashing risk score
        """)

    col1, col2 = st.columns([3, 1])

    with col1:
        company_url = st.text_input(
            "Enter company sustainability page URL",
            placeholder="https://company.com/sustainability",
            help="Enter the URL of a company's sustainability or ESG page"
        )

    with col2:
        st.write("")
        st.write("")
        analyze_btn = st.button(
            "Analyze",
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
