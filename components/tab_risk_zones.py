"""
Tab 2 Component: Risk Zones, Causes & Operations
Blackspot geospatial map, root cause pareto chart, road authority donut chart, and road hierarchy violin plot.
All visualizations use REAL observed government open data.
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
    """Generates the layout and graphs for Tab 2 using real government data."""
    if df.empty:
        return html.Div(
            [html.P("No data available for current selection.", className="text-warning p-4")],
            style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "8px"}
        )

    # 1. High-Risk Blackspots Geospatial Scatter Map (Validate coordinates)
    has_coords = "latitude" in df.columns and "longitude" in df.columns
    if has_coords:
        valid_geo = df[
            df["latitude"].notna() & df["longitude"].notna() &
            (df["latitude"] >= 5.5) & (df["latitude"] <= 20.5) &
            (df["longitude"] >= 97.0) & (df["longitude"] <= 106.0)
        ]
        if not valid_geo.empty:
            # Deterministic sorting without random: top 1,000 severe incidents
            sample_geo = valid_geo.sort_values(by=["fatalities", "total_casualties"], ascending=False).head(1000)
            fig_map = px.scatter_geo(
                sample_geo,
                lat="latitude",
                lon="longitude",
                color="risk_level" if "risk_level" in sample_geo.columns else "fatalities",
                color_discrete_map={
                    "Level 3: Critical (Fatal Incident)": "#FF4136",
                    "Level 2: Moderate (Serious Injury)": "#F59E0B",
                    "Level 1: Low (Minor Injury/No Death)": "#10B981"
                },
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
            apply_dark_theme(fig_map, f"🗺️ High-Risk Blackspots & Geospatial Zones (แสดง {len(sample_geo):,} จุดพิกัดจริง)", height=450)
            fig_map.update_layout(margin=dict(l=10, r=10, t=45, b=10))
            map_component = dcc.Graph(figure=fig_map, id="graph-blackspot-map", config={"displayModeBar": True})
        else:
            map_component = html.Div("Official source data does not contain valid latitude/longitude coordinates for this selection.", className="alert alert-warning py-2")
    else:
        map_component = html.Div("Official source data does not contain the fields required for this visualization (latitude/longitude missing).", className="alert alert-warning py-2")

    # 2. Key Accident Causes (Horizontal Pareto / Bar Chart)
    if "accident_cause" in df.columns:
        cause_counts = df["accident_cause"].value_counts().head(10).reset_index()
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
        apply_dark_theme(fig_causes, "⚠️ Primary Causes of Accidents (สาเหตุหลักที่รายงานจริง)")
        fig_causes.update_xaxes(title="Accident Count (จำนวนครั้ง)")
        causes_component = dcc.Graph(figure=fig_causes, id="graph-causes-pareto", config={"displayModeBar": True})
    else:
        causes_component = html.Div("Official source data does not contain the fields required for this visualization (accident_cause missing).", className="alert alert-warning py-2")

    # 3. Managing Entities (Donut Chart)
    agency_col = "road_agency" if "road_agency" in df.columns else ("managing_entity" if "managing_entity" in df.columns else None)
    if agency_col:
        entity_counts = df[agency_col].value_counts().reset_index()
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
        entities_component = dcc.Graph(figure=fig_entities, id="graph-managing-entities", config={"displayModeBar": True})
    else:
        entities_component = html.Div("Official source data does not contain the fields required for this visualization (road_agency missing).", className="alert alert-warning py-2")

    # 4. Severity Index by Road Hierarchy
    road_type_col = "road_type" if "road_type" in df.columns else ("road_hierarchy" if "road_hierarchy" in df.columns else None)
    if road_type_col and "total_casualties" in df.columns:
        fig_hierarchy = px.box(
            df,
            x=road_type_col,
            y="total_casualties",
            color=road_type_col,
            color_discrete_sequence=["#38BDF8", "#10B981", "#F59E0B", "#A855F7"],
            points=False
        )
        apply_dark_theme(fig_hierarchy, "🛣️ Severity Index by Road Hierarchy (ระดับความรุนแรงตามระดับสายทาง)")
        fig_hierarchy.update_yaxes(title="Casualties per Incident")
        fig_hierarchy.update_xaxes(title="Road Hierarchy")
        hierarchy_component = dcc.Graph(figure=fig_hierarchy, id="graph-road-hierarchy", config={"displayModeBar": True})
    else:
        hierarchy_component = html.Div("Official source data does not contain the fields required for this visualization.", className="alert alert-warning py-2")

    return html.Div([
        # Row 1: Blackspot Map (Full Width)
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([map_component])
                ], className="border-0 shadow-sm mb-4", style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "10px"})
            ], md=12)
        ]),

        # Row 2: Causes Pareto + Managing Entities Donut
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([causes_component])
                ], className="border-0 shadow-sm mb-4", style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "10px"})
            ], md=7),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([entities_component])
                ], className="border-0 shadow-sm mb-4", style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "10px"})
            ], md=5),
        ]),

        # Row 3: Road Hierarchy Box Plot
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([hierarchy_component])
                ], className="border-0 shadow-sm mb-4", style={"backgroundColor": COLOR_CARD_BG, "borderRadius": "10px"})
            ], md=12)
        ])
    ])
