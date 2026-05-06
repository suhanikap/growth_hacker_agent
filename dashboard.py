import streamlit as st
import pandas as pd
import sqlite3
import os
import requests

# 1. DATABASE PATH CONFIGURATION
# This ensures the cloud can find your 8KB database file
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'product_metrics.db')

def get_data():
    conn = sqlite3.connect(db_path)
    try:
        # Pulling the conversion data you generated
        df = pd.read_sql_query("SELECT * FROM funnel_stats", conn)
    except Exception as e:
        st.error(f"Database Error: {e}")
        return pd.DataFrame()
    finally:
        conn.close()
    return df

# 2. UI HEADER & USER PROFILE
st.set_page_config(page_title="Growth Hacker AI Agent", layout="wide")
st.title("🚀 Growth Hacker AI Agent: Conversion Monitor")

with st.sidebar:
    st.header("Agent Settings")
    model_choice = st.selectbox("Select AI Model", ["tinyllama"])
    st.info("Note: TinyLlama is recommended for local inference.")
    st.write("---")
    st.write(f"**Current User:** Suhani Kapoor") #
    st.write(f"**Role:** Agentic AI Product Manager") #

# 3. DATA PROCESSING
df = get_data()

if not df.empty:
    # Calculate Metrics
    df['conv_rate'] = (df['signups'] / df['views']) * 100
    avg_rate = df['conv_rate'].mean()
    current_rate = df['conv_rate'].iloc[-1]
    
    # 4. VISUALIZATION
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Historical Avg Conv Rate", f"{avg_rate:.2f}%")
    with col2:
        status_color = "normal" if current_rate > (avg_rate * 0.5) else "inverse"
        st.metric("Current Conv Rate", f"{current_rate:.2f}%", delta=f"{current_rate - avg_rate:.2f}%", delta_color=status_color)

    st.line_chart(df['conv_rate'])

    # 5. AGENTIC LOGIC (The "Crisis" Trigger)
    if current_rate < (avg_rate * 0.5):
        st.error("🚨 CRISIS DETECTED: Conversion rate has dropped by over 50%!")
        
        if st.button("Ask Agent for Strategy Report"):
            # This looks for your local Ollama instance
            prompt = f"Product conversion dropped from {avg_rate:.2f}% to {current_rate:.2f}%. Draft a 3-step strategy for the engineering team to fix this."
            
            try:
                response = requests.post('http://localhost:11434/api/generate', 
                                         json={'model': 'tinyllama', 'prompt': prompt, 'stream': False})
                st.write("### AI Agent Strategy Report:")
                st.write(response.json().get('response'))
            except:
                st.warning("Agent is offline. Ensure Ollama is running locally with 'tinyllama'.")
else:
    st.warning("No data found. Please run setup_db.py first.")
