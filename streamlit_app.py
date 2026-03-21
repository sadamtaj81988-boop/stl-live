#refresh 
import streamlit as st
import pandas as pd
import sqlite3
import time

# ---------------------------
# DATABASE
# ---------------------------
def init_db():
    conn = sqlite3.connect("stl_live.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            ts TEXT,
            channel TEXT,
            revenue REAL
        )
    """)
    conn.commit()
    conn.close()

def save_data(channel, revenue):
    conn = sqlite3.connect("stl_live.db")
    c = conn.cursor()
    c.execute("INSERT INTO history VALUES (?, ?, ?)",
              (time.strftime("%Y-%m-%d %H:%M:%S"), channel, revenue))
    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect("stl_live.db")
    df = pd.read_sql("SELECT * FROM history", conn)
    conn.close()
    return df

init_db()

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="STL LIVE ENGINE", layout="wide")

# ---------------------------
# NAVIGATION
# ---------------------------
page = st.sidebar.selectbox(
    "STL Navigation",
    ["Dashboard", "Blueprint", "Tracking", "Client Mode", "Architect Mode", "Global Shock", "Control Layer"]
)

st.title("⚡ STL LIVE – Structured Intelligence Engine")
st.caption("Real-time business diagnostics powered by STL Architecture")

# ---------------------------
# SIDEBAR INPUT
# ---------------------------
st.sidebar.header("Live Controls")

channel = st.sidebar.selectbox("Select Channel", ["Online", "Store", "Partner"])
revenue = st.sidebar.number_input("Enter Revenue", min_value=0.0, step=10.0)

if st.sidebar.button("Submit Data"):
    save_data(channel, revenue)

# ---------------------------
# LOAD DATA
# ---------------------------
df = load_data()

# ---------------------------
# DASHBOARD
# ---------------------------
if page == "Dashboard":
    st.header("📊 STL Dashboard")

    if not df.empty:
        pivot = df.groupby("channel")["revenue"].sum()
        st.bar_chart(pivot)

        st.subheader("Recent Data")
        st.dataframe(df.tail(10))
    else:
        st.warning("No data yet")

# ---------------------------
# BLUEPRINT
# ---------------------------
elif page == "Blueprint":
    st.header("🧠 STL Blueprint")

    st.markdown("""
    **STL Core Architecture**

    1. Consultation → Human Architect  
    2. Applications → Data Input  
    3. Pipelines → Processing  
    4. Storage → Database  
    5. Intelligence → Decision Engine  

    This system transforms raw input into structured intelligence.
    """)

# ---------------------------
# TRACKING
# ---------------------------
elif page == "Tracking":
    st.header("📈 STL Tracking")

    if not df.empty:
        df["ts"] = pd.to_datetime(df["ts"])
        pivot = df.pivot(index="ts", columns="channel", values="revenue")

        st.line_chart(pivot)

        st.caption("Live tracking of revenue across channels")
    else:
        st.warning("No tracking data available")

# ---------------------------
# CLIENT MODE
# ---------------------------
elif page == "Client Mode":
    st.header("💼 Client Mode")

    if not df.empty:
        total = df["revenue"].sum()
        best_channel = df.groupby("channel")["revenue"].sum().idxmax()

        st.metric("Total Revenue", f"${total:.2f}")
        st.success(f"Best Channel: {best_channel}")
    else:
        st.warning("No data yet")

# ---------------------------
# ARCHITECT MODE
# ---------------------------
elif page == "Architect Mode":
    st.header("⚙️ Architect Mode")

    st.markdown("""
    **System Design Insight**

    - Inputs are collected from channels  
    - Data flows through pipelines  
    - Stored in SQLite  
    - Analyzed in real-time  

    STL ensures structured flow from observation → decision.
    """)

# ---------------------------
# GLOBAL SHOCK
# ---------------------------
elif page == "Global Shock":
    st.header("🌍 Global Shock Simulation")

    shock = st.slider("Simulate Revenue Drop (%)", 0, 100, 20)

    if not df.empty:
        df["adjusted"] = df["revenue"] * (1 - shock/100)
        st.line_chart(df.groupby("channel")["adjusted"].sum())
    else:
        st.warning("No data to simulate")

# ---------------------------
# CONTROL LAYER
# ---------------------------
elif page == "Control Layer":
    st.header("🛡️ Control Layer")

    if not df.empty:
        weak = df.groupby("channel")["revenue"].sum().idxmin()

        st.error(f"Weak Channel Detected: {weak}")
        st.markdown("""
        **Actions:**
        - Reallocate resources
        - Optimize pipelines
        - Improve channel performance
        """)
    else:
        st.warning("System waiting for data")
