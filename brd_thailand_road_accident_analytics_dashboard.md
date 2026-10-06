# Business Requirements Document (BRD)
## Project: Thailand Road Accident Analytics & Safety Dashboard

---

## 1. Project Overview & Objectives

**Project Title:** Interactive Thailand Road Accident Analytics & Risk Management System  
**Target Platform:** Web-Based Dashboard (Python Backend + Plotly Frontend)  
**Target Audience:** Road Safety Analysts, Policy Makers, Traffic Police, Transport Department Officials, and General Public  
**Handoff Target:** Antigravity AI / Development Team  

### Key Business Questions to Answer:
1. **Tab 1 (Casualty & Vehicle Impact):** สถิติและปริมาณความรุนแรงของอุบัติเหตุเป็นอย่างไร จำแนกตามประเภทยานพาหนะ และสัดส่วนการรอดชีวิต/เสียชีวิตในแต่ละช่วงเวลา?
2. **Tab 2 (Risk Zones & Causes):** พื้นที่จุดเสี่ยง (Blackspots) อยู่ที่ไหนบ้าง สาเหตุหลักของการเกิดอุบัติเหตุคืออะไร และสัดส่วนความรุนแรงแยกตามระดับสายทาง/บริษัทขนส่งที่เกี่ยวข้อง?
3. **Tab 3 (Risk Factor & Mismatch Analysis):** การวิเคราะห์ความสัมพันธ์และช่องว่างความเสี่ยง (Risk Mismatch) ระหว่างปัจจัยแวดล้อม (สภาพถนน/อากาศ) พฤติกรรมผู้ขับขี่ และผลกระทบเชิงความรุนแรง เพื่อหาแนวทางป้องกัน

---

## 2. Technical Stack & Architectural Constraints

1. **Backend Framework:** Python (Dash / Streamlit / FastAPI with Dash Plotly)
2. **Visualization Engine:** Plotly / Plotly Express (Interactive charts & maps)
3. **Cross-Filtering Interactivity:** 
   - ทุกกราฟและองค์ประกอบในแต่ละ Tab ต้องเชื่อมโยงกันแบบ Dynamic Interactivity (Callback/Event Linking)
   - เมื่อผู้ใช้เลือก/คลิกข้อมูลในกราฟหนึ่ง (เช่น เลือกภูมิภาค หรือช่วงเวลา) กราฟอื่น ๆ ทั้งหมดใน Tab นั้นจะต้อง Filter และ Update ข้อมูลตามตัวเลือกทันที
4. **Data Input & Upload Module:**
   - รองรับการอัปโหลดไฟล์ CSV/Excel ข้อมูลอุบัติเหตุใหม่โดยผู้ใช้
   - มีระบบ Editable Data Table ให้ผู้ใช้ปรับเปลี่ยนตัวเลขหรือจำลองสถานการณ์ (Simulation) และ re-render Dashboard ทันที

---

## 3. Detailed Tab Specifications & Graph Requirements

### 📌 TAB 1: ปริมาณอุบัติเหตุ ผู้ได้รับบาดเจ็บ/เสียชีวิต และประเภทยานพาหนะ (Casualties & Vehicle Analytics)

**Objective:** ตอบคำถามเกี่ยวกับสถิติการเกิดอุบัติเหตุ จำนวนผู้บาดเจ็บ/เสียชีวิต และความสัมพันธ์กับประเภทยานพาหนะ

#### Required Visualizations:
1. **ยอดรวมและแนวโน้มการผลิตสถิติอุบัติเหตุรายปี (Accident & Casualty Trends by Year):**
   - *Graph Type:* Multi-line Chart / Area Chart (Plotly)
   - *Details:* แสดงจำนวนครั้งการเกิดอุบัติเหตุ จำนวนผู้บาดเจ็บ และจำนวนผู้เสียชีวิต จำแนกรายปี (เช่น 2020 - 2026)
2. **จำแนกประเภทยานพาหนะที่ประสบเหตุ (Vehicle Types Involved):**
   - *Graph Type:* Bar Chart / Treemap (Plotly)
   - *Details:* แสดงสัดส่วนยานพาหนะที่เกี่ยวข้อง (รถจักรยานยนต์, รถยนต์ส่วนบุคคล, รถบรรทุก, รถโดยสารสาธารณะ) พร้อมจำนวนเหตุที่เกิดขึ้น
3. **สถิติการได้งานทำ/อัตราการรอดชีวิตและการเสียชีวิตตามช่วงเวลาเรียนจบ/ปีที่เกิดเหตุ (Casualty Timeline Tracking):**
   - *Graph Type:* Stacked Bar Chart / Sankey Diagram
   - *Details:* จำนวนผู้ประสบเหตุที่ได้รับการรักษา/ปลอดภัย ผู้บาดเจ็บสาหัส และผู้เสียชีวิต จำแนกตามระยะเวลาหลังเกิดเหตุ (ปีที่ 1, ปีที่ 2, ปีที่ 3 ของการติดตามผล หรือช่วงเทศกาลสำคัญ)
4. **มูลค่าความเสียหายและค่าใช้จ่ายเฉลี่ย (Financial Impact & Cost Analysis):**
   - *Graph Type:* Box Plot / Indicator Cards
   - *Details:* สถิติมูลค่าความเสียหายทางเศรษฐกิจ ประเมินค่าเทอม/ค่ารักษาพยาบาล และค่าชดเชยเฉลี่ยต่อเคสอุบัติเหตุ

---

### 📌 TAB 2: ปริมาณจุดเสี่ยง ปัจจัยการเกิดเหตุ และหน่วยงาน/บริษัทที่เกี่ยวข้อง (Risk Zones, Causes & Operations)

**Objective:** ตอบคำถามเกี่ยวกับพื้นที่เสี่ยง สาเหตุหลักของการชน และหน่วยงาน/บริษัทขนส่งที่รับผิดชอบสายทาง

#### Required Visualizations:
1. **ปริมาณพื้นที่จุดเสี่ยงและตำแหน่งว่าง/จุดเกิดเหตุบ่อย (High-Risk Blackspots & Open Incidents):**
   - *Graph Type:* Interactive Mapbox / Scatter Geographic Plot (Plotly)
   - *Details:* แสดงแผนที่ความร้อน (Heatmap) พิกัดจุดเสี่ยงอันตราย (Blackspots) แยกตามระดับความรุนแรง (Low, Moderate, High Risk Red Zone)
2. **สาเหตุหลักของการเกิดอุบัติเหตุที่ต้องการการแก้ไข (Key Accident Causes / Required Safety Skills):**
   - *Graph Type:* Horizontal Bar Chart / Pareto Chart (Plotly)
   - *Details:* จัดอันดับสาเหตุการชน เช่น ขับรถเร็วเกินกำหนด, ตัดหน้ากระทันหัน, เมาแล้วขับ, สภาพถนนชำรุด, และหลับใน
3. **บริษัทขนส่ง / หน่วยงานรับดูแลสายทาง (Managing Entities & Fleet Operators):**
   - *Graph Type:* Donut Chart / Bubble Chart
   - *Details:* จำแนกสถิติตามประเภทสังกัดผู้รับผิดชอบ (กรมทางหลวง, กรมทางหลวงชนบท, อปท.) และบริษัทขนส่งเอกชนที่เกิดเหตุบ่อย
4. **ระดับความรุนแรงและค่าใช้จ่าย/เงินเดือนชดเชยตามระดับสายทาง (Severity Index by Road Hierarchy):**
   - *Graph Type:* Violin Plot / Grouped Bar Chart
   - *Details:* เปรียบเทียบความรุนแรงของอุบัติเหตุและค่าชดเชยเฉลี่ยในแต่ละระดับสายทาง (ทางหลวงแผ่นดิน, ทางหลวงชนบท, ถนนในเมือง)

---

### 📌 TAB 3: การวิเคราะห์ความเสี่ยงซ้อนทับและช่องว่างปัจจัยอุบัติเหตุ (Risk Mismatch & Gap Analysis)

**Objective:** วิเคราะห์เปรียบเทียบความเหลื่อมล้ำ (Mismatch) ระหว่างปัจจัยเสี่ยงจาก Tab 1 (ยานพาหนะ/พฤติกรรม) และ Tab 2 (สภาพแวดล้อม/สายทาง) เพื่อหาโซลูชันเชิงป้องกัน

#### Required Visualizations & Analysis:
1. **Matrix วิเคราะห์ความสัมพันธ์ Mismatch (Safety Capability vs Risk Exposure Matrix):**
   - *Graph Type:* Scatter Plot with Quadrants / Heatmap Matrix (Plotly)
   - *Details:* แกน X แสดงระดับความเสี่ยงของถนน (Road Risk Score) และ แกน Y แสดงพฤติกรรมผู้ขับขี่/ประเภทรถ (Driver Behavior Risk) เพื่อระบุกลุ่ม Mismatch สูงสุด (เช่น ถนนเสี่ยงสูง + ขับรถเร็ว)
2. **ช่องว่างความพร้อมด้านอุปกรณ์ความปลอดภัย (Safety Equipment Gap Analysis):**
   - *Graph Type:* Radar Chart / Waterfall Chart (Plotly)
   - *Details:* เปรียบเทียบสัดส่วนการใช้อุปกรณ์ความปลอดภัยมาตรฐาน (หมวกกันน็อค, เข็มขัดนิรภัย) กับอัตราการสูญเสียจริงในแต่ละพื้นที่
3. **Simulation Table & Recalculation Engine (ตารางแก้ไขข้อมูลจำลองสถานการณ์):**
   - *Component:* Editable Data Table (Dash DataTable / Ag-Grid)
   - *Details:* อนุญาตให้ผู้ใช้ปรับลด/เพิ่มตัวเลขปัจจัยเสี่ยง (เช่น ลดการขับเร็วลง 20%) แล้วกด Recalculate เพื่อคำนวณคาดการณ์จำนวนผู้บาดเจ็บ/เสียชีวิตที่จะลดลงแบบ Real-time

---

## 4. Non-Functional & UI/UX Requirements

1. **Theme & Color Palette:**
   - Modern Safety Analytics Theme (Dark Slate Background with Red `#FF4136`, Amber `#FFDC00`, and Green `#2ECC40` indicators).
2. **Performance:**
   - Dynamic Callbacks ต้องใช้เวลา Render ไม่เกิน 1.5 วินาทีเมื่อมีการ Filter ข้อมูล
3. **Data Export:**
   - รองรับการ Export กราฟทั้งหมดเป็น PNG/SVG และการ Export ตารางข้อมูลเป็น CSV/Excel
```

---

<ElicitationsGroup message="คุณสามารถเลือกดำเนินการต่อได้ดังนี้ครับ:">
  <Elicitation label="ส่งต่อให้ Antigravity พัฒนาเป็นโค้ด Python (Dash/Plotly) ฉบับเต็มทันที" query="ช่วยนำ BRD นี้ไปพัฒนาเป็นโค้ด Python Dashboard (Dash + Plotly) ในไฟล์ single HTML/Python ให้หน่อย"/>
  <Elicitation label="ปรับแก้โครงสร้างวิเคราะห์ใน BRD เพิ่มเติม" query="ขอปรับแก้รายวิชา/ตัวแปรใน BRD ให้เน้นอุบัติเหตุช่วงเทศกาลสงกรานต์/ปีใหม่"/>
</ElicitationsGroup>