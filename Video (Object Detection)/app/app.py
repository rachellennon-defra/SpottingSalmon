
#######################################################################################
# Spotting Salmon App
# Written by: Rachel Lennon & co-pilot troubleshooting
# Purpose: A UI for detecting and counting wild salmon from EA monitoring sites.
#######################################################################################

####################################
# SET UP
####################################

# Import packages
import os
import io
import zipfile
import numpy as np
import streamlit as st
from pathlib import Path
from PIL import Image
import pandas as pd
from databricks.sdk import WorkspaceClient
import tempfile, shutil
import subprocess
from PIL import Image, ImageDraw
import streamlit.components.v1 as components
from databricks import sql
from databricks.sdk.core import Config

cfg = Config()   # Uses your Databricks token/host automatically

@st.cache_resource
def get_sql_conn(http_path):
    return sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
    )

####################################
# OPEN PAGE
####################################

# Title
st.set_page_config(page_title="Spotting Salmon", layout="wide")
st.title("🐟 SpottingSalmon – Video Fish Counter")

####################################
# OPEN PAGE
####################################

# --- NEW: Show a Databricks AI/BI dashboard immediately under the title ---
st.subheader("📊 Monitoring Dashboard")

# Paste your published dashboard's EMBED URL below.
DATABRICKS_DASHBOARD_EMBED_URL = st.secrets.get(
    "DATABRICKS_DASHBOARD_EMBED_URL",
    None
)

# Tip: keep height generous for scrollable dashboards; width=100% is default
components.iframe(
    src=DATABRICKS_DASHBOARD_EMBED_URL,
    height=780,
    scrolling=True,
)

# (Optionally) a divider before the rest of the app UI
st.divider()

st.subheader("🔍 Upload Monitoring Videos")

####################################
# SAVE ZIP INTO UC VOLUME
####################################

w = WorkspaceClient()
uploaded_file = st.file_uploader("Upload a ZIP file with monitoring videos")

if st.button("Save upload"):
    if uploaded_file is None:
        st.error("Please upload a ZIP file.")
        st.stop()

    try:
        file_bytes = uploaded_file.read()
        file_name = uploaded_file.name

        if not file_name.lower().endswith(".zip"):
            st.error("Please upload a ZIP file.")
            st.stop()

        zf = zipfile.ZipFile(io.BytesIO(file_bytes))

        # UC folder - CHANGE
        dest_folder = (
            "YOUR/PATH"
            f"{file_name.replace('.zip','')}"
        )

        # Temp folder for previews
        temp_base = tempfile.mkdtemp(prefix="qc_videos_")
        st.session_state["temp_base_folder"] = temp_base

        uploaded_mp4_paths = []
        temp_mp4_paths = []

        for member in zf.namelist():
            if not member.lower().endswith(".mp4"):
                continue

            fname = os.path.basename(member)
            if not fname:
                continue

            file_content = zf.read(member)

            # 1) Upload to UC
            uc_path = f"{dest_folder}/{fname}"
            w.files.upload(uc_path, io.BytesIO(file_content), overwrite=True)
            uploaded_mp4_paths.append(uc_path)

            # 2) Save local temp copy
            temp_path = os.path.join(temp_base, fname)
            with open(temp_path, "wb") as f:
                f.write(file_content)
            temp_mp4_paths.append(temp_path)

        if not uploaded_mp4_paths:
            st.error("ZIP contained no .mp4 files.")
            st.stop()

        st.session_state["input_df"] = pd.DataFrame({"fish": uploaded_mp4_paths})
        st.session_state["uploaded_base_folder"] = dest_folder
        st.session_state["uploaded_mp4_paths"] = uploaded_mp4_paths
        st.session_state["temp_mp4_paths"] = temp_mp4_paths

        st.success(f"Uploaded {len(uploaded_mp4_paths)} videos into UC + local temp copies!")

    except Exception as e:
        st.error(f"Error saving: {e}")
            
####################################
# Model Inference
####################################

st.subheader("🔍 Run Inference")

if st.button("🚀 Start Inference"):
    if "input_df" not in st.session_state:
        st.error("No saved file found. Upload and click 'Save changes' first.")
    else:
        input_df = st.session_state["input_df"]

        if input_df.empty:
            st.error("No videos prepared. Upload a ZIP and click 'Save changes' first.")
        else:
            payload = {
                "fish": input_df["fish"].astype(str).tolist()
            }

            try:
                # --- Call serving endpoint ---
                response = w.serving_endpoints.query(
                    name="salmon_model_e",
                    inputs=payload
                )

                resp_dict = response.as_dict() if hasattr(response, "as_dict") else dict(response)

                preds = resp_dict["predictions"]
                preds_df = pd.DataFrame(preds)

                 # --- Fish counts ---

                st.subheader("🐟 Fish Count Summary")
                if "track_id" in preds_df.columns:
                    fish_counts = (
                        preds_df.groupby("video")["track_id"]
                        .nunique()
                        .reset_index(name="unique_fish")
                        .sort_values("unique_fish", ascending=False)
                    )
                else:
                    fish_counts = (
                        preds_df.groupby("video")
                        .size()
                        .reset_index(name="detections")
                        .sort_values("detections", ascending=False)
                    )

                st.dataframe(fish_counts)

                # --- SAVE PREDICTIONS TO UNITY CATALOG ---------------------------------------

                st.subheader("💾 Save Predictions to Unity Catalog")

                http_path = st.text_input(
                    "SQL Warehouse HTTP Path (from Databricks):",
                    placeholder="/sql/1.0/warehouses/09d64966392a2bda"
                )

                target_table = st.text_input(
                    "Existing UC Table (catalog.schema.table):",
                    placeholder="prd_dash_lab.dash_data_science_unrestricted.fish_tracking_summary"
                )

                if st.button("Append Predictions to UC Table"):
                    if not http_path or not target_table:
                        st.error("Please provide HTTP Path and table name.")
                    else:
                        try:
                            conn = get_sql_conn(http_path)

                            # Convert rows for parameterised insertion
                            rows = preds_df.to_dict(orient="records")
                            columns = list(preds_df.columns)
                            placeholders = ", ".join(["?"] * len(columns))
                            col_clause = ", ".join([f"`{c}`" for c in columns])

                            with conn.cursor() as cur:
                                for row in rows:
                                    cur.execute(
                                        f"INSERT INTO {target_table} ({col_clause}) VALUES ({placeholders})",
                                        list(row.values())
                                    )

                            st.success(f"Inserted {len(rows)} rows into {target_table}!")

                        except Exception as e:
                            st.error(f"Error writing to Unity Catalog: {e}")


                # ----------------------------------------------------
                # QC BLOCK
                # ----------------------------------------------------

                st.subheader("🎥 QC: Review Input Videos")

                # Ensure predictions + paths are available
                if (
                    "input_df" in st.session_state 
                    and "uploaded_mp4_paths" in st.session_state
                    and "temp_base_folder" in st.session_state
                ):
                    videos = preds_df["video"].unique()
                    selected_video = st.selectbox("Select a video:", videos)

                    if selected_video:
                        # Local temp copy path
                        base_name = os.path.basename(selected_video)
                        temp_base = st.session_state["temp_base_folder"]
                        temp_path = os.path.join(temp_base, base_name)

                        if not os.path.exists(temp_path):
                            st.error("Cannot find local temp copy. Re-upload ZIP.")
                            st.stop()

                        # ------------------------------------------------
                        # Show raw original video
                        # ------------------------------------------------
                        st.markdown("### 🎞️ Original Video")
                        with open(temp_path, "rb") as f:
                            st.video(f.read(), format="video/mp4")

            except Exception as e:
                st.error(f"Error saving: {e}")
