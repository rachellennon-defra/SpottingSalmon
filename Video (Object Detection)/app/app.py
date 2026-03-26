#######################################################################################
# Spotting Salmon App
# Written by: Rachel Lennon & co-pilot troubleshooting
#######################################################################################

####################################
# IMPORTS
####################################

import os
import io
import zipfile
import tempfile
import shutil
import atexit

import cv2
import pandas as pd
import numpy as np
import streamlit as st
from databricks.sdk import WorkspaceClient

####################################
# PAGE CONFIG
####################################

st.set_page_config(page_title="Spotting Salmon", layout="wide")

####################################
# CUSTOM CSS
####################################

st.markdown("""
<style>
/* App background */
.stApp {
    background-color: #f5f2ea;
}

/* Main page spacing */
.block-container {
    max-width: 1450px;
    padding-top: 3.2rem;
    padding-bottom: 2rem;
}

/* Top header */
.custom-header {
    background: #2f5d34;
    color: white;
    padding: 14px 22px;
    border-radius: 12px;
    margin-top: 0.5rem;
    margin-bottom: 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}


.header-sub {
    font-size: 0.9rem;
    opacity: 0.9;
}

/* Card panels */
.card {
    background: #fbfaf6;
    border: 1px solid #e1dbcf;
    border-radius: 14px;
    padding: 16px 18px;
    margin-bottom: 18px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* Titles inside cards */
.card-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #2f3a2f;
    margin-bottom: 6px;
}

.card-subtitle {
    color: #6b675f;
    font-size: 0.92rem;
    margin-bottom: 14px;
}

/* Buttons */
.stButton > button {
    background-color: #2f5d34;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.55rem 1rem;
    font-weight: 600;
}
.stButton > button:hover {
    background-color: #24492a;
    color: white;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #fbfaf6;
    border: 1px solid #ddd6c9;
    padding: 12px;
    border-radius: 12px;
}

/* Tabs */
.stTabs [role="tablist"] {
    gap: 10px;
}
.stTabs [role="tab"] {
    background: #ebe6db;
    border-radius: 10px 10px 0 0;
    padding: 10px 16px;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #2f5d34 !important;
    border-bottom: 3px solid #2f5d34 !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid #ddd6c9;
    border-radius: 10px;
    overflow: hidden;
}

/* Small muted label */
.muted {
    color: #6f6b63;
    font-size: 0.92rem;
}

/* KPI cards */
.kpi {
    background: white;
    border: 1px solid #e3ddd1;
    border-radius: 12px;
    padding: 14px;
    text-align: center;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}
.kpi-label {
    color: #6f6b63;
    font-size: 0.88rem;
}
.kpi-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #2f5d34;
    margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)

####################################
# HEADER
####################################

st.markdown("""
<div class="custom-header">
    <div> SpottingSalmon — Video Fish Counter</div>
    <div class="header-sub">EA Monitoring QC</div>
</div>
""", unsafe_allow_html=True)

####################################
# HELPERS
####################################

def safe_rmtree(path):
    try:
        if path and os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
    except:
        pass

def register_cleanup_once():
    if not st.session_state.get("_cleanup_registered"):
        def cleanup():
            safe_rmtree(st.session_state.get("temp_base_folder"))
        atexit.register(cleanup)
        st.session_state["_cleanup_registered"] = True

def coerce_numeric(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def standardise_bbox_columns(df):
    """
    Map model bbox columns to xmin/ymin/xmax/ymax if needed.
    Only adds these columns when x1/y1/x2/y2 exist.
    """
    if {"xmin", "ymin", "xmax", "ymax"}.issubset(df.columns):
        return df

    if {"x1", "y1", "x2", "y2"}.issubset(df.columns):
        df = df.copy()
        df["xmin"] = df["x1"]
        df["ymin"] = df["y1"]
        df["xmax"] = df["x2"]
        df["ymax"] = df["y2"]

    return df

def maybe_scale_bboxes(df, w, h):
    """If boxes look normalized (<=1.5), scale to pixel coords in-place."""
    needed = {"xmin", "ymin", "xmax", "ymax"}
    if not needed.issubset(df.columns):
        return df
    max_x = pd.concat([df["xmin"], df["xmax"]], axis=1).max(axis=1).max()
    max_y = pd.concat([df["ymin"], df["ymax"]], axis=1).max(axis=1).max()
    if pd.notnull(max_x) and pd.notnull(max_y) and max_x <= 1.5 and max_y <= 1.5:
        df["xmin"] = (df["xmin"] * w).round()
        df["xmax"] = (df["xmax"] * w).round()
        df["ymin"] = (df["ymin"] * h).round()
        df["ymax"] = (df["ymax"] * h).round()
    return df

def draw_bboxes(frame, preds, w, h):
    """Draw bounding boxes + labels on a BGR frame."""
    count = 0
    for _, row in preds.iterrows():
        if not {"xmin","ymin","xmax","ymax"}.issubset(row.index):
            continue
        try:
            x1, y1, x2, y2 = map(int, [row["xmin"], row["ymin"], row["xmax"], row["ymax"]])
        except Exception:
            continue

        x1 = max(0, min(x1, w - 1))
        x2 = max(0, min(x2, w - 1))
        y1 = max(0, min(y1, h - 1))
        y2 = max(0, min(y2, h - 1))

        if x2 <= x1 or y2 <= y1:
            continue

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0,0,255), 3)
        label = str(row["track_id"]) if "track_id" in preds.columns and pd.notnull(row.get("track_id")) else "fish"
        cv2.putText(frame, label, (x1, max(0, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)
        count += 1
    return count

####################################
# SESSION DEFAULTS
####################################

if "preds_df" not in st.session_state:
    st.session_state["preds_df"] = None

if "summary_df" not in st.session_state:
    st.session_state["summary_df"] = None

####################################
# DATABRICKS CLIENT
####################################

w = WorkspaceClient()

####################################
# TABS
####################################

tab_upload, tab_review, tab_summary = st.tabs(["Upload", "Review & Annotate", "Summary"])

####################################
# TAB 1 — UPLOAD
####################################

with tab_upload:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Upload Monitoring Videos</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-subtitle">Upload a ZIP file containing .mp4 monitoring videos.</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload ZIP file", type=["zip"], label_visibility="collapsed")

    if st.button("Save upload", key="save_upload_btn"):
        if not uploaded_file:
            st.error("Please upload a ZIP file.")
            st.stop()

        try:
            file_bytes = uploaded_file.read()
            file_name = uploaded_file.name

            if not file_name.lower().endswith(".zip"):
                st.error("Must upload a ZIP.")
                st.stop()

            zf = zipfile.ZipFile(io.BytesIO(file_bytes))

            dest_folder = (
                "/Volumes/prd_dash_lab/dash_data_science_unrestricted/"
                "shared_external_volume/rachels_stuff/"
                f"{file_name.replace('.zip','')}"
            )

            temp_base = os.path.join(tempfile.gettempdir(), "qc_videos_current")
            safe_rmtree(temp_base)
            os.makedirs(temp_base, exist_ok=True)

            st.session_state["temp_base_folder"] = temp_base
            register_cleanup_once()

            uploaded_uc = []
            local_paths = []

            mp4s = [m for m in zf.namelist() if m.lower().endswith(".mp4")]
            if not mp4s:
                st.error("ZIP contained no .mp4 files.")
                st.stop()

            prog = st.progress(0.0, text="Uploading videos...")

            for i, member in enumerate(mp4s, start=1):
                fname = os.path.basename(member)
                fbytes = zf.read(member)

                # Upload to UC
                uc_path = f"{dest_folder}/{fname}"
                w.files.upload(uc_path, io.BytesIO(fbytes), overwrite=True)
                uploaded_uc.append(uc_path)

                # Local temp copy for QC
                local_path = os.path.join(temp_base, fname)
                with open(local_path, "wb") as f:
                    f.write(fbytes)
                local_paths.append(local_path)

                prog.progress(i / len(mp4s), text=f"Uploading videos... ({i}/{len(mp4s)})")

            st.session_state["input_df"] = pd.DataFrame({"fish": uploaded_uc})
            st.session_state["uploaded_mp4_paths"] = uploaded_uc
            st.session_state["temp_mp4_paths"] = local_paths

            prog.empty()
            st.success("Upload complete ")

        except Exception as e:
            st.error(f"Error saving: {e}")

    if "uploaded_mp4_paths" in st.session_state and st.session_state["uploaded_mp4_paths"]:
        st.markdown("<br>", unsafe_allow_html=True)
        st.info(f"Ready: {len(st.session_state['uploaded_mp4_paths'])} videos available for inference.")

    st.markdown('</div>', unsafe_allow_html=True)

####################################
# TAB 2 — REVIEW & ANNOTATE
####################################

######################   this block is to check for temp files - only for debugging ##############################################

with st.expander("Temp Folder Debug"):
    temp_base = st.session_state.get("temp_base_folder")
    st.write("Temp folder path:", temp_base)

    if temp_base and os.path.exists(temp_base):
        files = []
        for f in os.listdir(temp_base):
            full_path = os.path.join(temp_base, f)
            files.append({
                "file_name": f,
                "full_path": full_path,
                "is_file": os.path.isfile(full_path),
                "size_mb": round(os.path.getsize(full_path) / (1024 * 1024), 2) if os.path.isfile(full_path) else None
            })

        if files:
            st.dataframe(pd.DataFrame(files), use_container_width=True)
        else:
            st.info("Temp folder exists but is empty.")
    else:
        st.warning("Temp folder not found.")

######################################################################################################################






with tab_review:
    left_col, right_col = st.columns([1, 2], gap="large")

    ####################################
    # LEFT PANEL
    ####################################
    with left_col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Run Model</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-subtitle">Generate fish detections for uploaded videos.</div>', unsafe_allow_html=True)

        if st.button(" Start Inference", key="start_inference_btn"):
            if "input_df" not in st.session_state:
                st.error("No uploaded videos found. Upload first.")
                st.stop()

            input_df = st.session_state["input_df"]
            if input_df.empty:
                st.error("Upload videos first.")
                st.stop()

            payload = {"fish": input_df["fish"].tolist()}

            try:
                response = w.serving_endpoints.query(
                    name="salmon_model_e",
                    inputs=payload
                )
                resp = response.as_dict() if hasattr(response, "as_dict") else dict(response)

                preds = resp.get("predictions", [])
                if not preds:
                    st.warning("Model returned no predictions.")
                    st.stop()

                preds_df = pd.DataFrame(preds)
                preds_df = coerce_numeric(preds_df, ["frame","xmin","ymin","xmax","ymax","x1","y1","x2","y2"])
                preds_df = standardise_bbox_columns(preds_df)

                if "track_id" in preds_df.columns:
                    summary = (
                        preds_df.groupby("video")["track_id"]
                        .nunique()
                        .reset_index(name="unique_fish")
                    )
                else:
                    summary = (
                        preds_df.groupby("video")
                        .size()
                        .reset_index(name="detections")
                    )

                st.session_state["preds_df"] = preds_df
                st.session_state["summary_df"] = summary
                st.success("Inference complete ")

            except Exception as e:
                st.error(f"Error during inference: {e}")

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Review Queue</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-subtitle">Choose a processed video to inspect.</div>', unsafe_allow_html=True)

        preds_df = st.session_state.get("preds_df")

        if preds_df is not None and not preds_df.empty:
            videos = preds_df["video"].dropna().unique()
            selected_video = st.selectbox("Select video:", videos, key="selected_video_box")
        else:
            selected_video = None
            st.info("Run inference to populate the review queue.")

        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.get("summary_df") is not None:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">Quick Summary</div>', unsafe_allow_html=True)

            summary_df = st.session_state["summary_df"]
            st.dataframe(summary_df, use_container_width=True, height=250)

            st.markdown('</div>', unsafe_allow_html=True)

    ####################################
    # RIGHT PANEL
    ####################################
    with right_col:
        preds_df = st.session_state.get("preds_df")

        if preds_df is not None and not preds_df.empty and selected_video:
            base = os.path.basename(selected_video)
            raw_path = os.path.join(st.session_state["temp_base_folder"], base)

            if not os.path.exists(raw_path):
                st.error("Local QC file missing.")
                st.stop()

            # -----------------------------------
            # SIDE-BY-SIDE VIDEO LAYOUT
            # -----------------------------------
            video_left, video_right = st.columns(2, gap="large")

            # ----------------------------
            # LEFT: RAW VIDEO
            # ----------------------------
            with video_left:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title">Original Video</div>', unsafe_allow_html=True)
                st.markdown('<div class="card-subtitle">Source monitoring footage uploaded for QC review.</div>', unsafe_allow_html=True)

                with open(raw_path, "rb") as f:
                    st.video(f.read())

                st.markdown('</div>', unsafe_allow_html=True)

            # ----------------------------
            # RIGHT: ANNOTATED VIDEO
            # ----------------------------
            with video_right:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title">Annotated Video</div>', unsafe_allow_html=True)
                st.markdown('<div class="card-subtitle">Model detections and fish tracking overlays.</div>', unsafe_allow_html=True)

                vpreds = preds_df[preds_df["video"] == selected_video].copy()

                if vpreds.empty:
                    st.info("No detections for this video.")
                elif "frame" not in vpreds.columns:
                    st.info("'frame' column missing from predictions.")
                else:
                    # Open raw to get properties
                    cap = cv2.VideoCapture(raw_path)
                    if not cap.isOpened():
                        st.error("Cannot open raw video.")
                        st.stop()

                    fps = cap.get(cv2.CAP_PROP_FPS) or 25
                    w_vid = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    h_vid = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)

                    # Scale boxes if normalized
                    vpreds = maybe_scale_bboxes(vpreds, w_vid, h_vid)

                    # Writer (WebM VP8)
                    work_dir = tempfile.mkdtemp(prefix="annot_")
                    out_path = os.path.join(work_dir, "annotated.webm")
                    writer = cv2.VideoWriter(
                        out_path,
                        cv2.VideoWriter_fourcc(*"VP80"),
                        fps,
                        (w_vid, h_vid)
                    )

                    if not writer.isOpened():
                        st.error("Failed to open VP8 writer.")
                        cap.release()
                        safe_rmtree(work_dir)
                        st.stop()

                    one_based = (pd.notnull(vpreds["frame"].min()) and int(vpreds["frame"].min()) >= 1)
                    boxes_drawn_total = 0
                    frame_num = 0

                    while True:
                        ok, frame = cap.read()
                        if not ok:
                            break

                        candidate = [frame_num - 1, frame_num, frame_num + 1]
                        if one_based:
                            candidate = [c + 1 for c in candidate]

                        pf = vpreds[vpreds["frame"].isin(candidate)]

                        boxes_drawn_total += draw_bboxes(frame, pf, w_vid, h_vid)
                        writer.write(frame)

                        frame_num += 1

                    cap.release()
                    writer.release()

                    with open(out_path, "rb") as f:
                        st.video(f.read(), format="video/webm")

                    with open(out_path, "rb") as f:
                        st.download_button(
                            "⬇️ Download Annotated WebM",
                            data=f,
                            file_name="annotated.webm",
                            mime="video/webm",
                            key="download_annotated_btn"
                        )

                    with st.expander("Debug Info"):
                        st.write({
                            "fps": fps,
                            "width": w_vid,
                            "height": h_vid,
                            "total_frames": total_frames,
                            "pred_rows_for_video": int(len(vpreds)),
                            "boxes_drawn_total": int(boxes_drawn_total)
                        })

                    safe_rmtree(work_dir)

                st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">Review Workspace</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-subtitle">Run inference and choose a video to begin QC review.</div>', unsafe_allow_html=True)
            st.info("No processed video selected yet.")
            st.markdown('</div>', unsafe_allow_html=True)

####################################
# TAB 3 — SUMMARY
####################################


with tab_summary:
    summary_df = st.session_state.get("summary_df")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Fish Count Summary</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-subtitle">Overview of model detections across uploaded videos.</div>', unsafe_allow_html=True)

    if summary_df is not None and not summary_df.empty:
        total_videos = len(summary_df)

        if "unique_fish" in summary_df.columns:
            total_fish = int(summary_df["unique_fish"].sum())
            avg_per_video = round(summary_df["unique_fish"].mean(), 1)
        else:
            total_fish = int(summary_df["detections"].sum())
            avg_per_video = round(summary_df["detections"].mean(), 1)

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown(f"""
            <div class="kpi">
                <div class="kpi-label">Videos</div>
                <div class="kpi-value">{total_videos}</div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class="kpi">
                <div class="kpi-label">Total Fish</div>
                <div class="kpi-value">{total_fish}</div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div class="kpi">
                <div class="kpi-label">Avg per Video</div>
                <div class="kpi-value">{avg_per_video}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        csv = summary_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ Download Summary CSV",
            data=csv,
            file_name="fish_count_summary.csv",
            mime="text/csv",
            key="download_summary_csv"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(summary_df, use_container_width=True)

    else:
        st.info("Run inference first to see summary analytics.")

    st.markdown('</div>', unsafe_allow_html=True)