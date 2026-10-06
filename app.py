"""
Thailand Road Accident Analytics & Safety Dashboard
Main Application File (Python Dash + Plotly + Bootstrap)
"""

import os
import io
import json
import pandas as pd
import dash
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc

from utils.data_loader import (
    load_accident_data, filter_accident_data, calculate_kpis,
    parse_uploaded_file, run_policy_simulation
)
from utils.style_constants import (
    COLOR_BG_DARK, COLOR_CARD_BG, COLOR_CARD_BORDER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_MUTED, COLOR_CRITICAL_RED,
    COLOR_WARNING_AMBER, COLOR_SAFE_GREEN, COLOR_CYAN_ACCENT
)
from components.tab_casualties import render_tab_casualties
from components.tab_risk_zones import render_tab_risk_zones
from components.tab_risk_mismatch import render_tab_risk_mismatch

# Initialize Dash application with Darkly Bootstrap Theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True,
    title="Thailand Road Accident Analytics & Risk Dashboard"
)
server = app.server

# Load default dataset
raw_df = load_accident_data()

# Global Options
YEAR_OPTIONS = [{"label": "All Years (2020-2026)", "value": "All"}] + [
    {"label": str(y), "value": y} for y in sorted(raw_df["year"].unique())
]
REGION_OPTIONS = [{"label": "All Regions (ทุกภูมิภาค)", "value": "All"}] + [
    {"label": r, "value": r} for r in sorted(raw_df["region"].unique())
]
VEHICLE_OPTIONS = [{"label": "All Vehicle Types (ทุกยานพาหนะ)", "value": "All"}] + [
    {"label": v, "value": v} for v in sorted(raw_df["vehicle_type"].unique())
]
PERIOD_OPTIONS = [{"label": "All Periods (ทุกช่วงเวลา)", "value": "All"}] + [
    {"label": p, "value": p} for p in sorted(raw_df["period_type"].unique())
]

# Helper for KPI Cards
def create_kpi_card(title, value_id, subtext_id, border_color="#38BDF8", icon="📊"):
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Span(icon, style={"fontSize": "22px", "marginRight": "8px"}),
                html.Span(title, className="text-uppercase small fw-bold", style={"color": COLOR_TEXT_MUTED})
            ], className="d-flex align-items-center mb-1"),
            html.H3("...", id=value_id, className="fw-bold mb-1", style={"color": COLOR_TEXT_PRIMARY}),
            html.Small("...", id=subtext_id, className="text-muted")
        ], className="p-3")
    ], style={
        "backgroundColor": COLOR_CARD_BG,
        "border": f"1px solid {COLOR_CARD_BORDER}",
        "borderLeft": f"4px solid {border_color}",
        "borderRadius": "8px"
    }, className="shadow-sm h-100")

# App Layout
app.layout = dbc.Container([
    # Client-side In-Memory Store
    dcc.Store(id="stored-raw-data", data=raw_df.to_json(orient="split", date_format="iso")),
    dcc.Download(id="download-dataframe-csv"),

    # Header Navbar
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H2([
                    html.Span("🚗 ", style={"fontSize": "1.4em"}),
                    "Thailand Road Accident Analytics & Safety Dashboard"
                ], className="fw-bold text-white mb-1"),
                html.P(
                    "ระบบวิเคราะห์สถิติอุบัติเหตุทางถนน พิกัดจุดเสี่ยงอันตราย และแบบจำลองมาตรการความปลอดภัย",
                    className="text-info mb-0"
                )
            ], className="py-3")
        ], md=8),
        dbc.Col([
            html.Div([
                dcc.Upload(
                    id="upload-data",
                    children=html.Button(
                        "📁 Upload CSV / Excel",
                        className="btn btn-outline-info btn-sm me-2 shadow-sm"
                    ),
                    multiple=False
                ),
                html.Button(
                    "📥 Export Filtered CSV",
                    id="btn-export-csv",
                    className="btn btn-outline-success btn-sm shadow-sm"
                )
            ], className="py-3 d-flex justify-content-md-end align-items-center")
        ], md=4)
    ], className="border-bottom border-secondary mb-3 align-items-center"),

    # Upload Notification Alert
    html.Div(id="upload-status-alert"),

    # Global Filters Bar
    dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("📅 Year Filter:", className="small text-muted fw-bold"),
                    dcc.Dropdown(id="filter-year", options=YEAR_OPTIONS, value="All", clearable=False,
                                 className="dash-bootstrap-dark")
                ], xs=12, sm=6, md=3, className="mb-2"),
                dbc.Col([
                    html.Label("📍 Region Filter:", className="small text-muted fw-bold"),
                    dcc.Dropdown(id="filter-region", options=REGION_OPTIONS, value="All", clearable=False,
                                 className="dash-bootstrap-dark")
                ], xs=12, sm=6, md=3, className="mb-2"),
                dbc.Col([
                    html.Label("🛵 Vehicle Filter:", className="small text-muted fw-bold"),
                    dcc.Dropdown(id="filter-vehicle", options=VEHICLE_OPTIONS, value="All", clearable=False,
                                 className="dash-bootstrap-dark")
                ], xs=12, sm=6, md=3, className="mb-2"),
                dbc.Col([
                    html.Label("🎉 Period / Festival:", className="small text-muted fw-bold"),
                    dcc.Dropdown(id="filter-period", options=PERIOD_OPTIONS, value="All", clearable=False,
                                 className="dash-bootstrap-dark")
                ], xs=12, sm=6, md=3, className="mb-2"),
            ], className="g-2")
        ], className="p-2")
    ], style={"backgroundColor": COLOR_CARD_BG, "border": f"1px solid {COLOR_CARD_BORDER}", "borderRadius": "8px"}, className="mb-3"),

    # Executive KPI Summary Cards
    dbc.Row([
        dbc.Col([
            create_kpi_card("Total Incidents", "kpi-incidents", "kpi-incidents-sub", "#38BDF8", "💥")
        ], xs=6, sm=4, md=2, className="mb-3"),
        dbc.Col([
            create_kpi_card("Total Fatalities", "kpi-fatalities", "kpi-fatalities-sub", COLOR_CRITICAL_RED, "⚰️")
        ], xs=6, sm=4, md=2, className="mb-3"),
        dbc.Col([
            create_kpi_card("Total Injuries", "kpi-injuries", "kpi-injuries-sub", COLOR_WARNING_AMBER, "🩹")
        ], xs=6, sm=4, md=2, className="mb-3"),
        dbc.Col([
            create_kpi_card("Fatality Rate", "kpi-fatality-rate", "kpi-fatality-rate-sub", "#F43F5E", "⚠️")
        ], xs=6, sm=4, md=2, className="mb-3"),
        dbc.Col([
            create_kpi_card("High Risk Blackspots", "kpi-blackspots", "kpi-blackspots-sub", "#FB923C", "📍")
        ], xs=6, sm=4, md=2, className="mb-3"),
        dbc.Col([
            create_kpi_card("Economic Loss", "kpi-loss", "kpi-loss-sub", COLOR_SAFE_GREEN, "💸")
        ], xs=6, sm=4, md=2, className="mb-3"),
    ], className="g-2 mb-2"),

    # Main Dashboard Tabs
    dbc.Tabs([
        dbc.Tab(
            label="📊 Tab 1: Casualties & Vehicle Impact",
            tab_id="tab-1",
            active_tab_class_name="fw-bold text-info border-info",
            label_class_name="text-light"
        ),
        dbc.Tab(
            label="🗺️ Tab 2: Risk Zones & Causes",
            tab_id="tab-2",
            active_tab_class_name="fw-bold text-info border-info",
            label_class_name="text-light"
        ),
        dbc.Tab(
            label="🔬 Tab 3: Risk Mismatch & Simulation",
            tab_id="tab-3",
            active_tab_class_name="fw-bold text-info border-info",
            label_class_name="text-light"
        ),
    ], id="main-tabs", active_tab="tab-1", className="mb-3 custom-tabs"),

    # Dynamic Tab Content Area
    dcc.Loading(
        id="loading-content",
        type="default",
        children=html.Div(id="tab-content-area")
    ),

    # Footer
    html.Footer([
        html.Div([
            html.Span("Open Government Data Attribution: Department of Highways (DOH) • ThaiRSC • RTP • DLT", className="text-muted small"),
            html.Span(" | Built for Thailand Road Safety & Analytics Intelligence", className="text-muted small")
        ], className="text-center py-4 border-top border-secondary mt-4")
    ])

], fluid=True, style={"backgroundColor": COLOR_BG_DARK, "minHeight": "100vh", "padding": "20px 24px"})


# Callback 1: Handle File Upload
@app.callback(
    Output("stored-raw-data", "data"),
    Output("upload-status-alert", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("stored-raw-data", "data"),
    prevent_initial_call=True
)
def handle_file_upload(contents, filename, current_data_json):
    if not contents:
        return current_data_json, dash.no_update
    new_df, err = parse_uploaded_file(contents, filename)
    if err:
        alert = dbc.Alert(f"⚠️ {err}", color="danger", dismissable=True, className="mt-2")
        return current_data_json, alert
    alert = dbc.Alert(f"✅ Successfully loaded {len(new_df):,} records from '{filename}'!", color="success", dismissable=True, className="mt-2")
    return new_df.to_json(orient="split", date_format="iso"), alert


# Callback 2: Update Filtered Data & KPIs & Tab Views
@app.callback(
    Output("kpi-incidents", "children"),
    Output("kpi-incidents-sub", "children"),
    Output("kpi-fatalities", "children"),
    Output("kpi-fatalities-sub", "children"),
    Output("kpi-injuries", "children"),
    Output("kpi-injuries-sub", "children"),
    Output("kpi-fatality-rate", "children"),
    Output("kpi-fatality-rate-sub", "children"),
    Output("kpi-blackspots", "children"),
    Output("kpi-blackspots-sub", "children"),
    Output("kpi-loss", "children"),
    Output("kpi-loss-sub", "children"),
    Output("tab-content-area", "children"),
    Input("filter-year", "value"),
    Input("filter-region", "value"),
    Input("filter-vehicle", "value"),
    Input("filter-period", "value"),
    Input("main-tabs", "active_tab"),
    Input("stored-raw-data", "data")
)
def update_dashboard(year, region, vehicle, period, active_tab, data_json):
    import io
    df = pd.read_json(io.StringIO(data_json), orient="split")
    filtered = filter_accident_data(
        df,
        years=[year] if year != "All" else None,
        regions=[region] if region != "All" else None,
        vehicle_types=[vehicle] if vehicle != "All" else None,
        period_types=[period] if period != "All" else None
    )

    kpis = calculate_kpis(filtered)

    incidents_val = f"{kpis['total_incidents']:,}"
    incidents_sub = "Recorded accidents"

    fatalities_val = f"{kpis['total_fatalities']:,}"
    fatalities_sub = f"{kpis['fatality_rate']}% of incidents"

    injuries_val = f"{kpis['total_serious'] + kpis['total_slight']:,}"
    injuries_sub = f"Serious: {kpis['total_serious']:,}"

    rate_val = f"{kpis['fatality_rate']}%"
    rate_sub = "Fatalities / Incidents"

    blackspots_val = f"{kpis['high_risk_incidents']:,}"
    blackspots_sub = f"{kpis['high_risk_share']}% Critical Zones"

    loss_val = f"฿{kpis['total_loss_mb']:,.1f}M"
    loss_sub = "Est. Economic Damage"

    # Render appropriate Tab
    if active_tab == "tab-1":
        content = render_tab_casualties(filtered)
    elif active_tab == "tab-2":
        content = render_tab_risk_zones(filtered)
    elif active_tab == "tab-3":
        content = render_tab_risk_mismatch(filtered)
    else:
        content = html.Div("Tab not recognized.")

    return (
        incidents_val, incidents_sub,
        fatalities_val, fatalities_sub,
        injuries_val, injuries_sub,
        rate_val, rate_sub,
        blackspots_val, blackspots_sub,
        loss_val, loss_sub,
        content
    )


# Callback 3: Simulation Engine Calculations
@app.callback(
    Output("simulation-results-container", "children"),
    Input("sim-slider-speed", "value"),
    Input("sim-slider-helmet", "value"),
    Input("sim-slider-drunk", "value"),
    State("stored-raw-data", "data"),
    prevent_initial_call=False
)
def update_simulation_outcomes(speed_val, helmet_val, drunk_val, data_json):
    if not data_json:
        return html.Div()
    df = pd.read_json(io.StringIO(data_json), orient="split")
    res = run_policy_simulation(df, speed_reduction_pct=speed_val or 0,
                                helmet_boost_pct=helmet_val or 0,
                                drunk_reduction_pct=drunk_val or 0)

    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Lives Saved (ประมาณการผู้เสียชีวิตที่ลดลง)", className="text-muted small"),
                    html.H4(f"-{res['fatalities_saved']} Lives", className="text-success fw-bold"),
                    html.Small(f"From {res['baseline_fatalities']} down to {res['simulated_fatalities']}", className="text-light")
                ])
            ], style={"backgroundColor": "#132338", "border": "1px solid #10B981", "borderRadius": "8px"})
        ], md=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Serious Injuries Prevented (ลดการบาดเจ็บสาหัส)", className="text-muted small"),
                    html.H4(f"-{res['serious_prevented']} Cases", className="text-warning fw-bold"),
                    html.Small(f"From {res['baseline_serious']} down to {res['simulated_serious']}", className="text-light")
                ])
            ], style={"backgroundColor": "#132338", "border": "1px solid #F59E0B", "borderRadius": "8px"})
        ], md=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Economic Savings (มูลค่าประหยัดได้ทางเศรษฐกิจ)", className="text-muted small"),
                    html.H4(f"+฿{res['economic_savings_mb']:,.1f} M THB", className="text-info fw-bold"),
                    html.Small("Based on DLT & WHO actuarial valuation", className="text-light")
                ])
            ], style={"backgroundColor": "#132338", "border": "1px solid #38BDF8", "borderRadius": "8px"})
        ], md=4),
    ], className="g-2")


# Callback 4: Export CSV
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn-export-csv", "n_clicks"),
    State("filter-year", "value"),
    State("filter-region", "value"),
    State("filter-vehicle", "value"),
    State("filter-period", "value"),
    State("stored-raw-data", "data"),
    prevent_initial_call=True
)
def export_filtered_csv(n_clicks, year, region, vehicle, period, data_json):
    if not n_clicks:
        return dash.no_update
    df = pd.read_json(io.StringIO(data_json), orient="split")
    filtered = filter_accident_data(
        df,
        years=[year] if year != "All" else None,
        regions=[region] if region != "All" else None,
        vehicle_types=[vehicle] if vehicle != "All" else None,
        period_types=[period] if period != "All" else None
    )
    return dcc.send_data_frame(filtered.to_csv, "thailand_road_accidents_filtered.csv", index=False)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
