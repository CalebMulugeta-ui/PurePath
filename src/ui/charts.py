import plotly.graph_objects as go
import streamlit as st


# Forest Green Color Palette for Risk Levels
def get_risk_color(score: int) -> str:
    """Get color based on risk score using forest-inspired palette."""
    if score < 25:
        return "#2D6A4F"  # Forest Primary - Trustworthy
    elif score < 50:
        return "#40916C"  # Forest Medium - Low Risk
    elif score < 75:
        return "#E67E22"  # Warm Orange - Moderate Risk
    else:
        return "#C0392B"  # Deep Red - Critical Risk


def render_truth_meter(risk_score: int):
    """
    Render a gauge chart showing greenwashing risk score
    with nature-inspired organic styling.

    Args:
        risk_score: Value from 0 (trustworthy) to 100 (high risk)
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={
            'text': "<b>Greenwashing Risk</b>",
            'font': {
                'size': 18,
                'color': '#1B4332',
                'family': 'Inter, Arial, sans-serif'
            }
        },
        number={
            'font': {
                'size': 42,
                'color': get_risk_color(risk_score),
                'family': 'Inter, Arial, sans-serif'
            },
            'suffix': '<span style="font-size: 18px; color: #6B7B6E;">/100</span>'
        },
        gauge={
            'axis': {
                'range': [0, 100],
                'tickwidth': 2,
                'tickcolor': "#B7E4C7",
                'tickvals': [0, 25, 50, 75, 100],
                'ticktext': ['Safe', 'Low', 'Moderate', 'High', 'Critical'],
                'tickfont': {
                    'size': 11,
                    'color': '#6B7B6E',
                    'family': 'Inter, Arial, sans-serif'
                }
            },
            'bar': {
                'color': get_risk_color(risk_score),
                'thickness': 0.75
            },
            'bgcolor': "#F8FAF7",
            'borderwidth': 3,
            'bordercolor': "#B7E4C7",
            'steps': [
                {'range': [0, 25], 'color': 'rgba(45, 106, 79, 0.2)'},     # Forest green tint
                {'range': [25, 50], 'color': 'rgba(64, 145, 108, 0.2)'},   # Medium green tint
                {'range': [50, 75], 'color': 'rgba(230, 126, 34, 0.2)'},   # Orange tint
                {'range': [75, 100], 'color': 'rgba(192, 57, 43, 0.2)'}    # Red tint
            ],
            'threshold': {
                'line': {'color': "#1B4332", 'width': 3},
                'thickness': 0.8,
                'value': risk_score
            }
        }
    ))

    fig.update_layout(
        height=280,
        margin=dict(l=30, r=30, t=60, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={
            'color': "#1B4332",
            'family': "Inter, Arial, sans-serif"
        }
    )

    # Add custom annotation for context
    risk_label = "Trustworthy" if risk_score < 25 else \
                 "Low Risk" if risk_score < 50 else \
                 "Moderate Risk" if risk_score < 75 else "Critical Risk"

    fig.add_annotation(
        x=0.5,
        y=-0.15,
        text=f"<b>{risk_label}</b>",
        showarrow=False,
        font={
            'size': 14,
            'color': get_risk_color(risk_score),
            'family': 'Inter, Arial, sans-serif'
        },
        xanchor='center'
    )

    st.plotly_chart(fig, use_container_width=True)
