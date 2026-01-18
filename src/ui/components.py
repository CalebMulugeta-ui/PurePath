import streamlit as st
from ..schemas.models import ESGClaim


CATEGORY_COLORS = {
    "Carbon Emissions": "#4CAF50",
    "Water Usage": "#2196F3",
    "Renewable Energy": "#FFC107",
    "Waste Reduction": "#9C27B0",
    "Supply Chain Sustainability": "#FF5722",
    "Biodiversity": "#00BCD4",
    "Social Impact": "#E91E63",
    "Corporate Governance": "#607D8B",
    "Net Zero": "#8BC34A",
    "Other": "#757575"
}


def render_claim_card(claim: ESGClaim):
    """Render a single ESG claim as a styled card."""
    color = CATEGORY_COLORS.get(claim.category, "#757575")

    details = []
    if claim.target_year:
        details.append(f"Target: {claim.target_year}")
    if claim.metric:
        details.append(f"Metric: {claim.metric}")
    details_text = " | ".join(details) if details else ""

    st.markdown(f"""
    <div style="
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid {color};
        background-color: rgba(255,255,255,0.05);
        margin-bottom: 0.5rem;
    ">
        <strong style="color: {color};">{claim.category}</strong>
        <p style="margin: 0.5rem 0; color: inherit;">{claim.statement}</p>
        <small style="color: gray;">{details_text}</small>
    </div>
    """, unsafe_allow_html=True)


def render_risk_badge(risk_score: int):
    """Render a colored badge showing risk level."""
    if risk_score < 25:
        color = "#4CAF50"
        label = "Low Risk"
    elif risk_score < 50:
        color = "#FFC107"
        label = "Moderate Risk"
    elif risk_score < 75:
        color = "#FF9800"
        label = "High Risk"
    else:
        color = "#f44336"
        label = "Critical Risk"

    st.markdown(f"""
    <span style="
        background-color: {color};
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-weight: bold;
    ">{label} ({risk_score}/100)</span>
    """, unsafe_allow_html=True)
