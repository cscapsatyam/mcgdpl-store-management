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

    # ఫిల్టర్స్‌ని పైన ఉంచడానికి
    col1, col2 = st.columns(2)
    supplier_col = "Supplier / Sendor Name"
    if supplier_col in df.columns:
      suppliers = ["అన్నీ (All)"] + list(df[supplier_col].dropna().unique())
      selected_supplier = col1.selectbox("Supplier / Sendor Name ఫిల్టర్:", suppliers)
      if selected_supplier != "అన్నీ (All)":
        df = df[df[supplier_col] == selected_supplier]

    receipt_col = "Type Reciept"
    if receipt_col in df.columns:
      receipts = ["అన్నీ (All)"] + list(df[receipt_col].dropna().unique())
      selected_receipt = col2.selectbox("Type Reciept ఫిల్టర్:", receipts)
      if selected_receipt != "అన్నీ (All)":
        df = df[df[receipt_col] == selected_receipt]

    st.markdown("---")

    # రోస్ సంఖ్యను బట్టి హైట్ ఆటోమేటిక్‌గా మారేలా సెట్ చేయడం
    calc_height = min(max(len(df) * 38 + 40, 150), 500)

    # కాలమ్స్ సైజులను కంట్రోల్ చేయడానికి Column Configuration
    column_config = {
        "S.No": st.column_config.NumberColumn(width="small"),
        "Store Entry No": st.column_config.NumberColumn(width="small"),
        "UOM": st.column_config.TextColumn(width="small"),
        "GRN No": st.column_config.TextColumn(width="small"),
        "PO No": st.column_config.TextColumn(width="small"),
        "Invoice No": st.column_config.TextColumn(width="medium"),
        "Supplier / Sendor Name": st.column_config.TextColumn(width="large"),
        "Description Of material": st.column_config.TextColumn(width="large"),
    }

    st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        disabled=True,
        height=calc_height,
        column_config=column_config,
    )
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
