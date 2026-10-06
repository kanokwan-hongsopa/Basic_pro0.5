# 🚗 Thailand Road Accident Analytics & Safety Dashboard

> **Interactive Road Safety Analytics, Blackspot Risk Modeling, and Policy Simulation System**

---

## 📌 Project Overview

Thailand's road traffic injuries and fatalities remain among the highest in Southeast Asia. This project delivers an enterprise-grade, interactive analytics dashboard and risk management system designed for **road safety analysts, policy makers, traffic police, transport department officials, and the public**.

The system synthesizes open government road accident data (Department of Highways, ThaiRSC, Royal Thai Police, and Department of Land Transport) into actionable intelligence through interactive spatial analysis, causal breakdown, risk mismatch modeling, and an interactive simulation engine for policy evaluation.

---

## 🎯 Key Business Questions & Dashboard Architecture

The dashboard is structured into three analytical tabs aligned with the Business Requirements Document (BRD):

### 1. 📊 Tab 1: Casualties & Vehicle Analytics (ปริมาณอุบัติเหตุและผลกระทบตามประเภทยานพาหนะ)
- **Accident & Casualty Trends by Year (2020–2026):** Multi-line/area time-series analysis comparing incident frequency, non-fatal injuries, and fatalities.
- **Vehicle Type Distribution:** Treemap and bar visualizations contrasting motorcycles, private cars, commercial trucks, and public transport.
- **Casualty Timeline & Severity Tracking:** Stacked tracking of medical outcomes (slight injury, severe injury, fatal) across seasons and festivals (e.g., New Year, Songkran).
- **Financial & Economic Loss Impact:** KPI summary cards and box plots estimating economic loss, medical expenses, and compensation costs.

### 2. 🗺️ Tab 2: Risk Zones, Causes & Operations (จุดเสี่ยง ปัจจัยการเกิดเหตุ และหน่วยงานดูแล)
- **High-Risk Blackspots & Geospatial Risk Map:** Interactive geographic map plotting accident clusters across Thailand with risk classification:
  - 🟢 **Level 1 (Low Risk / Baseline):** Minor collisions, property damage only.
  - 🟡 **Level 2 (Moderate Risk / Surveillance):** Recurring collisions, non-fatal injuries.
  - 🔴 **Level 3 (High Risk / Critical Blackspot):** Fatal accidents, multi-vehicle pileups, severe casualties.
- **Root Cause Pareto Analysis:** Horizontal bar and Pareto ranking of primary accident causes (Speeding, Drunk Driving, Cutting off, Road Defects, Driver Fatigue).
- **Managing Entities & Fleet Operators:** Donut and distribution analysis of responsible road agencies (Department of Highways - DOH, Department of Rural Roads - DRR, Local Municipalities - BMA/Local) and commercial transport operators.
- **Severity Index by Road Hierarchy:** Violin and grouped bar analysis examining severity across National Highways, Rural Highways, and Urban Roads.

### 3. 🔬 Tab 3: Risk Mismatch & Gap Simulation (การวิเคราะห์ความเสี่ยงซ้อนทับและการจำลองสถานการณ์)
- **Safety Capability vs. Risk Exposure Matrix:** 4-Quadrant scatter plot analyzing road infrastructure risk vs. driver behavioral risk to identify high-danger mismatch zones.
- **Safety Equipment Gap Analysis:** Radar comparison of safety compliance (helmet and seatbelt usage rates) against actual casualty rates across regions.
- **Real-Time Simulation & Recalculation Engine:** Interactive editable data table allowing analysts to simulate safety interventions (e.g., reducing speeding by 20%, increasing helmet compliance by 30%) and instantly observe recalculated casualty projections.

---

## 🛠️ Technology Stack & Requirements

- **Backend / Web Application:** Python 3.10+ (Dash, Plotly, Dash Bootstrap Components, Flask)
- **Data Manipulation & Computation:** Pandas, NumPy
- **Interactive Geospatial & Visuals:** Plotly Express, Plotly Graph Objects, Mapbox / OpenStreetMap
- **Styling & Theme:** Modern Dark Slate Analytics Theme with Safety Indicators:
  - Critical Red (`#FF4136`)
  - Warning Amber (`#FFDC00`)
  - Safe Green (`#2ECC40`)
  - Dark Slate Canvas (`#0F172A` / `#1E293B`)
- **Standalone Client Option:** Single-file interactive HTML dashboard (`index.html`) using Tailwind CSS and Chart.js/Plotly.js for instant deployment without local server setup.

---

## 📂 Project Structure

```text
Basic_pro0.5/
│
├── README.md                                         # Main project documentation & specification
├── PROJECT_STATUS.md                                 # Step-by-step implementation progress tracker
├── requirements.txt                                  # Python dependencies
│
├── brd_thailand_road_accident_analytics_dashboard.md # Business Requirements Document
├── thailand_road_accident_analysis.md                # System Architecture & Open Data Catalog
│
├── app.py                                            # Main Python Dash full-featured web application
├── index.html                                        # Standalone zero-dependency interactive dashboard
│
├── data/
│   ├── generate_dataset.py                           # Synthetic & open data generator script
│   └── thailand_road_accidents.csv                   # Structured Thailand road accident dataset
│
├── components/                                       # Dash modular UI components
│   ├── tab_casualties.py                             # Tab 1: Casualties & Vehicle Impact
│   ├── tab_risk_zones.py                             # Tab 2: Risk Zones & Causes
│   └── tab_risk_mismatch.py                          # Tab 3: Risk Mismatch & Simulation Engine
│
└── utils/                                            # Utility helpers
    ├── data_loader.py                                # Data parsing, validation, and aggregations
    └── style_constants.py                            # Dark theme palette, layouts, and typography
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10 or higher
- `pip` package manager

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/kanokwan-hongsopa/Basic_pro0.5.git
cd Basic_pro0.5

# Install dependencies
pip install -r requirements.txt
```

### 3. Generate or Inspect Dataset
```bash
python data/generate_dataset.py
```

### 4. Run the Dash Application
```bash
python app.py
```
Open your web browser and navigate to `http://127.0.0.1:8050/`.

### 5. Run the Standalone Browser Version
Alternatively, open `index.html` directly in any modern browser for a lightweight, single-file interactive experience.

---

## 📄 Open Data Attribution & Licenses
- Department of Highways (DOH) Open Data Portal ([data.go.th/dataset/roadaccident](https://data.go.th/dataset/roadaccident))
- Thailand Road Safety Collaboration (ThaiRSC) ([thairsc.com](https://www.thairsc.com/))
- Royal Thai Police (RTP) Traffic Statistics Portal ([data.go.th/organization/rtp](https://data.go.th/organization/rtp))
- Department of Land Transport (DLT) Vehicle Registration Data ([data.go.th/organization/dlt](https://data.go.th/organization/dlt))

Licensed under the Open Government Data License & MIT License.
