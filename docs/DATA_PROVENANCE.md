# 🏛️ Data Provenance & Lineage Specification
## Thailand Road Accident Analytics & Safety Dashboard

> **Document Version:** 1.0.0  
> **Published Date:** October 2026  
> **Source Origin:** Official Open Government Data Portal of Thailand ([data.go.th](https://data.go.th) & [datagov.mot.go.th](https://datagov.mot.go.th))

---

## 📌 Architectural Purpose & Integrity Principles

This document defines the strict data taxonomy and provenance architecture implemented across the **Thailand Road Accident Analytics Dashboard**. To guarantee auditability and statistical integrity:
1. **Zero Fabrication Policy:** No synthetic, mock, placeholder, random, or fabricated accident records exist in the production pipeline.
2. **Deterministic Source Traceability:** Every individual row in `data/processed/thailand_road_accidents_real.csv` is traceable to its official Open Data CKAN package, resource ID, and government publication URL.
3. **Explicit Three-Tier Taxonomy:** Every dashboard component and variable is explicitly categorized into one of three classifications:
   - **Tier A:** Real Observed Government Data
   - **Tier B:** Derived / Calculated Metrics (Deterministic Mathematical Formulations)
   - **Tier C:** Scenario Simulation Estimates (Policy What-If Models)

---

## 🗂️ Tier A: Real Observed Government Data

All records in this tier are direct empirical observations recorded by traffic safety officers, highway engineers, and emergency services under the Ministry of Transport network.

| Variable Name | Thai Source Column | Official Agency | Description / Data Type | Observation Coverage |
| :--- | :--- | :--- | :--- | :--- |
| `incident_id` | `ACC_CODE` | Ministry of Transport / DOH | Unique government incident code | 148,614 records (100%) |
| `year` | `ปีที่เกิดเหตุ` | MOT Information Center | Budget/Calendar year of crash | 2020 – 2026 |
| `incident_date` | `วันที่เกิดเหตุ` | MOT / DOH / DRR | Standardized incident date (`YYYY-MM-DD`) | 100% valid dates |
| `month`, `day`, `hour` | `วันที่เกิดเหตุ`, `เวลา` | Highway Patrol / DOH | Temporal timestamp breakdown | 100% parsed |
| `province` | `จังหวัด` | Royal Thai Government | Official Thai province name | 77 provinces |
| `latitude` | `LATITUDE` | DOH / DRR GPS Log | GPS WGS84 Latitude coordinate | 99.36% observed (0.64% unrecorded) |
| `longitude` | `LONGITUDE` | DOH / DRR GPS Log | GPS WGS84 Longitude coordinate | 99.36% observed (0.64% unrecorded) |
| `vehicle_type` | `รถคันที่1` / `accident_vehicle` | Transport Officers | First/primary vehicle involved in crash | 100% categorized |
| `accident_cause` | `มูลเหตุสันนิษฐาน` | Investigating Highway Engineers | Primary presumed cause of collision | 100% observed |
| `road_type` / `road_hierarchy` | `สายทางหน่วยงาน` | DOH / DRR / EXAT | Jurisdiction line classification (Highway, Rural, Expressway) | 100% observed |
| `road_agency` / `managing_entity` | `หน่วยงาน` | Ministry of Transport | Responsible government authority (DOH, DRR, EXAT) | 100% observed |
| `fatalities` | `ผู้เสียชีวิต` / `จำนวนผู้เสียชีวิต` | Ministry of Public Health / Police / DOH | Verified death toll at scene or hospital | 19,302 lives |
| `serious_injuries` | `ผู้บาดเจ็บสาหัส` | Emergency Medical / DOH | Severe bodily trauma requiring admission | 19,801 cases |
| `slight_injuries` | `ผู้บาดเจ็บเล็กน้อย` | Emergency Medical / DOH | Minor trauma not requiring hospitalization | 101,737 cases |
| `injuries` | `รวมจำนวนผู้บาดเจ็บ` | Calculated official sum | Sum of serious and slight injuries | 121,538 cases |

### Official Government Repositories Used:
- **Ministry of Transport Open Data Portal:** [datagov.mot.go.th](https://datagov.mot.go.th)
  - Dataset: *อุบัติเหตุบนโครงข่ายถนนของกระทรวงคมนาคม (roadaccident)*
  - Organization: ศูนย์เทคโนโลยีสารสนเทศและการสื่อสาร สำนักงานปลัดกระทรวงคมนาคม
- **Department of Highways (DOH):** [doh.go.th](https://www.doh.go.th)
  - Extracted Highway Network Records: 137,933 incidents
- **Department of Rural Roads (DRR):** [dataportal.drr.go.th](https://dataportal.drr.go.th)
  - Dataset: *ข้อมูลอุบัติเหตุ กรมทางหลวงชนบท (dataset_21_06)*
  - Extracted Rural Roads Records: 7,852 incidents
- **Expressway Authority of Thailand (EXAT):** [catalog.exat.co.th](https://catalog.exat.co.th)
  - Extracted Expressway Incidents: 2,829 incidents

---

## 📐 Tier B: Derived / Calculated Metrics

Derived metrics are calculated strictly from Tier A observed government variables using official government methodologies, deterministic domain rules, or spatial standards. No stochastic or synthetic noise is introduced.

| Metric Name | Formula / Mapping Rule | Authoritative Benchmark / Source | Purpose |
| :--- | :--- | :--- | :--- |
| `region` | Deterministic geographic mapping from `province` (Bangkok & Vicinity, Central, North, Northeast, East, West, South) | NESDC (สภาพัฒน์) & Royal Society Geographic Division | Standard macro-regional aggregation |
| `total_casualties` | $\text{fatalities} + \text{serious\_injuries} + \text{slight\_injuries}$ | WHO Global Status Report on Road Safety | Total human health impact per incident |
| `fatality_rate` | $\frac{\text{Total Fatalities}}{\text{Total Incidents}} \times 100$ | Department of Land Transport (DLT) KPI formula | Incident severity index |
| `economic_loss` (`estimated_economic_loss_thb`) | $(\text{fatalities} \times 5,000,000) + (\text{serious} \times 800,000) + (\text{slight} \times 100,000)$ | Department of Highways Road Research Office & TDRI (Thailand Development Research Institute) | Standard economic loss evaluation in Thai Baht (THB) |
| `period_type` | Date interval matching: Dec 29–Jan 4 $\to$ *New Year Festival*, Apr 11–Apr 17 $\to$ *Songkran Festival*, Otherwise $\to$ *Normal Period* | National Road Safety Directing Center (ศปถ.) "7 Dangerous Days" Campaign Calendar | Campaign and seasonal casualty tracking |
| `risk_level` | $\text{fatalities} > 0 \to \text{Level 3: Critical (Fatal)}$; $\text{serious} > 0 \to \text{Level 2: Moderate}$; Else $\to \text{Level 1: Low}$ | DOH Road Safety Hazard Classification Standard | Blackspot visual hierarchy on geospatial map |

---

## 🧪 Tier C: Scenario Simulation Estimates

Simulation outputs are generated by policy elasticity models. They are **never presented as observed government statistics** and are explicitly rendered with warning badges: `Scenario Simulation / Estimated Result`.

### 1. Underlying Model Equations

The policy simulation engine operates on real baseline records ($\text{filtered\_df}$) according to three policy interventions:

$$\text{Simulated Fatalities} = \sum_{i} \text{fatalities}_i \times \prod_{k \in \{\text{speed}, \text{drunk}, \text{gear}\}} \left(1 - \frac{\Delta P_k}{100} \cdot E_k^{\text{fatal}}\right)$$

$$\text{Simulated Serious Injuries} = \sum_{i} \text{serious}_i \times \prod_{k \in \{\text{speed}, \text{drunk}, \text{gear}\}} \left(1 - \frac{\Delta P_k}{100} \cdot E_k^{\text{injury}}\right)$$

### 2. Elasticity Coefficients ($E_k$)

| Policy Intervention | Variable Target | Fatality Elasticity ($E_k^{\text{fatal}}$) | Injury Elasticity ($E_k^{\text{injury}}$) | Academic / Empirical Reference |
| :--- | :--- | :---: | :---: | :--- |
| **Speed Limit Enforcement** | Incidents where `accident_cause` contains *Speeding* | **0.70** | **0.50** | **Nilsson's Power Model (2004)** for road traffic speed changes |
| **Drunk Driving Crackdown** | Incidents where `accident_cause` contains *Drunk / Alcohol* | **0.75** | **0.60** | **Fell et al. (2014)** sobriety checkpoint and deterrence elasticity |
| **Helmet / Gear Compliance** | Incidents where `vehicle_type` = *Motorcycle* | **0.40** | **0.00** | **WHO & Elvik (2009)** motorcycle helmet head injury protection factor |

### 3. Economic Savings Formulation

$$\text{Economic Savings (THB)} = (\Delta \text{Fatalities} \times 5,000,000) + (\Delta \text{Serious Injuries} \times 800,000)$$

---

## 🔍 Data Integrity Guarantees & Validation Traceability

Every row in the analytical output contains direct traceability fields:
- `source_agency`: Official issuing authority
- `source_dataset`: CKAN dataset identifier
- `source_resource_id`: Resource UUID from data.go.th / mot.go.th
- `source_url`: Verifiable HTTP resource link
- `source_year`: Fiscal year of publication
