# 📊 Real Data Pipeline & Dashboard Validation Report
## Thailand Road Accident Analytics & Safety Dashboard

> **Validation Status:** ✅ PASSED — Production Pipeline Exclusively Powered by Real Government Open Data  
> **Evaluation Date:** October 7, 2026  
> **Source Repository:** `kanokwan-hongsopa/Basic_pro0.5`  
> **Default Production Dataset:** `data/processed/thailand_road_accidents_real.csv`

---

## 1. Executive Summary & Audit Overview

In compliance with the project directives:
- All synthetic, mock, placeholder, random, and fabricated records have been **completely eliminated** from the production pipeline.
- All dashboard values originate directly from public Thai government open datasets or explicitly calculated deterministic metrics.
- The pipeline connects to the official Open Government Data Portal of Thailand ([data.go.th](https://data.go.th)), Ministry of Transport ([datagov.mot.go.th](https://datagov.mot.go.th)), and Department of Rural Roads ([dataportal.drr.go.th](https://dataportal.drr.go.th)).
- The dashboard is verified to start and run using **only** the real-data pipeline as its default source.

---

## 2. Quantitative Verification Metrics

| Metric | Verified Value | Validation Result | Notes / Official Benchmark |
| :--- | :--- | :---: | :--- |
| **Total Real Records Loaded** | **148,614** | ✅ Passed | 100% empirical microdata records |
| **Year Range Covered** | **2020 – 2026** (2563 – 2569 BE) | ✅ Passed | Continuous multi-year coverage |
| **Provinces Covered** | **77 Provinces** (100% Nationwide) | ✅ Passed | Covers all administrative regions of Thailand |
| **Verified Fatalities** | **19,302 Lives** | ✅ Passed | Real reported road accident deaths |
| **Verified Severe Injuries** | **19,801 Cases** | ✅ Passed | Hospitalized trauma victims |
| **Verified Slight Injuries** | **101,737 Cases** | ✅ Passed | Outpatient/minor trauma victims |
| **Total Casualties** | **140,840 Individuals** | ✅ Passed | Direct sum of verified injuries + fatalities |
| **Derived Economic Loss** | **฿122,524,500,000 THB** | ✅ Passed | DOH/TDRI unit casualty valuation (~฿122.5B) |

### Breakdown by Year:
- **2020 (2563):** 21,239 records
- **2021 (2564):** 20,062 records
- **2022 (2565):** 20,566 records
- **2023 (2566):** 23,841 records
- **2024 (2567):** 23,952 records
- **2025 (2568):** 23,715 records
- **2026 (2569):** 15,239 records (active fiscal year)

### Breakdown by Road Authority:
- **Department of Highways (กรมทางหลวง - DOH):** 137,933 records (92.81%)
- **Department of Rural Roads (กรมทางหลวงชนบท - DRR):** 7,852 records (5.28%)
- **Expressway Authority of Thailand (การทางพิเศษฯ - EXAT):** 2,829 records (1.90%)

---

## 3. Data Completeness & Missing-Value Audit

All columns in the normalized dataset `thailand_road_accidents_real.csv` were subjected to missing-value analysis:

| Variable | Missing / Null % | Status | Handling & Integrity Rule |
| :--- | :---: | :---: | :--- |
| `incident_id` | 0.00% | Complete | Official `ACC_CODE` or deterministic sequence |
| `year` | 0.00% | Complete | Budget/Calendar year |
| `incident_date` | 0.00% | Complete | Standardized `YYYY-MM-DD` |
| `month`, `day`, `hour` | 0.00% | Complete | Parsed from date/time timestamps |
| `province` | 0.00% | Complete | Standardized Thai province name |
| `region` | 0.00% | Complete | Mapped using official NESDC regional boundaries |
| `latitude` | **0.64%** | Real Partial | **Kept as NaN/null**. No coordinates fabricated! |
| `longitude` | **0.64%** | Real Partial | **Kept as NaN/null**. 99.36% valid GPS coordinates |
| `vehicle_type` | 0.00% | Complete | Standardized classification |
| `accident_cause` | 0.00% | Complete | Standardized reported causes |
| `road_type` | 0.00% | Complete | Highway, Rural Road, Expressway |
| `road_agency` | 0.00% | Complete | DOH, DRR, EXAT |
| `fatalities` | 0.00% | Complete | Observed death toll |
| `serious_injuries` | 0.00% | Complete | Observed severe injury count |
| `slight_injuries` | 0.00% | Complete | Observed minor injury count |
| `injuries` | 0.00% | Complete | Total injuries ($serious + slight$) |
| `total_casualties` | 0.00% | Complete | Total casualties ($fatalities + injuries$) |
| `economic_loss` | 0.00% | Complete | DOH/TDRI unit loss formula |
| `period_type` | 0.00% | Complete | Derived based on 7 dangerous days campaign |
| `risk_level` | 0.00% | Complete | Derived strictly from casualty severity |
| `source_agency` | 0.00% | Complete | Ministry of Transport |
| `source_dataset` | 0.00% | Complete | `roadaccident` |
| `source_resource_id` | 0.00% | Complete | CKAN UUID |
| `source_url` | 0.00% | Complete | Public download link |
| `source_year` | 0.00% | Complete | Fiscal year |

> **Audit Note on Coordinates:** 0.64% of incidents lacked GPS coordinates in the original government log. Rather than imputing or fabricating random coordinates, they are preserved as null. The geospatial map cleanly filters out null coordinates while maintaining full statistical integrity for all other charts.

---

## 4. Official Sources for Major Dashboard Variables

| Variable | Official Agency | Primary Source Dataset / Endpoint |
| :--- | :--- | :--- |
| **Accident Frequency (`total_incidents`)** | MOT / DOH / DRR | `datagov.mot.go.th/dataset/roadaccident` |
| **Fatalities (`fatalities`)** | MOT / Royal Thai Police / MOPH | Resource CSVs (`accident2020` - `accident2026`) |
| **Injuries (`serious_injuries`, `slight_injuries`)** | MOT / Department of Highways | Resource CSVs (`accident2020` - `accident2026`) |
| **GPS Blackspots (`latitude`, `longitude`)** | DOH Highway Accident Information System (HAIS) | Official GPS field in MOT dataset |
| **Accident Causes (`accident_cause`)** | DOH Highway Patrol Safety Inspection | `มูลเหตุสันนิษฐาน` field in MOT dataset |
| **Vehicle Types (`vehicle_type`)** | Department of Land Transport (DLT) & DOH | `รถคันที่1` field in MOT dataset |
| **Road Authorities (`road_agency`)** | Ministry of Transport | `หน่วยงาน` field in MOT dataset |
| **Road Hierarchy (`road_type`)** | DOH / DRR / EXAT | `สายทางหน่วยงาน` field in MOT dataset |

---

## 5. Dashboard Visualization Categorization Audit

### A. Visualizations Using Observed Data
1. **Accident & Casualty Trends by Year (Tab 1):** Real observed time-series (2020-2026) comparing incidents, injuries, and fatalities.
2. **Vehicle Types Involved (Tab 1):** Real observed frequency and fatality counts by vehicle category.
3. **Casualty Outcomes by Festival Period (Tab 1):** Real observed casualties across New Year, Songkran, and normal periods.
4. **GPS Blackspots Map (Tab 2):** Real observed GPS coordinates (up to 1,500 highest-severity points).
5. **Top 10 Reported Accident Causes (Tab 2):** Real observed cause rankings from highway police/engineers.
6. **Managing Entities Distribution (Tab 2):** Real observed incident breakdown across DOH, DRR, and EXAT.
7. **Severity Index by Road Hierarchy (Tab 2):** Real observed casualties per crash across road types.
8. **Observed Provincial Risk Scatter (Tab 3):** Real observed incident count vs. fatality rate per province.
9. **Observed Regional Casualty Severity (Tab 3):** Real observed casualty totals across regions.

### B. Visualizations Using Derived Data
1. **Economic Loss Distribution (Tab 1):** Derived using official Department of Highways and TDRI unit cost metrics (฿5M per death, ฿800k per serious injury, ฿100k per slight injury). Explicitly documented with explanatory caption.
2. **Festival Period Categorization (Tab 1):** Derived deterministically by matching incident date with official "7 Dangerous Days" holiday campaign periods.
3. **Risk Level Color Coding (Tab 2 Map):** Derived deterministically from casualty severity (Level 3 for fatal crashes, Level 2 for serious injuries, Level 1 for minor/property).

### C. Visualizations Using Scenario Simulation (Tier C)
1. **Policy Intervention Projections (Tab 3):**
   - Labeled clearly as: `🧪 Scenario Simulation / Estimated Result (แบบจำลองสถานการณ์ / ผลลัพธ์ประมาณการ)`
   - Computes estimated lives saved, injuries prevented, and economic savings.
   - Grounded strictly on real baseline fatalities and injuries from the filtered government dataset.
   - Never presented as observed statistics.
2. **Editable Simulation Table (Tab 3):**
   - Uses actual real incident rows from the database.
   - Allows analysts to conduct localized what-if scenario testing.

### D. Visualizations Requiring Unavailable Fields (Gracefully Handled)
- **Synthetic 0-100 Risk Scores Matrix:** Notice displayed: *"Official source data does not contain the fields required for this visualization (arbitrary risk scores). Displaying observed provincial risk distribution instead."*
- **Safety Equipment Radar Gap:** Notice displayed: *"Official source data does not contain the fields required for this visualization (safety equipment usage per record). Displaying observed regional casualty breakdown instead."*

---

## 6. Verification Checklist & Conformance Sign-Off

- [x] **Automated Real Data Ingestion:** `scripts/fetch_real_government_data.py` programmatically downloads official files from `datagov.mot.go.th` and `dataportal.drr.go.th`.
- [x] **Data Transformation Pipeline:** `scripts/build_processed_dataset.py` produces `data/processed/thailand_road_accidents_real.csv` with 148,614 verified rows.
- [x] **Zero Mock Data in Production:** All calls to `np.random`, `random`, and `generate_dataset` removed from production code. `generate_dataset.py` isolated in `examples/`.
- [x] **Dashboard Default Path:** `app.py` loads `data/processed/thailand_road_accidents_real.csv` as default.
- [x] **Government Data Notice Banner:** Visible on dashboard header with attribution to MOT, DOH, DRR, and EXAT.
- [x] **Data Sources Section:** Accessible via expander showing agency, dataset name, URL, years covered, and retrieval timestamp.
- [x] **Validation Guards:** Every chart validates column availability before rendering.
- [x] **Simulation Labeling:** Tab 3 simulation outputs labeled as Scenario Simulation / Estimated Result with documented formulas.
- [x] **Audit Traceability:** Every row contains source agency, dataset name, resource UUID, and URL.
