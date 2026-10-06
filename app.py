import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ----------------- Configuration & CSS -----------------
st.set_page_config(page_title="KKU Dashboard", page_icon="🎓", layout="wide")

# Inject Custom CSS (Cute Cartoon Retro Style)
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600&family=Mali:wght@400;500;600&display=swap');

/* Apply global font and background */
.stApp {
    background-color: #FFF8E7; 
    font-family: 'Fredoka', 'Mali', sans-serif;
    color: #4A4A4A;
}

/* Custom HTML components styling */
.kpi-container {
    display: flex;
    justify-content: space-between;
    gap: 20px;
    margin-bottom: 30px;
}
.kpi-card {
    background-color: #FFFFFF;
    border-radius: 20px;
    padding: 20px;
    box-shadow: 4px 4px 0px 0px rgba(167, 59, 36, 0.2), 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    text-align: center;
    border: 3px solid #FADCB3;
    flex: 1;
    transition: transform 0.2s;
}
.kpi-card:hover {
    transform: translateY(-5px);
}
.kpi-title {
    font-size: 1.1em;
    color: #6C757D;
    margin-bottom: 10px;
    font-weight: 500;
}
.kpi-value {
    font-size: 2em;
    color: #A73B24;
    font-weight: 600;
}
.data-source {
    font-size: 0.85em;
    color: #8D8D8D;
    text-align: right;
    margin-top: 10px;
    font-style: italic;
    display: block;
}
.chart-card {
    background-color: #FFFFFF;
    border-radius: 24px;
    padding: 20px;
    box-shadow: 4px 4px 0px 0px rgba(167, 59, 36, 0.15), 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    border: 3px solid #F0D9C1;
    margin-top: 15px;
    margin-bottom: 30px;
}
h1 {
    color: #A73B24 !important;
    text-align: center;
    font-weight: 600;
    text-shadow: 2px 2px 0px #FADCB3;
    margin-bottom: 30px;
}
/* Streamlit specific UI overrides */
div[data-baseweb="select"] > div {
    border-radius: 12px;
    border: 2px solid #F0D9C1;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ----------------- Data Loading -----------------
@st.cache_data
def load_data():
    df = pd.read_csv('data.csv')
    demand_mapping = {
        'Shortage': 100,
        'High Demand': 80,
        'Balanced': 50,
        'Moderate Oversupply': 20
    }
    df['Demand_Index'] = df['Demand_Status'].map(demand_mapping)
    return df

df = load_data()

# ----------------- Layout & Interaction -----------------
st.markdown("<h1>🎓 KKU Admissions & Graduate Career Outcomes</h1>", unsafe_allow_html=True)

# Filter
cluster_options = ['All Clusters'] + list(df['Cluster_Name'].unique())
selected_cluster = st.selectbox("🎯 Filter by Cluster:", cluster_options)

if selected_cluster == 'All Clusters':
    filtered_df = df
else:
    filtered_df = df[df['Cluster_Name'] == selected_cluster]

# KPI Calculations
avg_emp = filtered_df['Employment_Rate'].mean()
avg_tui = filtered_df['Tuition_Fee_Per_Term'].mean()
avg_sal = filtered_df['Starting_Salary'].mean()

# Render KPI Cards via Custom HTML
kpi_html = f"""
<div class="kpi-container">
    <div class="kpi-card">
        <div class="kpi-title">Avg Employment Rate</div>
        <div class="kpi-value">{avg_emp:.1f}%</div>
        <div class="data-source">Source: KKU Academic Administration</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Avg Tuition Fee / Term</div>
        <div class="kpi-value">{avg_tui:,.0f} ฿</div>
        <div class="data-source">Source: KKU Admissions</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-title">Avg Starting Salary</div>
        <div class="kpi-value">{avg_sal:,.0f} ฿</div>
        <div class="data-source">Source: myTCAS Stat</div>
    </div>
</div>
"""
st.markdown(kpi_html, unsafe_allow_html=True)

# Define color palette
PRIMARY_COLOR = '#A73B24'
CLUSTER_COLORS = {
    'Health Sciences': '#E27D60',
    'STEM & AI': '#85CDCA',
    'Social Sciences': '#E8A87C'
}

# ----------------- Charts -----------------
# 1. Scatter Plot
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
fig_scatter = px.scatter(
    filtered_df,
    x='Competition_Ratio',
    y='Starting_Salary',
    size='Tuition_Fee_Per_Term',
    color='Cluster_Name',
    hover_name='Major',
    color_discrete_map=CLUSTER_COLORS,
    title='<b>ROI vs Admission Competitiveness</b>',
    labels={
        'Competition_Ratio': 'Competition Ratio (Applicants : Seats)',
        'Starting_Salary': 'Starting Salary (THB)',
        'Cluster_Name': 'Cluster'
    }
)
fig_scatter.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Fredoka, sans-serif', color='#4A4A4A'),
    title_font=dict(color=PRIMARY_COLOR, size=20)
)
fig_scatter.update_traces(marker=dict(line=dict(width=2, color='DarkSlateGrey')))
st.plotly_chart(fig_scatter, use_container_width=True)
st.markdown('<span class="data-source">Source: myTCAS Stat & KKU Admissions Data</span></div>', unsafe_allow_html=True)

# 2. Dual Bar Chart
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(
    x=filtered_df['Major'],
    y=filtered_df['TCAS_Quota_Seats'],
    name='Supply (Quota Seats)',
    marker_color='#F4A261'
))
fig_bar.add_trace(go.Scatter(
    x=filtered_df['Major'],
    y=filtered_df['Demand_Index'],
    name='Market Demand Index (0-100)',
    mode='lines+markers',
    marker=dict(size=12, color=PRIMARY_COLOR),
    line=dict(width=4, color=PRIMARY_COLOR),
    yaxis='y2'
))
fig_bar.update_layout(
    title='<b>Graduate Supply vs Market Demand Gap</b>',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Fredoka, sans-serif', color='#4A4A4A'),
    title_font=dict(color=PRIMARY_COLOR, size=20),
    xaxis=dict(title='Major'),
    yaxis=dict(title='Supply (Seats)'),
    yaxis2=dict(
        title='Demand Index',
        overlaying='y',
        side='right',
        range=[0, 110]
    ),
    legend=dict(x=0.01, y=0.99, bgcolor='rgba(255,255,255,0.8)')
)
st.plotly_chart(fig_bar, use_container_width=True)
st.markdown('<span class="data-source">Source: MHESI Labor Market Report & KKU Quota Seats</span></div>', unsafe_allow_html=True)
