import os
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Enterprise Store Management System", layout="wide"
)

# Custom Styling for Professional Look
st.markdown(
    """
    <style>
    .main {
        background-color: #f8f9fa;
    }
    div.stButton > button {
        background-color: #0d6efd;
        color: white;
        border-radius: 4px;
        padding: 0.35rem 0.75rem;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #0b5ed7;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Session State variables
if "current_df" not in st.session_state:
  st.session_state.current_df = pd.DataFrame()

# Payments data file path for permanent storage
PAYMENTS_FILE = "payments_data.csv"

if "payments_df" not in st.session_state:
  if os.path.exists(PAYMENTS_FILE):
    try:
      st.session_state.payments_df = pd.read_csv(PAYMENTS_FILE)
    except Exception as e:
      st.session_state.payments_df = pd.DataFrame(
          columns=[
              "Supplier Name",
              "Payment Date",
              "Reference No",
              "Paid Amount",
              "Remarks",
          ]
      )
  else:
    st.session_state.payments_df = pd.DataFrame(
        columns=[
            "Supplier Name",
            "Payment Date",
            "Reference No",
            "Paid Amount",
            "Remarks",
        ]
    )

# Automatically load Book1.xlsx from GitHub
if st.session_state.current_df.empty:
  try:
    df_auto = pd.read_excel("Book1.xlsx", sheet_name=0)
    st.session_state.current_df = df_auto
  except Exception as e:
    pass

# Sidebar Navigation
st.sidebar.title("Navigation Panel")
page = st.sidebar.radio(
    "Select Module:",
    [
        "1. Home / Dashboard",
        "2. Material Register View",
        "3. New Record Creation",
        "4. All Suppliers List",
        "5. Material List",
        "6. Invoice Wise Total Value",
        "7. Vendor Payments Entry",
        "8. Vendor Outstanding Detailed Report",
    ],
)

# ================= PAGE 1: HOME =================
if page == "1. Home / Dashboard":
  st.title("📦 Store Management Dashboard")
  st.markdown("Overview of store inventory and receipt records.")

  if not st.session_state.current_df.empty:
    df = st.session_state.current_df.copy()

    col1, col2 = st.columns(2)
    supplier_col = "Supplier / Sendor Name"
    if supplier_col in df.columns:
      suppliers = ["All"] + list(df[supplier_col].dropna().unique())
      selected_supplier = col1.selectbox("Filter by Supplier Name:", suppliers)
      if selected_supplier != "All":
        df = df[df[supplier_col] == selected_supplier]

    receipt_col = "Type Reciept"
    if receipt_col in df.columns:
      receipts = ["All"] + list(df[receipt_col].dropna().unique())
      selected_receipt = col2.selectbox("Filter by Receipt Type:", receipts)
      if selected_receipt != "All":
        df = df[df[receipt_col] == selected_receipt]

    df = df.reset_index(drop=True)
    if "S.No" in df.columns:
      df["S.No"] = range(1, len(df) + 1)
    else:
      df.insert(0, "S.No", range(1, len(df) + 1))

    st.markdown("---")
    col_btn1, col_btn2 = st.columns([6, 1])
    with col_btn2:
      if st.button("🖨️ Print / PDF"):
        st.markdown(
            """
                <script>
                window.print();
                </script>
                """,
            unsafe_allow_html=True,
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

# ================= PAGE 6: INVOICE WISE TOTAL VALUE =================
elif page == "6. Invoice Wise Total Value":
  st.title("📊 Invoice Summary & Total Valuation")
  st.markdown("Aggregated financial view categorized by supplier and invoice.")

  if not st.session_state.current_df.empty:
    df = st.session_state.current_df.copy()
    sup_col = "Supplier / Sendor Name"
    inv_col = "Invoice No"

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
      suppliers_list = ["All"] + list(df[sup_col].dropna().unique())
      selected_sup_filter = st.selectbox(
          "🔍 Filter by Supplier:", suppliers_list
      )

      if selected_sup_filter != "All":
        df = df[df[sup_col] == selected_sup_filter]

      if val_col and val_col in df.columns:
        df[val_col] = pd.to_numeric(
            df[val_col].astype(str).str.replace(r"[^\d.]", "", regex=True),
            errors="coerce",
        ).fillna(0)

        optional_cols = [
            "Store Entry No",
            "Invoice Date",
            "GRN No",
            "GRN Date",
        ]
        available_extra_cols = [
            c for c in optional_cols if c in df.columns
        ]
        group_cols = [sup_col, inv_col] + available_extra_cols

        summary_df = (
            df.groupby(group_cols)[val_col]
            .sum()
            .reset_index()
            .rename(columns={val_col: "Total Invoice Value"})
        )

        summary_df = summary_df.reset_index(drop=True)
        summary_df.insert(0, "S.No", range(1, len(summary_df) + 1))

        st.markdown("---")
        col_btn1, col_btn2 = st.columns([6, 1])
        with col_btn2:
          if st.button("🖨️ Print / PDF", key="print_btn_page6"):
            st.markdown(
                """
                    <script>
                    window.print();
                    </script>
                    """,
                unsafe_allow_html=True,
            )

        st.markdown("### Consolidated Invoice Valuation Table:")
        st.data_editor(
            summary_df, hide_index=True, use_container_width=True, disabled=True
        )
      else:
        st.warning("⚠️ Valuation column could not be identified.")
    else:
      st.error("Required columns ('Supplier' or 'Invoice No') are missing.")
  else:
    st.info("Please load data records first.")

# ================= PAGE 7: VENDOR PAYMENTS ENTRY =================
elif page == "7. Vendor Payments Entry":
  st.title("💳 HO Payments Management")
  st.markdown("Record and track head office disbursements made to vendors.")

  if not st.session_state.current_df.empty:
    df = st.session_state.current_df.copy()
    sup_col = "Supplier / Sendor Name"

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

    if sup_col in df.columns and val_col:
      df[val_col] = pd.to_numeric(
          df[val_col].astype(str).str.replace(r"[^\d.]", "", regex=True),
          errors="coerce",
      ).fillna(0)

      st.subheader("➕ New Payment Entry Form")
      suppliers_unique = list(df[sup_col].dropna().unique())

      with st.form("payment_form"):
        col_p1, col_p2 = st.columns(2)
        p_supplier = col_p1.selectbox("Select Supplier Name:", suppliers_unique)
        p_date = col_p2.date_input("Payment Date:")

        col_p3, col_p4 = st.columns(2)
        p_ref = col_p3.text_input("Reference No (UTR / Cheque / Ref ID):")
        p_amount = col_p4.number_input(
            "Paid Amount (₹):", min_value=0.0, step=100.0
        )
        p_remarks = st.text_input("Remarks / Description:")

        submitted = st.form_submit_button("Save Payment Record")
        if submitted:
          new_payment = pd.DataFrame(
              {
                  "Supplier Name": [p_supplier],
                  "Payment Date": [str(p_date)],
                  "Reference No": [p_ref],
                  "Paid Amount": [p_amount],
                  "Remarks": [p_remarks],
              }
          )
          st.session_state.payments_df = pd.concat(
              [st.session_state.payments_df, new_payment], ignore_index=True
          )
          # పర్మనెంట్‌గా CSV ఫైల్‌లో సేవ్ చేయడం
          st.session_state.payments_df.to_csv(PAYMENTS_FILE, index=False)
          st.success(
              f"Successfully recorded payment of ₹ {p_amount:,.2f} for"
              f" {p_supplier} and saved permanently!"
          )

      st.markdown("---")
      st.subheader("📋 Supplier Financial Standing Summary:")

      total_inv_by_sup = (
          df.groupby(sup_col)[val_col]
          .sum()
          .reset_index()
          .rename(columns={val_col: "Total Invoice Amount"})
      )

      if not st.session_state.payments_df.empty:
        total_paid_by_sup = (
            st.session_state.payments_df.groupby("Supplier Name")["Paid Amount"]
            .sum()
            .reset_index()
            .rename(columns={"Supplier Name": sup_col})
        )
        outstanding_df = pd.merge(
            total_inv_by_sup, total_paid_by_sup, on=sup_col, how="left"
        ).fillna({"Paid Amount": 0})
      else:
        outstanding_df = total_inv_by_sup.copy()
        outstanding_df["Paid Amount"] = 0

      outstanding_df["Outstanding Amount"] = (
          outstanding_df["Total Invoice Amount"] - outstanding_df["Paid Amount"]
      )

      outstanding_df = outstanding_df.reset_index(drop=True)
      outstanding_df.insert(0, "S.No", range(1, len(outstanding_df) + 1))

      st.data_editor(
          outstanding_df,
          hide_index=True,
          use_container_width=True,
          disabled=True,
      )

      if not st.session_state.payments_df.empty:
        st.markdown("---")
        st.subheader("📜 Complete Payment History Log:")
        pay_hist_df = st.session_state.payments_df.reset_index(drop=True)
        pay_hist_df.insert(0, "S.No", range(1, len(pay_hist_df) + 1))
        st.data_editor(
            pay_hist_df,
            hide_index=True,
            use_container_width=True,
            disabled=True,
        )
    else:
      st.error("Required supplier or valuation columns missing from dataset.")
  else:
    st.info("Please load data records first.")

# ================= PAGE 8: VENDOR OUTSTANDING DETAILED REPORT =================
elif page == "8. Vendor Outstanding Detailed Report":
  st.title("📑 Vendor Statement & Ledger Report")
  st.markdown(
      "Detailed ledger breakdown of invoices, disbursements, and net"
      " outstanding balances."
  )

  if not st.session_state.current_df.empty:
    df = st.session_state.current_df.copy()
    sup_col = "Supplier / Sendor Name"
    inv_col = "Invoice No"

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

    if sup_col in df.columns and val_col:
      df[val_col] = pd.to_numeric(
          df[val_col].astype(str).str.replace(r"[^\d.]", "", regex=True),
          errors="coerce",
      ).fillna(0)

      suppliers_list = list(df[sup_col].dropna().unique())
      selected_supplier_det = st.selectbox(
          "🔍 Select Vendor Account for Statement:",
          suppliers_list,
          key="det_sup_select",
      )

      st.markdown("---")

      sup_invoices = (
          df[df[sup_col] == selected_supplier_det].copy().reset_index(drop=True)
      )
      if "S.No" in sup_invoices.columns:
        sup_invoices["S.No"] = range(1, len(sup_invoices) + 1)
      else:
        sup_invoices.insert(0, "S.No", range(1, len(sup_invoices) + 1))

      total_inv_amt = sup_invoices[val_col].sum()

      if not st.session_state.payments_df.empty:
        sup_payments = (
            st.session_state.payments_df[
                st.session_state.payments_df["Supplier Name"]
                == selected_supplier_det
            ]
            .copy()
            .reset_index(drop=True)
        )
        sup_payments.insert(0, "S.No", range(1, len(sup_payments) + 1))
        total_paid_amt = sup_payments["Paid Amount"].sum()
      else:
        sup_payments = pd.DataFrame()
        total_paid_amt = 0.0

      net_outstanding = total_inv_amt - total_paid_amt

      col_m1, col_m2, col_m3 = st.columns(3)
      col_m1.metric("📦 Total Invoice Value", f"₹ {total_inv_amt:,.2f}")
      col_m2.metric("💳 Total Paid Value", f"₹ {total_paid_amt:,.2f}")
      col_m3.metric("⚠️ Net Outstanding Balance", f"₹ {net_outstanding:,.2f}")

      st.markdown("---")

      col_b1, col_b2 = st.columns([6, 1])
      with col_b2:
        if st.button("🖨️ Print / PDF", key="print_btn_page8"):
          st.markdown(
              """
                  <script>
                  window.print();
                  </script>
                  """,
              unsafe_allow_html=True,
          )

      st.subheader(f"📂 — {selected_supplier_det}")
      st.data_editor(
          sup_invoices,
          hide_index=True,
          use_container_width=True,
          disabled=True,
          key="det_inv_table",
      )

      st.markdown("---")
      st.subheader(f"💳 Payment Disbursement Log — {selected_supplier_det}")
      if not sup_payments.empty:
        st.data_editor(
            sup_payments,
            hide_index=True,
            use_container_width=True,
            disabled=True,
            key="det_pay_table",
        )
      else:
        st.info("No payment transactions recorded for this vendor.")

    else:
      st.error("Required dataset columns not detected.")
  else:
    st.info("Please load data records first.")

# Handle Remaining Pages as Professional Placeholders
elif page in [
    "2. Material Register View",
    "3. New Record Creation",
    "4. All Suppliers List",
    "5. Material List",
]:
  st.title(page)
  st.markdown(
      "This module is configured to standard corporate template parameters."
  )
  st.info("Module ready for operational deployment.")
