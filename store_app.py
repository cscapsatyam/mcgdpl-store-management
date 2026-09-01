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
        "6. Invoice Wise Total Value",
    ],
)

# ================= PAGE 1: HOME =================
if page == "1. Home / Dashboard":
  st.title("📦 Store Management System")

  if not st.session_state.current_df.empty:
    df = st.session_state.current_df.copy()

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
    calc_height = min(max(len(df) * 38 + 40, 150), 500)

    st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        disabled=True,
        height=calc_height,
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

# ================= PAGE 6: INVOICE WISE TOTAL VALUE =================
elif page == "6. Invoice Wise Total Value":
  st.title("📊 Supplier & Invoice Wise Total Value Summary")

  if not st.session_state.current_df.empty:
    df = st.session_state.current_df.copy()

    sup_col = "Supplier / Sendor Name"
    inv_col = "Invoice No"

    # వాల్యూ కాలమ్ వెతకడం
    possible_val_cols = [
        "Inovice value",
        "Invoice Value",
        "Total Amount",
        "Total Value",
        "Amount",
        "Value",
        "Total",
    ]
    val_col = None
    for col in possible_val_cols:
      matched_cols = [c for c in df.columns if c.strip().lower() == col.lower()]
      if matched_cols:
        val_col = matched_cols[0]
        break

    if sup_col in df.columns and inv_col in df.columns:
      suppliers_list = ["అన్నీ (All)"] + list(df[sup_col].dropna().unique())
      selected_sup_filter = st.selectbox(
          "🔍 సప్లయర్ వారీగా ఫిల్టర్ చేయండి:", suppliers_list
      )

      if selected_sup_filter != "అన్నీ (All)":
        df = df[df[sup_col] == selected_sup_filter]

      if val_col and val_col in df.columns:
        df[val_col] = pd.to_numeric(
            df[val_col].astype(str).str.replace(r"[^\d.]", "", regex=True),
            errors="coerce",
        ).fillna(0)

        # అదనపు కాలమ్స్ (Store Entry No, Invoice Date, GRN No, GRN Date) ఎక్సెల్ లో ఉన్నాయో లేదో చెక్ చేసి తీసుకోవడం
        optional_cols = [
            "Store Entry No",
            "Invoice Date",
            "GRN No",
            "GRN Date",
        ]
        available_extra_cols = [
            c for c in optional_cols if c in df.columns
        ]

        # గ్రూప్ చేసే కాలమ్స్ జాబితా
        group_cols = [sup_col, inv_col] + available_extra_cols

        summary_df = (
            df.groupby(group_cols)[val_col]
            .sum()
            .reset_index()
            .rename(columns={val_col: "Total Invoice Value"})
        )

        st.markdown(
"
        )
        st.data_editor(
            summary_df, hide_index=True, use_container_width=True, disabled=True
        )
      else:
        st.warning("⚠️ ఎక్సెల్ ఫైల్‌లో వాల్యూ కాలమ్ కనుగొనబడలేదు.")
    else:
      st.error(
          "ఎక్సెల్ ఫైల్‌లో 'Supplier / Sendor Name' లేదా 'Invoice No' కాలమ్స్"
          " లేవు."
      )
  else:
    st.info("దయచేసి ముందుగా డాటా లోడ్ చేయండి.")
