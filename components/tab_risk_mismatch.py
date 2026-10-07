"""
Tab 3 Component: Risk Mismatch & Gap Simulation Engine
Validates official government data availability.
Labels simulation outputs strictly as Scenario Simulation / Estimated Result.
"""

from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.style_constants import (
    COLOR_CARD_BG, COLOR_CRITICAL_RED, COLOR_WARNING_AMBER, COLOR_SAFE_GREEN,
    COLOR_CYAN_ACCENT, COLOR_PURPLE_ACCENT, apply_dark_theme
)

def render_tab_risk_mismatch(df):
    """Generates the layout and graphs for Tab 3 with official data validation."""
    if df.empty:
        return html.Div(
            [html.P("No data available for current selection.", className="text-warning p-4")],
            style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "8px"}
        )

    # 1. Safety Capability vs Risk Exposure Matrix (Validate official columns)
    has_scores = ("road_risk_score" in df.columns and "driver_behavior_risk_score" in df.columns)
    if has_scores:
        sample_df = df.head(500)
        fig_matrix = go.Figure()
        fig_matrix.add_trace(go.Scatter(
            x=sample_df["road_risk_score"],
            y=sample_df["driver_behavior_risk_score"],
            mode="markers",
            marker=dict(
                size=sample_df["total_casualties"] * 3 + 5,
                color=sample_df["fatalities"],
                colorscale=[[0, "#38BDF8"], [0.5, "#F59E0B"], [1, "#FF4136"]],
                showscale=True,
                colorbar=dict(title="Fatalities", tickfont=dict(color="#94A3B8"))
            ),
            text=[f"Province: {p}<br>Cause: {c}<br>Road: {r}" for p, c, r in zip(
                sample_df["province"], sample_df["accident_cause"], sample_df["road_hierarchy"]
            )],
            hoverinfo="text"
        ))
        fig_matrix.add_vline(x=50, line_width=1.5, line_dash="dash", line_color="#64748B")
        fig_matrix.add_hline(y=50, line_width=1.5, line_dash="dash", line_color="#64748B")
        apply_dark_theme(fig_matrix, "🎯 Risk Mismatch Matrix (Infrastructure vs Behavior)")
        matrix_component = dcc.Graph(figure=fig_matrix, id="graph-mismatch-matrix", config={"displayModeBar": True})
    else:
        # Official source data does not contain arbitrary risk scores
        prov_agg = df.groupby("province").agg({
            "incident_id": "count",
            "fatalities": "sum"
        }).reset_index()
        prov_agg["fatality_rate"] = (prov_agg["fatalities"] / prov_agg["incident_id"] * 100).round(2)
        prov_top = prov_agg.sort_values(by="incident_id", ascending=False).head(20)

        fig_matrix = px.scatter(
            prov_top,
            x="incident_id",
            y="fatality_rate",
            size="fatalities",
            color="fatalities",
            text="province",
            color_continuous_scale=[[0, "#38BDF8"], [0.5, "#F59E0B"], [1, "#FF4136"]],
            labels={"incident_id": "Incidents", "fatality_rate": "Fatality Rate (%)"}
        )
        fig_matrix.update_traces(textposition="top center")
        apply_dark_theme(fig_matrix, "🎯 Observed Risk Exposure: Incident Frequency vs Fatality Rate")
        matrix_component = html.Div([
            html.Div(
                "ℹ️ Official source data does not contain the fields required for this visualization (arbitrary 0-100 risk scores). Displaying observed provincial risk distribution instead.",
                className="alert alert-info py-2 small mb-2"
            ),
            dcc.Graph(figure=fig_matrix, id="graph-mismatch-matrix", config={"displayModeBar": True})
        ])

    # 2. Safety Equipment Compliance (Validate official columns)
    has_equip = ("safety_equipment_used" in df.columns)
    if has_equip:
        region_equip = df.groupby("region").agg({
            "safety_equipment_used": lambda x: (x == "Yes").mean() * 100,
            "fatalities": lambda x: (x > 0).mean() * 100,
            "serious_injuries": lambda x: (x > 0).mean() * 100,
        }).reset_index()

        fig_radar = go.Figure()
        for _, row in region_equip.iterrows():
            fig_radar.add_trace(go.Scatterpolar(
                r=[row["safety_equipment_used"], 100 - row["fatalities"], 100 - row["serious_injuries"]],
                theta=["Equipment Usage %", "Survival Rate %", "Injury Prevention %"],
                fill="toself",
                name=row["region"]
            ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], color="#94A3B8", gridcolor="#334155"),
                angularaxis=dict(color="#F8FAFC", gridcolor="#334155"),
                bgcolor="#1E293B"
            ),
            paper_bgcolor=COLOR_CARD_BG,
            font=dict(color="#94A3B8")
        )
        apply_dark_theme(fig_radar, "🛡️ Safety Equipment Compliance vs Resilience Radar")
        radar_component = dcc.Graph(figure=fig_radar, id="graph-safety-radar", config={"displayModeBar": True})
    else:
        # Official source does not record individual equipment usage
        reg_agg = df.groupby("region").agg({
            "fatalities": "sum",
            "serious_injuries": "sum"
        }).reset_index()

        fig_reg = go.Figure()
        fig_reg.add_trace(go.Bar(name="Fatalities", x=reg_agg["region"], y=reg_agg["fatalities"], marker_color=COLOR_CRITICAL_RED))
        fig_reg.add_trace(go.Bar(name="Serious Injuries", x=reg_agg["region"], y=reg_agg["serious_injuries"], marker_color=COLOR_WARNING_AMBER))
        fig_reg.update_layout(barmode="group")
        apply_dark_theme(fig_reg, "🛡️ Observed Casualty Severity by Region")
        radar_component = html.Div([
            html.Div(
                "ℹ️ Official source data does not contain the fields required for this visualization (safety equipment usage per record). Displaying observed regional casualty breakdown instead.",
                className="alert alert-info py-2 small mb-2"
            ),
            dcc.Graph(figure=fig_reg, id="graph-safety-radar", config={"displayModeBar": True})
        ])

    # 3. Editable Simulation Table Sample (Top Records from Real Data)
    sim_table_cols = [
        "incident_id", "province", "road_hierarchy", "accident_cause",
        "vehicle_type", "fatalities", "serious_injuries", "estimated_economic_loss_thb"
    ]
    cols_present = [c for c in sim_table_cols if c in df.columns]
    sim_table_data = df.head(15)[cols_present].copy()

    return html.Div([
        # Row 1: Quadrants Matrix + Radar Gap
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([matrix_component])
                ], className="border-0 shadow-sm mb-4", style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "10px"})
            ], md=7),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([radar_component])
                ], className="border-0 shadow-sm mb-4", style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "10px"})
            ], md=5),
        ]),

        # Row 2: Policy Simulation Controls & Real-Time Projections
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("🧪 Scenario Simulation / Estimated Result (แบบจำลองสถานการณ์ / ผลลัพธ์ประมาณการ)", className="text-warning mb-0 fw-bold")
                    ], style={"backgroundColor": "#0F172A", "borderBottom": "1px solid #334155"}),
                    dbc.CardBody([
                        html.P(
                            "ข้อควรทราบ: ผลลัพธ์ในส่วนนี้เป็นการประมาณการผ่านแบบจำลองเชิงนโยบาย (What-If Analysis) "
                            "โดยใช้สถิติตัวเลขจริงของกระทรวงคมนาคมเป็นฐานคำนวณ ไม่ใช่ตัวเลขสังเกตการณ์จริง",
                            className="text-muted small mb-3"
                        ),
                        dbc.Row([
                            dbc.Col([
                                html.Label("🚗 Enforce Speed Limit Reduction (%):", className="text-light small fw-bold"),
                                dcc.Slider(
                                    id="sim-slider-speed",
                                    min=0, max=50, step=5, value=20,
                                    marks={0: "0%", 20: "20%", 50: "50%"},
                                    tooltip={"placement": "bottom", "always_visible": False}
                                )
                            ], md=4),
                            dbc.Col([
                                html.Label("🪖 Boost Helmet / Seatbelt Compliance (%):", className="text-light small fw-bold"),
                                dcc.Slider(
                                    id="sim-slider-helmet",
                                    min=0, max=50, step=5, value=25,
                                    marks={0: "0%", 25: "25%", 50: "50%"},
                                    tooltip={"placement": "bottom", "always_visible": False}
                                )
                            ], md=4),
                            dbc.Col([
                                html.Label("🛑 Drunk Driving Crackdown (%):", className="text-light small fw-bold"),
                                dcc.Slider(
                                    id="sim-slider-drunk",
                                    min=0, max=50, step=5, value=30,
                                    marks={0: "0%", 30: "30%", 50: "50%"},
                                    tooltip={"placement": "bottom", "always_visible": False}
                                )
                            ], md=4),
                        ], className="mb-3"),

                        # Simulation Outcome Cards
                        html.Div(id="simulation-results-container", className="mt-3"),

                        # Simulation Editable Table
                        html.H6("📝 Editable Incident Simulation Table (ทดลองแก้ไขข้อมูลเหตุการณ์สด):", className="text-info mt-4 mb-2"),
                        html.P("คลิกที่เซลล์ในคอลัมน์ Fatalities หรือ Serious Injuries เพื่อทดลองปรับเปลี่ยนตัวเลขได้โดยตรง", className="text-muted small"),
                        dash_table.DataTable(
                            id="simulation-editable-table",
                            columns=[
                                {"name": "Incident ID", "id": "incident_id", "editable": False},
                                {"name": "Province", "id": "province", "editable": False},
                                {"name": "Road Type", "id": "road_hierarchy", "editable": False},
                                {"name": "Primary Cause", "id": "accident_cause", "editable": False},
                                {"name": "Vehicle", "id": "vehicle_type", "editable": False},
                                {"name": "Fatalities", "id": "fatalities", "editable": True, "type": "numeric"},
                                {"name": "Serious Injuries", "id": "serious_injuries", "editable": True, "type": "numeric"},
                                {"name": "Economic Loss (THB)", "id": "estimated_economic_loss_thb", "editable": False, "type": "numeric", "format": {"specifier": ",.0f"}},
                            ],
                            data=sim_table_data.to_dict("records"),
                            page_size=8,
                            style_header={
                                "backgroundColor": "#0F172A",
                                "color": "#F8FAFC",
                                "fontWeight": "bold",
                                "border": "1px solid #334155"
                            },
                            style_data={
                                "backgroundColor": "#1E293B",
                                "color": "#F8FAFC",
                                "border": "1px solid #334155"
                            },
                            style_data_conditional=[
                                {
                                    "if": {"column_editable": True},
                                    "backgroundColor": "#132338",
                                    "color": "#38BDF8",
                                    "fontWeight": "bold"
                                }
                            ]
                        )
                    ])
                ], className="border-0 shadow-sm", style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "10px"})
            ], md=12)
        ])
    ])
