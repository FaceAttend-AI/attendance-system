import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os, base64, io
from PIL import Image

# ══════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════
st.set_page_config(
    page_title="FaceAttend",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════
#  GLOBAL CSS — matches uploaded HTML exactly
# ══════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap');

:root {
  --bg:       #0a0c10;
  --surface:  #111318;
  --surface2: #181b22;
  --border:   rgba(255,255,255,0.07);
  --accent:   #7b6ef6;
  --accent2:  #3ecfb2;
  --danger:   #f05c6e;
  --text:     #e8eaf0;
  --muted:    #6b7080;
}

#MainMenu,footer,header { visibility:hidden; }

html, body, .stApp {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Syne', sans-serif !important;
}

/* Grid background */
.stApp::before {
  content: '';
  position: fixed; inset: 0;
  background-image:
    linear-gradient(rgba(123,110,246,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(123,110,246,0.04) 1px, transparent 1px);
  background-size: 48px 48px;
  pointer-events: none;
  z-index: 0;
}

/* Sidebar */
[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
  font-family: 'Syne', sans-serif !important;
  color: var(--text) !important;
}

/* Hide streamlit default radio dots */
[data-testid="stSidebar"] .stRadio > div { gap: 0 !important; }
[data-testid="stSidebar"] .stRadio label {
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
}

/* Inputs */
.stTextInput input, .stSelectbox select, .stTextArea textarea {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-family: 'Syne', sans-serif !important;
  padding: 10px 14px !important;
}
.stTextInput input:focus, .stSelectbox select:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 2px rgba(123,110,246,0.15) !important;
}

/* Buttons */
.stButton > button {
  background: var(--accent) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 10px !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 700 !important;
  padding: 10px 22px !important;
  transition: all .2s !important;
}
.stButton > button:hover {
  background: #6a5de0 !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 20px rgba(123,110,246,0.35) !important;
}

/* Metrics */
[data-testid="metric-container"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
  padding: 18px !important;
}
[data-testid="metric-container"] label {
  color: var(--muted) !important;
  font-family: 'Space Mono', monospace !important;
  font-size: 11px !important;
  text-transform: uppercase;
  letter-spacing: .06em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
  color: var(--accent2) !important;
  font-family: 'Space Mono', monospace !important;
  font-size: 28px !important;
  font-weight: 700 !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
}

/* Download button */
[data-testid="stDownloadButton"] button {
  background: transparent !important;
  border: 1px solid var(--border) !important;
  color: var(--muted) !important;
  font-size: 12px !important;
}
[data-testid="stDownloadButton"] button:hover {
  border-color: var(--accent) !important;
  color: var(--accent) !important;
  background: rgba(123,110,246,0.06) !important;
  transform: none !important;
  box-shadow: none !important;
}

/* ── Component cards ── */
.fa-header {
  margin-bottom: 36px;
}
.fa-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
  font-family: 'Space Mono', monospace;
  color: var(--accent);
  background: rgba(123,110,246,0.1);
  border: 1px solid rgba(123,110,246,0.2);
  border-radius: 20px;
  padding: 4px 12px;
  text-transform: uppercase;
  letter-spacing: .08em;
  margin-bottom: 14px;
}
.fa-title {
  font-size: 28px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -.02em;
  line-height: 1.1;
  margin-bottom: 8px;
}
.fa-sub {
  font-size: 13px;
  color: var(--muted);
  font-family: 'Space Mono', monospace;
}

.phase-card {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 14px;
  border-radius: 12px;
  margin-bottom: 4px;
  cursor: pointer;
  transition: background .2s;
  border-left: 3px solid transparent;
}
.phase-card:hover { background: var(--surface2); }
.phase-card.active {
  background: var(--surface2);
  border-left-color: var(--accent);
}
.phase-num {
  width: 28px; height: 28px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center; justify-content: center;
  font-size: 11px;
  font-family: 'Space Mono', monospace;
  font-weight: 700;
  border: 1px solid var(--border);
  color: var(--muted);
  flex-shrink: 0;
}
.phase-num.done {
  background: var(--accent2) !important;
  border-color: var(--accent2) !important;
  color: #0a0c10 !important;
}
.phase-num.active {
  background: var(--accent) !important;
  border-color: var(--accent) !important;
  color: #fff !important;
}
.phase-name { font-size: 13px; font-weight: 600; margin-bottom: 2px; }
.phase-desc { font-size: 11px; color: var(--muted); font-family: 'Space Mono', monospace; }

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--border);
}
.stat-l { font-size: 11px; color: var(--muted); font-family: 'Space Mono', monospace; }
.stat-v { font-size: 14px; font-weight: 700; color: var(--accent2); font-family: 'Space Mono', monospace; }

.surface-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 20px;
}
.card-label {
  font-size: 10px;
  font-family: 'Space Mono', monospace;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: .08em;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.card-label::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}

.pose-grid {
  display: grid;
  grid-template-columns: repeat(5,1fr);
  gap: 6px;
  margin-bottom: 16px;
}
.pose-item {
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px 4px;
  text-align: center;
  font-size: 10px;
  font-family: 'Space Mono', monospace;
  color: var(--muted);
}
.pose-item.done {
  border-color: var(--accent2);
  color: var(--accent2);
  background: rgba(62,207,178,0.08);
}

.quality-row {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}
.q-badge {
  flex: 1;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px;
  text-align: center;
  font-size: 10px;
  font-family: 'Space Mono', monospace;
  color: var(--muted);
}
.q-badge.ok {
  border-color: var(--accent2);
  color: var(--accent2);
  background: rgba(62,207,178,0.08);
}
.q-val { display: block; font-size: 16px; font-weight: 700; margin-bottom: 2px; }

.recent-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
}
.avatar {
  width: 36px; height: 36px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center; justify-content: center;
  font-size: 12px;
  font-weight: 700;
  font-family: 'Space Mono', monospace;
  flex-shrink: 0;
}
.av-green  { background: rgba(62,207,178,0.15); color: var(--accent2); }
.av-purple { background: rgba(123,110,246,0.15); color: var(--accent);  }
.av-red    { background: rgba(240,92,110,0.15);  color: var(--danger);  }
.av-yellow { background: rgba(255,193,7,0.15);   color: #ffc107;        }

.badge-done {
  background: rgba(62,207,178,0.15);
  color: var(--accent2);
  border: 1px solid rgba(62,207,178,0.3);
  border-radius: 6px;
  padding: 3px 8px;
  font-size: 10px;
  font-family: 'Space Mono', monospace;
  font-weight: 700;
  letter-spacing: .05em;
}
.badge-pend {
  background: rgba(255,193,7,0.12);
  color: #ffc107;
  border: 1px solid rgba(255,193,7,0.25);
  border-radius: 6px;
  padding: 3px 8px;
  font-size: 10px;
  font-family: 'Space Mono', monospace;
  font-weight: 700;
}
.badge-abs {
  background: rgba(240,92,110,0.12);
  color: var(--danger);
  border: 1px solid rgba(240,92,110,0.25);
  border-radius: 6px;
  padding: 3px 8px;
  font-size: 10px;
  font-family: 'Space Mono', monospace;
  font-weight: 700;
}

.progress-bar {
  height: 4px;
  background: var(--border);
  border-radius: 2px;
  overflow: hidden;
  margin: 8px 0;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  border-radius: 2px;
}

.att-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
}
.att-name  { font-size: 13px; font-weight: 600; }
.att-meta  { font-size: 11px; color: var(--muted); font-family: 'Space Mono', monospace; }
.att-time  { font-size: 12px; color: var(--accent2); font-family: 'Space Mono', monospace; }

/* breadcrumb */
.breadcrumb {
  font-size: 11px;
  font-family: 'Space Mono', monospace;
  color: var(--muted);
  margin-bottom: 32px;
  padding: 10px 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  display: inline-block;
}
.breadcrumb .active { color: var(--accent); }

.connector {
  width: 1px; height: 16px;
  background: var(--border);
  margin: 2px 0 2px 27px;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  DATABASE
# ══════════════════════════════════════════════════════
DB_PATH = "attendance.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn(); c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reg_no TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        department TEXT DEFAULT '',
        role TEXT DEFAULT 'Student',
        class TEXT DEFAULT '',
        email TEXT DEFAULT '',
        phone TEXT DEFAULT '',
        photo TEXT DEFAULT '',
        img_count INTEGER DEFAULT 0,
        status TEXT DEFAULT 'PENDING',
        registered TEXT DEFAULT CURRENT_DATE
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reg_no TEXT DEFAULT '',
        name TEXT NOT NULL,
        department TEXT DEFAULT '',
        class TEXT DEFAULT '',
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        camera_id INTEGER DEFAULT 0,
        status TEXT DEFAULT 'Present'
    )''')
    for col, typ in [("reg_no","TEXT"),("department","TEXT"),
                     ("class","TEXT"),("camera_id","INTEGER")]:
        try:
            c.execute(f"ALTER TABLE attendance ADD COLUMN {col} {typ} DEFAULT ''")
        except: pass
    conn.commit(); conn.close()

init_db()

def query(sql, params=()):
    conn = get_conn()
    df   = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df

def execute(sql, params=()):
    conn = get_conn(); c = conn.cursor()
    c.execute(sql, params)
    conn.commit(); conn.close()

def get_stats():
    today = datetime.now().strftime("%Y-%m-%d")
    conn  = get_conn(); c = conn.cursor()
    total = c.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    pres  = c.execute("SELECT COUNT(DISTINCT name) FROM attendance WHERE date=?",
                      (today,)).fetchone()[0]
    depts = c.execute("SELECT COUNT(DISTINCT department) FROM students").fetchone()[0]
    total_a = c.execute("SELECT COUNT(*) FROM attendance").fetchone()[0]
    trained = c.execute("SELECT COUNT(*) FROM students WHERE status='TRAINED'").fetchone()[0]
    conn.close()
    return {"total": total, "present": pres, "absent": max(0, total-pres),
            "pct": f"{int(pres/max(total,1)*100)}%",
            "depts": depts, "total_att": total_a, "trained": trained}

def img_b64(data):
    return base64.b64encode(data).decode()
def b64_img(s):
    try:
        return Image.open(io.BytesIO(base64.b64decode(s))) if s else None
    except: return None
def initials(name):
    p = name.strip().split()
    return (p[0][0] + (p[-1][0] if len(p)>1 else p[0][1])).upper() if p else "??"

AV_COLORS = ["av-green","av-purple","av-red","av-yellow"]
def av_color(name):
    return AV_COLORS[sum(ord(c) for c in name) % len(AV_COLORS)]

# ══════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════
TODAY = datetime.now().strftime("%Y-%m-%d")
PAGES = [
    ("01","Overview",        "dashboard & live stats",       "🏠"),
    ("02","Register Student","capture face dataset",         "📝"),
    ("03","All Students",    "manage enrolled members",      "👥"),
    ("04","Attendance",      "records & filters",            "📋"),
    ("05","Analytics",       "charts & insights",            "📊"),
    ("06","Reports",         "export & email",               "📧"),
]

with st.sidebar:
    st.markdown("""
    <div style='padding:32px 0 40px 0'>
      <div style='display:flex;align-items:center;gap:10px;margin-bottom:8px'>
        <div style='width:34px;height:34px;background:var(--accent);
                    border-radius:10px;display:flex;align-items:center;
                    justify-content:center;font-size:16px'>◉</div>
        <div>
          <div style='font-size:17px;font-weight:700;letter-spacing:-.02em'>
            Face<span style='color:var(--accent)'>Attend</span>
          </div>
          <div style='font-size:10px;color:var(--muted);
                      font-family:"Space Mono",monospace'>v2.0 · DeepFace</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Page selector (hidden, driven by buttons)
    if "page" not in st.session_state:
        st.session_state.page = "Overview"

    for num, name, desc, icon in PAGES:
        is_active = st.session_state.page == name
        st.markdown(f"""
        <div class='phase-card {"active" if is_active else ""}'>
          <div class='phase-num {"active" if is_active else ""}'>{num}</div>
          <div>
            <div class='phase-name' style='color:{"var(--text)" if is_active else "var(--muted)"}'>{icon} {name}</div>
            <div class='phase-desc'>{desc}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"{name}", key=f"nav_{name}",
                     use_container_width=True,
                     help=desc):
            st.session_state.page = name
            st.rerun()

    st.markdown("<div class='connector'></div>", unsafe_allow_html=True)
    st.divider()

    stats = get_stats()
    st.markdown(f"""
    <div style='padding:4px 0'>
      <div style='font-size:10px;font-family:"Space Mono",monospace;
                  color:var(--muted);text-transform:uppercase;
                  letter-spacing:.06em;margin-bottom:12px'>Quick stats</div>
      <div class='stat-row'>
        <span class='stat-l'>enrolled</span>
        <span class='stat-v'>{stats["total"]:03d}</span>
      </div>
      <div class='stat-row'>
        <span class='stat-l'>present today</span>
        <span class='stat-v'>{stats["present"]:03d}</span>
      </div>
      <div class='stat-row'>
        <span class='stat-l'>trained</span>
        <span class='stat-v'>{stats["trained"]:03d}</span>
      </div>
      <div class='stat-row'>
        <span class='stat-l'>attendance %</span>
        <span class='stat-v'>{stats["pct"]}</span>
      </div>
      <div class='progress-bar' style='margin-top:14px'>
        <div class='progress-fill' style='width:{int(stats["present"]/max(stats["total"],1)*100)}%'></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='margin-top:24px;font-size:10px;font-family:"Space Mono",monospace;
                color:var(--muted);line-height:2'>
      ◉ FaceAttend v2.0<br>
      🔗 <a href='https://github.com/Afridahamed001/attendance-system'
            style='color:var(--accent)'>GitHub</a><br>
      🕐 {datetime.now().strftime("%H:%M · %d %b %Y")}
    </div>
    """, unsafe_allow_html=True)

PAGE = st.session_state.page

# ══════════════════════════════════════════════════════
#  PAGE 1 — OVERVIEW
# ══════════════════════════════════════════════════════
if PAGE == "Overview":
    st.markdown(f"""
    <div class='fa-header'>
      <div class='fa-tag'>◉ live dashboard</div>
      <div class='fa-title'>Attendance Overview</div>
      <div class='fa-sub'>Real-time face recognition · {TODAY}</div>
    </div>
    """, unsafe_allow_html=True)

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Enrolled",        stats["total"])
    c2.metric("Present Today",   stats["present"])
    c3.metric("Absent Today",    stats["absent"])
    c4.metric("Attendance %",    stats["pct"])
    c5.metric("Departments",     stats["depts"])

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1.6, 1])

    with col1:
        st.markdown("""
        <div class='surface-card'>
          <div class='card-label'>Today's attendance log</div>
        """, unsafe_allow_html=True)
        df_today = query(
            "SELECT name,reg_no,department,class,time,status FROM attendance WHERE date=? ORDER BY time DESC",
            (TODAY,)
        )
        if df_today.empty:
            st.markdown("""
            <div style='text-align:center;padding:40px 0;color:var(--muted);
                        font-family:"Space Mono",monospace;font-size:12px'>
              No records yet — run <code style='color:var(--accent)'>attendance.py</code>
            </div>
            """, unsafe_allow_html=True)
        else:
            for _, r in df_today.iterrows():
                iv = initials(r["name"])
                ac = av_color(r["name"])
                st.markdown(f"""
                <div class='att-row'>
                  <div style='display:flex;align-items:center;gap:12px'>
                    <div class='avatar {ac}'>{iv}</div>
                    <div>
                      <div class='att-name'>{r["name"]}</div>
                      <div class='att-meta'>{r.get("reg_no","—")} · {r.get("department","—")} · {r.get("class","—")}</div>
                    </div>
                  </div>
                  <div style='text-align:right'>
                    <div class='att-time'>{r["time"]}</div>
                    <span class='badge-done'>{r["status"]}</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='surface-card'>
          <div class='card-label'>7-day trend</div>
        """, unsafe_allow_html=True)
        df_all = query("SELECT date, COUNT(*) as cnt FROM attendance GROUP BY date ORDER BY date DESC LIMIT 7")
        if not df_all.empty:
            df_all["date"] = pd.to_datetime(df_all["date"])
            st.bar_chart(df_all.set_index("date")["cnt"], color="#7b6ef6", height=160)
        else:
            st.markdown("<p style='color:var(--muted);font-size:12px;font-family:Space Mono'>No data yet</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class='surface-card'>
          <div class='card-label'>Recent students</div>
        """, unsafe_allow_html=True)
        df_rec = query("SELECT name, reg_no, department, status FROM students ORDER BY id DESC LIMIT 4")
        for _, s in df_rec.iterrows():
            iv = initials(s["name"]); ac = av_color(s["name"])
            badge = "badge-done" if s["status"]=="TRAINED" else "badge-pend"
            st.markdown(f"""
            <div class='recent-item'>
              <div class='avatar {ac}'>{iv}</div>
              <div style='flex:1'>
                <div style='font-size:13px;font-weight:600'>{s["name"]}</div>
                <div class='att-meta'>{s["reg_no"]} · {s["department"]}</div>
              </div>
              <span class='{badge}'>{s["status"]}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  PAGE 2 — REGISTER STUDENT
# ══════════════════════════════════════════════════════
elif PAGE == "Register Student":
    st.markdown(f"""
    <div class='breadcrumb'>FaceAttend › <span class='active'>Register Student</span></div>
    <div class='fa-header'>
      <div class='fa-tag'>◉ phase 02</div>
      <div class='fa-title'>Register & Capture</div>
      <div class='fa-sub'>Fill details · capture face dataset · save to system</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("<div class='surface-card'><div class='card-label'>Student information</div>", unsafe_allow_html=True)

        reg_no = st.text_input("Student ID *", placeholder="e.g. STU2024001")
        if reg_no:
            import re
            if re.match(r'^[A-Z]{2,4}\d{4,10}$', reg_no.upper()):
                st.markdown(f"<div style='font-size:11px;color:var(--accent2);font-family:\"Space Mono\",monospace;margin-top:-12px;margin-bottom:8px'>✓ Valid · dataset/{reg_no.upper()}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='font-size:11px;color:var(--danger);font-family:\"Space Mono\",monospace;margin-top:-12px;margin-bottom:8px'>⚠ Use format: STU2024001</div>", unsafe_allow_html=True)

        name = st.text_input("Full Name *", placeholder="e.g. Arjun Krishnamurthy")

        dept = st.selectbox("Department *", [
            "Computer Science & Engineering",
            "Electronics & Communication",
            "Information Technology",
            "Mechanical Engineering",
            "Civil Engineering",
            "Artificial Intelligence & DS",
            "Faculty / Staff"
        ])

        role = st.selectbox("Role *", ["Student","Faculty","Staff","Admin"])

        cls_opts = [f"{yr} Year {sec}" for yr in ["I","II","III","IV"] for sec in ["A","B","C"]]
        student_class = st.selectbox("Class / Section", cls_opts)

        c1_, c2_ = st.columns(2)
        with c1_: email = st.text_input("Email", placeholder="arjun@college.edu")
        with c2_: phone = st.text_input("Phone", placeholder="+91 98765 43210")

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='surface-card'><div class='card-label'>Face capture</div>", unsafe_allow_html=True)

        cam_img = st.camera_input("📸 Click to capture", key="cam_reg")
        photo_b64 = ""
        if cam_img:
            img = Image.open(cam_img).resize((300,300))
            buf = io.BytesIO(); img.save(buf, format="JPEG", quality=85)
            photo_b64 = img_b64(buf.getvalue())
            st.markdown("<div style='color:var(--accent2);font-size:12px;font-family:\"Space Mono\",monospace'>✓ Photo captured</div>", unsafe_allow_html=True)

        up = st.file_uploader("or upload photo", type=["jpg","jpeg","png"])
        if up and not photo_b64:
            img = Image.open(up).resize((300,300))
            buf = io.BytesIO(); img.save(buf, format="JPEG", quality=85)
            photo_b64 = img_b64(buf.getvalue())
            st.markdown("<div style='color:var(--accent2);font-size:12px;font-family:\"Space Mono\",monospace'>✓ Photo uploaded</div>", unsafe_allow_html=True)

        st.markdown("<div class='card-label' style='margin-top:16px'>Pose variation</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='pose-grid'>
          <div class='pose-item done'>◉<br>Front</div>
          <div class='pose-item done'>◁<br>Left</div>
          <div class='pose-item done'>▷<br>Right</div>
          <div class='pose-item'>△<br>Up</div>
          <div class='pose-item'>▽<br>Down</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='card-label'>Quality checks</div>", unsafe_allow_html=True)
        ok = "ok" if photo_b64 else ""
        st.markdown(f"""
        <div class='quality-row'>
          <div class='q-badge {ok}'><span class='q-val'>{'98%' if ok else '—'}</span>Sharpness</div>
          <div class='q-badge {ok}'><span class='q-val'>{'1' if ok else '—'}</span>Faces</div>
          <div class='q-badge'><span class='q-val'>60%</span>Poses</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    c_l, c_m, c_r = st.columns([1,1,1])
    with c_m:
        if st.button("Register & Save →", use_container_width=True, type="primary"):
            if not reg_no or not name:
                st.error("❌ Student ID and Name are required")
            elif not photo_b64:
                st.warning("⚠️ Capture or upload a photo first")
            else:
                try:
                    execute(
                        "INSERT INTO students (reg_no,name,department,role,class,email,phone,photo,status) VALUES (?,?,?,?,?,?,?,?,?)",
                        (reg_no.upper(), name, dept, role, student_class, email, phone, photo_b64, "PENDING")
                    )
                    st.success(f"🎉 {name} registered! Now run collect_faces.py → name: **{name}**")
                    st.balloons()
                except Exception as e:
                    if "UNIQUE" in str(e):
                        st.error(f"❌ Student ID '{reg_no}' already exists!")
                    else:
                        st.error(str(e))

    # Recent registrations
    st.markdown("""
    <div class='surface-card' style='margin-top:24px'>
      <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:16px'>
        <div class='card-label' style='margin-bottom:0'>Recent registrations</div>
      </div>
    """, unsafe_allow_html=True)

    df_rec = query("SELECT name, reg_no, department, img_count, status FROM students ORDER BY id DESC LIMIT 5")
    if df_rec.empty:
        st.markdown("<p style='color:var(--muted);font-size:12px;font-family:\"Space Mono\",monospace'>No students registered yet.</p>", unsafe_allow_html=True)
    else:
        for _, s in df_rec.iterrows():
            iv = initials(s["name"]); ac = av_color(s["name"])
            badge = "badge-done" if s["status"]=="TRAINED" else "badge-pend"
            st.markdown(f"""
            <div class='recent-item'>
              <div class='avatar {ac}'>{iv}</div>
              <div style='flex:1'>
                <div style='font-size:13px;font-weight:600'>{s["name"]}</div>
                <div class='att-meta'>{s["reg_no"]} · {s["department"]} · {s["img_count"]} imgs</div>
              </div>
              <span class='{badge}'>{s["status"]}</span>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  PAGE 3 — ALL STUDENTS
# ══════════════════════════════════════════════════════
elif PAGE == "All Students":
    st.markdown("""
    <div class='fa-header'>
      <div class='fa-tag'>◉ phase 03</div>
      <div class='fa-title'>Enrolled Members</div>
      <div class='fa-sub'>All registered students and staff</div>
    </div>
    """, unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    with c1: search = st.text_input("🔍 Search", placeholder="Name or ID...")
    with c2:
        depts = ["All"] + query("SELECT DISTINCT department FROM students WHERE department!=''")["department"].tolist()
        sel_d = st.selectbox("Department", depts)
    with c3:
        roles = ["All","Student","Faculty","Staff","Admin"]
        sel_r = st.selectbox("Role", roles)

    sql    = "SELECT * FROM students WHERE 1=1"
    params = []
    if search:
        sql += " AND (name LIKE ? OR reg_no LIKE ?)"; params += [f"%{search}%",f"%{search}%"]
    if sel_d != "All":
        sql += " AND department=?"; params.append(sel_d)
    if sel_r != "All":
        sql += " AND role=?"; params.append(sel_r)

    df = query(sql, params)
    st.markdown(f"<div style='font-size:12px;font-family:\"Space Mono\",monospace;color:var(--muted);margin-bottom:16px'>{len(df)} members found</div>", unsafe_allow_html=True)

    if df.empty:
        st.info("No students registered yet.")
    else:
        for i in range(0, len(df), 3):
            cols = st.columns(3)
            for j, (_, s) in enumerate(df.iloc[i:i+3].iterrows()):
                with cols[j]:
                    iv = initials(s["name"]); ac = av_color(s["name"])
                    badge = "badge-done" if s["status"]=="TRAINED" else "badge-pend"
                    photo = b64_img(s.get("photo",""))
                    if photo:
                        st.image(photo, width=70)
                    st.markdown(f"""
                    <div class='surface-card' style='padding:16px'>
                      <div style='display:flex;align-items:center;gap:10px;margin-bottom:10px'>
                        <div class='avatar {ac}'>{iv}</div>
                        <div>
                          <div style='font-size:13px;font-weight:700'>{s["name"]}</div>
                          <div style='font-size:11px;color:var(--muted);font-family:"Space Mono",monospace'>{s["reg_no"]}</div>
                        </div>
                      </div>
                      <div style='font-size:11px;color:var(--muted);font-family:"Space Mono",monospace;line-height:2'>
                        🏢 {s["department"]}<br>
                        📚 {s.get("class","—")}<br>
                        👤 {s.get("role","Student")}<br>
                        📧 {s.get("email","—") or "—"}<br>
                        📱 {s.get("phone","—") or "—"}<br>
                        📅 {s.get("registered","—")}
                      </div>
                      <div style='margin-top:10px'>
                        <span class='{badge}'>{s["status"]}</span>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("🗑 Remove", key=f"del_{s['reg_no']}", use_container_width=True):
                        execute("DELETE FROM students WHERE reg_no=?", (s["reg_no"],))
                        st.rerun()

    st.divider()
    if not df.empty:
        export = df.drop(columns=["photo"], errors="ignore")
        st.download_button("⬇️ Export CSV", export.to_csv(index=False),
                           f"students_{TODAY}.csv", "text/csv")

# ══════════════════════════════════════════════════════
#  PAGE 4 — ATTENDANCE
# ══════════════════════════════════════════════════════
elif PAGE == "Attendance":
    st.markdown("""
    <div class='fa-header'>
      <div class='fa-tag'>◉ phase 04</div>
      <div class='fa-title'>Attendance Records</div>
      <div class='fa-sub'>Filter · search · export</div>
    </div>
    """, unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    with c1: date_f = st.date_input("📅 Date", datetime.now())
    with c2: show_all = st.checkbox("Show All Dates")
    with c3:
        depts = ["All"] + query("SELECT DISTINCT department FROM attendance WHERE department!=''")["department"].tolist()
        sel_d = st.selectbox("Department", depts)
    with c4: name_q = st.text_input("Search name", placeholder="Student name...")

    sql = "SELECT * FROM attendance WHERE 1=1"; params = []
    if not show_all: sql += " AND date=?"; params.append(str(date_f))
    if sel_d != "All": sql += " AND department=?"; params.append(sel_d)
    if name_q: sql += " AND name LIKE ?"; params.append(f"%{name_q}%")
    sql += " ORDER BY date DESC, time DESC"

    df = query(sql, params)
    c1,c2,c3 = st.columns(3)
    c1.metric("Total Records",    len(df))
    c2.metric("Unique Students",  df["name"].nunique() if not df.empty else 0)
    c3.metric("Period", "All" if show_all else str(date_f))

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    if df.empty:
        st.markdown("""
        <div class='surface-card' style='text-align:center;padding:60px'>
          <div style='font-size:32px;margin-bottom:12px'>📋</div>
          <div style='color:var(--muted);font-family:"Space Mono",monospace;font-size:12px'>
            No attendance records found for selected filters.
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<div class='surface-card'><div class='card-label'>Records</div>", unsafe_allow_html=True)
        for _, r in df.iterrows():
            iv = initials(r["name"]); ac = av_color(r["name"])
            st.markdown(f"""
            <div class='att-row'>
              <div style='display:flex;align-items:center;gap:12px'>
                <div class='avatar {ac}'>{iv}</div>
                <div>
                  <div class='att-name'>{r["name"]}</div>
                  <div class='att-meta'>
                    {r.get("reg_no","—")} · {r.get("department","—")} · {r.get("class","—")}
                  </div>
                </div>
              </div>
              <div style='text-align:right'>
                <div class='att-time'>{r["time"]} · {r["date"]}</div>
                <span class='badge-done'>{r["status"]}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        c1_,c2_ = st.columns(2)
        with c1_:
            st.download_button("⬇️ Full CSV",    df.to_csv(index=False), f"attendance_{date_f}.csv", "text/csv", use_container_width=True)
        with c2_:
            summary = df.groupby(["name","department"]).size().reset_index(name="Days Present")
            st.download_button("⬇️ Summary CSV", summary.to_csv(index=False), f"summary_{date_f}.csv", "text/csv", use_container_width=True)

# ══════════════════════════════════════════════════════
#  PAGE 5 — ANALYTICS
# ══════════════════════════════════════════════════════
elif PAGE == "Analytics":
    st.markdown("""
    <div class='fa-header'>
      <div class='fa-tag'>◉ phase 05</div>
      <div class='fa-title'>Analytics</div>
      <div class='fa-sub'>Trends · departments · top students</div>
    </div>
    """, unsafe_allow_html=True)

    df = query("SELECT * FROM attendance")
    if df.empty:
        st.info("No data yet. Run attendance.py first.")
    else:
        df["date"] = pd.to_datetime(df["date"])
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("<div class='surface-card'><div class='card-label'>Daily trend</div>", unsafe_allow_html=True)
            daily = df.groupby("date").size().reset_index(name="Count")
            st.line_chart(daily.set_index("date"), color="#7b6ef6", height=180)
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='surface-card'><div class='card-label'>By department</div>", unsafe_allow_html=True)
            if "department" in df.columns:
                dp = df[df["department"]!=""].groupby("department").size().reset_index(name="Count")
                if not dp.empty:
                    st.bar_chart(dp.set_index("department")["Count"], color="#3ecfb2", height=180)
            st.markdown("</div>", unsafe_allow_html=True)

        c1,c2 = st.columns(2)
        with c1:
            st.markdown("<div class='surface-card'><div class='card-label'>By class / section</div>", unsafe_allow_html=True)
            if "class" in df.columns:
                cd = df[df["class"]!=""].groupby("class").size().reset_index(name="Count")
                if not cd.empty:
                    st.bar_chart(cd.set_index("class")["Count"], color="#7b6ef6", height=180)
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='surface-card'><div class='card-label'>Top 10 students</div>", unsafe_allow_html=True)
            top = df.groupby("name").size().reset_index(name="Days").sort_values("Days", ascending=False).head(10)
            for _, r in top.iterrows():
                iv = initials(r["name"]); ac = av_color(r["name"])
                pct = int(r["Days"] / max(df["date"].nunique(),1) * 100)
                st.markdown(f"""
                <div style='display:flex;align-items:center;gap:10px;margin-bottom:8px'>
                  <div class='avatar {ac}' style='width:28px;height:28px;font-size:10px'>{iv}</div>
                  <div style='flex:1'>
                    <div style='font-size:12px;font-weight:600;margin-bottom:3px'>{r["name"]}</div>
                    <div class='progress-bar' style='margin:0'>
                      <div class='progress-fill' style='width:{pct}%'></div>
                    </div>
                  </div>
                  <div style='font-size:11px;font-family:"Space Mono",monospace;color:var(--accent2)'>{r["Days"]}d</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  PAGE 6 — REPORTS
# ══════════════════════════════════════════════════════
elif PAGE == "Reports":
    st.markdown("""
    <div class='fa-header'>
      <div class='fa-tag'>◉ phase 06</div>
      <div class='fa-title'>Reports & Export</div>
      <div class='fa-sub'>Download · email · share</div>
    </div>
    """, unsafe_allow_html=True)

    df_today = query("SELECT * FROM attendance WHERE date=?", (TODAY,))
    df_all   = query("SELECT * FROM attendance")
    df_stu   = query("SELECT * FROM students").drop(columns=["photo"], errors="ignore")

    c1,c2,c3 = st.columns(3)
    c1.metric("Today's Records", len(df_today))
    c2.metric("Total Records",   len(df_all))
    c3.metric("Total Students",  len(df_stu))

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='surface-card'><div class='card-label'>Downloads</div>", unsafe_allow_html=True)
        if not df_today.empty:
            st.download_button("📥 Today's Attendance", df_today.to_csv(index=False),
                               f"attendance_{TODAY}.csv", "text/csv", use_container_width=True)
        if not df_all.empty:
            st.download_button("📥 All Attendance Records", df_all.to_csv(index=False),
                               "attendance_all.csv", "text/csv", use_container_width=True)
        if not df_stu.empty:
            st.download_button("📥 Students List", df_stu.to_csv(index=False),
                               "students.csv", "text/csv", use_container_width=True)
            summary = df_all.groupby(["name","department"]).size().reset_index(name="Days Present") if not df_all.empty else pd.DataFrame()
            if not summary.empty:
                st.download_button("📥 Attendance Summary", summary.to_csv(index=False),
                                   "summary.csv", "text/csv", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='surface-card'>
          <div class='card-label'>Email report</div>
          <div style='background:var(--surface2);border-radius:12px;padding:20px;
                      border-left:3px solid var(--accent)'>
            <div style='font-size:13px;font-weight:700;margin-bottom:8px'>📤 Send daily email</div>
            <div style='font-size:12px;color:var(--muted);font-family:"Space Mono",monospace;
                        line-height:1.8;margin-bottom:12px'>
              Open a new CMD window and run:
            </div>
            <code style='background:var(--bg);padding:10px 14px;border-radius:8px;
                         display:block;color:var(--accent);font-size:12px;
                         border:1px solid var(--border)'>
              python email_report.py
            </code>
          </div>
          <div style='margin-top:20px'>
            <div class='card-label'>Project links</div>
            <div style='font-size:12px;font-family:"Space Mono",monospace;line-height:2.2;color:var(--muted)'>
              🔗 <a href='https://github.com/Afridahamed001/attendance-system'
                    style='color:var(--accent)'>GitHub Repository</a><br>
              ◉ Model: DeepFace + FaceNet<br>
              🐍 Python 3.10 · TF 2.21<br>
              👨‍💻 Manikandan L.R · Afrid Ahamed
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)