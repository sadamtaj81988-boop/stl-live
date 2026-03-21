#fix
import sqlite3
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st
st.set_page_config(page_title="STL LIVE — Structured Intelligence Engine", layout="wide")
# 🧭 SIDEBAR NAVIGATION
st.sidebar.title("STL LIVE")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Blueprint",
        "Tracking",
        "Client Mode",
        "Architect Mode",
        "Global Shock",
        "Control Layer"
    ]
)
APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "stl_live.db"



def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            channel TEXT NOT NULL,
            visitors REAL NOT NULL,
            purchases REAL NOT NULL,
            revenue REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def insert_snapshot(df: pd.DataFrame):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    ts = datetime.utcnow().isoformat(timespec="seconds")
    rows = [
        (ts, str(row["channel"]), float(row["visitors"]), float(row["purchases"]), float(row["revenue"]))
        for _, row in df.iterrows()
    ]
    cur.executemany(
        "INSERT INTO snapshots (ts, channel, visitors, purchases, revenue) VALUES (?, ?, ?, ?, ?)",
        rows
    )
    conn.commit()
    conn.close()
    return ts

def load_history():
    conn = sqlite3.connect(DB_PATH)
    try:
        hist = pd.read_sql_query(
            "SELECT ts, channel, visitors, purchases, revenue FROM snapshots ORDER BY ts ASC, channel ASC",
            conn
        )
    finally:
        conn.close()
    return hist

def get_input_data(input_mode: str):
    required_cols = ["channel", "visitors", "purchases", "revenue"]

    if input_mode == "Manual entry":
        default_df = pd.DataFrame([
            {"channel": "Store", "visitors": 2000, "purchases": 400, "revenue": 12000},
            {"channel": "Online", "visitors": 10000, "purchases": 200, "revenue": 8000},
            {"channel": "Marketplace", "visitors": 3000, "purchases": 90, "revenue": 4500},
        ])
        return st.data_editor(default_df, num_rows="dynamic", use_container_width=True)

    if input_mode == "Upload CSV":
        uploaded = st.file_uploader(
            "Upload CSV with columns: channel, visitors, purchases, revenue",
            type=["csv"]
        )
        if uploaded is None:
            st.info("Upload a CSV to continue.")
            return None
        df = pd.read_csv(uploaded)
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            st.error(f"Missing required columns: {', '.join(missing)}")
            return None
        return df

    if input_mode == "Google Sheets":
        st.caption("Paste a public Google Sheets CSV export URL.")
        sheet_url = st.text_input("Google Sheets CSV URL")
        if not sheet_url:
            st.info("Paste a Google Sheets CSV URL to continue.")
            return None
        try:
            df = pd.read_csv(sheet_url)
        except Exception as e:
            st.error(f"Could not read Google Sheets URL: {e}")
            return None
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            st.error(f"Missing required columns: {', '.join(missing)}")
            return None
        return df

def run_analysis(df: pd.DataFrame):
    df = df.copy()

    for col in ["visitors", "purchases", "revenue"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["conversion_rate"] = (df["purchases"] / df["visitors"].replace(0, pd.NA) * 100).fillna(0)
    df["avg_order_value"] = (df["revenue"] / df["purchases"].replace(0, pd.NA)).fillna(0)

    total_revenue = float(df["revenue"].sum())
    total_visitors = float(df["visitors"].sum())
    total_purchases = float(df["purchases"].sum())
    overall_conversion = (total_purchases / total_visitors * 100) if total_visitors else 0.0

    if total_revenue:
        df["revenue_share_pct"] = (df["revenue"] / total_revenue * 100).round(1)
    else:
        df["revenue_share_pct"] = 0.0

    best_revenue_row = df.loc[df["revenue"].idxmax()]
    best_conversion_row = df.loc[df["conversion_rate"].idxmax()]
    weakest_conversion_row = df.loc[df["conversion_rate"].idxmin()]
    highest_traffic_row = df.loc[df["visitors"].idxmax()]

    stl_live = round(
        (overall_conversion * 0.4) +
        ((total_revenue / 10000) * 0.3) +
        (1.0 if str(weakest_conversion_row["channel"]) != str(best_revenue_row["channel"]) else 0.3),
        2
    )

    outputs = {
        "understood": (
            f"Revenue leader: {best_revenue_row['channel']} generated ${best_revenue_row['revenue']:,.0f}, "
            f"representing {best_revenue_row['revenue_share_pct']:.1f}% of total revenue. "
            f"Overall conversion is {overall_conversion:.2f}%."
        ),
        "hallow": (
            f"Pattern detected: {highest_traffic_row['channel']} has the highest traffic at "
            f"{highest_traffic_row['visitors']:,.0f} visitors. Best conversion is "
            f"{best_conversion_row['channel']} at {best_conversion_row['conversion_rate']:.2f}%, while "
            f"the weakest conversion is {weakest_conversion_row['channel']} at "
            f"{weakest_conversion_row['conversion_rate']:.2f}%."
        ),
        "honor": (
            f"Pipeline diagnosis: {weakest_conversion_row['channel']} shows the largest gap between "
            f"traffic and completed purchases. Friction is likely occurring in trust, offer clarity, "
            f"or checkout flow."
        ),
        "higher": (
            "Structured comparison across traffic, conversion, revenue share, and average order value "
            "shows whether the problem is acquisition, monetization, or channel imbalance."
        ),
        "hunter": (
            f"Decision output: preserve the winning patterns in {best_conversion_row['channel']} and "
            f"apply those learnings to {weakest_conversion_row['channel']}. Audit landing pages, pricing, "
            f"checkout steps, and trust signals."
        ),
        "hydro": (
            f"Hydro flow recommendation: direct 60% of optimization effort to {weakest_conversion_row['channel']} "
            f"to fix conversion flow, and 40% toward scaling {best_revenue_row['channel']}."
        ),
    }

    alerts = []
    min_conv = float(df["conversion_rate"].min())
    if min_conv < 3:
        alerts.append(("error", f"🚨 Conversion alert: {weakest_conversion_row['channel']} is critically low at {min_conv:.2f}%."))

    if total_revenue < 10000:
        alerts.append(("warning", "⚠️ Revenue warning: total revenue is below the current threshold."))

    revenue_imbalance = float(df["revenue"].max() - df["revenue"].min()) if len(df) > 1 else 0
    if revenue_imbalance > 5000:
        alerts.append(("warning", "🔥 Imbalance alert: one channel is dominating revenue heavily."))

    for _, row in df.iterrows():
        if float(row["visitors"]) > 5000 and float(row["conversion_rate"]) < 5:
            alerts.append(("error", f"🚨 Pipeline issue: {row['channel']} has high traffic but low conversion."))

    alerts.append(("info", f"💧 Hydro signal: redirect resources toward {weakest_conversion_row['channel']}."))

    metrics = {
        "total_revenue": total_revenue,
        "total_visitors": total_visitors,
        "total_purchases": total_purchases,
        "overall_conversion": overall_conversion,
        "best_revenue_channel": str(best_revenue_row["channel"]),
        "weakest_conversion_channel": str(weakest_conversion_row["channel"]),
        "stl_live": stl_live,
    }

    return df, outputs, metrics, alerts

init_db()

st.title("STL LIVE — Structured Intelligence Engine")
st.caption("Real-time business diagnostics and decision system")

with st.sidebar:
    st.header("Live Controls")
    input_mode = st.radio("Input source", ["Manual entry", "Upload CSV", "Google Sheets"])
    auto_refresh = st.checkbox("Auto refresh dashboard", value=False)
    refresh_seconds = st.slider("Refresh every N seconds", 5, 60, 15, 5)
    if auto_refresh:
        st.markdown(
            f"<meta http-equiv='refresh' content='{refresh_seconds}'>",
            unsafe_allow_html=True
        )
        st.caption("Auto refresh enabled for this session.")
    save_snapshot = st.checkbox("Save snapshot after run", value=False)

st.markdown("## Input Layer")
df = get_input_data(input_mode)

run_analysis_button = st.button("Run Live Analysis", type="primary", disabled=(df is None))

if run_analysis_button and df is not None:
    result_df, outputs, metrics, alerts = run_analysis(pd.DataFrame(df))

    if save_snapshot:
        ts = insert_snapshot(result_df[["channel", "visitors", "purchases", "revenue"]])
        st.success(f"Snapshot saved at {ts} UTC.")
st.markdown("## Alerts")
# (nothing here)

st.markdown("---")
st.markdown("## System Health")

    
        

    


    
        

    

    st.markdown("---")
    st.markdown("## System Health")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("STL LIVE", f"{metrics['stl_live']}")
    m2.metric("Total Revenue", f"${metrics['total_revenue']:,.0f}")
    m3.metric("Overall Conversion", f"{metrics['overall_conversion']:.2f}%")
    m4.metric("Weakest Conversion Channel", metrics["weakest_conversion_channel"])

    st.markdown("---")
    st.markdown("## Channel Performance Overview")
    st.dataframe(result_df, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Revenue by Channel")
        st.bar_chart(result_df.set_index("channel")[["revenue"]])
    with c2:
        st.markdown("### Conversion Rate by Channel")
        st.bar_chart(result_df.set_index("channel")[["conversion_rate"]])

    st.markdown("---")
    st.markdown("## STL Intelligence Results")
    st.subheader("Understood")
    st.write(outputs["understood"])
    st.subheader("Hallow")
    st.write(outputs["hallow"])
    st.subheader("Honor")
    st.write(outputs["honor"])
    st.subheader("Higher")
    st.write(outputs["higher"])
    st.subheader("Hunter")
    st.write(outputs["hunter"])

    st.markdown("---")
    st.markdown("## Resource Allocation (Hydro)")
    st.info(outputs["hydro"])

    st.markdown("---")
    st.markdown("## System Alerts")
    for alert_type, message in alerts:
        if alert_type == "error":
            st.error(message)
        elif alert_type == "warning":
            st.warning(message)
        else:
            st.info(message)

    st.markdown("---")
    st.markdown("## Consultant Summary")
    st.success(
        "STL LIVE has analyzed your system. Key issues have been identified and resource "
        "allocation has been recommended. Use these insights to optimize performance and scale effectively."
    )

st.markdown("---")
st.markdown("## Historical Trend Layer")
history = load_history()
if history.empty:
    st.info("No saved snapshots yet. Run analysis and enable 'Save snapshot after run' to start trend tracking.")
else:
    grouped = history.groupby(["ts", "channel"], as_index=False)[["visitors", "purchases", "revenue"]].sum()
    st.dataframe(grouped, use_container_width=True)
    trend_metric = st.selectbox("Trend metric", ["revenue", "visitors", "purchases"])
    pivot = grouped.pivot(index="ts", columns="channel", values=trend_metric).fillna(0)
    st.line_chart(pivot)
    st.caption(f"Latest snapshot: {grouped['ts'].max()} UTC")
    # 👇 VERY BOTTOM OF FILE

if page == "Dashboard":
    st.title("📊 STL LIVE Dashboard")

elif page == "Blueprint":
    st.title("🧠 STL Blueprint")

elif page == "Tracking":
    st.title("📊 STL Tracking")

elif page == "Client Mode":
    st.title("💼 Client Mode")

elif page == "Architect Mode":
    st.title("⚙️ Architect Mode")

elif page == "Global Shock":
    st.title("🌍 Global Shock")

elif page == "Control Layer":
    st.title("🛡 Control Layer")
st.markdown("---")