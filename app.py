"""
Thailand Road Accident Analytics & Safety Dashboard
Interactive Streamlit Application
"""

import os
import io
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import (
    load_accident_data, filter_accident_data, calculate_kpis, run_policy_simulation
)
from utils.style_constants import (
    COLOR_BG_DARK, COLOR_CARD_BG, COLOR_CARD_BORDER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_MUTED, COLOR_CRITICAL_RED,
    COLOR_WARNING_AMBER, COLOR_SAFE_GREEN, COLOR_CYAN_ACCENT,
    RISK_COLOR_MAP, VEHICLE_COLOR_MAP, apply_dark_theme
)

# -------------------------------------------------------------
# 1. Page Configuration & Custom CSS
# -------------------------------------------------------------
st.set_page_config(
    page_title="Thailand Road Accident Analytics",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Dark Slate Theme
st.markdown("""
<style>
    /* Dark Slate Theme Custom Styles */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    header[data-testid="stHeader"] {
        background-color: #0F172A;
    }
    section[data-testid="stSidebar"] {
        background-color: #1E293B;
        border-right: 1px solid #334155;
    }
    
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #1E293B;
        border: 1px solid #334155;
        padding: 14px 18px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    div[data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetricValue"] {
        color: #F8FAFC !important;
        font-weight: 700 !important;
    }
    
    /* Tabs */
    button[data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.95rem;
        color: #94A3B8;
        border-radius: 6px 6px 0 0;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #38BDF8 !important;
        border-bottom-color: #38BDF8 !important;
    }
    
    /* Simulation Container */
    .simulation-box {
        background-color: #132338;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


# -------------------------------------------------------------
# 2. Data Loading & Session State Management
# -------------------------------------------------------------
@st.cache_data
def get_default_data():
    return load_accident_data()

if "custom_df" not in st.session_state:
    st.session_state.custom_df = None

# Sidebar Data Upload
st.sidebar.markdown("### 📁 จัดการชุดข้อมูล (Data Input)")
uploaded_file = st.sidebar.file_uploader(
    "อัปโหลดไฟล์อุบัติเหตุใหม่ (CSV / Excel):",
    type=["csv", "xlsx", "xls"],
    help="อัปโหลดชุดข้อมูลเพื่อแทนที่ข้อมูลตัวอย่าง"
)

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            st.session_state.custom_df = pd.read_csv(uploaded_file)
        else:
            st.session_state.custom_df = pd.read_excel(uploaded_file)
        st.sidebar.success(f"✅ โหลดสำเร็จ: {len(st.session_state.custom_df):,} แถว")
    except Exception as e:
        st.sidebar.error(f"❌ เกิดข้อผิดพลาด: {str(e)}")

# Active DataFrame
df_base = st.session_state.custom_df if st.session_state.custom_df is not None else get_default_data()

# -------------------------------------------------------------
# 3. Sidebar Filters
# -------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 ตัวกรองข้อมูล (Filter Panel)")

# Filter: Year
available_years = sorted(df_base["year"].unique())
year_options = ["All Years"] + [str(y) for y in available_years]
selected_year = st.sidebar.selectbox("📅 ปีงบประมาณ (Year):", year_options, index=0)

# Filter: Region
available_regions = sorted(df_base["region"].unique())
region_options = ["All Regions"] + list(available_regions)
selected_region = st.sidebar.selectbox("📍 ภูมิภาค (Region):", region_options, index=0)

# Filter: Vehicle Type
available_vehicles = sorted(df_base["vehicle_type"].unique())
vehicle_options = ["All Vehicles"] + list(available_vehicles)
selected_vehicle = st.sidebar.selectbox("🛵 ประเภทยานพาหนะ (Vehicle):", vehicle_options, index=0)

# Filter: Period / Festival
available_periods = sorted(df_base["period_type"].unique())
period_options = ["All Periods"] + list(available_periods)
selected_period = st.sidebar.selectbox("🎉 ช่วงเวลา/เทศกาล (Period):", period_options, index=0)

# Filter: Road Hierarchy
available_roads = sorted(df_base["road_hierarchy"].unique())
road_options = ["All Road Types"] + list(available_roads)
selected_road = st.sidebar.selectbox("🛣️ ประเภทสายทาง (Road Hierarchy):", road_options, index=0)

# Apply Filters
filtered_df = filter_accident_data(
    df_base,
    years=[int(selected_year)] if selected_year != "All Years" else None,
    regions=[selected_region] if selected_region != "All Regions" else None,
    vehicle_types=[selected_vehicle] if selected_vehicle != "All Vehicles" else None,
    period_types=[selected_period] if selected_period != "All Periods" else None,
    road_types=[selected_road] if selected_road != "All Road Types" else None
)

# Export Button in Sidebar
st.sidebar.markdown("---")
csv_data = filtered_df.to_csv(index=False).encode('utf-8-sig')
st.sidebar.download_button(
    label="📥 ดาวน์โหลดข้อมูลที่กรอง (CSV)",
    data=csv_data,
    file_name="thailand_road_accidents_filtered.csv",
    mime="text/csv",
    use_container_width=True
)

st.sidebar.caption("Open Government Data Attribution: DOH • ThaiRSC • RTP • DLT")

# -------------------------------------------------------------
# 4. Header & Executive KPI Summary Cards
# -------------------------------------------------------------
st.title("🚗 Thailand Road Accident Analytics & Safety Dashboard")
st.markdown("ระบบวิเคราะห์สถิติอุบัติเหตุทางถนน พิกัดจุดเสี่ยงอันตราย และแบบจำลองมาตรการความปลอดภัยเชิงนโยบาย")

# Calculate KPIs
kpis = calculate_kpis(filtered_df)

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.metric("Total Incidents", f"{kpis['total_incidents']:,}", delta="อุบัติเหตุทั้งหมด")
with col2:
    st.metric("Fatalities", f"{kpis['total_fatalities']:,}", delta=f"{kpis['fatality_rate']}% อัตราเสียชีวิต", delta_color="inverse")
with col3:
    st.metric("Total Injuries", f"{kpis['total_serious'] + kpis['total_slight']:,}", delta=f"สาหัส {kpis['total_serious']:,} ราย", delta_color="inverse")
with col4:
    st.metric("Fatality Rate", f"{kpis['fatality_rate']}%", delta="รายต่อ 100 เหตุการณ์", delta_color="inverse")
with col5:
    st.metric("High-Risk Blackspots", f"{kpis['high_risk_incidents']:,}", delta=f"{kpis['high_risk_share']}% Critical Zones", delta_color="inverse")
with col6:
    st.metric("Economic Loss", f"฿{kpis['total_loss_mb']:,.1f}M", delta="มูลค่าความเสียหายรวม")

st.markdown("---")

# -------------------------------------------------------------
# 5. Main Dashboard Tabs
# -------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📊 Tab 1: Casualties & Vehicle Impact",
    "🗺️ Tab 2: Risk Zones & Causes",
    "🔬 Tab 3: Risk Mismatch & Simulation Engine"
])

# -------------------------------------------------------------
# TAB 1: Casualties & Vehicle Impact
# -------------------------------------------------------------
with tab1:
    st.subheader("สถิติและปริมาณความรุนแรงของอุบัติเหตุ จำแนกตามประเภทยานพาหนะ")

    r1_col1, r1_col2 = st.columns([7, 5])
    with r1_col1:
        # Yearly Trend Chart
        yearly = filtered_df.groupby("year").agg({
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
            line=dict(color=COLOR_CYAN_ACCENT, width=3), marker=dict(size=7)
        ))
        fig_trends.add_trace(go.Scatter(
            x=yearly["year"], y=yearly["total_injuries"],
            mode="lines+markers", name="Injuries (บาดเจ็บ)",
            line=dict(color=COLOR_WARNING_AMBER, width=2.5, dash="dot"), marker=dict(size=6)
        ))
        fig_trends.add_trace(go.Scatter(
            x=yearly["year"], y=yearly["fatalities"],
            mode="lines+markers", name="Fatalities (เสียชีวิต)",
            line=dict(color=COLOR_CRITICAL_RED, width=3), marker=dict(size=8, symbol="diamond")
        ))
        apply_dark_theme(fig_trends, "📈 แนวโน้มอุบัติเหตุและผู้บาดเจ็บ/เสียชีวิตรายปี (2020-2026)")
        fig_trends.update_xaxes(dtick=1)
        st.plotly_chart(fig_trends, use_container_width=True)

    with r1_col2:
        # Vehicle Type Distribution
        veh_summary = filtered_df.groupby("vehicle_type").agg({
            "incident_id": "count",
            "fatalities": "sum"
        }).reset_index().rename(columns={"incident_id": "incidents"}).sort_values(by="incidents", ascending=True)

        fig_veh = go.Figure()
        colors = [VEHICLE_COLOR_MAP.get(v, "#38BDF8") for v in veh_summary["vehicle_type"]]
        fig_veh.add_trace(go.Bar(
            y=veh_summary["vehicle_type"],
            x=veh_summary["incidents"],
            orientation="h",
            marker_color=colors,
            text=veh_summary["incidents"].apply(lambda x: f"{x:,}"),
            textposition="outside"
        ))
        apply_dark_theme(fig_veh, "🛵 ประเภทยานพาหนะที่ประสบเหตุ (Vehicle Types Involved)")
        fig_veh.update_xaxes(title="จำนวนครั้ง (ครั้ง)")
        st.plotly_chart(fig_veh, use_container_width=True)

    r2_col1, r2_col2 = st.columns(2)
    with r2_col1:
        # Casualty Outcomes by Period
        period_group = filtered_df.groupby("period_type").agg({
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
        apply_dark_theme(fig_outcomes, "⏱️ จำแนกผลลัพธ์ความรุนแรงตามช่วงเทศกาล (Casualty Timeline)")
        st.plotly_chart(fig_outcomes, use_container_width=True)

    with r2_col2:
        # Economic Loss Boxplot
        fig_cost = px.box(
            filtered_df,
            x="vehicle_type",
            y="estimated_economic_loss_thb",
            color="vehicle_type",
            color_discrete_map=VEHICLE_COLOR_MAP,
            points=False
        )
        apply_dark_theme(fig_cost, "💰 มูลค่าความเสียหายทางเศรษฐกิจ ต่อเคส (Financial Loss Distribution)")
        fig_cost.update_yaxes(title="ความเสียหาย (บาท)", tickformat=",.0f")
        fig_cost.update_xaxes(title="ประเภทยานพาหนะ")
        st.plotly_chart(fig_cost, use_container_width=True)


# -------------------------------------------------------------
# TAB 2: Risk Zones & Causes
# -------------------------------------------------------------
with tab2:
    st.subheader("พื้นที่จุดเสี่ยง (Blackspots) สาเหตุหลัก และหน่วยงานที่รับผิดชอบสายทาง")

    # Geospatial Map
    sample_geo = filtered_df.sample(n=min(len(filtered_df), 800), random_state=42) if len(filtered_df) > 800 else filtered_df
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
    apply_dark_theme(fig_map, "🗺️ แผนที่พิกัดจุดเสี่ยงอันตราย (High-Risk Blackspots Map)", height=500)
    st.plotly_chart(fig_map, use_container_width=True)

    t2_col1, t2_col2 = st.columns(2)
    with t2_col1:
        # Causes Horizontal Pareto
        cause_counts = filtered_df["accident_cause"].value_counts().reset_index()
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
        apply_dark_theme(fig_causes, "⚠️ สาเหตุหลักของการเกิดอุบัติเหตุ (Top Accident Causes)")
        fig_causes.update_xaxes(title="จำนวนครั้ง (ครั้ง)")
        st.plotly_chart(fig_causes, use_container_width=True)

    with t2_col2:
        # Managing Entities Donut
        entity_counts = filtered_df["managing_entity"].value_counts().reset_index()
        entity_counts.columns = ["entity", "count"]

        fig_entities = go.Figure(data=[go.Pie(
            labels=entity_counts["entity"],
            values=entity_counts["count"],
            hole=0.48,
            marker=dict(colors=["#38BDF8", "#10B981", "#F59E0B", "#A855F7", "#EC4899"]),
            textinfo="percent+label",
            insidetextorientation="radial"
        )])
        apply_dark_theme(fig_entities, "🏛️ หน่วยงานผู้ดูแลสายทาง (Managing Entities & Authorities)")
        fig_entities.update_layout(showlegend=False)
        st.plotly_chart(fig_entities, use_container_width=True)

    # Road Hierarchy Severity
    fig_hierarchy = px.box(
        filtered_df,
        x="road_hierarchy",
        y="total_casualties",
        color="road_hierarchy",
        color_discrete_sequence=["#38BDF8", "#10B981", "#F59E0B", "#A855F7"],
        points=False
    )
    apply_dark_theme(fig_hierarchy, "🛣️ ระดับความรุนแรงตามระดับสายทาง (Severity Index by Road Hierarchy)")
    fig_hierarchy.update_yaxes(title="Casualties per Incident")
    fig_hierarchy.update_xaxes(title="Road Hierarchy")
    st.plotly_chart(fig_hierarchy, use_container_width=True)


# -------------------------------------------------------------
# TAB 3: Risk Mismatch & Simulation Engine
# -------------------------------------------------------------
with tab3:
    st.subheader("การวิเคราะห์ความเสี่ยงซ้อนทับ (Risk Mismatch) และแบบจำลองมาตรการเชิงนโยบาย")

    m_col1, m_col2 = st.columns([7, 5])
    with m_col1:
        # 4-Quadrant Scatter Matrix
        sample_mismatch = filtered_df.sample(n=min(len(filtered_df), 500), random_state=42) if len(filtered_df) > 500 else filtered_df
        fig_matrix = go.Figure()
        fig_matrix.add_trace(go.Scatter(
            x=sample_mismatch["road_risk_score"],
            y=sample_mismatch["driver_behavior_risk_score"],
            mode="markers",
            marker=dict(
                size=sample_mismatch["total_casualties"] * 3 + 5,
                color=sample_mismatch["fatalities"],
                colorscale=[[0, "#38BDF8"], [0.5, "#F59E0B"], [1, "#FF4136"]],
                showscale=True,
                colorbar=dict(title="Fatalities", tickfont=dict(color="#94A3B8"))
            ),
            text=[f"Province: {p}<br>Cause: {c}<br>Road: {r}" for p, c, r in zip(
                sample_mismatch["province"], sample_mismatch["accident_cause"], sample_mismatch["road_hierarchy"]
            )],
            hoverinfo="text"
        ))
        fig_matrix.add_vline(x=50, line_width=1.5, line_dash="dash", line_color="#64748B")
        fig_matrix.add_hline(y=50, line_width=1.5, line_dash="dash", line_color="#64748B")
        fig_matrix.add_annotation(x=75, y=90, text="🔴 Critical Mismatch (Danger)", showarrow=False,
                                 font=dict(color="#FF4136", size=12))
        fig_matrix.add_annotation(x=25, y=90, text="🟡 Human Error Dominant", showarrow=False,
                                 font=dict(color="#FFDC00", size=12))
        fig_matrix.add_annotation(x=75, y=15, text="🟡 Road Defect Dominant", showarrow=False,
                                 font=dict(color="#FFDC00", size=12))
        fig_matrix.add_annotation(x=25, y=15, text="🟢 Baseline Low Risk", showarrow=False,
                                 font=dict(color="#2ECC40", size=12))
        apply_dark_theme(fig_matrix, "🎯 Safety Capability vs Risk Exposure Matrix (Infrastructure vs Behavior)")
        fig_matrix.update_xaxes(title="Road Infrastructure Risk Score (0-100)", range=[0, 100])
        fig_matrix.update_yaxes(title="Driver Behavioral Risk Score (0-100)", range=[0, 100])
        st.plotly_chart(fig_matrix, use_container_width=True)

    with m_col2:
        # Safety Equipment Radar Chart
        region_equip = filtered_df.groupby("region").agg({
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
            margin=dict(l=30, r=30, t=50, b=30)
        )
        apply_dark_theme(fig_radar, "🛡️ ความพร้อมอุปกรณ์ความปลอดภัยเทียบอัตราการสูญเสีย (Radar Gap)")
        st.plotly_chart(fig_radar, use_container_width=True)

    # -------------------------------------------------------------
    # Simulation Section
    # -------------------------------------------------------------
    st.markdown("### 🎛️ Policy Simulation & Recalculation Engine")
    st.markdown("ปรับแต่งตัวแปรนโยบายเพื่อจำลองการลดลงของจำนวนผู้เสียชีวิต บาดเจ็บ และความคุ้มค่าทางเศรษฐกิจ")

    sim_col1, sim_col2, sim_col3 = st.columns(3)
    with sim_col1:
        speed_red = st.slider("🚗 กวดขันความเร็ว (Speed Reduction %):", min_value=0, max_value=50, value=20, step=5)
    with sim_col2:
        helmet_boost = st.slider("🪖 รณรงค์สวมหมวก/คาดเข็มขัด (Safety Equip Boost %):", min_value=0, max_value=50, value=25, step=5)
    with sim_col3:
        drunk_red = st.slider("🛑 ปราบปรามเมาแล้วขับ (Drunk Driving Crackdown %):", min_value=0, max_value=50, value=30, step=5)

    sim_res = run_policy_simulation(
        filtered_df,
        speed_reduction_pct=speed_red,
        helmet_boost_pct=helmet_boost,
        drunk_reduction_pct=drunk_red
    )

    p1, p2, p3 = st.columns(3)
    with p1:
        st.metric(
            "ประมาณการช่วยชีวิตได้ (Lives Saved)",
            f"-{sim_res['fatalities_saved']} Lives",
            f"จาก {sim_res['baseline_fatalities']} เหลือ {sim_res['simulated_fatalities']} ราย",
            delta_color="normal"
        )
    with p2:
        st.metric(
            "ลดการบาดเจ็บสาหัส (Injuries Prevented)",
            f"-{sim_res['serious_prevented']} Cases",
            f"จาก {sim_res['baseline_serious']} เหลือ {sim_res['simulated_serious']} ราย",
            delta_color="normal"
        )
    with p3:
        st.metric(
            "มูลค่าประหยัดได้ทางเศรษฐกิจ (Economic Savings)",
            f"+฿{sim_res['economic_savings_mb']:,.1f} M THB",
            "ตามเกณฑ์ประเมิน DLT / WHO",
            delta_color="normal"
        )

    # Editable Simulation Table using st.data_editor
    st.markdown("#### 📝 Editable Simulation Data Table (ตารางแก้ไขข้อมูลจำลองสถานการณ์)")
    st.caption("ดับเบิลคลิกแก้ไขตัวเลขในคอลัมน์ Fatalities หรือ Serious Injuries ได้โดยตรง ระบบจะบันทึกและจำลองผลแบบ Real-Time")

    sample_edit_df = filtered_df.head(12)[[
        "incident_id", "province", "road_hierarchy", "accident_cause",
        "vehicle_type", "fatalities", "serious_injuries", "estimated_economic_loss_thb"
    ]].copy()

    edited_table = st.data_editor(
        sample_edit_df,
        column_config={
            "incident_id": st.column_config.TextColumn("Incident ID", disabled=True),
            "province": st.column_config.TextColumn("Province", disabled=True),
            "road_hierarchy": st.column_config.TextColumn("Road Type", disabled=True),
            "accident_cause": st.column_config.TextColumn("Cause", disabled=True),
            "vehicle_type": st.column_config.TextColumn("Vehicle", disabled=True),
            "fatalities": st.column_config.NumberColumn("Fatalities*", min_value=0, max_value=20, step=1),
            "serious_injuries": st.column_config.NumberColumn("Serious Injuries*", min_value=0, max_value=50, step=1),
            "estimated_economic_loss_thb": st.column_config.NumberColumn("Loss (THB)", format="฿%d", disabled=True)
        },
        disabled=["incident_id", "province", "road_hierarchy", "accident_cause", "vehicle_type", "estimated_economic_loss_thb"],
        hide_index=True,
        use_container_width=True,
        key="simulation_table_editor"
    )

    if edited_table is not None:
        total_edited_fatalities = int(edited_table["fatalities"].sum())
        orig_fatalities = int(sample_edit_df["fatalities"].sum())
        diff_fat = total_edited_fatalities - orig_fatalities
        if diff_fat != 0:
            st.info(f"📊 ผลกระทบจากการปรับค่าในตารางจำลอง: ผู้เสียชีวิตรวมเปลี่ยนแปลง {diff_fat:+d} ราย (จาก {orig_fatalities} เป็น {total_edited_fatalities} ราย)")

# -------------------------------------------------------------
# Footer
# -------------------------------------------------------------
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748B; font-size: 0.85rem; padding: 10px;'>"
    "Thailand Road Accident Analytics System • Streamlit Framework Edition • Open Government Data License"
    "</div>",
    unsafe_allow_html=True
)
