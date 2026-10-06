"""
Tab 2 Component: Risk Zones, Causes & Operations
Blackspot geospatial map, root cause pareto chart, road authority donut chart, and road hierarchy violin plot.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.style_constants import (
    COLOR_CARD_BG, COLOR_CRITICAL_RED, COLOR_WARNING_AMBER, COLOR_SAFE_GREEN,
    COLOR_CYAN_ACCENT, COLOR_PURPLE_ACCENT, apply_dark_theme, RISK_COLOR_MAP
)

def render_tab_risk_zones(df):
    """Generates the layout and graphs for Tab 2."""
    if df.empty:
        return html.Div(
            [html.P("No data available for current selection.", className="text-warning p-4")],
            style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "8px"}
        )

    # 1. High-Risk Blackspots Geospatial Scatter Map
    # Subsample if too large for smooth web rendering
    sample_geo = df.sample(n=min(len(df), 800), random_state=42) if len(df) > 800 else df

    fig_map = px.scatter_geo(
        sample_geo,
        lat="latitude",
        lon="longitude",
        color="risk_level",
        color_discrete_map=RISK_COLOR_MAP,
        size="total_casualties",
        size_max=14,
        hover_name="province",
        hover_data={
            "latitude": False,
            "longitude": False,
            "accident_cause": True,
            "fatalities": True,
            "vehicle_type": True,
            "road_hierarchy": True
        },
        scope="asia"
    )
    # Center map on Thailand
    fig_map.update_geos(
        center=dict(lat=13.736717, lon=100.523186),
        projection_scale=6.5,
        visible=True,
        resolution=50,
        showland=True, landcolor="#1E293B",
        showocean=True, oceancolor="#0F172A",
        showlakes=True, lakecolor="#0F172A",
        showrivers=False,
        showcountries=True, countrycolor="#334155",
        countrywidth=1.2,
        bgcolor="#0F172A"
    )
    apply_dark_theme(fig_map, "🗺️ High-Risk Blackspots & Geospatial Zones (พิกัดจุดเสี่ยงอันตรายทั่วประเทศ)", height=450)
    fig_map.update_layout(margin=dict(l=10, r=10, t=45, b=10))

    # 2. Key Accident Causes (Horizontal Pareto / Bar Chart)
    cause_counts = df["accident_cause"].value_counts().reset_index()
    cause_counts.columns = ["cause", "count"]
    cause_counts = cause_counts.sort_values(by="count", ascending=True)

    fig_causes = go.Figure()
    fig_causes.add_trace(go.Bar(
        y=cause_counts["cause"],
        x=cause_counts["count"],
        orientation="h",
        marker=dict(
            color=cause_counts["count"],
            colorscale=[[0, "#38BDF8"], [0.5, "#F59E0B"], [1, "#FF4136"]],
            showscale=False
        ),
        text=cause_counts["count"].apply(lambda x: f"{x:,}"),
        textposition="outside"
    ))
    apply_dark_theme(fig_causes, "⚠️ Primary Causes of Accidents (สาเหตุหลักของการเกิดอุบัติเหตุ)")
    fig_causes.update_xaxes(title="Accident Count (จำนวนครั้ง)")

    # 3. Managing Entities / Fleet Operators (Donut Chart)
    entity_counts = df["managing_entity"].value_counts().reset_index()
    entity_counts.columns = ["entity", "count"]

    fig_entities = go.Figure(data=[go.Pie(
        labels=entity_counts["entity"],
        values=entity_counts["count"],
        hole=0.48,
        marker=dict(colors=["#38BDF8", "#10B981", "#F59E0B", "#A855F7", "#EC4899"]),
        textinfo="percent+label",
        insidetextorientation="radial"
    )])
    apply_dark_theme(fig_entities, "🏛️ Managing Entities & Road Authorities (หน่วยงานรับผิดชอบสายทาง)")
    fig_entities.update_layout(showlegend=False)

    # 4. Severity Index by Road Hierarchy (Violin Plot / Grouped Bar)
    fig_hierarchy = px.box(
        df,
        x="road_hierarchy",
        y="total_casualties",
        color="road_hierarchy",
        color_discrete_sequence=["#38BDF8", "#10B981", "#F59E0B", "#A855F7"],
        points=False
    )
    apply_dark_theme(fig_hierarchy, "🛣️ Casualty Severity by Road Hierarchy (ระดับความรุนแรงตามระดับสายทาง)")
    fig_hierarchy.update_yaxes(title="Casualties per Incident")
    fig_hierarchy.update_xaxes(title="Road Classification")

    return html.Div([
        # Row 1: Mapbox/Scatter Geo (Full Width or 8-col)
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig_map, id="graph-geo-map", config={"displayModeBar": True})
                    ])
                ], className="border-0 shadow-sm mb-4", style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "10px"})
            ], md=12),
        ]),

        # Row 2: Causes Bar + Authority Donut + Hierarchy Box
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig_causes, id="graph-causes", config={"displayModeBar": True})
                    ])
                ], className="border-0 shadow-sm mb-4", style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "10px"})
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig_entities, id="graph-entities", config={"displayModeBar": True})
                    ])
                ], className="border-0 shadow-sm mb-4", style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "10px"})
            ], md=6),
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig_hierarchy, id="graph-hierarchy", config={"displayModeBar": True})
                    ])
                ], className="border-0 shadow-sm mb-4", style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "10px"})
            ], md=12),
        ])
    ])
