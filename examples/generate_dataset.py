"""
Synthetic & Open Data Pipeline for Thailand Road Accident Analytics
Generates realistic accident microdata based on Department of Highways,
ThaiRSC, Royal Thai Police, and DLT patterns (2020-2026).
"""

import os
import numpy as np
import pandas as pd

def generate_accident_dataset(num_records=2500, random_seed=42):
    np.random.seed(random_seed)

    provinces_info = [
        {"province": "Bangkok", "region": "Bangkok & Vicinity", "lat": 13.7563, "lon": 100.5018, "weight": 0.22},
        {"province": "Nonthaburi", "region": "Bangkok & Vicinity", "lat": 13.8621, "lon": 100.5134, "weight": 0.06},
        {"province": "Chiang Mai", "region": "North", "lat": 18.7883, "lon": 98.9853, "weight": 0.10},
        {"province": "Chiang Rai", "region": "North", "lat": 19.9105, "lon": 99.8406, "weight": 0.05},
        {"province": "Phitsanulok", "region": "North", "lat": 16.8211, "lon": 100.2659, "weight": 0.04},
        {"province": "Nakhon Ratchasima", "region": "Northeast", "lat": 14.9799, "lon": 102.0978, "weight": 0.11},
        {"province": "Khon Kaen", "region": "Northeast", "lat": 16.4322, "lon": 102.8236, "weight": 0.07},
        {"province": "Ubon Ratchathani", "region": "Northeast", "lat": 15.2448, "lon": 104.8473, "weight": 0.05},
        {"province": "Chonburi", "region": "Central", "lat": 13.3611, "lon": 100.9847, "weight": 0.10},
        {"province": "Ayutthaya", "region": "Central", "lat": 14.3532, "lon": 100.5684, "weight": 0.04},
        {"province": "Saraburi", "region": "Central", "lat": 14.5289, "lon": 100.9108, "weight": 0.04},
        {"province": "Phuket", "region": "South", "lat": 7.8804, "lon": 98.3923, "weight": 0.05},
        {"province": "Surat Thani", "region": "South", "lat": 9.1382, "lon": 99.3215, "weight": 0.04},
        {"province": "Songkhla", "region": "South", "lat": 7.1756, "lon": 100.6143, "weight": 0.03},
    ]

    prov_weights = [p["weight"] for p in provinces_info]
    prov_weights = np.array(prov_weights) / sum(prov_weights)
    selected_indices = np.random.choice(len(provinces_info), size=num_records, p=prov_weights)

    years = np.random.choice([2020, 2021, 2022, 2023, 2024, 2025, 2026], size=num_records, p=[0.12, 0.13, 0.15, 0.16, 0.16, 0.15, 0.13])
    months = np.random.randint(1, 13, size=num_records)
    days = np.random.randint(1, 29, size=num_records)
    hours = np.random.randint(0, 24, size=num_records)

    vehicle_types = ["Motorcycle", "Private Car", "Commercial Truck", "Public Bus/Van"]
    vehicle_p = [0.55, 0.25, 0.12, 0.08]
    vehicles = np.random.choice(vehicle_types, size=num_records, p=vehicle_p)

    causes = [
        "Speeding (ขับรถเร็วเกินกำหนด)",
        "Cutting off abruptly (ตัดหน้ากระชั้นชิด)",
        "Drunk driving (เมาแล้วขับ)",
        "Fatigue / Falling asleep (หลับใน)",
        "Road defect / Slippery surface (ถนนชำรุด/ลื่น)",
        "Running red light / Signal violation (ฝ่าฝืนสัญญาณไฟ)",
    ]
    causes_p = [0.38, 0.22, 0.16, 0.11, 0.08, 0.05]
    accident_causes = np.random.choice(causes, size=num_records, p=causes_p)

    road_hierarchies = [
        "National Highway (ทางหลวงแผ่นดิน)",
        "Rural Road (ทางหลวงชนบท)",
        "Urban / City Road (ถนนในเมือง/ท้องถิ่น)",
        "Expressway (ทางพิเศษ)",
    ]
    road_p = [0.48, 0.24, 0.20, 0.08]
    roads = np.random.choice(road_hierarchies, size=num_records, p=road_p)

    def assign_entity(road):
        if "National" in road:
            return "Department of Highways (DOH - กรมทางหลวง)"
        elif "Rural" in road:
            return "Department of Rural Roads (DRR - กรมทางหลวงชนบท)"
        elif "Expressway" in road:
            return "EXAT (การทางพิเศษแห่งประเทศไทย)"
        else:
            return "Local Administration / BMA (อปท./กทม.)"

    managing_entities = [assign_entity(r) for r in roads]

    festivals = []
    for m, d in zip(months, days):
        if (m == 12 and d >= 28) or (m == 1 and d <= 4):
            festivals.append("New Year Festival (เทศกาลปีใหม่)")
        elif m == 4 and (10 <= d <= 17):
            festivals.append("Songkran Festival (เทศกาลสงกรานต์)")
        else:
            festivals.append("Normal Period (ช่วงเวลาปกติ)")

    # Lat/Lon with realistic jitter
    lats = []
    lons = []
    provinces = []
    regions = []
    for idx in selected_indices:
        p = provinces_info[idx]
        provinces.append(p["province"])
        regions.append(p["region"])
        lats.append(round(p["lat"] + np.random.normal(0, 0.09), 5))
        lons.append(round(p["lon"] + np.random.normal(0, 0.09), 5))

    # Calculate severity and casualties based on vehicle, cause, speed
    fatalities = []
    serious_injuries = []
    slight_injuries = []
    risk_levels = []
    economic_losses = []
    safety_equip_used = []
    road_risk_scores = []
    driver_behavior_scores = []

    for v, c, r, fest, h in zip(vehicles, accident_causes, roads, festivals, hours):
        base_fatality_prob = 0.05
        if v == "Motorcycle":
            base_fatality_prob += 0.09
        elif v == "Commercial Truck":
            base_fatality_prob += 0.06

        if "Speeding" in c or "Drunk" in c:
            base_fatality_prob += 0.08
        if "National Highway" in r:
            base_fatality_prob += 0.04
        if fest != "Normal Period (ช่วงเวลาปกติ)":
            base_fatality_prob += 0.05
        if 0 <= h <= 5 or 22 <= h <= 23:
            base_fatality_prob += 0.05

        has_helmet_seatbelt = np.random.rand() > (0.45 if v == "Motorcycle" else 0.20)
        safety_equip_used.append("Yes" if has_helmet_seatbelt else "No")
        if not has_helmet_seatbelt:
            base_fatality_prob += 0.08

        # Determine fatalities
        if np.random.rand() < base_fatality_prob:
            fat = np.random.choice([1, 2, 3], p=[0.82, 0.14, 0.04])
            ser = np.random.choice([0, 1, 2], p=[0.4, 0.4, 0.2])
            sli = np.random.choice([0, 1], p=[0.6, 0.4])
            risk = "Level 3: Critical Blackspot (Red Zone)"
        else:
            fat = 0
            if np.random.rand() < 0.45:
                ser = np.random.choice([1, 2], p=[0.75, 0.25])
                sli = np.random.choice([1, 2, 3], p=[0.5, 0.35, 0.15])
                risk = "Level 2: Moderate Risk (Surveillance Zone)"
            else:
                ser = 0
                sli = np.random.choice([0, 1], p=[0.4, 0.6])
                risk = "Level 1: Low Risk (Baseline Zone)"

        fatalities.append(fat)
        serious_injuries.append(ser)
        slight_injuries.append(sli)
        risk_levels.append(risk)

        # Economic loss calculation (THB)
        # Death avg: ~5-10M THB, Serious injury: ~500k-1.5M THB, Slight: ~30k-100k THB, Vehicle: ~50k-500k THB
        veh_cost = 50000 if v == "Motorcycle" else (250000 if v == "Private Car" else 750000)
        direct_loss = (fat * np.random.uniform(3500000, 6000000) +
                       ser * np.random.uniform(400000, 1200000) +
                       sli * np.random.uniform(20000, 80000) +
                       veh_cost * np.random.uniform(0.5, 1.8))
        economic_losses.append(round(direct_loss, 2))

        # Risk Mismatch Matrix Scores (0 - 100)
        road_score = np.random.normal(55 if "National" in r else 40, 15)
        behavior_score = np.random.normal(65 if ("Speeding" in c or "Drunk" in c) else 38, 16)
        road_risk_scores.append(round(min(max(road_score, 10.0), 98.0), 1))
        driver_behavior_scores.append(round(min(max(behavior_score, 10.0), 98.0), 1))

    df = pd.DataFrame({
        "incident_id": [f"THA-{2020+i%7}-{100000+i}" for i in range(num_records)],
        "year": years,
        "month": months,
        "day": days,
        "hour": hours,
        "date": [f"{y}-{m:02d}-{d:02d}" for y, m, d in zip(years, months, days)],
        "region": regions,
        "province": provinces,
        "latitude": lats,
        "longitude": lons,
        "road_hierarchy": roads,
        "managing_entity": managing_entities,
        "vehicle_type": vehicles,
        "accident_cause": accident_causes,
        "period_type": festivals,
        "risk_level": risk_levels,
        "safety_equipment_used": safety_equip_used,
        "fatalities": fatalities,
        "serious_injuries": serious_injuries,
        "slight_injuries": slight_injuries,
        "total_casualties": [f + s + sl for f, s, sl in zip(fatalities, serious_injuries, slight_injuries)],
        "estimated_economic_loss_thb": economic_losses,
        "road_risk_score": road_risk_scores,
        "driver_behavior_risk_score": driver_behavior_scores,
    })

    return df

if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "thailand_road_accidents.csv")
    print(f"Generating Thailand road accident dataset to {csv_path}...")
    dataset = generate_accident_dataset(num_records=3000)
    dataset.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"Success! Generated {len(dataset)} records. Columns: {list(dataset.columns)}")
