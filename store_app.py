import io
import os
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
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


# --- Helper Function: Professional PDF A4 Landscape Layout (CGST/SGST Widths Optimized) ---
def generate_pdf_download(df, title="Store Inventory Report"):
  buffer = io.BytesIO()
  # A4 Landscape with compact margins to maximize printable area
  doc = SimpleDocTemplate(
      buffer,
      pagesize=landscape(A4),
      rightMargin=10,
      leftMargin=10,
      topMargin=20,
      bottomMargin=20,
  )
  elements = []

  styles = getSampleStyleSheet()
  title_style = styles["Title"]
  title_style.fontSize = 13
  elements.append(Paragraph(f"<b>{title}</b>", title_style))
  elements.append(Paragraph("<br/>", styles["Normal"]))

  header_cell_style = ParagraphStyle(
      "HeaderCell",
      parent=styles["Normal"],
      fontName="Helvetica-Bold",
      fontSize=6,
      leading=7.5,
      alignment=1,
      textColor=colors.whitesmoke,
  )

  body_cell_style = ParagraphStyle(
      "BodyCell",
      parent=styles["Normal"],
      fontName="Helvetica",
      fontSize=5.5,
      leading=7,
      alignment=1,
      textColor=colors.HexColor("#222222"),
  )

  table_data = []
  header_row = [
      Paragraph(str(col), header_cell_style) for col in df.columns.tolist()
  ]
  table_data.append(header_row)

  for _, row in df.iterrows():
    row_data = [
        Paragraph(str(val) if val is not None else "", body_cell_style)
        for val in row.values
    ]
    table_data.append(row_data)

  # 📌 కాలమ్ పేరును బట్టి కస్టమ్ విడ్త్ (CGST & SGST విడ్త్ తగ్గించబడింది)
  total_available_width = 822  # A4 Landscape available width
  num_cols = len(df.columns)
  col_widths = []

  for col in df.columns:
    col_l = str(col).lower()
    if "description" in col_l or "material" in col_l:
      col_widths.append(95)  # మెటీరియల్ డిస్క్రిప్షన్‌కు మరింత ఎక్కువ వెడల్పు
    elif "supplier" in col_l or "sender" in col_l:
      col_widths.append(80)  # సప్లయర్ పేరుకు
    elif "cgst" in col_l or "sgst" in col_l:
      col_widths.append(
          22
      )  # 📌 CGST & SGST కాలమ్స్ చాలా చిన్నవిగా (తగ్గించబడ్డాయి)
    elif "date" in col_l:
      col_widths.append(42)  # డేట్స్‌కు
    elif "no" in col_l or "sl" in col_l:
      col_widths.append(28)  # నంబర్స్‌కు
    else:
      col_widths.append(
          max(35, total_available_width / num_cols)
      )  # మిగతా వాటికి ఆటో-డిస్ట్రిబ్యూషన్

  table = Table(table_data, colWidths=col_widths, repeatRows=1)
  table.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6efd")),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
          ("TOPPADDING", (0, 0), (-1, -1), 4.5),
          (
              "BACKGROUND",
              (0, 1),
              (-1, -1),
              colors.HexColor("#ffffff"),
          ),
          ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fdfdfe")]),
          ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
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
    df_auto = pd.read_excel(GITHUB_EXCEL_URL, sheet_name=0, header=0)

    df_auto = df_auto.loc[
        :, ~df_auto.columns.astype(str).str.contains("^Unnamed", case=False)
    ]
    recv_col = find_column(df_auto, ["Received Qty"])
    if recv_col:
      df_auto = df_auto.drop(columns=[recv_col])

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
