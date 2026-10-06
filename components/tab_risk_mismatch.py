"""
Tab 3 Component: Risk Mismatch & Gap Simulation Engine
Safety Capability vs Risk Exposure Quadrant Matrix, Safety Equipment Radar Gap,
and Interactive Simulation Table & Recalculation Engine.
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
    """Generates the layout and graphs for Tab 3."""
    if df.empty:
        return html.Div(
            [html.P("No data available for current selection.", className="text-warning p-4")],
            style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "8px"}
        )

    # 1. Safety Capability vs Risk Exposure Quadrant Scatter Plot
    sample_df = df.sample(n=min(len(df), 500), random_state=42) if len(df) > 500 else df
    
    fig_matrix = go.Figure()
    
    # Add scatter points
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
    
    # Add Quadrant dividing lines (at X=50, Y=50)
    fig_matrix.add_vline(x=50, line_width=1.5, line_dash="dash", line_color="#64748B")
    fig_matrix.add_hline(y=50, line_width=1.5, line_dash="dash", line_color="#64748B")
    
    # Quadrant annotations
    fig_matrix.add_annotation(x=75, y=90, text="🔴 Critical Mismatch (Danger)", showarrow=False,
                             font=dict(color="#FF4136", size=12, family="Inter"))
    fig_matrix.add_annotation(x=25, y=90, text="🟡 Human Error Dominant", showarrow=False,
                             font=dict(color="#FFDC00", size=12, family="Inter"))
    fig_matrix.add_annotation(x=75, y=15, text="🟡 Road Defect Dominant", showarrow=False,
                             font=dict(color="#FFDC00", size=12, family="Inter"))
    fig_matrix.add_annotation(x=25, y=15, text="🟢 Baseline Low Risk", showarrow=False,
                             font=dict(color="#2ECC40", size=12, family="Inter"))
                             
    apply_dark_theme(fig_matrix, "🎯 Risk Mismatch Matrix (Infrastructure vs Behavior Risk Quadrants)")
    fig_matrix.update_xaxes(title="Road Infrastructure Risk Score (0-100)", range=[0, 100])
    fig_matrix.update_yaxes(title="Driver Behavioral Risk Score (0-100)", range=[0, 100])

    # 2. Safety Equipment Gap Analysis (Radar Chart by Region)
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
        font=dict(color="#94A3B8"),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    apply_dark_theme(fig_radar, "🛡️ Safety Equipment Compliance vs Resilience Radar by Region")

    # 3. Editable Simulation Table Sample (Top 10 High Risk Records)
    sim_table_data = df[df["risk_level"].str.contains("Level 3|Level 2", na=False)].head(15)[[
        "incident_id", "province", "road_hierarchy", "accident_cause",
        "vehicle_type", "fatalities", "serious_injuries", "estimated_economic_loss_thb"
    ]].copy()
    sim_table_data["estimated_economic_loss_thb"] = sim_table_data["estimated_economic_loss_thb"].round(0)

    return html.Div([
        # Row 1: Quadrants Matrix + Radar Gap
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig_matrix, id="graph-mismatch-matrix", config={"displayModeBar": True})
                    ])
                ], className="border-0 shadow-sm mb-4", style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "10px"})
            ], md=7),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig_radar, id="graph-safety-radar", config={"displayModeBar": True})
                    ])
                ], className="border-0 shadow-sm mb-4", style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "10px"})
            ], md=5),
        ]),

        # Row 2: Policy Simulation Controls & Real-Time Projections
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("🎛️ Policy Intervention Simulation Engine (จำลองผลลัพธ์มาตรการความปลอดภัย)", className="text-white mb-0")
                    ], style={"backgroundColor": "#0F172A", "borderBottom": "1px solid #334155"}),
                    dbc.CardBody([
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
                            style_cell={
                                "backgroundColor": "#1E293B",
                                "color": "#CBD5E1",
                                "border": "1px solid #334155",
                                "fontSize": "12px",
                                "padding": "8px"
                            },
                            style_data_conditional=[
                                {
                                    "if": {"column_editable": True},
                                    "backgroundColor": "#243248",
                                    "color": "#38BDF8",
                                    "cursor": "pointer"
                                }
                            ]
                        )
                    ])
                ], className="border-0 shadow-sm mb-4", style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "10px"})
            ], md=12)
        ])
    ])
