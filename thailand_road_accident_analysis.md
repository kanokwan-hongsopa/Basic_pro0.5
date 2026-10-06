# 🚗 Open Data & System Architecture: Thailand Road Accident Analysis
> **Document Purpose:** Complete analysis guide, open data catalog, statistical breakdown, and AI Handoff Specification for creating an Interactive Road Safety Web Application.

---

## 1. 📂 แหล่งข้อมูล Open Data (Thailand Road Accident Datasets)

ข้อมูลทั้งหมดเป็น Open Data จากหน่วยงานภาครัฐและองค์กรเพื่อความปลอดภัยทางถนน สามารถนำไปใช้งาน พัฒนาต่อยอด หรือวิเคราะห์ทางสถิติได้โดยไม่มีค่าใช้จ่าย

### 1.1 ข้อมูลอุบัติเหตุทางหลวง (Department of Highways Accident Data)
* **คำอธิบาย:** ชุดข้อมูลสถิติการเกิดอุบัติเหตุบนทางหลวงทั่วประเทศไทย จัดเก็บโดยกรมทางหลวง ประกอบด้วยพิกัด GPS, สภาพอากาศ, ลักษณะการชน, สาเหตุหลัก, ประเภทยานพาหนะ, และจำนวนผู้บาดเจ็บ/เสียชีวิต
* **รูปแบบไฟล์:** CSV / API
* **สัญญาอนุญาต:** Open Government Data License
* **ลิงก์ดาวน์โหลด:** 
  * [Data.go.th - สถิติอุบัติเหตุบนทางหลวง](https://data.go.th/dataset/roadaccident)
  * [ระบบสารสนเทศอุบัติเหตุ กรมทางหลวง](https://maint.doh.go.th/maint/accident)

### 1.2 ข้อมูลผู้ประสบภัยจากรถ โดยศูนย์ข้อมูลอุบัติเหตุ (ThaiRSC Data)
* **คำอธิบาย:** ข้อมูลเชิงลึกเกี่ยวกับการรับแจ้งอุบัติเหตุทางถนนทั่วประเทศ รายงานตัวเลขผู้บาดเจ็บ ผู้เสียชีวิต จำแนกรายจังหวัด รายช่วงเวลา และจำแนกตามประเภทรถ (โดยเฉพาะรถจักรยานยนต์)
* **รูปแบบไฟล์:** CSV / Dashboard Export
* **สัญญาอนุญาต:** Public Open Data
* **ลิงก์ดาวน์โหลด:** [ThaiRSC Open Data Portal](https://www.thairsc.com/)

### 1.3 ข้อมูลสถิติคดีอุบัติเหตุจราจร (Royal Thai Police Open Data)
* **คำอธิบาย:** สถิติการดำเนินคดีอุบัติเหตุจราจรทางถนน สาเหตุเชิงพฤติกรรม (เช่น ขับรถเร็วเกินกำหนด, เมาแล้วขับ, ตัดหน้ากระทันหัน) และการจัดอันดับพื้นที่จุดเสี่ยงจราจร
* **รูปแบบไฟล์:** CSV / PDF Reports
* **ลิงก์ดาวน์โหลด:** [สำนักงานตำรวจแห่งชาติ Data Portal](https://data.go.th/organization/rtp)

### 1.4 ข้อมูลสถิติผู้ถือใบอนุญาตขับรถ และจำนวนรถจดทะเบียน (Department of Land Transport)
* **คำอธิบาย:** ชุดข้อมูลตัวแปรควบคุม (Control Variables) สำหรับนำไปคำนวณอัตราการเกิดอุบัติเหตุต่อจำนวนประชากรหรือจำนวนรถจดทะเบียน (Accident Rate per Registered Vehicles)
* **รูปแบบไฟล์:** CSV / Excel
* **ลิงก์ดาวน์โหลด:** [กรมการขนส่งทางบก Open Data](https://data.go.th/organization/dlt)

---

## 2. 🚦 การจัดระดับความเสี่ยงของพื้นที่และสายทาง (Risk & Severity Level Classification)

จำแนกระดับความเสี่ยงและพฤติกรรมการเกิดอุบัติเหตุออกเป็น 3 ระดับ เพื่อใช้กำหนดมาตรการเฝ้าระวังและการวิเคราะห์ข้อมูล:

```
+-----------------------------------------------------------------------+
|                    ROAD RISK & SEVERITY LEVELS                        |
+-----------------------------------------------------------------------+
|  [Level 1: Low Risk / Baseline]                                       |
|  - Minor collisions, property damage only                             |
|  - Low traffic volume, non-blackspot zones                            |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|  [Level 2: Moderate Risk / Surveillance Zone]                        |
|  - Non-fatal injuries, recurring collision patterns                   |
|  - High traffic density, intersections, urban corridors               |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|  [Level 3: High Risk / Critical Blackspot (Red Zone)]                 |
|  - Fatal accidents, multi-vehicle pileups, severe casualties          |
|  - Sharp curves, steep grades, high-speed arterial roads              |
+-----------------------------------------------------------------------+
```

### 2.1 Level 1: ระดับเริ่มต้น (Low Risk / Baseline Zone)
* **ลักษณะ:** พื้นที่ที่มีอัตราการเกิดอุบัติเหตุต่ำ ความรุนแรงส่วนใหญ่เป็นเพียงทรัพย์สินเสียหาย (Property Damage Only - PDO) ไม่มีผู้เสียชีวิต
* **ประเภทเหตุการณ์:** เฉี่ยวชนขณะจอด, ชนเสา/สิ่งกีดขวางความเร็วต่ำ, การเฉี่ยวชนในซอยหรือเขตชุมชนความเร็วต่ำ
* **ตัวแปรเป้าหมาย:** จำนวนครั้งการชน (Accident Count), มูลค่าความเสียหายทางทรัพย์สิน

### 2.2 Level 2: ระดับปานกลาง (Moderate Risk / Surveillance Zone)
* **ลักษณะ:** พื้นที่เฝ้าระวังที่มีการเกิดอุบัติเหตุซ้ำซ้อน มีผู้ได้รับบาดเจ็บเล็กน้อยถึงปานกลาง (Slight to Serious Injuries) แต่ไม่มีผู้เสียชีวิตในรอบปี
* **ประเภทเหตุการณ์:** ชนท้ายบริเวณทางแยก, ชนขณะเปลี่ยนเลนบนถนนสายหลัก, รถจักรยานยนต์ล้มเองเนื่องจากสภาพถนน
* **ตัวแปรเป้าหมาย:** จำนวนผู้บาดเจ็บ (Casualty Count), ดัชนีความคั่งคั่งของการจราจร (Traffic Density), ปัจจัยด้านช่วงเวลา (Peak Hours)

### 2.3 Level 3: ระดับเชี่ยวชาญ/วิกฤต (High Risk / Critical Blackspot - Red Zone)
* **ลักษณะ:** จุดเสี่ยงอันตรายสูง (Blackspots) มีสถิติการเสียชีวิตสูง (Fatal Accidents) หรือเกิดอุบัติเหตุรุนแรงซ้ำซ้อนอย่างมีนัยสำคัญทางสถิติ
* **ประเภทเหตุการณ์:** การชนประสานงาบนทางหลวงไร้เกาะกลาง, รถแหกโค้งอันตราย, อุบัติเหตุหมู่ (Multi-vehicle Pileups), การชนคนเดินเท้าบนทางข้ามความเร็วสูง
* **ตัวแปรเป้าหมาย:** อัตราการเสียชีวิต (Fatality Rate), ความเร็วเฉลี่ยขณะเกิดเหตุ (Collision Speed), ดัชนีความรุนแรง (Severity Index)

---

## 3. 📊 ปัจจัยเสี่ยงและทักษะสถิติที่จำเป็น (Statistical Variables & Methodology)

### 3.1 ตัวแปรทางสถิติที่สำคัญในใบคำขอวิเคราะห์ (Key Statistical Variables)

| หมวดหมู่ตัวแปร | ตัวแปร (Variables) | คำอธิบายและการนำไปวิเคราะห์ |
| :--- | :--- | :--- |
| **เชิงเวลา (Temporal)** | Time of Day, Day of Week, Season/Festivals | วิเคราะห์ช่วงเวลาเสี่ยงสูง (เช่น ช่วง 7 วันอันตราย, ช่วงกลางคืน 00:00 - 04:00 น.) |
| **เชิงพื้นที่ (Spatial)** | Lat/Long, Road Type, Curve Radius, Intersection Type | ทำ Spatial Clustering (K-Means, DBSCAN) เพื่อระบุจุด Blackspot |
| **พฤติกรรม (Behavioral)** | Helmet Usage, Seatbelt, Speeding, Alcohol Level | วิเคราะห์ปัจจัยร่วม (Risk Factors) ที่ส่งผลต่อความรุนแรงของการบาดเจ็บ |
| **สภาพแวดล้อม (Environmental)** | Weather, Road Surface Condition, Lighting | คำอธิบายปัจจัยภายนอกด้วย Odds Ratio และ Logistic Regression |
| **ยานพาหนะ (Vehicle)** | Vehicle Type (Motorcycle, Car, Truck), Age of Vehicle | เปรียบเทียบอัตราความเสี่ยงแยกตามประเภทพาหนะ |

### 3.2 สถิติและโมเดลที่ใช้ในการวิเคราะห์ (Statistical Methods)
1. **Descriptive & Exploratory Analysis (EDA):** คำนวณ Mean, Median, Percentiles, Fatality Rate per 100,000 Population
2. **Hypothesis Testing:**
   * **Chi-Square Test of Independence:** ทดสอบความสัมพันธ์ระหว่างประเภทรถกับระดับความรุนแรง
   * **ANOVA / Kruskal-Wallis:** เปรียบเทียบจำนวนอุบัติเหตุเฉลี่ยระหว่างภูมิภาคหรือช่วงเทศกาล
3. **Predictive & Risk Modeling:**
   * **Logistic Regression / Binary Probit:** พยากรณ์โอกาสการเสียชีวิตจากปัจจัยเสี่ยง (สวมหมวก vs ไม่สวมหมวก, ความเร็ว)
   * **Poisson / Negative Binomial Regression:** โมเดลทำนายจำนวนครั้งการเกิดอุบัติเหตุในแต่ละจุดทางหลวง

---

## 4. 🤖 Handoff Description (สำหรับส่งต่อให้ AI สร้าง Interactive HTML)

### 🎯 Project Goal
สร้าง Web Application แบบ **Interactive & Editable Single-File HTML** เพื่อสรุป วิเคราะห์ และจำลองสถานการณ์สถิติอุบัติเหตุทางถนนในประเทศไทย โดยผู้ใช้สามารถปรับแต่งตัวเลขในตาราง และดูการ recalculate ของสถิติและกราฟได้ทันที

---

### 🛠️ Technical Specifications
- **Architecture:** Single-file HTML (`index.html`) รวม CSS/JS ทั้งหมด
- **Styling Framework:** Tailwind CSS (ผ่าน CDN)
- **Visualization Library:** Chart.js หรือ Plotly.js (ผ่าน CDN)
- **Icons:** Lucide Icons หรือ FontAwesome (ผ่าน CDN)
- **Features Required:**
  1. Responsive Layout พร้อม Sidebar หรือ Navigation Header
  2. Dynamic Filtering System (เลือกปี, ภูมิภาค, ประเภทรถ, ช่วงเวลา)
  3. Executive KPI Dashboard Cards (จำนวนเหตุ, บาดเจ็บ, เสียชีวิต, Fatality Rate)
  4. Interactive Charts (Line Chart, Bar Chart, Doughnut Chart)
  5. **Editable Data Table:** ผู้ใช้สามารถคลิกแก้ไขจำนวนผู้บาดเจ็บ/เสียชีวิต หรือเปลี่ยนค่า Factor ในตารางเพื่อดูผลลัพธ์การคำนวณใหม่แบบ Real-time

---

### 📑 Application Layout Design

```
+-----------------------------------------------------------------------+
|  HEADER: Thailand Road Accident Interactive Analytics Dashboard        |
+-----------------------------------------------------------------------+
| FILTERS: [ Year Range v ] [ Region v ] [ Vehicle Type v ] [ Reset ]   |
+-----------------------------------------------------------------------+
|  KPI CARDS                                                            |
|  [ Total Incidents ]  [ Fatalities ]  [ Injuries ]  [ High Risk Zone ]|
+-----------------------------------------------------------------------+
|  CHARTS ROW 1                                                         |
|  +---------------------------------+ +------------------------------+ |
|  | Monthly Trend (Line Chart)      | | Causes Breakdown (Bar Chart) | |
|  +---------------------------------+ +------------------------------+ |
+-----------------------------------------------------------------------+
|  CHARTS ROW 2 & EDITABLE TABLE                                        |
|  +---------------------------------+ +------------------------------+ |
|  | Vehicle Type Share (Doughnut)   | | Interactive Editable Table   | |
|  |                                 | | [Edit cells -> Auto-update]| |
|  +---------------------------------+ +------------------------------+ |
+-----------------------------------------------------------------------+
```

---

### 🤖 Prompt คำสั่งส่งต่อให้ AI (Prompt for Next AI Agent)

```text
Act as a Senior Frontend Developer & Data Visualization Expert. 

Generate a fully functional, single-file interactive HTML web application for "Thailand Road Accident Data & Risk Analysis" based on the following requirements:

1. TECH STACK:
   - Pure HTML5 + Tailwind CSS (via CDN)
   - Chart.js (via CDN) for data visualizations
   - Vanilla JavaScript (ES6+)

2. KEY DASHBOARD COMPONENTS:
   - Header & Control Panel: Dropdowns for Year (2021-2026), Region (North, Central, NE, South, BKK), and Vehicle Type (Motorcycle, Private Car, Commercial Truck, Bus).
   - KPI Summary Cards: Total Incidents, Total Fatalities, Total Injuries, and Fatality Index (Deaths per 100 Accidents) with dynamic status indicators.
   - Interactive Charts:
     * Line Chart: Monthly Accident Trends
     * Horizontal Bar Chart: Top Causes of Accidents (e.g., Speeding, Drunk Driving, Cutting off)
     * Doughnut Chart: Distribution by Vehicle Type
   - Editable Simulation Data Table:
     * Displays regional or seasonal accident records.
     * Contains editable input fields or contenteditable cells for Incident Counts and Fatalities.
     * Event Listener: When a user modifies any number in the table, all KPI cards and Chart.js graphs must RE-CALCULATE and dynamically update immediately without page refresh.

3. DESIGN REQUIREMENT:
   - Clean, modern, medical/public safety theme (Dark slate or clean light mode with Red/Amber alert colors for High-Risk areas).
   - Fully responsive and self-contained in a single HTML file.
```