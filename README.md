# KKU Admissions & Graduate Career Outcomes Dashboard

## Dashboard Goal
Create an Interactive Dashboard to compare the **"Return on Investment (ROI) and Educational Value"** alongside the **"Admission Competitiveness"** of Khon Kaen University (KKU).

## Project Scope & Requirements
A multi-tab Python Dash/Plotly Dashboard focusing on:
- KKU student statistics
- Official TCAS admission metrics (capacity, applicants, competition rates, and score statistics from KKU Admissions and myTCAS)
- Tuition fees
- Employment rates and starting salaries
- Labor market demands and skill mismatches

### 1. Real Data Integration & Verified Sources
- Ingest strictly real-world open data and official statistics from KKU's Academic Administration and Development Division, KKU Admissions, myTCAS Stat portal, and MHESI.
- **Mandatory Requirement**: Every single card, table, and chart MUST display its official source/reference citation clearly underneath to verify data authenticity.

### 2. Cross-Table & Interactivity Linking
- Dynamic cross-filtering and synchronization across all tables, charts, and tabs.
- Selecting a metric or filter in one component must instantly update all related data views across the entire dashboard.

### 3. Visual Design & Theme
- **Aesthetic**: Cute, playful, retro-cartoon style with soft rounded elements (`border-radius: 16px - 24px`) and soft card shadows.
- **Primary Brand Color**: Terracotta / Brick Red - `HEX #A73B24` (RGB: 167, 59, 36 | CMYK: C24 M88 Y99 K17).
- Harmonize `#A73B24` with creamy backgrounds, warm pastel tones, and clean typography to deliver a cozy and highly engaging cartoon dashboard feel.

### 4. Key Visualizations
- **Top Metrics Row (KPI Cards)**: Overall employment rate, average tuition fee per term, and average starting salary.
- **Scatter Plot (ROI vs Competitiveness)**: X-axis: Competition Ratio, Y-axis: Starting Salary, Bubble Size: Tuition Fee, Color: Cluster.
- **Dual Bar Chart (Demand vs Supply Gap)**: Compare Supply (Graduates) with Market Demand Index.
- **Filter**: Users can filter data by faculty cluster (Health, STEM, Social Sciences).

## Data Schema Reference
Data ingestion contract (CSV format):
```csv
Cluster_Name,Faculty,Major,TCAS_Quota_Seats,TCAS_Applicants,Competition_Ratio,Tuition_Fee_Per_Term,Employment_Rate,Starting_Salary,Demand_Status
Health Sciences,Medicine,Medicine,280,3500,12.5,18000,98.5,45000,Shortage
Health Sciences,Pharmacy,Pharmacy,120,3800,31.6,18000,96.0,28000,High Demand
STEM & AI,Computing,Data Science & AI,60,1100,18.3,15000,93.5,30000,High Demand
STEM & AI,Engineering,Robotics Engineering,40,650,16.2,30000,94.0,32000,High Demand
Social Sciences,Law,Law,300,2800,9.3,10000,85.0,18000,Balanced
```

JSON Protocol Context:
```json
{
  "university": "Khon Kaen University",
  "data_scope": ["TCAS Admissions", "Tuition Fees", "Graduate Outcomes", "Labor Demand"],
  "tcas_distribution": {
    "Round1_Portfolio": 25,
    "Round2_Quota_NE": 55,
    "Round3_Admission": 20
  },
  "clusters": [
    {
      "name": "Health Sciences",
      "competition_ratio_avg": 95.0,
      "avg_starting_salary": 32000,
      "employment_rate_pct": 96.5,
      "tuition_per_term": 18000,
      "market_demand_status": "High Demand / Shortage"
    }
  ]
}
```
