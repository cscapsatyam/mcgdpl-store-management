import io
import os
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle
import streamlit as st

# 🔗 మీ GitHub Raw Excel లింక్
GITHUB_EXCEL_URL = (
    "https://raw.githubusercontent.com/cscapsatyam/mcgdpl-store-management/main/BookA1.xlsx"
)

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


# --- Helper Function: PDF A4 Landscape Layout & Perfect Pro Spacing ---
def generate_pdf_download(df, title="Store Inventory Report"):
  buffer = io.BytesIO()
  # A4 Landscape with spacious margins for clean layout
  doc = SimpleDocTemplate(
      buffer,
      pagesize=landscape(A4),
      rightMargin=20,
      leftMargin=20,
      topMargin=25,
      bottomMargin=25,
  )
  elements = []

  styles = getSampleStyleSheet()
  title_style = styles["Title"]
  title_style.fontSize = 14
  elements.append(Paragraph(f"<b>{title}</b>", title_style))
  elements.append(Paragraph("<br/>", styles["Normal"]))

  # Data formatting for PDF
  pdf_data = [df.columns.tolist()] + df.astype(str).values.tolist()

  # A4 Landscape width calculation for expanded row/column size
  num_cols = len(df.columns)
  col_width = 800 / num_cols if num_cols > 0 else 60
  col_widths = [col_width] * num_cols

  table = Table(pdf_data, colWidths=col_widths, repeatRows=1)
  table.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6efd")),
          ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
          ("ALIGN", (0, 0), (-1, -1), "CENTER"),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
          ("FONTSIZE", (0, 0), (-1, -1), 7),  # Clear & readable font size
          ("BOTTOMPADDING", (0, 0), (-1, -1), 6),  # Increased row height
          ("TOPPADDING", (0, 0), (-1, -1), 6),
          ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bbbbbb")),
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
    @media print {
        header, footer, nav, .stSidebar, div[data-testid="stSidebar"] {
            display: none !important;
        }
        body {
            background: white !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Session State & GitHub నుండి డేటా లోడ్ చేయడం
if "current_df" not in st.session_state:
  st.session_state.current_df = pd.DataFrame()

if st.session_state.current_df.empty:
  try:
    # 📌 ఎలాంటి ఎక్స్‌ట్రా హెడర్ ఇబ్బందులు లేకుండా నేరుగా ఎక్సెల్ డేటాను రీడ్ చేయడం (header=0)
    df_auto = pd.read_excel(GITHUB_EXCEL_URL, sheet_name=0, header=0)

    # 1. Unnamed ఖాళీ కాలమ్స్‌ని తొలగించడం
    df_auto = df_auto.loc[
        :, ~df_auto.columns.astype(str).str.contains("^Unnamed", case=False)
    ]

    # 2. 'Received Qty' కాలమ్ ఉంటే తొలగించడం
    recv_col = find_column(df_auto, ["Received Qty"])
    if recv_col:
      df_auto = df_auto.drop(columns=[recv_col])

    # 3. డేట్స్ మరియు డెసిమల్ నంబర్స్ క్లీన్ చేయడం (రౌండ్ ఆఫ్ 2 డెసిమల్స్)
    for col in df_auto.columns:
      col_lower = str(col).lower()
      if "date" in col_lower or "dt" in col_lower:
        df_auto[col] = (
            pd.to_datetime(df_auto[col], errors="coerce")
            .dt.strftime("%Y-%m-%d")
            .fillna("")
        )
        df_auto[col] = df_auto[col].replace("NaT", "").replace("NaN", "")
      else:
        try:
          numeric_series = pd.to_numeric(df_auto[col], errors="coerce")
          if (
              numeric_series.notnull().sum() > 0
              and "no" not in col_lower
              and "sl" not in col_lower
          ):
            df_auto[col] = numeric_series.round(2).fillna("")
        except:
          pass

        df_auto[col] = (
            df_auto[col]
            .astype(str)
            .str.replace("00:00:00", "", regex=False)
            .str.strip()
        )
        df_auto[col] = (
            df_auto[col]
            .replace("nan", "")
            .replace("NaT", "")
            .replace("None", "")
        )

    st.session_state.current_df = df_auto
  except Exception as e:
    st.warning(f"GitHub నుండి డేటా లోడ్ కాలేదు: {e}")

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

    calc_height = min(max(len(df) * 45 + 50, 200), 650)
    st.dataframe(df, hide_index=True, use_container_width=True, height=calc_height)
  else:
    st.info("Please load data source first.")

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
    challan_qty_col = find_column(
        df, ["Invoice/Delivery Challan Qty", "Qty", "Quantity"]
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

    if challan_qty_col and challan_qty_col in df.columns:
      total_qty = (
          pd.to_numeric(
              df[challan_qty_col]
              .astype(str)
              .str.replace(r"[^\d.]", "", regex=True),
              errors="coerce",
          )
          .fillna(0)
          .sum()
      )

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("Selected Supplier", selected_supplier)
    m2.metric("Sub-Total Value", f"₹ {sub_total_val:,.2f}")
    m3.metric("Total Challan Qty", f"{total_qty:,.2f}")

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

    calc_height = min(max(len(df) * 45 + 50, 200), 650)
    st.dataframe(df, hide_index=True, use_container_width=True, height=calc_height)
  else:
    st.info("Please load data source first.")
