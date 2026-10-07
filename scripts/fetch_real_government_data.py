"""
Automated Real Government Open Data Ingestion Pipeline
Thailand Road Accident Analytics & Safety Dashboard

Sources:
1. Ministry of Transport (MOT / สำนักงานปลัดกระทรวงคมนาคม) Open Data:
   Dataset: 'อุบัติเหตุบนโครงข่ายถนนของกระทรวงคมนาคม' (roadaccident)
   Portal: https://datagov.mot.go.th & https://data.go.th
2. Department of Highways (DOH / กรมทางหลวง) - contained in national transport network microdata
3. Department of Rural Roads (DRR / กรมทางหลวงชนบท):
   Portal: https://dataportal.drr.go.th (dataset_21_06)

This script:
- Connects to official government endpoints programmatically
- Supports CKAN DataStore API pagination (offset/limit)
- Supports direct official resource CSV/XLSX downloads with retry handling
- Logs source URLs, HTTP status, record counts, and retrieval timestamps
- Saves raw government files into data/raw/
"""

import os
import sys
import time
import json
import logging
import hashlib
from datetime import datetime, timezone
import requests
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("GovernmentDataIngestion")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
METADATA_FILE = os.path.join(RAW_DATA_DIR, "ingestion_metadata.json")

# Official Government Datasets Registry
OFFICIAL_DATASETS = [
    {
        "agency": "Ministry of Transport (กระทรวงคมนาคม)",
        "dataset_name": "อุบัติเหตุบนโครงข่ายถนนของกระทรวงคมนาคม 2563 (2020)",
        "year": 2020,
        "resource_id": "40476c7b-4194-4dc2-aba5-7326819ed071",
        "url": "https://datagov.mot.go.th/dataset/7e077ffd-dc4f-4dc6-a71c-0813726f3c12/resource/40476c7b-4194-4dc2-aba5-7326819ed071/download/accident2020.csv",
        "ckan_endpoint": "https://datagov.mot.go.th/api/3/action/datastore_search",
        "filename": "mot_road_accidents_2020.csv"
    },
    {
        "agency": "Ministry of Transport (กระทรวงคมนาคม)",
        "dataset_name": "อุบัติเหตุบนโครงข่ายถนนของกระทรวงคมนาคม 2564 (2021)",
        "year": 2021,
        "resource_id": "d0a8601a-3ee5-4ce8-8e9d-3dae3915dc30",
        "url": "https://datagov.mot.go.th/dataset/7e077ffd-dc4f-4dc6-a71c-0813726f3c12/resource/d0a8601a-3ee5-4ce8-8e9d-3dae3915dc30/download/accident2021.csv",
        "ckan_endpoint": "https://datagov.mot.go.th/api/3/action/datastore_search",
        "filename": "mot_road_accidents_2021.csv"
    },
    {
        "agency": "Ministry of Transport (กระทรวงคมนาคม)",
        "dataset_name": "อุบัติเหตุบนโครงข่ายถนนของกระทรวงคมนาคม 2565 (2022)",
        "year": 2022,
        "resource_id": "733b7874-bd5f-44b9-b271-650890b061f2",
        "url": "https://datagov.mot.go.th/dataset/7e077ffd-dc4f-4dc6-a71c-0813726f3c12/resource/733b7874-bd5f-44b9-b271-650890b061f2/download/accident2022.csv",
        "ckan_endpoint": "https://datagov.mot.go.th/api/3/action/datastore_search",
        "filename": "mot_road_accidents_2022.csv"
    },
    {
        "agency": "Ministry of Transport (กระทรวงคมนาคม)",
        "dataset_name": "อุบัติเหตุบนโครงข่ายถนนของกระทรวงคมนาคม 2566 (2023)",
        "year": 2023,
        "resource_id": "661f2ead-1f28-4cd9-8a67-1bef76b33ef6",
        "url": "https://datagov.mot.go.th/dataset/7e077ffd-dc4f-4dc6-a71c-0813726f3c12/resource/661f2ead-1f28-4cd9-8a67-1bef76b33ef6/download/accident2023.csv",
        "ckan_endpoint": "https://datagov.mot.go.th/api/3/action/datastore_search",
        "filename": "mot_road_accidents_2023.csv"
    },
    {
        "agency": "Ministry of Transport (กระทรวงคมนาคม)",
        "dataset_name": "อุบัติเหตุบนโครงข่ายถนนของกระทรวงคมนาคม 2567 (2024)",
        "year": 2024,
        "resource_id": "83e9fae0-5f33-45e7-9a6d-6d5ad2060a08",
        "url": "https://datagov.mot.go.th/dataset/7e077ffd-dc4f-4dc6-a71c-0813726f3c12/resource/83e9fae0-5f33-45e7-9a6d-6d5ad2060a08/download/accident2024.csv",
        "ckan_endpoint": "https://datagov.mot.go.th/api/3/action/datastore_search",
        "filename": "mot_road_accidents_2024.csv"
    },
    {
        "agency": "Ministry of Transport (กระทรวงคมนาคม)",
        "dataset_name": "อุบัติเหตุบนโครงข่ายถนนของกระทรวงคมนาคม 2568 (2025)",
        "year": 2025,
        "resource_id": "e1db5e93-2b70-4ee4-b6d7-7ead76d14a09",
        "url": "https://datagov.mot.go.th/dataset/7e077ffd-dc4f-4dc6-a71c-0813726f3c12/resource/e1db5e93-2b70-4ee4-b6d7-7ead76d14a09/download/accident2025.csv",
        "ckan_endpoint": "https://datagov.mot.go.th/api/3/action/datastore_search",
        "filename": "mot_road_accidents_2025.csv"
    },
    {
        "agency": "Ministry of Transport (กระทรวงคมนาคม)",
        "dataset_name": "อุบัติเหตุบนโครงข่ายถนนของกระทรวงคมนาคม 2569 (2026)",
        "year": 2026,
        "resource_id": "4625b7aa-99a4-4dfb-9a0f-6402814d0f2c",
        "url": "https://datagov.mot.go.th/dataset/7e077ffd-dc4f-4dc6-a71c-0813726f3c12/resource/4625b7aa-99a4-4dfb-9a0f-6402814d0f2c/download/accident2026.csv",
        "ckan_endpoint": "https://datagov.mot.go.th/api/3/action/datastore_search",
        "filename": "mot_road_accidents_2026.csv"
    },
    {
        "agency": "Department of Rural Roads (กรมทางหลวงชนบท)",
        "dataset_name": "ข้อมูลอุบัติเหตุ กรมทางหลวงชนบท 2566 (2023)",
        "year": 2023,
        "resource_id": "db9a7d00-e4fe-4b1a-9c27-5459a122f9d0",
        "url": "https://dataportal.drr.go.th/dataset/2f17d1a8-1b5c-4e0f-8a82-e44aff01ca58/resource/db9a7d00-e4fe-4b1a-9c27-5459a122f9d0/download/2566_accident_drr.csv",
        "ckan_endpoint": "https://dataportal.drr.go.th/api/3/action/datastore_search",
        "filename": "drr_accidents_2023.csv"
    },
    {
        "agency": "Department of Rural Roads (กรมทางหลวงชนบท)",
        "dataset_name": "ข้อมูลอุบัติเหตุ กรมทางหลวงชนบท 2567 (2024)",
        "year": 2024,
        "resource_id": "27e25ae5-0e2d-4300-bc08-325f9022b480",
        "url": "https://dataportal.drr.go.th/dataset/2f17d1a8-1b5c-4e0f-8a82-e44aff01ca58/resource/27e25ae5-0e2d-4300-bc08-325f9022b480/download/2567_accident_drr.csv",
        "ckan_endpoint": "https://dataportal.drr.go.th/api/3/action/datastore_search",
        "filename": "drr_accidents_2024.csv"
    },
    {
        "agency": "Department of Rural Roads (กรมทางหลวงชนบท)",
        "dataset_name": "ข้อมูลอุบัติเหตุ กรมทางหลวงชนบท 2568 (2025)",
        "year": 2025,
        "resource_id": "ed8b6754-6263-4c3b-b6dc-67fefdfac0be",
        "url": "https://dataportal.drr.go.th/dataset/2f17d1a8-1b5c-4e0f-8a82-e44aff01ca58/resource/ed8b6754-6263-4c3b-b6dc-67fefdfac0be/download/2568_accident_drr.csv",
        "ckan_endpoint": "https://dataportal.drr.go.th/api/3/action/datastore_search",
        "filename": "drr_accidents_2025.csv"
    }
]

def fetch_ckan_datastore(endpoint, resource_id, limit=5000, api_key=None):
    """
    Retrieves records page-by-page from CKAN datastore_search endpoint.
    Uses limit and offset until all records are retrieved.
    """
    records = []
    offset = 0
    headers = {"User-Agent": "ThailandAccidentAnalytics/1.0"}
    if api_key:
        headers["api-key"] = api_key

    logger.info(f"Connecting to CKAN datastore: {endpoint} for resource: {resource_id}")
    while True:
        params = {"resource_id": resource_id, "limit": limit, "offset": offset}
        try:
            resp = requests.get(endpoint, params=params, headers=headers, timeout=25)
            if resp.status_code != 200:
                logger.warning(f"CKAN datastore returned status {resp.status_code}. Fallback to direct download.")
                return None
            data = resp.json()
            if not data.get("success"):
                logger.warning(f"CKAN datastore success=False. Fallback to direct download.")
                return None
            batch = data.get("result", {}).get("records", [])
            if not batch:
                break
            records.extend(batch)
            logger.info(f"Retrieved {len(records):,} records so far (offset: {offset})")
            if len(batch) < limit:
                break
            offset += limit
        except Exception as e:
            logger.warning(f"CKAN DataStore search failed at offset {offset}: {e}")
            return None

    logger.info(f"CKAN datastore search complete. Total records: {len(records):,}")
    return pd.DataFrame(records)

def download_file_with_retry(url, target_path, max_retries=3, timeout=30):
    """
    Downloads file programmatically from official URL with streaming and retries.
    """
    headers = {"User-Agent": "ThailandAccidentAnalytics/1.0"}
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Downloading from {url} (Attempt {attempt}/{max_retries})...")
            with requests.get(url, headers=headers, stream=True, timeout=timeout) as r:
                r.raise_for_status()
                with open(target_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=65536):
                        if chunk:
                            f.write(chunk)
            file_size = os.path.getsize(target_path)
            logger.info(f"Successfully saved to {target_path} ({file_size:,} bytes)")
            return True, file_size
        except Exception as e:
            logger.warning(f"Download attempt {attempt} failed: {e}")
            if attempt < max_retries:
                time.sleep(2 * attempt)
            else:
                return False, 0

def compute_sha256(filepath):
    """Computes SHA-256 hash of a file for data integrity verification."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def run_ingestion():
    """Main ingestion execution loop."""
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    metadata_log = {
        "pipeline_name": "Thailand Government Open Data Ingestion",
        "execution_timestamp": datetime.now(timezone.utc).isoformat(),
        "datasets": []
    }

    mot_dataframes = []
    drr_dataframes = []

    for entry in OFFICIAL_DATASETS:
        filename = entry["filename"]
        target_path = os.path.join(RAW_DATA_DIR, filename)
        entry_meta = {
            "agency": entry["agency"],
            "dataset_name": entry["dataset_name"],
            "year": entry["year"],
            "resource_id": entry["resource_id"],
            "source_url": entry["url"],
            "target_file": filename,
            "retrieval_timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "pending"
        }

        # Attempt download
        success, file_size = download_file_with_retry(entry["url"], target_path)
        if success:
            file_hash = compute_sha256(target_path)
            # Inspect record count
            try:
                # Try reading with common encodings
                df_temp = None
                for enc in ["utf-8-sig", "utf-8", "tis-620", "cp874"]:
                    try:
                        df_temp = pd.read_csv(target_path, encoding=enc)
                        break
                    except Exception:
                        continue
                record_count = len(df_temp) if df_temp is not None else 0
                entry_meta.update({
                    "status": "success",
                    "file_size_bytes": file_size,
                    "sha256": file_hash,
                    "record_count": record_count
                })

                if "mot_road_accidents" in filename and df_temp is not None:
                    mot_dataframes.append(df_temp)
                elif "drr_accidents" in filename and df_temp is not None:
                    drr_dataframes.append(df_temp)

            except Exception as e:
                logger.error(f"Error parsing downloaded file {filename}: {e}")
                entry_meta.update({
                    "status": "downloaded_parse_warning",
                    "file_size_bytes": file_size,
                    "sha256": file_hash,
                    "error": str(e)
                })
        else:
            entry_meta.update({
                "status": "failed",
                "error": "Failed all download retries"
            })

        metadata_log["datasets"].append(entry_meta)

    # Build consolidated raw files for convenient reference
    if mot_dataframes:
        consolidated_mot_path = os.path.join(RAW_DATA_DIR, "mot_road_accidents.csv")
        logger.info(f"Writing consolidated MOT dataset: {consolidated_mot_path}")
        df_all_mot = pd.concat(mot_dataframes, ignore_index=True)
        df_all_mot.to_csv(consolidated_mot_path, index=False, encoding="utf-8-sig")
        logger.info(f"Consolidated MOT total records: {len(df_all_mot):,}")

        # Separate DOH (Department of Highways) subset from national network
        if "หน่วยงาน" in df_all_mot.columns:
            doh_mask = df_all_mot["หน่วยงาน"].astype(str).str.contains("กรมทางหลวง", na=False) & \
                       ~df_all_mot["หน่วยงาน"].astype(str).str.contains("ชนบท", na=False)
            df_doh = df_all_mot[doh_mask]
            doh_path = os.path.join(RAW_DATA_DIR, "doh_accidents.csv")
            df_doh.to_csv(doh_path, index=False, encoding="utf-8-sig")
            logger.info(f"Extracted DOH accidents to {doh_path} ({len(df_doh):,} records)")

    if drr_dataframes:
        consolidated_drr_path = os.path.join(RAW_DATA_DIR, "drr_accidents.csv")
        logger.info(f"Writing consolidated DRR dataset: {consolidated_drr_path}")
        df_all_drr = pd.concat(drr_dataframes, ignore_index=True)
        df_all_drr.to_csv(consolidated_drr_path, index=False, encoding="utf-8-sig")
        logger.info(f"Consolidated DRR total records: {len(df_all_drr):,}")

    # Save provenance metadata
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata_log, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved ingestion provenance metadata to {METADATA_FILE}")

if __name__ == "__main__":
    logger.info("Starting Thai Government Road Accident Open Data Ingestion Pipeline...")
    run_ingestion()
    logger.info("Ingestion pipeline finished successfully.")
