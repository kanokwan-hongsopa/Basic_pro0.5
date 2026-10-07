"""
Tab 1 Component: Casualties & Vehicle Impact Analytics
Accident trends, vehicle distribution treemap/bar, casualty timeline tracking, and financial loss boxplots.
Visualizations use REAL observed government open data.
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
    """Generates the layout and graphs for Tab 1 with column validation."""
    if df.empty:
        return html.Div(
            [html.P("No data available for current selection.", className="text-warning p-4")],
            style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "8px"}
        )

    # 1. Yearly Trend Graph (Multi-line)
    if "year" in df.columns and "fatalities" in df.columns:
        yearly = df.groupby("year").agg({
            "incident_id": "count",
            "fatalities": "sum",
            "serious_injuries": "sum" if "serious_injuries" in df.columns else ("injuries" if "injuries" in df.columns else "fatalities"),
            "slight_injuries": "sum" if "slight_injuries" in df.columns else "fatalities"
        }).reset_index()
        yearly["total_injuries"] = yearly.get("serious_injuries", 0) + yearly.get("slight_injuries", 0)

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
        apply_dark_theme(fig_trends, "📈 Accident & Casualty Trends by Year (สถิติจริง 2020-2026)")
        fig_trends.update_xaxes(dtick=1)
        trends_comp = dcc.Graph(figure=fig_trends, id="graph-trends", config={"displayModeBar": True})
    else:
        trends_comp = html.Div("Official source data does not contain the fields required for this visualization (year/fatalities).", className="alert alert-warning py-2")

    # 2. Vehicle Types Involved (Horizontal Bar)
    if "vehicle_type" in df.columns:
        veh_summary = df.groupby("vehicle_type").agg({
            "incident_id": "count",
            "fatalities": "sum" if "fatalities" in df.columns else "count"
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
        apply_dark_theme(fig_vehicles, "🛵 Vehicle Types Involved in Accidents (ยานพาหนะคันเกิดเหตุ)")
        fig_vehicles.update_xaxes(title="Incident Count (ครั้ง)")
        veh_comp = dcc.Graph(figure=fig_vehicles, id="graph-vehicles", config={"displayModeBar": True})
    else:
        veh_comp = html.Div("Official source data does not contain the fields required for this visualization (vehicle_type).", className="alert alert-warning py-2")

    # 3. Casualty Timeline Tracking / Outcome Breakdown by Period
    if "period_type" in df.columns and "fatalities" in df.columns:
        period_group = df.groupby("period_type").agg({
            "slight_injuries": "sum" if "slight_injuries" in df.columns else "count",
            "serious_injuries": "sum" if "serious_injuries" in df.columns else "count",
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
        apply_dark_theme(fig_outcomes, "⏱️ Casualty Outcomes by Period & Festival (จำแนกตามช่วงเทศกาล)")
        outcomes_comp = dcc.Graph(figure=fig_outcomes, id="graph-outcomes", config={"displayModeBar": True})
    else:
        outcomes_comp = html.Div("Official source data does not contain the fields required for this visualization (period_type).", className="alert alert-warning py-2")

    # 4. Financial & Economic Loss Impact (Box Plot by Vehicle)
    loss_col = "economic_loss" if "economic_loss" in df.columns else ("estimated_economic_loss_thb" if "estimated_economic_loss_thb" in df.columns else None)
    if loss_col and "vehicle_type" in df.columns:
        fig_cost = px.box(
            df[df[loss_col] > 0],
            x="vehicle_type",
            y=loss_col,
            color="vehicle_type",
            color_discrete_map=VEHICLE_COLOR_MAP,
            points=False
        )
        apply_dark_theme(fig_cost, "💰 Estimated Economic Loss by Vehicle (คำนวณตามเกณฑ์ประเมิน DOH/TDRI)")
        fig_cost.update_yaxes(title="Economic Loss (THB)", tickformat=",.0f")
        fig_cost.update_xaxes(title="Vehicle Type")
        cost_comp = html.Div([
            dcc.Graph(figure=fig_cost, id="graph-cost", config={"displayModeBar": True}),
            html.Small("ℹ️ หมายเหตุ: มูลค่าความเสียหายคำนวณตามเกณฑ์ความสูญเสียของกรมทางหลวง (ผู้เสียชีวิต 5M, สาหัส 800k, เล็กน้อย 100k THB)", className="text-muted")
        ])
    else:
        cost_comp = html.Div("Official source data does not contain the fields required for this visualization.", className="alert alert-warning py-2")

    return html.Div([
        # Row 1: Trends + Vehicles
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([trends_comp])
                ], className="border-0 shadow-sm mb-4", style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "10px"})
            ], md=7),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([veh_comp])
                ], className="border-0 shadow-sm mb-4", style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "10px"})
            ], md=5),
        ]),

        # Row 2: Casualty Timeline + Financial Impact
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([outcomes_comp])
                ], className="border-0 shadow-sm mb-4", style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "10px"})
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([cost_comp])
                ], className="border-0 shadow-sm mb-4", style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "10px"})
            ], md=6),
        ])
    ])
