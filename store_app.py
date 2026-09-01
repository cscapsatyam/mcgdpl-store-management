import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Store Management System", layout="wide")

# Initialize Session State variables
if "current_df" not in st.session_state:
  st.session_state.current_df = pd.DataFrame()
if "custom_suppliers" not in st.session_state:
  st.session_state.custom_suppliers = []
if "custom_materials" not in st.session_state:
  st.session_state.custom_materials = []

# ఆటోమేటిక్‌గా గిథబ్ నుండి Book1.xlsx ఫైల్‌ని లోడ్ చేయడం
if st.session_state.current_df.empty:
  try:
    df_auto = pd.read_excel("Book1.xlsx", sheet_name=0)
    st.session_state.current_df = df_auto
  except Exception as e:
    pass

# Sidebar Navigation
page = st.sidebar.radio(
    "పేజీని ఎంచుకోండి:",
    [
        "1. Home / Dashboard",
        "2. Material Register View",
        "3. New Record Creation",
        "4. All Suppliers List",
        "5. Material List",
    ],
)

# ================= PAGE 1: HOME =================
if page == "1. Home / Dashboard":
  st.title("📦 Store Management System")

  if not st.session_state.current_df.empty:
    df = st.session_state.current_df.copy()
    # మెసేజ్‌లు మరియు హెడ్డింగ్‌లు పూర్తిగా తొలగించబడి, నేరుగా టేబుల్ మాత్రమే కనిపిస్తుంది
    st.data_editor(df, hide_index=True, use_container_width=True, disabled=True)
  else:
    uploaded_file = st.file_uploader(
        "📁 మీ ఎక్సెల్ ఫైల్‌ని ఇక్కడ అప్‌లోడ్ చేయండి", type=["xlsx", "xls"]
    )
    if uploaded_file is not None:
      try:
        df = pd.read_excel(uploaded_file, sheet_name=0)
        st.session_state.current_df = df
        st.rerun()
      except Exception as e:
        st.error(f"ఎర్రర్: {e}")
