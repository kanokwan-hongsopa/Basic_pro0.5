"""
Data loading, validation, filtering, and statistical KPI calculations
for Thailand Road Accident Analytics Dashboard.

Strict Rule: Uses REAL Thai Government Open Data only.
Default path: data/processed/thailand_road_accidents_real.csv
No synthetic, random, or mock records are generated.
"""

import os
import io
import base64
import pandas as pd
import numpy as np

DEFAULT_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "processed",
    "thailand_road_accidents_real.csv"
)

def load_accident_data(filepath=None):
    """
    Loads and standardizes the real official government accident dataset.
    Raises FileNotFoundError if data is missing, directing user to ingestion script.
    Never generates synthetic or mock records.
    """
    path = filepath or DEFAULT_DATA_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Official processed government dataset not found at '{path}'.\n"
            "Please run:\n"
            "  python scripts/fetch_real_government_data.py\n"
            "  python scripts/build_processed_dataset.py\n"
            "to ingest and build the real dataset from official open data portals."
        )

    df = pd.read_csv(path, low_memory=False)

    # Numerical columns to coerce
    num_cols = [
        "year", "month", "day", "hour",
        "fatalities", "serious_injuries", "slight_injuries", "injuries",
        "total_casualties", "economic_loss", "estimated_economic_loss_thb"
    ]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Coordinates: coerce to numeric, keeping invalid/null coordinates as NaN (never fake them)
    for coord in ["latitude", "longitude"]:
        if coord in df.columns:
            df[coord] = pd.to_numeric(df[coord], errors="coerce")

    # Categorical columns
    cat_cols = [
        "incident_id", "incident_date", "region", "province",
        "road_type", "road_agency", "road_hierarchy", "managing_entity",
        "vehicle_type", "accident_cause", "period_type", "risk_level",
        "source_agency", "source_dataset", "source_resource_id", "source_url", "source_year"
    ]
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str)

    return df

def filter_accident_data(df, years=None, regions=None, vehicle_types=None, period_types=None, road_types=None):
    """Filters dataset according to user-selected controls."""
    filtered = df.copy()
    if years and "All" not in years and "All Years" not in years:
        if not isinstance(years, list):
            years = [years]
        # Allow both int and str matching
        int_years = [int(y) for y in years if str(y).isdigit()]
        filtered = filtered[filtered["year"].isin(int_years)]

    if regions and "All" not in regions and "All Regions" not in regions:
        if not isinstance(regions, list):
            regions = [regions]
        filtered = filtered[filtered["region"].isin(regions)]

    if vehicle_types and "All" not in vehicle_types and "All Vehicles" not in vehicle_types:
        if not isinstance(vehicle_types, list):
            vehicle_types = [vehicle_types]
        filtered = filtered[filtered["vehicle_type"].isin(vehicle_types)]

    if period_types and "All" not in period_types and "All Periods" not in period_types:
        if not isinstance(period_types, list):
            period_types = [period_types]
        filtered = filtered[filtered["period_type"].isin(period_types)]

    if road_types and "All" not in road_types and "All Road Types" not in road_types:
        if not isinstance(road_types, list):
            road_types = [road_types]
        road_col = "road_hierarchy" if "road_hierarchy" in filtered.columns else "road_type"
        filtered = filtered[filtered[road_col].isin(road_types)]

    return filtered

def calculate_kpis(df):
    """Calculates executive KPI metrics from filtered real government data."""
    total_incidents = len(df)
    total_fatalities = int(df["fatalities"].sum()) if total_incidents > 0 and "fatalities" in df.columns else 0
    total_serious = int(df["serious_injuries"].sum()) if total_incidents > 0 and "serious_injuries" in df.columns else 0
    total_slight = int(df["slight_injuries"].sum()) if total_incidents > 0 and "slight_injuries" in df.columns else 0
    total_casualties = total_fatalities + total_serious + total_slight

    fatality_rate = (total_fatalities / total_incidents * 100) if total_incidents > 0 else 0.0

    loss_col = "economic_loss" if "economic_loss" in df.columns else ("estimated_economic_loss_thb" if "estimated_economic_loss_thb" in df.columns else None)
    total_loss_mb = (df[loss_col].sum() / 1_000_000) if total_incidents > 0 and loss_col else 0.0

    # High risk incidents: incidents resulting in fatalities
    if "risk_level" in df.columns:
        high_risk_incidents = len(df[df["risk_level"].str.contains("Level 3|Critical|Fatal", case=False, na=False)]) if total_incidents > 0 else 0
    elif "fatalities" in df.columns:
        high_risk_incidents = len(df[df["fatalities"] > 0]) if total_incidents > 0 else 0
    else:
        high_risk_incidents = 0

    return {
        "total_incidents": total_incidents,
        "total_fatalities": total_fatalities,
        "total_serious": total_serious,
        "total_slight": total_slight,
        "total_casualties": total_casualties,
        "fatality_rate": round(fatality_rate, 2),
        "total_loss_mb": round(total_loss_mb, 1),
        "high_risk_incidents": high_risk_incidents,
        "high_risk_share": round((high_risk_incidents / total_incidents * 100), 1) if total_incidents > 0 else 0.0
    }

def parse_uploaded_file(contents, filename):
    """Parses user-uploaded CSV or Excel file."""
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    try:
        if "csv" in filename.lower():
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8-sig", errors="ignore")))
        elif "xls" in filename.lower():
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return None, "Unsupported file format. Please upload a CSV or Excel (.xlsx) file."
        return df, None
    except Exception as e:
        return None, f"Error parsing file: {str(e)}"

def run_policy_simulation(df, speed_reduction_pct=0.0, helmet_boost_pct=0.0, drunk_reduction_pct=0.0):
    """
    Model-based what-if policy scenario analysis:
    - Input baseline: Observed real government casualty statistics from df
    - Output: Scenario Simulation / Estimated Result (clearly labeled, not observed data)
    
    Simulation assumptions & elasticity formulas:
    - Speed reduction: reduces speeding-related fatalities by (speed_pct * 0.70) and serious injuries by (speed_pct * 0.50)
      (Based on Nilsson's Power Model for road traffic speed elasticity)
    - Helmet/safety equipment boost: reduces motorcycle-related fatalities by (boost_pct * 0.40)
      (Based on WHO Road Safety / Elvik 2009 helmet protection factor)
    - Drunk driving crackdown: reduces alcohol-related fatal incidents by (drunk_pct * 0.75) and serious injuries by (drunk_pct * 0.60)
    - Economic valuation: 5.0M THB saved per fatality prevented, 0.8M THB saved per serious injury prevented
      (Department of Highways & TDRI casualty cost model)
    """
    sim_df = df.copy()
    n_rows = len(sim_df)
    if n_rows == 0:
        return {
            "baseline_fatalities": 0, "simulated_fatalities": 0.0, "fatalities_saved": 0.0,
            "baseline_serious": 0, "simulated_serious": 0.0, "serious_prevented": 0.0,
            "economic_savings_mb": 0.0
        }

    fatality_factors = np.ones(n_rows, dtype=float)
    injury_factors = np.ones(n_rows, dtype=float)

    # 1. Speed intervention
    if "accident_cause" in sim_df.columns:
        is_speed = sim_df["accident_cause"].str.contains("Speed|เร็ว", case=False, na=False)
        fatality_factors[is_speed] *= max(0.0, (1.0 - (speed_reduction_pct / 100.0) * 0.70))
        injury_factors[is_speed] *= max(0.0, (1.0 - (speed_reduction_pct / 100.0) * 0.50))

    # 2. Drunk driving intervention
    if "accident_cause" in sim_df.columns:
        is_drunk = sim_df["accident_cause"].str.contains("Drunk|เมา|สุรา", case=False, na=False)
        fatality_factors[is_drunk] *= max(0.0, (1.0 - (drunk_reduction_pct / 100.0) * 0.75))
        injury_factors[is_drunk] *= max(0.0, (1.0 - (drunk_reduction_pct / 100.0) * 0.60))

    # 3. Helmet / Safety gear boost intervention
    if "vehicle_type" in sim_df.columns:
        is_mc = sim_df["vehicle_type"].str.contains("Motorcycle|จักรยานยนต์|มอเตอร์ไซค์", case=False, na=False)
        fatality_factors[is_mc] *= max(0.0, (1.0 - (helmet_boost_pct / 100.0) * 0.40))

    # Apply factor vectors
    fatalities_col = "fatalities" if "fatalities" in sim_df.columns else "dead_total"
    serious_col = "serious_injuries" if "serious_injuries" in sim_df.columns else "injury_severe_total"

    base_fatalities = float(sim_df[fatalities_col].sum()) if fatalities_col in sim_df.columns else 0.0
    base_serious = float(sim_df[serious_col].sum()) if serious_col in sim_df.columns else 0.0

    sim_fatalities = float(np.sum(sim_df[fatalities_col].values * fatality_factors)) if fatalities_col in sim_df.columns else 0.0
    sim_serious = float(np.sum(sim_df[serious_col].values * injury_factors)) if serious_col in sim_df.columns else 0.0

    fatality_diff = max(0.0, base_fatalities - sim_fatalities)
    serious_diff = max(0.0, base_serious - sim_serious)

    # Economic savings: 5M THB per fatality, 0.8M THB per serious injury
    economic_savings_mb = (fatality_diff * 5.0) + (serious_diff * 0.8)

    return {
        "baseline_fatalities": int(round(base_fatalities)),
        "simulated_fatalities": round(sim_fatalities, 1),
        "fatalities_saved": round(fatality_diff, 1),
        "baseline_serious": int(round(base_serious)),
        "simulated_serious": round(sim_serious, 1),
        "serious_prevented": round(serious_diff, 1),
        "economic_savings_mb": round(max(economic_savings_mb, 0.0), 2)
    }
