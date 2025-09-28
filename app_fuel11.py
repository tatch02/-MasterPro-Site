# SiteMaster Pro — Streamlit Edition
# ---------------------------------------------------------------
# Mirrors the uploaded mockup ("4ED APP 1.html") and the spec (Sit.pdf)
# with a modular, stylish Streamlit app scaffold. Replace the sample
# data generators with your real data sources when ready.
# ---------------------------------------------------------------

from __future__ import annotations

import io
import math
import textwrap
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Optional trendlines (avoid hard dependency on statsmodels)
try:
    import statsmodels.api as sm  # noqa: F401
    TRENDLINE = "ols"
except Exception:
    TRENDLINE = None

# ---------------------------------------------------------------
# Page config & global style
# ---------------------------------------------------------------
st.set_page_config(
    page_title="SiteMaster Pro — Construction Management",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Global CSS to emulate the Tailwind-y look from the HTML mockup
CUSTOM_CSS = """
<style>
/***** Layout cleanup *****/
[data-testid="stSidebar"] > div { padding-top: 1rem; }
header[data-testid="stHeader"] { background: rgba(255,255,255,.75); backdrop-filter: saturate(180%) blur(10px); border-bottom: 1px solid #eee; }

/***** Card & badge system *****/
.card { background: #fff; border: 1px solid #eef0f4; border-radius: 14px; padding: 18px; box-shadow: 0 1px 2px rgba(0,0,0,.03); transition: box-shadow .2s ease; }
.card:hover { box-shadow: 0 6px 18px rgba(36, 41, 46, .06); }
.card-title { font-weight: 700; font-size: 1.05rem; margin-bottom: .75rem; }
.kpi { font-weight: 800; font-size: 1.7rem; line-height: 1; }
.kpi-sub { color: #667085; font-weight: 600; margin-top: 2px; }
.pill { display: inline-block; padding: 4px 10px; border-radius: 999px; font-size: .72rem; font-weight: 600; }
.status-good { background: #ecfdf5; color: #047857; }
.status-warning { background: #fff7ed; color: #c2410c; }
.status-critical { background: #fef2f2; color: #b91c1c; }
.status-pending { background: #eff6ff; color: #1d4ed8; }

.gradient-blue { background: linear-gradient(135deg,#dbeafe 0%,#eff6ff 100%); }
.gradient-green { background: linear-gradient(135deg,#dcfce7 0%,#ecfdf5 100%); }
.gradient-orange { background: linear-gradient(135deg,#ffedd5 0%,#fff7ed 100%); }
.gradient-purple { background: linear-gradient(135deg,#ede9fe 0%,#faf5ff 100%); }

.progress { width: 100%; height: 10px; border-radius: 999px; background: #e5e7eb; overflow: hidden; }
.progress > span { display:block; height: 100%; background: #2563eb; border-radius: 999px; }

.pulse-dot { width:10px; height:10px; background:#22c55e; border-radius:999px; box-shadow:0 0 0 rgba(34,197,94, 0.7); animation:pulse 2s infinite; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(34,197,94, 0.5);} 70% { box-shadow: 0 0 0 12px rgba(34,197,94, 0);} 100% { box-shadow: 0 0 0 0 rgba(34,197,94, 0);} }

.small { font-size: .75rem; color:#6b7280; }
.muted { color:#6b7280; }
.divider { height:1px; background:#eef0f4; margin: 8px 0 16px; }

/***** Hide default footer *****/
footer { visibility: hidden; height: 0; }

/* Tweak dataframe look */
[data-testid="stTable"] table { border-collapse: separate; border-spacing: 0; }
[data-testid="stTable"] th { background: #f8fafc; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------
# Header (branding + quick actions)
# ---------------------------------------------------------------
col_brand, col_status, col_actions, col_profile = st.columns([1.4, 1, 1, 1.2])
with col_brand:
    st.markdown(
        """
        <div style="display:flex;gap:12px;align-items:center;">
            <div style="width:40px;height:40px;border-radius:12px;background:linear-gradient(135deg,#f97316,#dc2626);display:flex;align-items:center;justify-content:center;color:white;font-weight:800;">🏗️</div>
            <div>
              <div style="font-weight:800;font-size:1.15rem;">SiteMaster <span style="color:#ea580c;">Pro</span></div>
              <div class="small">Integrated Construction Management Platform</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col_status:
    st.markdown(
        """
        <div style="display:flex;gap:8px;align-items:center;justify-content:flex-start;margin-top:8px;">
            <span class="pulse-dot"></span>
            <span class="muted">Site Alpha Online</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col_actions:
    # Build a simple daily report text buffer as placeholder
    today = datetime.now().strftime("%Y-%m-%d")
    report_text = f"SiteMaster Pro — Daily Report ( {today} )\n\nAll systems operational. Replace with real auto-generated content."
    st.download_button("Download Daily Report", report_text.encode(), file_name=f"daily_report_{today}.txt")
    st.button("Alerts (5)")
with col_profile:
    st.markdown(
        """
        <div style="display:flex;gap:10px;align-items:center;justify-content:flex-end;">
          <div style="width:36px;height:36px;border-radius:999px;background:linear-gradient(135deg,#60a5fa,#2563eb);display:flex;align-items:center;justify-content:center;color:white;font-weight:700;">DM</div>
          <div style="text-align:right;">
            <div style="font-weight:700;">Dennis Mintah</div>
            <div class="small">Site Manager</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------
with st.sidebar:
    st.title("🏗️ SiteMaster Pro")
    st.caption("Modular construction ops dashboard")
    section = st.radio(
        "Go to module",
        (
            "Main Dashboard",
            "Fleet Management",
            "Fuel Farm",
            "Stores Management",
            "Block Production",
            "HR Management",
            "Quantity Surveying",
        ),
        index=0,
    )
    st.write("")
    st.info(
        "Tip: connect your real datasets to replace the dummy dataframes below. Each section is self-contained for easy wiring.")

# ---------------------------------------------------------------
# Demo data helpers (replace with real sources later)
# ---------------------------------------------------------------
@st.cache_data
def demo_production_df(days: int = 14) -> pd.DataFrame:
    now = datetime.now()
    dates = [now - timedelta(days=i) for i in range(days)][::-1]
    return pd.DataFrame({
        "date": dates,
        "blocks": np.random.randint(6000, 9500, size=days),
        "cost": np.random.randint(8000, 14000, size=days),
        "safety": np.random.randint(90, 100, size=days),
    })

@st.cache_data
def demo_resource_util() -> pd.DataFrame:
    return pd.DataFrame({
        "resource": ["Fleet", "Equipment", "Personnel", "Materials"],
        "value": [32, 24, 28, 16],
    })

@st.cache_data
def demo_activity() -> pd.DataFrame:
    return pd.DataFrame({
        "metric": ["Earthworks", "Haulage", "Mixing", "Lifting", "Stocking", "QC"],
        "score": np.random.randint(60, 95, 6),
    })

@st.cache_data
def demo_fleet_table() -> pd.DataFrame:
    return pd.DataFrame([
        ["EX-001", "Excavator", "Active", "Site A — Block 3", 0.85, "2025-01-15", "John Doe"],
        ["DT-002", "Dump Truck", "Active", "Quarry Site", 0.45, "2025-01-20", "Mike Johnson"],
        ["CR-003", "Crane", "Maintenance", "Workshop", 0.15, "In Progress", "—"],
        ["MX-004", "Mixer", "Active", "Production Area", 0.78, "2025-01-25", "Sarah Wilson"],
    ], columns=["Vehicle ID", "Type", "Status", "GPS Location", "Fuel Level", "Next Service", "Operator"])

@st.cache_data
def demo_fuel_weekly() -> pd.DataFrame:
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    diesel = [1200, 950, 980, 1100, 1050, 875, 900]
    petrol = [350, 300, 280, 310, 295, 250, 260]
    return pd.DataFrame({"day": days, "Diesel (L)": diesel, "Petrol (L)": petrol})

@st.cache_data
def demo_top_consumers() -> pd.DataFrame:
    return pd.DataFrame({
        "Equipment": ["EX-001", "DT-002", "MX-004", "CR-003", "GEN-001"],
        "Litres": [520, 470, 390, 340, 260]
    })

@st.cache_data
def demo_activity_usage() -> pd.DataFrame:
    return pd.DataFrame({
        "Activity": ["Excavation", "Transport", "Mixing", "Lifting", "Power"],
        "Litres": [38, 31, 16, 9, 6]
    })

@st.cache_data
def demo_inventory_df() -> pd.DataFrame:
    return pd.DataFrame([
        ["Cement 50kg", "Materials", 450, "bag", 150, "Good"],
        ["Sand", "Materials", 25, "ton", 10, "Low"],
        ["Safety Helmets", "PPE", 285, "pcs", 100, "Good"],
        ["Gloves", "PPE", 120, "pair", 80, "Low"],
        ["Rebar 12mm", "Materials", 4.5, "ton", 5, "Critical"],
    ], columns=["Item", "Category", "Stock", "Unit", "Min Threshold", "Status"])

@st.cache_data
def demo_hr_df() -> pd.DataFrame:
    return pd.DataFrame([
        ["EMP-001","John Doe","Production","Operator","Present"],
        ["EMP-002","Jane Smith","Operations","Driver","Present"],
        ["EMP-003","Samuel Boateng","Security","Guard","Sick Leave"],
        ["EMP-004","Akosua Mensah","Admin","HR Officer","Present"],
        ["EMP-005","Kwesi Owusu","Production","QC","Annual Leave"],
    ], columns=["Employee ID","Name","Department","Role","Status"])    

# ---------------------------------------------------------------
# Building blocks (UI)
# ---------------------------------------------------------------

def kpi_card(emoji: str, value: str, label: str, pill_text: str | None = None, pill_class: str = "status-good", sub: str | None = None):
    pill_html = f'<span class="pill {pill_class}">{pill_text}</span>' if pill_text else ""
    sub_html = f'<div class="small">{sub}</div>' if sub else ""
    st.markdown(
        f"""
        <div class="card">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
                <div style="width:48px;height:48px;border-radius:12px;background:#f1f5f9;display:flex;align-items:center;justify-content:center;font-size:22px;">{emoji}</div>
                {pill_html}
            </div>
            <div class="kpi">{value}</div>
            <div class="kpi-sub">{label}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------
# Sections
# ---------------------------------------------------------------

def page_dashboard():
    st.subheader("Real-Time Operations Dashboard")
    st.caption("Continuous monitoring of all construction site activities")

    # KPIs row (mirrors the HTML defaults)
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("🚚", "24", "Fleet Status", pill_text="85% Active", sub="20 active, 4 maintenance")
    with c2: kpi_card("⛽", "8,450L", "Fuel Available", pill_text="Good Stock")
    with c3: kpi_card("🏭", "8,450", "Blocks Produced", pill_text="70%", pill_class="status-warning", sub="Target: 12,000 blocks")
    with c4: kpi_card("👷", "156", "Workers Present", pill_text="98%", sub="3 on leave, 1 sick")

    st.write("")
    # Analytics & Charts
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="card"><div class="card-title">Production Overview</div>', unsafe_allow_html=True)
        df = demo_production_df(14)
        fig = px.line(df, x="date", y="blocks", markers=True)
        fig.update_layout(margin=dict(l=10,r=10,t=10,b=10), height=300)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><div class="card-title">Resource Utilization</div>', unsafe_allow_html=True)
        util = demo_resource_util()
        fig = px.pie(util, names="resource", values="value", hole=.6)
        fig.update_layout(showlegend=True, margin=dict(l=10,r=10,t=10,b=10), height=300)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="card"><div class="card-title">Live Site Activity</div>', unsafe_allow_html=True)
        act = demo_activity()
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=act["score"], theta=act["metric"], fill="toself"))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, margin=dict(l=10,r=10,t=10,b=10), height=300)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    # Environmental & Operational Monitoring
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("🌡️", "28°C", "Temperature", sub="Partly cloudy, 65% humidity")
    with c2: kpi_card("💨", "12 km/h", "Wind Speed", sub="Northeast direction")
    with c3: kpi_card("📈", "87%", "Site Efficiency", pill_text="Above target", pill_class="status-warning", sub="Target ≥ 85%")
    with c4: kpi_card("⚡", "245 kW", "Power Usage", sub="3 generators active")

    st.write("")
    # Performance Analytics (scatter + equipment health)
    c1, c2 = st.columns((1.1, 1))
    with c1:
        st.markdown('<div class="card"><div class="card-title">Cost vs Production Efficiency</div>', unsafe_allow_html=True)
        np.random.seed(42)
        sc = pd.DataFrame({
            "Efficiency": np.random.uniform(60, 98, 48),
            "Output": np.random.uniform(5000, 12000, 48),
        })
        fig = px.scatter(sc, x="Efficiency", y="Output", trendline=TRENDLINE)
        fig.update_layout(margin=dict(l=10,r=10,t=10,b=10), height=320)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><div class="card-title">Advanced Equipment Health Monitor</div>', unsafe_allow_html=True)
        for name, health, meta, tone in [
            ("Excavator EX-001", 92, "Last service: 5 days ago", "good"),
            ("Dump Truck DT-002", 88, "Last service: 3 days ago", "good"),
            ("Crane CR-003", 65, "⚠️ Maintenance required", "warn"),
            ("Mixer MX-004", 95, "✅ Excellent condition", "good"),
        ]:
            bg = "gradient-green" if tone == "good" else "gradient-orange"
            st.markdown(
                f"""
                <div class="{bg}" style="border:1px solid #dcfce7;padding:12px;border-radius:12px;margin-bottom:10px;display:flex;align-items:center;justify-content:space-between;">
                    <div style="display:flex;gap:10px;align-items:center;">
                        <span class="pulse-dot"></span>
                        <div>
                          <div style="font-weight:700;">{name}</div>
                          <div class="small">{meta}</div>
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-weight:800;color:#16a34a;font-size:1.1rem;">{health}%</div>
                        <div class="progress" style="width:80px;margin-top:6px;"><span style="width:{health}%;background:{'#16a34a' if tone=='good' else '#f59e0b'}"></span></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    # Weekly Performance Trends
    st.markdown('<div class="card"><div class="card-title">Weekly Performance Trends</div>', unsafe_allow_html=True)
    perf = demo_production_df(14)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=perf["date"], y=perf["blocks"], mode="lines+markers", name="Production"))
    fig.add_trace(go.Scatter(x=perf["date"], y=perf["cost"], mode="lines+markers", name="Cost"))
    fig.add_trace(go.Scatter(x=perf["date"], y=perf["safety"], mode="lines+markers", name="Safety"))
    fig.update_layout(margin=dict(l=10,r=10,t=10,b=10), height=320)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Activity Feed
    st.markdown('<div class="card"><div class="card-title">Recent Activity Feed</div>', unsafe_allow_html=True)
    feed = [
        ("✅", "Production Target Achieved", "Block production reached 8,450 units today", "2 hours ago", "#ecfdf5", "#047857"),
        ("🚚", "Equipment Status Update", "Excavator EX-001 completed maintenance, back online", "4 hours ago", "#eff6ff", "#1d4ed8"),
        ("📦", "Material Delivery", "200 bags of cement delivered and stored", "6 hours ago", "#fff7ed", "#c2410c"),
        ("⚠️", "Maintenance Alert", "Crane CR-003 requires scheduled maintenance", "6 hours ago", "#fef2f2", "#b91c1c"),
    ]
    for icon, title, desc, when, bg, color in feed:
        st.markdown(
            f"""
            <div style="display:flex;gap:12px;align-items:flex-start;padding:12px;border-radius:12px;background:{bg};border:1px solid #e5e7eb;margin-bottom:10px;">
              <div style="width:32px;height:32px;border-radius:999px;background:rgba(0,0,0,.04);display:flex;align-items:center;justify-content:center;">{icon}</div>
              <div style="flex:1;">
                <div style="font-weight:700;color:{color}">{title}</div>
                <div class="muted" style="font-size:.9rem">{desc}</div>
                <div class="small" style="margin-top:4px;color:{color}">{when}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)


def page_fuel():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import plotly.graph_objects as go

    # ---- Small CSS specific to fuel section (cards, pills, grid, hover, chart containers) ----
    STYLES = """
    <style>
    body { background: #f9fafb; }
    .fuel-grid { display: grid; gap: 1rem; grid-template-columns: repeat(4, 1fr) !important; }
    .grid-3 { grid-template-columns: repeat(3, 1fr); }
    .grid-2 { grid-template-columns: repeat(2, 1fr); }
    .card, .chart-card { background: #fff; border: 1px solid #eef0f4; border-radius: 12px; padding: 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); transition: box-shadow .25s ease, transform .15s ease; margin-bottom:1rem;}
    .card:hover, .chart-card:hover { box-shadow: 0 8px 20px rgba(36,41,46,0.06); transform: translateY(-4px); }
    .card-title { font-weight:700; font-size:1.02rem; margin-bottom:0.75rem; color:#111827; }
    .kpi { font-weight:800; font-size:1.8rem; color:#111827; margin-top:6px; }
    .kpi-sub { color:#6b7280; font-weight:600; margin-top:4px; }
    .pill { display:inline-block; padding:4px 10px; border-radius:999px; font-size:12px; font-weight:600; }
    .status-good { background:#ecfdf5; color:#047857; }
    .status-warning { background:#fff7ed; color:#c2410c; }
    .status-critical { background:#fef2f2; color:#b91c1c; }
    .kpi-icon { width:40px; height:40px; border-radius:10px; background:#f3f4f6; display:flex; align-items:center; justify-content:center; font-size:18px; }
    .mini-grid { display:grid; grid-template-columns: 1fr auto; align-items:center; gap:8px; }
    .chart-container { padding:10px; border-radius:12px; background:#fff; border:1px solid #eef0f4; box-shadow:0 1px 2px rgba(0,0,0,0.04); margin-bottom:1rem; }
    @media (max-width: 900px) { .grid-2 { grid-template-columns: 1fr; } .grid-3 { grid-template-columns: 1fr; } }
    .tbl { width:100%; border-collapse: collapse; font-size:0.95rem; }
    .tbl th { background:#f8fafc; text-align:left; padding:10px; font-weight:700; border-bottom:1px solid #e6edf3; }
    .tbl td { padding:10px; border-bottom:1px solid #f3f6f9; }
    .pill-cell { padding:6px 10px; border-radius:999px; font-weight:700; display:inline-block; font-size:0.85rem; }
    </style>
    """
    st.markdown(STYLES, unsafe_allow_html=True)

    # ---- Header ----
    st.markdown("<h2 style='margin:0 0 6px;'>⛽ Fuel Farm Management Dashboard</h2>", unsafe_allow_html=True)
    st.markdown(
        "<div style='color:#6b7280;margin-bottom:1rem;'>Real-time fuel inventory and consumption monitoring (July 16 - August 25, 2025)</div>",
        unsafe_allow_html=True)

    # ---- Load datasets ----
    # Make sure files are named dipping_dataset.csv and equipment_dataset.csv and exist in the working directory.
    @st.cache_data
    def load_and_prepare(dipping_path="dipping_dataset.csv", equipment_path="equipment_dataset.csv"):
        dipping = pd.read_csv(dipping_path, parse_dates=['Date'], dayfirst=False)
        equipment = pd.read_csv(equipment_path, parse_dates=['Date'], dayfirst=False)

        # Normalize column names (strip spaces, lower)
        def clean_cols(df):
            df.columns = [c.strip() for c in df.columns]
            return df

        dipping = clean_cols(dipping)
        equipment = clean_cols(equipment)

        # Ensure expected columns exist - create safe copies / fallback names
        # Common dipping columns expected:
        # 'Date', 'Morning Dip Time', 'Morning Dip Reading (Liters)', 'Fuel Attendant Name',
        # 'Security Personnel Name', 'Evening Dip Time', 'Evening Dip Reading (Liters)',
        # 'Diesel Issued/Used (Liters)', 'Fuel Attendant Personnel', 'Security Personnel', 'Balance (Liters)'
        # If numeric columns are strings with commas, remove commas and convert
        num_cols = ['Morning Dip Reading (Liters)', 'Evening Dip Reading (Liters)', 'Diesel Issued/Used (Liters)',
                    'Balance (Liters)']
        for col in num_cols:
            if col in dipping.columns:
                dipping[col] = pd.to_numeric(dipping[col].astype(str).str.replace(',', '').str.strip(), errors='coerce')

        # Equipment dataset - expected cols:
        # 'Date','Equipment Name','Registration No.','Fleet No','Fuel Issued  (LTS)','Start hour (H)','End hour (H)',
        # 'Engine work hour (EH-SH)','Odometer Start (KM)','Odometer End (KM)','Distance Covered (KM)',
        # 'Fuel Efficiency - (Km/Ltrs)','Fuel consumed','Driver/Operator Name','Comment/ Remarks'
        # Clean numeric fuel column (note original sample has "Fuel Issued  (LTS)" two spaces)
        # find best match for fuel issued column
        possible_fuel_cols = [c for c in equipment.columns if 'fuel' in c.lower() and (
                    'issued' in c.lower() or '(lts)' in c.lower() or 'l' in c.lower())]
        fuel_col = possible_fuel_cols[0] if possible_fuel_cols else None
        if fuel_col:
            equipment['__fuel_issued__'] = pd.to_numeric(
                equipment[fuel_col].astype(str).str.replace(',', '').str.strip(), errors='coerce')
        else:
            equipment['__fuel_issued__'] = np.nan

        # Normalize comment/remarks column name
        comment_col_candidates = [c for c in equipment.columns if 'comment' in c.lower() or 'remark' in c.lower()]
        comment_col = comment_col_candidates[0] if comment_col_candidates else None
        if comment_col:
            equipment['__comment__'] = equipment[comment_col].astype(str)
        else:
            equipment['__comment__'] = 'Unknown'

        # Normalize fleet no column
        fleet_candidates = [c for c in equipment.columns if 'fleet' in c.lower()]
        fleet_col = fleet_candidates[0] if fleet_candidates else None
        if fleet_col:
            equipment['__fleet__'] = equipment[fleet_col].astype(str)
        else:
            equipment['__fleet__'] = equipment['Equipment Name'].astype(str)

        # Ensure date sorted
        dipping = dipping.sort_values('Date').reset_index(drop=True)
        equipment = equipment.sort_values('Date').reset_index(drop=True)

        return dipping, equipment

    try:
        dipping_df, equipment_df = load_and_prepare()
    except FileNotFoundError as e:
        st.error(
            "Couldn't find one of the dataset files. Make sure 'dipping_dataset.csv' and 'equipment_dataset.csv' are in the app folder.")
        st.stop()

    # ---- KPI calculations (from Dipping Dataset) ----
    if dipping_df.empty:
        st.error("Dipping dataset is empty. Please provide a valid dipping_dataset.csv")
        st.stop()

    latest_row = dipping_df.iloc[-1]
    available_l = float(latest_row.get('Balance (Liters)', np.nan))
    daily_latest = float(latest_row.get('Diesel Issued/Used (Liters)', np.nan))
    # fallback if Diesel Issued uses another name
    if np.isnan(daily_latest):
        diesel_cols = [c for c in dipping_df.columns if
                       'diesel' in c.lower() and ('issued' in c.lower() or 'used' in c.lower())]
        if diesel_cols:
            daily_latest = float(
                pd.to_numeric(str(latest_row.get(diesel_cols[0], 0)).replace(',', ''), errors='coerce'))

    # Average daily use (mean of Diesel Issued/Used)
    diesel_col_candidates = [c for c in dipping_df.columns if
                             'diesel' in c.lower() and ('issued' in c.lower() or 'used' in c.lower())]
    if diesel_col_candidates:
        avg_daily = dipping_df[diesel_col_candidates[0]].replace(',', '', regex=True).astype(float).mean()
    else:
        avg_daily = float(dipping_df.get('Diesel Issued/Used (Liters)', pd.Series(dtype=float)).mean())

    # Peak day
    peak_day = dipping_df[diesel_col_candidates[0]].max() if diesel_col_candidates else dipping_df[
        'Diesel Issued/Used (Liters)'].max()

    tank_capacity = 60000  # fixed
    # Forecast based on latest daily usage (avoid division by zero)
    if daily_latest and daily_latest > 0:
        forecast_days = max((available_l - 5000) / daily_latest, 0)
    else:
        forecast_days = np.nan

    # ---- KPI Cards (single row) ----
    st.markdown(f"""
    <div class='fuel-grid'>
      <div class="card">
        <div class="mini-grid">
          <div style="display:flex;gap:12px;align-items:center;">
            <div class="kpi-icon">⛽</div>
            <div><span class="pill status-good">✅ Good Stock</span></div>
          </div>
        </div>
        <div class="kpi">{available_l:,.0f} L</div>
        <div class="kpi-sub">Available Diesel</div>
      </div>

      <div class="card">
        <div class="mini-grid">
          <div style="display:flex;gap:12px;align-items:center;">
            <div class="kpi-icon">📉</div>
            <div><span class="pill status-warning">⚠ Latest usage</span></div>
          </div>
        </div>
        <div class="kpi">{daily_latest:,.0f} L</div>
        <div class="kpi-sub">Daily Consumption</div>
      </div>

      <div class="card">
        <div class="mini-grid">
          <div style="display:flex;gap:12px;align-items:center;">
            <div class="kpi-icon">📊</div>
            <div><span class="pill status-warning">⚠ 40-day average</span></div>
          </div>
        </div>
        <div class="kpi">{avg_daily:,.0f} L</div>
        <div class="kpi-sub">Avg Daily Use</div>
      </div>

      <div class="card">
        <div class="mini-grid">
          <div style="display:flex;gap:12px;align-items:center;">
            <div class="kpi-icon">🔥</div>
            <div><span class="pill status-critical">❌ Peak day (critical)</span></div>
          </div>
        </div>
        <div class="kpi">{peak_day:,.0f} L</div>
        <div class="kpi-sub">Max Consumption</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # ---------------------------
    # MONTHLY & DAILY CONSUMPTION with slicers
    # ---------------------------
    # Prepare week and month groupings (for slicers)
    dipping_df['ISOWeek'] = dipping_df['Date'].dt.isocalendar().week
    dipping_df['MonthName'] = dipping_df['Date'].dt.month_name()

    # Build month selector
    unique_months = list(dipping_df['MonthName'].unique())
    unique_weeks = list(dipping_df['ISOWeek'].unique())

    # ---------------------------
    # MONTHLY & DAILY CONSUMPTION with slicers (Updated)
    # ---------------------------
    col1, col2 = st.columns(2)

    # --- Monthly Diesel Consumption ---
    with col1:
        st.subheader("Monthly Diesel Consumption")
        month_selected = st.selectbox("Select Month", options=unique_months, index=0)

        # Filter for the selected month
        month_df = dipping_df[dipping_df['MonthName'] == month_selected].copy()

        if not month_df.empty and diesel_col_candidates:
            # Create 'WeekOfMonth' (1,2,3,...) relative to the month
            month_df['WeekOfMonth'] = month_df['Date'].apply(lambda d: (d.day - 1) // 7 + 1)

            # Aggregate diesel usage by week of the month
            weekly_sum = month_df.groupby('WeekOfMonth')[diesel_col_candidates[0]].sum()

            # Labels: "Week 1", "Week 2", ...
            week_labels = [f"Week {w}" for w in weekly_sum.index]

            monthly_chart = go.Figure(data=[go.Bar(
                x=week_labels,
                y=weekly_sum.values,
                marker_color='#3b82f6'
            )])
        else:
            monthly_chart = go.Figure()

        monthly_chart.update_layout(
            yaxis_title="Litres",
            xaxis_title="Week of Month",
            template='plotly_white'
        )

        st.plotly_chart(monthly_chart, use_container_width=True)

    # --- Daily Fuel Consumption Trend (smooth line + area) ---
    with col2:
        st.subheader("Daily Fuel Consumption Trend (select week)")

        if not month_df.empty and diesel_col_candidates:
            # Get unique week numbers for selected month
            week_options = sorted(month_df['WeekOfMonth'].unique())
            week_selected = st.selectbox("Select Week of Month", options=week_options, index=0)

            # Filter for selected week
            week_df = month_df[month_df['WeekOfMonth'] == week_selected].copy()

            if not week_df.empty:
                # Ensure dates are sorted
                week_df = week_df.sort_values('Date')
                daily_labels = week_df['Date'].dt.strftime('%a %d-%b')
                daily_values = week_df[diesel_col_candidates[0]].values

                # Smooth green line with light green area fill
                daily_chart = go.Figure()
                daily_chart.add_trace(go.Scatter(
                    x=daily_labels,
                    y=daily_values,
                    mode='lines+markers',
                    line=dict(color='#10b981', width=3, shape='spline'),  # smooth green curve
                    fill='tozeroy',  # fill under curve
                    fillcolor='rgba(16,185,129,0.2)'  # light green
                ))
            else:
                daily_chart = go.Figure()
        else:
            daily_chart = go.Figure()

        daily_chart.update_layout(
            yaxis_title="Litres",
            xaxis_title="Date",
            template='plotly_white',
            height=400
        )

        st.plotly_chart(daily_chart, use_container_width=True)

    st.markdown("---")

    # ---------------------------
    # Recent Fuel Deliveries (placeholder) and Recent Fuel Records
    # ---------------------------
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Recent Fuel Deliveries")
        recent_deliveries = pd.DataFrame({
            "Date": ["15-Jul-25", "22-Aug-25", "10-Sept-25"],
            "Supplier": ["Vivo Energy", "Vivo Energy", "Vivo Energy"],
            "Litres": [54000, 54000, 54000],
            "Rate": [12.8, 12.8, 12.8],
            "Cost": [691200, 691200, 691200],
            "Status": ["Delivered", "Delivered", "Pending"]
        })

        def color_status(val):
            color = '#dcfce7' if val == 'Delivered' else '#fef3c7'
            return f'background-color: {color}'

        st.dataframe(recent_deliveries.style.applymap(color_status, subset=['Status']))

    with col2:
        st.subheader("Recent Fuel Records")
        # latest 5 records with newest at top
        recent_records = dipping_df.sort_values('Date', ascending=False).head(5)[
            ['Date', 'Fuel Attendant Name', 'Security Personnel Name', diesel_col_candidates[0]]]
        recent_records = recent_records.rename(columns={diesel_col_candidates[0]: 'Diesel Issued/Used (Liters)'})
        st.dataframe(recent_records)

    st.markdown("---")

    # ---------------------------
    # CHARTS ROW 2: Top 5 Consumers (by Fleet No) & Activity donut (top5 + other)
    # ---------------------------
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 5 Fuel Consumers (by Fleet No)")
        # group by fleet no (__fleet__ created earlier)
        top_consumers = equipment_df.groupby('__fleet__')['__fuel_issued__'].sum().sort_values(ascending=False).head(5)
        consumers_chart = go.Figure(data=[go.Bar(
            x=top_consumers.index,
            y=top_consumers.values,
            marker_color=['#f59e0b', '#10b981', '#ef4444', '#3b82f6', '#8b5cf6']
        )])
        consumers_chart.update_layout(yaxis_title="Litres", template='plotly_white')
        st.plotly_chart(consumers_chart, use_container_width=True)

    with col2:
        st.subheader("Fuel Usage by Activity (Top 5 + Other)")
        activity = equipment_df.groupby('__comment__')['__fuel_issued__'].sum().sort_values(ascending=False)

        if not activity.empty:
            top5_act = activity.head(5)
            others_sum = activity.iloc[5:].sum() if activity.shape[0] > 5 else 0

            labels = list(top5_act.index)
            values = list(top5_act.values)
            if others_sum > 0:
                labels.append('Other Works')
                values.append(others_sum)

            fuel_activity_chart = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.5,
                marker=dict(
                    colors=['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#4B5563'],
                    line=dict(color='white', width=2)  # tiny white spaces between slices
                ),
                domain=dict(y=[0.1, 0.9])  # move chart slightly up
            )])

            # --- Update layout: bigger chart & legend in 2 rows ---
            fuel_activity_chart.update_layout(
                template='plotly_white',
                height=550,  # increase chart height
                width=550,  # increase chart width
                margin=dict(t=50, b=120),  # prevent legend overlap
                legend=dict(
                    orientation='h',  # horizontal
                    y=-0.25,  # move below chart
                    x=0.5,  # center horizontally
                    xanchor='center',
                    yanchor='bottom',
                    traceorder='normal',
                    font=dict(size=12),
                    itemwidth=80  # allows wrapping to 2 rows if needed
                )
            )
        else:
            fuel_activity_chart = go.Figure()

        st.plotly_chart(fuel_activity_chart, use_container_width=True)

    # ---------------------------
    # BOTTOM ROW: Tank gauge & Daily Balance Trend
    # ---------------------------
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Tank Level & Forecast")
        # gauge percentage relative to tank capacity
        tank_level_pct = (available_l / tank_capacity) * 100 if tank_capacity else 0
        combo_chart = go.Figure()
        combo_chart.add_trace(go.Indicator(
            mode="gauge+number",
            value=tank_level_pct,
            number={'suffix': "%"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "#10b981"},
                   'steps': [{'range': [0, 35], 'color': '#fee2e2'},
                             {'range': [35, 60], 'color': '#fef3c7'},
                             {'range': [60, 100], 'color': '#dcfce7'}]}
        ))
        forecast_text = f"{forecast_days:.0f} Days Until 5,000L" if not np.isnan(
            forecast_days) else "Forecast unavailable"
        combo_chart.add_annotation(x=0.5, y=-0.15,
                                   text=f"{forecast_text}<br>✅ Good Level - Latest usage: {daily_latest:.0f}L/day",
                                   showarrow=False, xref="paper", yref="paper", align="center")
        combo_chart.update_layout(height=400, margin=dict(t=50, b=50))
        st.plotly_chart(combo_chart, use_container_width=True)

    with col2:
        st.subheader("Daily Fuel Balance Trend")
        balance_chart = go.Figure(data=[go.Scatter(
            x=dipping_df['Date'],
            y=dipping_df['Balance (Liters)'],
            fill='tozeroy',
            line=dict(color='#3b82f6', width=2),
            mode='lines+markers'
        )])
        balance_chart.update_layout(yaxis_title="Litres", template='plotly_white', height=400)
        st.plotly_chart(balance_chart, use_container_width=True)

    st.markdown("---")

    # ---------------------------
    # ADDITIONAL ANALYTICS: Daily Consumption Patterns (Balance as vertical bar) & Dip Reading Accuracy
    # ---------------------------
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Daily Diesel Issued/Used (Liters) by Date")

        # Ensure diesel column exists
        if diesel_col_candidates:
            diesel_col = diesel_col_candidates[0]
            bar_chart = go.Figure(data=[go.Bar(
                x=dipping_df['Date'].dt.strftime('%d-%b'),
                y=dipping_df[diesel_col],
                marker_color='#f59e0b'
            )])
            bar_chart.update_layout(
                yaxis_title="Diesel Issued/Used (L)",
                template='plotly_white',
                xaxis_title="Date"
            )
            st.plotly_chart(bar_chart, use_container_width=True)
        else:
            st.warning("Diesel Issued/Used column not found in dipping dataset.")

    with col2:
        st.subheader("Dip Reading Accuracy")
        acc_chart = go.Figure()
        if 'Morning Dip Reading (Liters)' in dipping_df.columns:
            acc_chart.add_trace(go.Scatter(
                x=dipping_df['Date'],
                y=dipping_df['Morning Dip Reading (Liters)'],
                mode='lines+markers', name='Morning', line=dict(color='#3b82f6', width=2)))
        if 'Evening Dip Reading (Liters)' in dipping_df.columns:
            acc_chart.add_trace(go.Scatter(
                x=dipping_df['Date'],
                y=dipping_df['Evening Dip Reading (Liters)'],
                mode='lines+markers', name='Evening', line=dict(color='#10b981', width=2)))
        acc_chart.update_layout(yaxis_title="Litres", template='plotly_white', legend=dict(orientation='h'))
        st.plotly_chart(acc_chart, use_container_width=True)

    # ---------------------------
    # PERSONNEL PERFORMANCE
    # ---------------------------
    attendant_counts = dipping_df['Fuel Attendant Name'].value_counts()
    security_counts = dipping_df['Security Personnel Name'].value_counts()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Fuel Attendant Performance")

        # Sort attendants by value (largest first)
        attendant_counts_sorted = attendant_counts.sort_values(ascending=False)

        # Define custom colors: green, red, orange, blue, dark grey
        custom_colors = ['#10b981', '#ef4444', '#f59e0b', '#3b82f6', '#4B5563']

        # Adjust length of colors to match number of attendants
        colors_to_use = custom_colors[:len(attendant_counts_sorted)] + ['#4B5563'] * (
            len(attendant_counts_sorted) - 5 if len(attendant_counts_sorted) > 5 else 0)

        # Create list of text positions (default 'inside', but adjust for Hannah Acheampong)
        text_positions = ['inside'] * len(attendant_counts_sorted)
        if "Hannah Acheampong" in attendant_counts_sorted.index:
            idx = list(attendant_counts_sorted.index).index("Hannah Acheampong")
            text_positions[idx] = 'auto'  # push hers away from the circumference

        # Create pie chart
        attendant_chart = go.Figure(data=[go.Pie(
            labels=attendant_counts_sorted.index,
            values=attendant_counts_sorted.values,
            marker=dict(colors=colors_to_use, line=dict(color='white', width=2)),  # white spacing
            textinfo='percent',
            textposition=text_positions,  # apply per-slice text positioning
            insidetextorientation='auto',
            textfont=dict(size=14, color='white')
        )])

        attendant_chart.update_layout(
            template='plotly_white',
            margin=dict(t=50, b=120),
            legend=dict(
                orientation='h',  # horizontal legend
                y=-0.25,  # place below chart
                x=0.5,  # center horizontally
                xanchor='center',
                yanchor='bottom',
                font=dict(size=12),
                itemwidth=80
            )
        )

        st.plotly_chart(attendant_chart, use_container_width=True)

    with col2:
        st.subheader("Security Personnel Rotation")
        security_chart = go.Figure(data=[go.Bar(
            x=security_counts.values,
            y=security_counts.index,
            orientation='h',
            marker_color=['#f59e0b', '#10b981', '#ef4444']
        )])
        security_chart.update_layout(xaxis_title="Shifts", yaxis=dict(autorange="reversed"), template='plotly_white')
        st.plotly_chart(security_chart, use_container_width=True)

# def page_fuel():
#     st.subheader("Fuel Farm Management")
#     st.caption("Real-time fuel inventory and consumption monitoring")

#     # Parameters (editable defaults that mirror the mockup)
#     total_diesel = st.session_state.get("total_diesel", 12450)
#     price_per_l = st.session_state.get("price_per_l", 12.50)
#     daily_consumption = st.session_state.get("daily_consumption", 1250)
#     capacity = st.session_state.get("capacity", 22000)

#     days_rem = round(total_diesel / max(daily_consumption, 1), 2)
#     inv_value = total_diesel * price_per_l
#     daily_cost = daily_consumption * price_per_l
#     percent = int((total_diesel / capacity) * 100)

#     c1, c2, c3, c4 = st.columns(4)
#     with c1: kpi_card("⛽", f"{total_diesel:,}L", "Total Diesel Available", pill_text="Good Stock")
#     with c2: kpi_card("💵", f"GH₵ {inv_value:,.0f}", "Inventory Value", pill_text="Current Value")
#     with c3: kpi_card("📉", f"{daily_consumption:,}L", "Daily Consumption", pill_text="Daily Use", pill_class="status-warning")
#     with c4: kpi_card("📆", f"GH₵ {daily_cost:,.0f}", "Daily Cost", pill_text=f"{days_rem} Days", pill_class="status-warning")

#     c1, c2 = st.columns(2)
#     with c1:
#         st.markdown('<div class="card"><div class="card-title">Weekly Diesel Consumption Trends</div>', unsafe_allow_html=True)
#         fw = demo_fuel_weekly().melt(id_vars=["day"], var_name="Type", value_name="Litres")
#         fig = px.bar(fw, x="day", y="Litres", color="Type", barmode="group")
#         fig.update_layout(margin=dict(l=10,r=10,t=10,b=10), height=320)
#         st.plotly_chart(fig, use_container_width=True)
#         st.markdown('</div>', unsafe_allow_html=True)
#     with c2:
#         st.markdown('<div class="card"><div class="card-title">Main Diesel Tank Status</div>', unsafe_allow_html=True)
#         st.write(f"**{total_diesel:,}L / {capacity:,}L**")
#         st.progress(percent / 100.0, text=f"{percent}% of capacity")
#         st.caption(f"Current value: GH₵ {inv_value:,.0f} ({total_diesel:,}L × GH₵ {price_per_l:,.2f}) | Days remaining: {days_rem}")
#         # Quick adjusters
#         with st.expander("Adjust current values"):
#             st.session_state["total_diesel"] = st.number_input("Current diesel volume (L)", 0, 1000000, total_diesel, step=50)
#             st.session_state["price_per_l"] = st.number_input("Price per litre (GH₵)", 0.0, 1000.0, price_per_l, step=0.1)
#             st.session_state["daily_consumption"] = st.number_input("Daily consumption (L)", 0, 100000, daily_consumption, step=10)
#             st.session_state["capacity"] = st.number_input("Tank capacity (L)", 0, 1000000, capacity, step=100)
#         st.markdown('</div>', unsafe_allow_html=True)

#     # Records
#     c1, c2 = st.columns(2)
#     with c1:
#         st.markdown('<div class="card"><div class="card-title">Recent Fuel Deliveries</div>', unsafe_allow_html=True)
#         deliv = pd.DataFrame([
#             ["Shell Diesel Premium", 5000, 12.50, "Main Tank", "Jan 3, 2025 08:30", "Completed"],
#             ["Total Diesel", 3000, 12.50, "Reserve Tank", "Jan 1, 2025 10:15", "Completed"],
#             ["Goil Diesel", 4000, 12.50, "Main Tank", "Jan 5, 2025 09:00", "Scheduled"],
#         ], columns=["Supplier","Quantity (L)","Unit Price","Destination","Timestamp","Status"])
#         st.dataframe(deliv, use_container_width=True, hide_index=True)
#         st.markdown('</div>', unsafe_allow_html=True)
#     with c2:
#         st.markdown('<div class="card"><div class="card-title">Recent Fuel Records</div>', unsafe_allow_html=True)
#         rec = pd.DataFrame([
#             ["EX-001 — John Doe", 120, 1500, "Main Tank", "Today 14:30", "Completed"],
#             ["DT-002 — Mike Johnson", 85, 1062.5, "Main Tank", "Today 12:15", "Completed"],
#             ["CR-003 — Maintenance", 65, 812.5, "Reserve Tank", "Today 10:45", "Completed"],
#             ["GEN-001 — Generator", 45, 562.5, "Emergency Tank", "Yesterday 16:20", "Completed"],
#         ], columns=["Asset / Operator","Litres","Cost (GH₵)","Source","Timestamp","Status"])
#         st.dataframe(rec, use_container_width=True, hide_index=True)
#         st.markdown('</div>', unsafe_allow_html=True)

#     c1, c2 = st.columns(2)
#     with c1:
#         st.markdown('<div class="card"><div class="card-title">Top 5 Fuel Consumers</div>', unsafe_allow_html=True)
#         tc = demo_top_consumers()
#         fig = px.bar(tc, x="Equipment", y="Litres")
#         fig.update_layout(margin=dict(l=10,r=10,t=10,b=10), height=320)
#         st.plotly_chart(fig, use_container_width=True)
#         st.markdown('</div>', unsafe_allow_html=True)
#     with c2:
#         st.markdown('<div class="card"><div class="card-title">Fuel Usage by Activity Type</div>', unsafe_allow_html=True)
#         au = demo_activity_usage()
#         fig = px.pie(au, names="Activity", values="Litres", hole=.5)
#         fig.update_layout(margin=dict(l=10,r=10,t=10,b=10), height=320)
#         st.plotly_chart(fig, use_container_width=True)
#         st.markdown('</div>', unsafe_allow_html=True)

#     # CSV hook for your real fuel data
#     st.markdown('<div class="card"><div class="card-title">Upload Fuel CSV (optional)</div>', unsafe_allow_html=True)
#     up = st.file_uploader("Upload your fuel CSV to override the demo charts", type=["csv"])    
#     if up is not None:
#         try:
#             user_df = pd.read_csv(up)
#             st.success("CSV loaded. Showing a preview — wire the columns to charts as needed.")
#             st.dataframe(user_df.head(100), use_container_width=True, hide_index=True)
#             st.info("Map your column names to the expected fields inside this section once your schema is finalized.")
#         except Exception as e:
#             st.error(f"Could not read CSV: {e}")
#     st.markdown('</div>', unsafe_allow_html=True)


def page_stores():
    st.subheader("Stores Management")
    st.caption("Inventory of materials and equipment")

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("🧱", "450", "Cement bags", pill_text="In Stock")
    with c2: kpi_card("🏖️", "25 t", "Sand available", pill_text="Used 8 t today", pill_class="status-warning")
    with c3: kpi_card("🦺", "285", "Safety equipment", pill_text="Ready")
    with c4: kpi_card("🔔", "5", "Low-stock alerts", pill_text="Attention", pill_class="status-critical")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card"><div class="card-title">Inventory Value Trend</div>', unsafe_allow_html=True)
        df = pd.DataFrame({"Date": pd.date_range("2024-09-01", periods=12, freq="MS"), "Value (GH₵)": np.random.randint(180000, 320000, 12)})
        fig = px.line(df, x="Date", y="Value (GH₵)", markers=True)
        fig.update_layout(margin=dict(l=10,r=10,t=10,b=10), height=320)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><div class="card-title">Stock Movements (In vs Out)</div>', unsafe_allow_html=True)
        df = pd.DataFrame({"Month": pd.date_range("2024-09-01", periods=12, freq="MS"), "Stock In": np.random.randint(300, 700, 12), "Stock Out": np.random.randint(250, 650, 12)})
        fig = px.bar(df, x="Month", y=["Stock In","Stock Out"], barmode="group")
        fig.update_layout(margin=dict(l=10,r=10,t=10,b=10), height=320)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-title">Inventory Management Table</div>', unsafe_allow_html=True)
    st.dataframe(demo_inventory_df(), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)


def page_production():
    st.subheader("Block Production")
    st.caption("Tracking of block production and deliveries")

    c1, c2 = st.columns(2)
    with c1: kpi_card("🧱", "8,450", "5\" blocks produced", pill_text="70.4% of goal")
    with c2: kpi_card("🧱", "6,850", "6\" blocks produced", pill_text="57.1% of goal", pill_class="status-warning")

    st.markdown('<div class="card"><div class="card-title">Weekly Production (5\" vs 6\")</div>', unsafe_allow_html=True)
    df = pd.DataFrame({
        "Day": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
        "5\"": np.random.randint(700, 1400, 7),
        "6\"": np.random.randint(600, 1200, 7),
    })
    fig = px.bar(df, x="Day", y=["5\"","6\""], barmode="group")
    fig.update_layout(margin=dict(l=10,r=10,t=10,b=10), height=320)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-title">Production Records</div>', unsafe_allow_html=True)
    rec = pd.DataFrame({
        "Date": pd.date_range(datetime.now().date() - timedelta(days=6), periods=7),
        "Type": ["5\""]*4 + ["6\""]*3,
        "Qty": np.random.randint(850, 1400, 7),
        "Cement bags": np.random.randint(60, 160, 7),
        "Target": np.random.randint(1000, 1500, 7),
        "Quality score": np.random.randint(92, 100, 7),
    })
    st.dataframe(rec, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)


def page_hr():
    st.subheader("HR Management")
    st.caption("Workforce and attendance management")

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("👥", "160", "Total employees", pill_text="Company-wide")
    with c2: kpi_card("✅", "156", "Present today", pill_text="97.5% attendance")
    with c3: kpi_card("🗓️", "3", "Approved leave", pill_text="On leave", pill_class="status-pending")
    with c4: kpi_card("🤒", "1", "Sick leave", pill_text="Health", pill_class="status-warning")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card"><div class="card-title">Department Distribution</div>', unsafe_allow_html=True)
        df = pd.DataFrame({"Department": ["Production","Operations","Admin","Security"], "Headcount": [42,53,18,24]})
        fig = px.pie(df, names="Department", values="Headcount", hole=.45)
        fig.update_layout(margin=dict(l=10,r=10,t=10,b=10), height=320)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><div class="card-title">Employee Management</div>', unsafe_allow_html=True)
        st.dataframe(demo_hr_df(), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)


def page_qs():
    st.subheader("Quantity Surveying")
    st.caption("Project financial tracking and BoQ")

    contract = 2_400_000
    spent = 1_800_000
    remaining = contract - spent
    progress = 0.68

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("📑", f"GH₵ {contract:,.0f}", "Contract Value")
    with c2: kpi_card("💸", f"GH₵ {spent:,.0f}", "Spent to Date", pill_text="75% of budget", pill_class="status-warning")
    with c3: kpi_card("🏦", f"GH₵ {remaining:,.0f}", "Budget Remaining", pill_text="25% left")
    with c4: kpi_card("📊", f"{int(progress*100)}%", "Physical Progress", pill_text="On track")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card"><div class="card-title">Cost Breakdown</div>', unsafe_allow_html=True)
        df = pd.DataFrame({"Category":["Materials","Labour","Equipment","Overheads"], "GH₵":[1_200_000, 720_000, 360_000, 120_000]})
        fig = px.pie(df, names="Category", values="GH₵", hole=.45)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(margin=dict(l=10,r=10,t=10,b=10), height=320)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><div class="card-title">BoQ — Sample</div>', unsafe_allow_html=True)
        boq = pd.DataFrame([
            ["Earthworks — site clearance", "m²", 3500, 12.5, 43_750, "42%"],
            ["Concrete works — foundations", "m³", 1200, 250, 300_000, "68%"],
            ["Blockwork 5\" walls", "m²", 6800, 45, 306_000, "55%"],
            ["Roof structure", "m²", 2100, 95, 199_500, "23%"],
        ], columns=["Description","Unit","Qty","Rate (GH₵)","Amount (GH₵)","Progress"])
        st.dataframe(boq, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------
# Router
# ---------------------------------------------------------------
if section == "Main Dashboard":
    page_dashboard()
elif section == "Fleet Management":
    page_fleet()
elif section == "Fuel Farm":
    page_fuel()
elif section == "Stores Management":
    page_stores()
elif section == "Block Production":
    page_production()
elif section == "HR Management":
    page_hr()
elif section == "Quantity Surveying":
    page_qs()

