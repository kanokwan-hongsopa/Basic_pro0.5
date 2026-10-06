"""
Tab 1 Component: Casualties & Vehicle Impact Analytics
Accident trends, vehicle distribution treemap/bar, casualty timeline tracking, and financial loss boxplots.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.style_constants import (
    COLOR_CARD_BG, COLOR_TEXT_PRIMARY, COLOR_TEXT_MUTED,
    COLOR_CRITICAL_RED, COLOR_WARNING_AMBER, COLOR_SAFE_GREEN,
    COLOR_CYAN_ACCENT, apply_dark_theme, VEHICLE_COLOR_MAP
)

def render_tab_casualties(df):
    """Generates the layout and graphs for Tab 1."""
    if df.empty:
        return html.Div(
            [html.P("No data available for current selection.", className="text-warning p-4")],
            style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "8px"}
        )

    # 1. Yearly Trend Graph (Multi-line / Area)
    yearly = df.groupby("year").agg({
        "incident_id": "count",
        "fatalities": "sum",
        "serious_injuries": "sum",
        "slight_injuries": "sum"
    }).reset_index()
    yearly["total_injuries"] = yearly["serious_injuries"] + yearly["slight_injuries"]

    fig_trends = go.Figure()
    fig_trends.add_trace(go.Scatter(
        x=yearly["year"], y=yearly["incident_id"],
        mode="lines+markers", name="Total Incidents (อุบัติเหตุ)",
        line=dict(color=COLOR_CYAN_ACCENT, width=3),
        marker=dict(size=7)
    ))
    fig_trends.add_trace(go.Scatter(
        x=yearly["year"], y=yearly["total_injuries"],
        mode="lines+markers", name="Injuries (บาดเจ็บ)",
        line=dict(color=COLOR_WARNING_AMBER, width=2.5, dash="dot"),
        marker=dict(size=6)
    ))
    fig_trends.add_trace(go.Scatter(
        x=yearly["year"], y=yearly["fatalities"],
        mode="lines+markers", name="Fatalities (เสียชีวิต)",
        line=dict(color=COLOR_CRITICAL_RED, width=3),
        marker=dict(size=8, symbol="diamond")
    ))
    apply_dark_theme(fig_trends, "📈 Accident & Casualty Trends by Year (สถิติและแนวโน้มรายปี 2020-2026)")
    fig_trends.update_xaxes(dtick=1)

    # 2. Vehicle Types Involved (Treemap or Horizontal Bar)
    veh_summary = df.groupby("vehicle_type").agg({
        "incident_id": "count",
        "fatalities": "sum",
        "total_casualties": "sum"
    }).reset_index().rename(columns={"incident_id": "incidents"}).sort_values(by="incidents", ascending=True)

    fig_vehicles = go.Figure()
    colors = [VEHICLE_COLOR_MAP.get(v, "#38BDF8") for v in veh_summary["vehicle_type"]]
    fig_vehicles.add_trace(go.Bar(
        y=veh_summary["vehicle_type"],
        x=veh_summary["incidents"],
        orientation="h",
        name="Incidents",
        marker_color=colors,
        text=veh_summary["incidents"].apply(lambda x: f"{x:,}"),
        textposition="outside"
    ))
    apply_dark_theme(fig_vehicles, "🛵 Vehicle Types Involved in Accidents (ยานพาหนะที่ประสบเหตุ)")
    fig_vehicles.update_xaxes(title="Incident Count (ครั้ง)")

    # 3. Casualty Timeline Tracking / Outcome Breakdown by Period
    period_group = df.groupby("period_type").agg({
        "slight_injuries": "sum",
        "serious_injuries": "sum",
        "fatalities": "sum"
    }).reset_index()

    fig_outcomes = go.Figure()
    fig_outcomes.add_trace(go.Bar(
        x=period_group["period_type"], y=period_group["slight_injuries"],
        name="Slight Injury (บาดเจ็บเล็กน้อย)", marker_color=COLOR_SAFE_GREEN
    ))
    fig_outcomes.add_trace(go.Bar(
        x=period_group["period_type"], y=period_group["serious_injuries"],
        name="Serious Injury (บาดเจ็บสาหัส)", marker_color=COLOR_WARNING_AMBER
    ))
    fig_outcomes.add_trace(go.Bar(
        x=period_group["period_type"], y=period_group["fatalities"],
        name="Fatality (เสียชีวิต)", marker_color=COLOR_CRITICAL_RED
    ))
    fig_outcomes.update_layout(barmode="stack")
    apply_dark_theme(fig_outcomes, "⏱️ Casualty Outcomes by Period & Festival (จำแนกความรุนแรงตามช่วงเทศกาล)")

    # 4. Financial & Economic Loss Impact (Box Plot by Vehicle)
    fig_cost = px.box(
        df,
        x="vehicle_type",
        y="estimated_economic_loss_thb",
        color="vehicle_type",
        color_discrete_map=VEHICLE_COLOR_MAP,
        points=False
    )
    apply_dark_theme(fig_cost, "💰 Economic Loss Distribution by Vehicle (มูลค่าความเสียหายทางเศรษฐกิจ ต่อเคส)")
    fig_cost.update_yaxes(title="Economic Loss (THB)", tickformat=",.0f")
    fig_cost.update_xaxes(title="Vehicle Type")

    return html.Div([
        # Row 1: Trends + Vehicles
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig_trends, id="graph-trends", config={"displayModeBar": True})
                    ])
                ], className="border-0 shadow-sm mb-4", style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "10px"})
            ], md=7),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig_vehicles, id="graph-vehicles", config={"displayModeBar": True})
                    ])
                ], className="border-0 shadow-sm mb-4", style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "10px"})
            ], md=5),
        ]),

        # Row 2: Casualty Timeline + Financial Impact
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig_outcomes, id="graph-outcomes", config={"displayModeBar": True})
                    ])
                ], className="border-0 shadow-sm mb-4", style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "10px"})
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig_cost, id="graph-cost", config={"displayModeBar": True})
                    ])
                ], className="border-0 shadow-sm mb-4", style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "10px"})
            ], md=6),
        ])
    ])
