import streamlit as st
import pandas as pd
import sqlite3
import ollama

# Page Configuration
st.set_page_config(page_title="Growth Hacker Agent", page_icon="🚀", layout="wide")

# Custom Styling for a Professional PM Look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("Agent Settings")
    selected_model = st.selectbox("Select AI Model", ["tinyllama", "phi3:mini"], index=0)
    st.info("Note: TinyLlama is recommended for systems with < 4GB Available RAM.")
    
    st.divider()
    st.write("Current User: Suhani Kapoor")
    st.write("Role: Agentic AI Product Manager")

# --- DATA LAYER ---
def get_data():
    # To switch to Live Google Sheets:
    # conn = st.connection("gsheets", type=GSheetsConnection)
    # return conn.read(spreadsheet="YOUR_URL")
    
    conn = sqlite3.connect('product_metrics.db')
    df = pd.read_sql_query("SELECT * FROM funnel_stats", conn)
    conn.close()
    return df

df = get_data()
df['conv_rate'] = (df['signups'] / df['views']) * 100

# --- HEADER SECTION ---
st.title("🚀 Growth Hacker AI Agent")
st.markdown("### Real-time Conversion Monitoring & Autonomous Strategy")

# --- METRIC CARDS ---
latest_rate = df['conv_rate'].iloc[-1]
avg_rate = df['conv_rate'].iloc[:-1].mean()
delta = latest_rate - avg_rate

m1, m2, m3 = st.columns(3)
m1.metric("Current Conversion", f"{latest_rate:.2f}%", f"{delta:.2f}%")
m2.metric("Historical Average", f"{avg_rate:.2f}%")
m3.metric("Status", "CRISIS" if latest_rate < (avg_rate * 0.5) else "HEALTHY")

# --- VISUALIZATION ---
st.subheader("Performance Trend")
st.line_chart(df, x=None, y="conv_rate", use_container_width=True)

# --- AGENTIC LOGIC ---
if latest_rate < (avg_rate * 0.5):
    st.error("🚨 **Alert:** Conversion rate has dropped below 50% of the typical average.")
    
    if st.button("Generate Autonomous Strategy Report"):
        with st.spinner(f"Agent is analyzing using {selected_model}..."):
            try:
                prompt = (
                    f"CRITICAL ALERT: Current conversion is {latest_rate:.2f}% (Avg: {avg_rate:.2f}%). "
                    "As a Senior Growth PM, provide a root-cause analysis and a professional Slack message "
                    "to the Engineering team. Sign off as 'Growth AI Agent'."
                )
                
                response = ollama.chat(model=selected_model, messages=[{'role': 'user', 'content': prompt}])
                
                st.markdown("---")
                st.subheader("🤖 Agent Strategy Report")
                st.write(response['message']['content'])
                st.success("Report Generated Successfully.")
                
            except Exception as e:
                st.error(f"Hardware Error: {e}. Ensure Ollama is running and model is pulled.")
else:
     st.success("✅ System is performing within normal parameters.")
