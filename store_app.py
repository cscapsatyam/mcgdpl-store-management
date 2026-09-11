import io
import os
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle
import streamlit as st

# 🔗 మీ GitHub Raw Excel లింక్ ఆటోమేటిక్‌గా సెట్ చేయబడింది
GITHUB_EXCEL_URL = "https://raw.githubusercontent.com/cscapsatyam/mcgdpl-store-management/main/BookA1.xlsx"

st.set_page_config(
    page_title="Movone Infrastructure Private Limited", layout="wide"
)


# --- Helper Function: Excel Column Names Flexibly Find చేయడానికి ---
def find_column(df, possible_keywords):
  for col in df.columns:
    clean_col = (
        str(col)
        .lower()
        .replace(" ", "")
        .replace("/", "")
        .replace(".", "")
        .replace("_", "")
    )
    for kw in possible_keywords:
      clean_kw = (
          kw.lower()
          .replace(" ", "")
          .replace("/", "")
          .replace(".", "")
          .replace("_", "")
      )
      if clean_kw in clean_col:
        return col
  return None


# --- Helper Function: Direct PDF Generate చేయడానికి ---
def generate_pdf_download(df, title="Store Inventory Report"):
  buffer = io.BytesIO()
  doc = SimpleDocTemplate(
      buffer,
      pagesize=landscape(A4),
      rightMargin=15,
      leftMargin=15,
      topMargin=20,
      bottomMargin=20,
  )
  elements = []

  styles = getSampleStyleSheet()
  title_style = styles["Title"]
  title_style.fontSize = 14
  elements.append(Paragraph(f"<b>{title}</b>", title_style))

  pdf_data = [df.columns.tolist()] + df.astype(str).values.tolist()

  table = Table(pdf_data, repeatRows=1)
  table.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6efd")),
          ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
          ("ALIGN", (0, 0), (-1, -1), "CENTER"),
          ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
          ("FONTSIZE", (0, 0), (-1, -1), 7),
          ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
          ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
      ])
  )

  elements.append(table)
  doc.build(elements)
  buffer.seek(0)
  return buffer.getvalue()


# Custom ERP Styling
st.markdown(
    """
    <style>
    .main {
        background-color: #f4f6f9;
    }
    div.stButton > button {
        background-color: #0d6efd;
        color: white;
        border-radius: 6px;
        padding: 0.4rem 1rem;
        border: none;
        font-weight: 500;
    }
    div.stButton > button:hover {
        background-color: #0b5ed7;
        color: white;
    }
    .erp-header {
        background-color: #ffffff;
        padding: 15px 20px;
        border-bottom: 2px solid #0d6efd;
        margin-bottom: 20px;
        border-radius: 6px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Session State & GitHub నుండి డేటా ఆటోమేటిక్‌గా లోడ్ చేయడం
if "current_df" not in st.session_state:
  st.session_state.current_df = pd.DataFrame()

if st.session_state.current_df.empty:
  try:
    df_auto = pd.read_excel(GITHUB_EXCEL_URL, sheet_name=0)
    st.session_state.current_df = df_auto
  except Exception as e:
    st.warning(
        f"GitHub నుండి డేటా లోడ్ కాలేదు: {e}. దయచేసి ఫైల్ పేరు లేదా పాత్ సరిగ్గా"
        " ఉందో లేదో తనిఖీ చేయండి."
    )

# --- ERP TOP NAVIGATION TABS ---
st.markdown(
    """
    <div class="erp-header">
        <h2 style='margin:0; color: #0d6efd;'>🏢 Enterprise Store Management ERP</h2>
        <p style='margin:0; color: #6c757d; font-size: 14px;'>Centralized Material & Vendor Accounts Hub</p>
    </div>
    """,
    unsafe_allow_html=True,
)

page = st.radio(
    "Navigation Menu",
    ["1. Dashboard / Home", "2. Material Register View"],
    horizontal=True,
)

st.markdown("---")

# ================= PAGE 1: HOME (NO FILTERS) =================
if page == "1. Dashboard / Home":
  st.title("📦 Store Management Dashboard")
  st.markdown("Overview of complete store inventory records.")

  if not st.session_state.current_df.empty:
    df = st.session_state.current_df.copy()

    df = df.reset_index(drop=True)
    sl_col = find_column(df, ["Sl No", "S.No", "SlNo", "SNo", "Serial No"])
    if sl_col:
      df[sl_col] = range(1, len(df) + 1)
    else:
      df.insert(0, "Sl No", range(1, len(df) + 1))

    # PDF Download Button
    pdf_bytes = generate_pdf_download(
        df, title="Complete Store Inventory Report"
    )

    col_btn1, col_btn2 = st.columns([6, 1])
    with col_btn2:
      st.download_button(
          label="📥 Download PDF",
          data=pdf_bytes,
          file_name="Store_Inventory_Report.pdf",
          mime="application/pdf",
          use_container_width=True,
      )

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
        "📁 Upload Excel Data Source", type=["xlsx", "xls"]
    )
    if uploaded_file is not None:
      try:
        df = pd.read_excel(uploaded_file, sheet_name=0)
        st.session_state.current_df = df
        st.rerun()
      except Exception as e:
        st.error(f"Error loading file: {e}")

# ================= PAGE 2: MATERIAL REGISTER VIEW =================
elif page == "2. Material Register View":
  st.title("📋 Material Register View")
  st.markdown("Filter material records and view supplier sub-totals.")

  if not st.session_state.current_df.empty:
    df = st.session_state.current_df.copy()

    col1, col2 = st.columns(2)

    # 1. Supplier Filter
    supplier_col = find_column(
        df, ["Supplier/Sender Name", "Supplier", "Sender", "Vendor"]
    )
    selected_supplier = "All"
    if supplier_col:
      suppliers = ["All"] + list(df[supplier_col].dropna().unique())
      selected_supplier = col1.selectbox(
          "Filter by Supplier Name:", suppliers, key="page2_supplier"
      )
      if selected_supplier != "All":
        df = df[df[supplier_col] == selected_supplier]

    # 2. Receipt Filter
    receipt_col = find_column(
        df,
        [
            "Vehicle No.Type of Receipt",
            "Type of Receipt",
            "Receipt Type",
            "Receipt",
            "Reciept",
        ],
    )
    if receipt_col:
      receipts = ["All"] + list(df[receipt_col].dropna().unique())
      selected_receipt = col2.selectbox(
          "Filter by Receipt Type:", receipts, key="page2_receipt"
      )
      if selected_receipt != "All":
        df = df[df[receipt_col] == selected_receipt]

    # 3. Sub-Totals Calculation
    total_val_col = find_column(
        df,
        [
            "Total Invoie Value",
            "Total Invoice Value",
            "Invoice Basic Total Value",
            "Total Amount",
            "Amount",
            "Value",
        ],
    )
    qty_col = find_column(
        df, ["Received Qty", "Invoice/Delivery Challan Qty", "Qty", "Quantity"]
    )

    sub_total_val = 0.0
    total_qty = 0.0

    if total_val_col and total_val_col in df.columns:
      sub_total_val = (
          pd.to_numeric(
              df[total_val_col].astype(str).str.replace(r"[^\d.]", "", regex=True),
              errors="coerce",
          )
          .fillna(0)
          .sum()
      )

    if qty_col and qty_col in df.columns:
      total_qty = (
          pd.to_numeric(
              df[qty_col].astype(str).str.replace(r"[^\d.]", "", regex=True),
              errors="coerce",
          )
          .fillna(0)
          .sum()
      )

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("Selected Supplier", selected_supplier)
    m2.metric("Sub-Total Value", f"₹ {sub_total_val:,.2f}")
    m3.metric("Total Received Qty", f"{total_qty:,.2f}")

    df = df.reset_index(drop=True)
    sl_col = find_column(df, ["Sl No", "S.No", "SlNo", "SNo", "Serial No"])
    if sl_col:
      df[sl_col] = range(1, len(df) + 1)
    else:
      df.insert(0, "Sl No", range(1, len(df) + 1))

    st.markdown("---")

    # Filtered PDF Download Button
    pdf_bytes_filtered = generate_pdf_download(
        df, title=f"Material Register - Supplier: {selected_supplier}"
    )

    col_b1, col_b2 = st.columns([6, 1])
    with col_b2:
      st.download_button(
          label="📥 Download PDF",
          data=pdf_bytes_filtered,
          file_name=f"Material_Register_{selected_supplier}.pdf",
          mime="application/pdf",
          use_container_width=True,
      )

    calc_height = min(max(len(df) * 38 + 40, 150), 500)
    st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        disabled=True,
        height=calc_height,
    )
  else:
    st.info("Please upload or load Excel data source first.")
