"""
Data loading, validation, filtering, and statistical KPI calculations
for Thailand Road Accident Analytics Dashboard.
"""

import os
import base64
import io
import pandas as pd
import numpy as np

DEFAULT_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "thailand_road_accidents.csv"
)

def load_accident_data(filepath=None):
    """Loads and standardizes the accident dataset."""
    path = filepath or DEFAULT_DATA_PATH
    if not os.path.exists(path):
        from data.generate_dataset import generate_accident_dataset
        df = generate_accident_dataset(num_records=3000)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_csv(path, index=False, encoding="utf-8-sig")
        return df
    
    df = pd.read_csv(path)
    # Ensure numerical columns
    num_cols = ["year", "month", "day", "hour", "latitude", "longitude",
                "fatalities", "serious_injuries", "slight_injuries",
                "total_casualties", "estimated_economic_loss_thb",
                "road_risk_score", "driver_behavior_risk_score"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    
    # Fill categorical nulls
    cat_cols = ["region", "province", "road_hierarchy", "managing_entity",
                "vehicle_type", "accident_cause", "period_type", "risk_level",
                "safety_equipment_used"]
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str)
            
    return df

def filter_accident_data(df, years=None, regions=None, vehicle_types=None, period_types=None, road_types=None):
    """Filters dataset according to user-selected controls."""
    filtered = df.copy()
    if years and "All" not in years:
        if not isinstance(years, list):
            years = [years]
        filtered = filtered[filtered["year"].isin(years)]
        
    if regions and "All" not in regions:
        if not isinstance(regions, list):
            regions = [regions]
        filtered = filtered[filtered["region"].isin(regions)]
        
    if vehicle_types and "All" not in vehicle_types:
        if not isinstance(vehicle_types, list):
            vehicle_types = [vehicle_types]
        filtered = filtered[filtered["vehicle_type"].isin(vehicle_types)]
        
    if period_types and "All" not in period_types:
        if not isinstance(period_types, list):
            period_types = [period_types]
        filtered = filtered[filtered["period_type"].isin(period_types)]
        
    if road_types and "All" not in road_types:
        if not isinstance(road_types, list):
            road_types = [road_types]
        filtered = filtered[filtered["road_hierarchy"].isin(road_types)]
        
    return filtered

def calculate_kpis(df):
    """Calculates executive KPI metrics from filtered data."""
    total_incidents = len(df)
    total_fatalities = int(df["fatalities"].sum()) if total_incidents > 0 else 0
    total_serious = int(df["serious_injuries"].sum()) if total_incidents > 0 else 0
    total_slight = int(df["slight_injuries"].sum()) if total_incidents > 0 else 0
    total_casualties = total_fatalities + total_serious + total_slight
    
    fatality_rate = (total_fatalities / total_incidents * 100) if total_incidents > 0 else 0.0
    total_loss_mb = (df["estimated_economic_loss_thb"].sum() / 1_000_000) if total_incidents > 0 else 0.0
    
    high_risk_incidents = len(df[df["risk_level"].str.contains("Level 3|Critical|Red", case=False, na=False)]) if total_incidents > 0 else 0
    
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
    Simulates casualty reduction and economic savings based on policy interventions:
    - speed_reduction_pct: e.g. 20 (reduces speeding-related fatal incidents by 20% * 0.7)
    - helmet_boost_pct: e.g. 25 (reduces motorcycle fatalities by 25% * 0.4)
    - drunk_reduction_pct: e.g. 30 (reduces drunk-driving fatal/serious incidents by 30% * 0.8)
    """
    sim_df = df.copy()
    
    # Calculate reduction factor for each row
    fatality_factors = np.ones(len(sim_df))
    injury_factors = np.ones(len(sim_df))
    
    # Speed intervention
    is_speed = sim_df["accident_cause"].str.contains("Speed", case=False, na=False)
    fatality_factors[is_speed] *= (1.0 - (speed_reduction_pct / 100.0) * 0.70)
    injury_factors[is_speed] *= (1.0 - (speed_reduction_pct / 100.0) * 0.50)
    
    # Drunk driving intervention
    is_drunk = sim_df["accident_cause"].str.contains("Drunk", case=False, na=False)
    fatality_factors[is_drunk] *= (1.0 - (drunk_reduction_pct / 100.0) * 0.75)
    injury_factors[is_drunk] *= (1.0 - (drunk_reduction_pct / 100.0) * 0.60)
    
    # Helmet / seatbelt boost intervention
    is_mc = sim_df["vehicle_type"].str.contains("Motorcycle", case=False, na=False)
    fatality_factors[is_mc] *= (1.0 - (helmet_boost_pct / 100.0) * 0.40)
    
    # Apply factors
    sim_df["simulated_fatalities"] = np.round(sim_df["fatalities"] * fatality_factors, 1)
    sim_df["simulated_serious"] = np.round(sim_df["serious_injuries"] * injury_factors, 1)
    sim_df["simulated_slight"] = np.round(sim_df["slight_injuries"] * injury_factors, 1)
    
    # Economic savings estimate
    fatality_diff = sim_df["fatalities"].sum() - sim_df["simulated_fatalities"].sum()
    injury_diff = sim_df["serious_injuries"].sum() - sim_df["simulated_serious"].sum()
    economic_savings_mb = (fatality_diff * 5.0) + (injury_diff * 0.8)  # ~5M THB per life, ~800k per serious injury
    
    return {
        "baseline_fatalities": int(sim_df["fatalities"].sum()),
        "simulated_fatalities": round(sim_df["simulated_fatalities"].sum(), 1),
        "fatalities_saved": round(fatality_diff, 1),
        "baseline_serious": int(sim_df["serious_injuries"].sum()),
        "simulated_serious": round(sim_df["simulated_serious"].sum(), 1),
        "serious_prevented": round(injury_diff, 1),
        "economic_savings_mb": round(max(economic_savings_mb, 0.0), 2)
    }
