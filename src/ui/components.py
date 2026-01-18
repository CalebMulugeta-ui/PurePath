import streamlit as st
from ..schemas.models import ESGClaim


# Forest Green Eco-Friendly Color Palette
CATEGORY_COLORS = {
    "Carbon Emissions": "#2D6A4F",      # Forest Primary
    "Water Usage": "#1B4332",           # Forest Dark
    "Renewable Energy": "#40916C",      # Forest Medium
    "Waste Reduction": "#52B788",       # Forest Light
    "Supply Chain Sustainability": "#74C69D",  # Forest Pale
    "Biodiversity": "#95D5B2",          # Forest Mist
    "Social Impact": "#5C4033",         # Earth Brown
    "Corporate Governance": "#8B7355",  # Bark Brown
    "Net Zero": "#B7E4C7",              # Forest Frost
    "Other": "#6B7B6E"                  # Muted Green-Gray
}

# Category icons for visual enhancement
CATEGORY_ICONS = {
    "Carbon Emissions": "🏭",
    "Water Usage": "💧",
    "Renewable Energy": "⚡",
    "Waste Reduction": "♻️",
    "Supply Chain Sustainability": "🔗",
    "Biodiversity": "🦋",
    "Social Impact": "👥",
    "Corporate Governance": "🏛️",
    "Net Zero": "🎯",
    "Other": "📋"
}


def render_claim_card(claim: ESGClaim):
    """Render a single ESG claim as a styled card with organic design."""
    color = CATEGORY_COLORS.get(claim.category, "#6B7B6E")
    icon = CATEGORY_ICONS.get(claim.category, "📋")

    details = []
    if claim.target_year:
        details.append(f"<span style='color: #40916C;'>📅 Target: {claim.target_year}</span>")
    if claim.metric:
        details.append(f"<span style='color: #40916C;'>📊 Metric: {claim.metric}</span>")
    details_text = " &nbsp;•&nbsp; ".join(details) if details else ""

    st.markdown(f"""
    <div style="
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        padding: 1.25rem;
        border-radius: 12px;
        border-left: 4px solid {color};
        box-shadow: 0 2px 12px rgba(27, 67, 50, 0.08);
        margin-bottom: 0.75rem;
        transition: all 0.3s ease;
        border: 1px solid rgba(183, 228, 199, 0.5);
    ">
        <div style="
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.75rem;
        ">
            <span style="font-size: 1.2rem;">{icon}</span>
            <strong style="
                color: {color};
                font-family: 'Inter', sans-serif;
                font-size: 0.85rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            ">{claim.category}</strong>
        </div>
        <p style="
            margin: 0 0 0.75rem 0;
            color: #1B4332;
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            font-size: 0.95rem;
        ">{claim.statement}</p>
        <div style="
            font-size: 0.8rem;
            color: #6B7B6E;
            font-family: 'Inter', sans-serif;
        ">{details_text}</div>
    </div>
    """, unsafe_allow_html=True)


def render_risk_badge(risk_score: int):
    """Render a colored badge showing risk level with organic styling."""
    if risk_score < 25:
        color = "#2D6A4F"
        bg_color = "rgba(45, 106, 79, 0.15)"
        label = "Low Risk"
        icon = "🌿"
        description = "Claims appear well-substantiated"
    elif risk_score < 50:
        color = "#40916C"
        bg_color = "rgba(64, 145, 108, 0.15)"
        label = "Moderate Risk"
        icon = "🌱"
        description = "Some claims need verification"
    elif risk_score < 75:
        color = "#E67E22"
        bg_color = "rgba(230, 126, 34, 0.15)"
        label = "High Risk"
        icon = "⚠️"
        description = "Multiple concerning claims detected"
    else:
        color = "#C0392B"
        bg_color = "rgba(192, 57, 43, 0.15)"
        label = "Critical Risk"
        icon = "🚨"
        description = "Significant greenwashing indicators"

    st.markdown(f"""
    <div style="
        background: {bg_color};
        border: 2px solid {color};
        border-radius: 16px;
        padding: 1rem 1.25rem;
        display: inline-block;
    ">
        <div style="
            display: flex;
            align-items: center;
            gap: 0.75rem;
        ">
            <span style="font-size: 1.5rem;">{icon}</span>
            <div>
                <div style="
                    color: {color};
                    font-weight: 700;
                    font-size: 1.1rem;
                    font-family: 'Inter', sans-serif;
                ">{label}</div>
                <div style="
                    color: {color};
                    font-size: 0.85rem;
                    opacity: 0.9;
                    font-family: 'Inter', sans-serif;
                ">Score: {risk_score}/100</div>
            </div>
        </div>
        <p style="
            margin: 0.75rem 0 0 0;
            color: #1B4332;
            font-size: 0.85rem;
            font-family: 'Inter', sans-serif;
        ">{description}</p>
    </div>
    """, unsafe_allow_html=True)
