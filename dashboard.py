import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Attendance System",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Automated Attendance System")
st.markdown("**Face Recognition powered by DeepFace + FaceNet**")
st.divider()

def get_attendance(date=None):
    conn = sqlite3.connect("attendance.db")
    if date:
        df = pd.read_sql_query(
            "SELECT * FROM attendance WHERE date=? ORDER BY time DESC",
            conn, params=(date,)
        )
    else:
        df = pd.read_sql_query(
            "SELECT * FROM attendance ORDER BY date DESC, time DESC",
            conn
        )
    conn.close()
    return df

# ── Sidebar filters ──────────────────────────────────
st.sidebar.header("🔍 Filter Records")
today = datetime.now().strftime("%Y-%m-%d")
filter_date = st.sidebar.date_input("Select Date", datetime.now())
show_all    = st.sidebar.checkbox("Show All Records", value=False)

# ── Load data ────────────────────────────────────────
if show_all:
    df = get_attendance()
else:
    df = get_attendance(date=str(filter_date))

# ── Metrics ──────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📅 Date", str(filter_date) if not show_all else "All Dates")
with col2:
    st.metric("👥 Total Present", len(df))
with col3:
    unique = df['name'].nunique() if not df.empty else 0
    st.metric("🧑 Unique Persons", unique)

st.divider()

# ── Table ─────────────────────────────────────────────
if df.empty:
    st.warning("⚠️ No attendance records found for this date.")
else:
    st.subheader("📄 Attendance Records")
    st.dataframe(df, use_container_width=True)

    # ── Download button ───────────────────────────────
    csv = df.to_csv(index=False)
    st.download_button(
        label     = "⬇️ Download as CSV",
        data      = csv,
        file_name = f"attendance_{filter_date}.csv",
        mime      = "text/csv"
    )

# ── Auto refresh ──────────────────────────────────────
st.divider()
if st.button("🔄 Refresh"):
    st.rerun()

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")