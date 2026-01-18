import plotly.graph_objects as go
import streamlit as st


def get_risk_color(score: int) -> str:
    """Get color based on risk score."""
    if score < 25:
        return "#4CAF50"  # Green
    elif score < 50:
        return "#FFC107"  # Yellow
    elif score < 75:
        return "#FF9800"  # Orange
    else:
        return "#f44336"  # Red


def render_truth_meter(risk_score: int):
    """
    Render a gauge chart showing greenwashing risk score.

    Args:
        risk_score: Value from 0 (trustworthy) to 100 (high risk)
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Greenwashing Risk", 'font': {'size': 20}},
        gauge={
            'axis': {
                'range': [0, 100],
                'tickwidth': 1,
                'tickcolor': "darkgray",
                'tickvals': [0, 25, 50, 75, 100],
                'ticktext': ['Trustworthy', 'Low', 'Moderate', 'High', 'Critical']
            },
            'bar': {'color': get_risk_color(risk_score)},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 25], 'color': '#c8e6c9'},    # Light green
                {'range': [25, 50], 'color': '#fff9c4'},   # Light yellow
                {'range': [50, 75], 'color': '#ffe0b2'},   # Light orange
                {'range': [75, 100], 'color': '#ffcdd2'}   # Light red
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': risk_score
            }
        }
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "darkgray", 'family': "Arial"}
    )

    st.plotly_chart(fig, use_container_width=True)
