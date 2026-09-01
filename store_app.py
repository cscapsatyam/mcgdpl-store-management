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

standard_columns = [
    "S.No",
    "Store Entry No",
    "Actualy Recived Date",
    "GRN No",
    "GRN Date",
    "Supplier / Sendor Name",
    "Description Of material",
    "UOM",
    "PO No",
    "Invoice No",
    "date",
    "Receiving Qty",
    "unit rate",
    "CGST",
    "SGST",
    "Fright",
    "Inovice value",
    "Vechile Number",
    "Type Reciept",
    "Remarks",
]

# ఆటోమేటిక్‌గా గిథబ్ నుండి Book1.xlsx ఫైల్‌ని లోడ్ చేయడానికి ప్రయత్నిస్తుంది
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
    st.success("✅ డేటా ఆటోమేటిక్‌గా లోడ్ చేయబడింది!")
  else:
    st.markdown(
        "### స్వాగతం! దయచేసి ఎక్సెల్ ఫైల్‌ను అప్‌లోడ్ చేయండి లేదా సైడ్‌బార్"
        " ద్వారా ఇతర పేజీలకు వెళ్లండి."
    )
    uploaded_file = st.file_uploader(
        "📁 మీ ఎక్సెల్ ఫైల్‌ని ఇక్కడ అప్‌లోడ్ చేయండి", type=["xlsx", "xls"]
    )
    if uploaded_file is not None:
      try:
        df = pd.read_excel(uploaded_file, sheet_name=0)
        st.session_state.current_df = df
        st.success("ఫైల్ విజయవంతంగా అప్‌లోడ్ చేయబడింది!")
        st.rerun()
      except Exception as e:
        st.error(f"ఎర్రర్: {e}")
