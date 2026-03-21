import streamlit as st
import pandas as pd
import sqlite3
import time

# -----------------------
# DATABASE
# -----------------------
def init_db():
    conn = sqlite3.connect("stl_live.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            ts TEXT,
            channel TEXT,
            revenue REAL,
            visitors INTEGER,
            purchases INTEGER
        )
    """)
    conn.commit()
    conn.close()

def save_snapshot(df):
    conn = sqlite3.connect("stl_live.db")
    df["ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
    df.to_sql("history", conn, if_exists="append", index=False)
    conn.close()

def load_history():
    conn = sqlite3.connect("stl_live.db")
    df = pd.read_sql("SELECT * FROM history", conn)
    conn.close()
    return df

# -----------------------
# STL ENGINE
# -----------------------
def run_stl(df):
    df["conversion"] = (df["purchases"] / df["visitors"]) * 100

    total_revenue = df["revenue"].sum()
    overall_conversion = (df["purchases"].sum() / df["visitors"].sum()) * 100

    best_channel = df.loc[df["conversion"].idxmax(), "channel"]
    worst_channel = df.loc[df["conversion"].idxmin(), "channel"]

    stl_live = round((overall_conversion / 10), 2)

    alerts = []

    if df["conversion"].min() < 5:
        alerts.append(("error", "🚨 Low conversion detected"))

    if df["revenue"].max() > total_revenue * 0.7:
        alerts.append(("warning", "🔥 Revenue imbalance detected"))

    return {
        "df": df,
        "total_revenue": total_revenue,
        "overall_conversion": overall_conversion,
        "best_channel": best_channel,
        "worst_channel": worst_channel,
        "stl_live": stl_live,
        "alerts": alerts
    }

# -----------------------
# INIT
# -----------------------
st.set_page_config(layout="wide")
init_db()

# -----------------------
# NAVIGATION
# -----------------------
page = st.sidebar.selectbox(
    "STL Navigation",
    ["Dashboard", "Blueprint", "Tracking", "Control Layer"]
)

# -----------------------
# DASHBOARD
# -----------------------
if page == "Dashboard":

    st.title("STL LIVE — Structured Intelligence Engine")
    st.caption("Real-time business diagnostics and decision system")

    with st.sidebar:
        st.header("Live Controls")

        input_mode = st.radio("Input Mode", ["Manual", "Demo Data"])
        auto_refresh = st.checkbox("Auto Refresh")
        refresh_seconds = st.slider("Refresh every (sec)", 5, 60, 10)

    if auto_refresh:
        st.markdown(
            f"<meta http-equiv='refresh' content='{refresh_seconds}'>",
            unsafe_allow_html=True
        )

    # -----------------------
    # INPUT DATA
    # -----------------------
    if input_mode == "Demo Data":
        df = pd.DataFrame({
            "channel": ["Store", "Online", "Marketplace"],
            "visitors": [2000, 10000, 3000],
            "purchases": [400, 200, 90],
            "revenue": [12000, 8000, 4500]
        })
    else:
        df = pd.DataFrame({
            "channel": ["Store", "Online", "Marketplace"],
            "visitors": [
                st.number_input("Store Visitors", 0, 100000, 2000),
                st.number_input("Online Visitors", 0, 100000, 10000),
                st.number_input("Marketplace Visitors", 0, 100000, 3000)
            ],
            "purchases": [
                st.number_input("Store Purchases", 0, 10000, 400),
                st.number_input("Online Purchases", 0, 10000, 200),
                st.number_input("Marketplace Purchases", 0, 10000, 90)
            ],
            "revenue": [
                st.number_input("Store Revenue", 0, 100000, 12000),
                st.number_input("Online Revenue", 0, 100000, 8000),
                st.number_input("Marketplace Revenue", 0, 100000, 4500)
            ]
        })

    # -----------------------
    # RUN STL
    # -----------------------
    result = run_stl(df)

    st.subheader("System Health")
    st.metric("STL LIVE", result["stl_live"])
    st.metric("Total Revenue", f"${result['total_revenue']}")
    st.metric("Conversion %", f"{result['overall_conversion']:.2f}%")
    st.write(f"Weakest Channel: **{result['worst_channel']}**")

    st.subheader("Channel Performance")
    st.dataframe(result["df"])

    st.bar_chart(result["df"].set_index("channel")["revenue"])

    st.subheader("Alerts")
    for level, msg in result["alerts"]:
        if level == "error":
            st.error(msg)
        elif level == "warning":
            st.warning(msg)

    if st.button("Save Snapshot"):
        save_snapshot(result["df"])
        st.success("Snapshot saved!")

# -----------------------
# BLUEPRINT
# -----------------------
elif page == "Blueprint":
    st.title("STL Blueprint")

    st.markdown("""
    **Hallow** → Pattern detection  
    **Honor** → Pipeline diagnosis  
    **Higher** → Structured comparison  
    **Hunter** → Decision output  

    This system transforms raw business data into strategic intelligence.
    """)

# -----------------------
# TRACKING
# -----------------------
elif page == "Tracking":
    st.title("Historical Tracking")

    history = load_history()

    if history.empty:
        st.info("No data yet")
    else:
        st.dataframe(history)
        st.line_chart(history.groupby("ts")["revenue"].sum())

# -----------------------
# CONTROL LAYER
# -----------------------
elif page == "Control Layer":
    st.title("Control Layer")

    st.markdown("""
    This layer represents STL governance:

    - Alert monitoring  
    - Resource redirection (Hydro)  
    - Decision enforcement  

    Your system is now fully structured.
    """)
