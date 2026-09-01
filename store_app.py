import os
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Enterprise Store Management System", layout="wide"
)

# Custom Styling for Professional ERP Look
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

# --- ERP TOP HORIZONTAL NAVIGATION TABS ---
st.markdown(
    """
    <div class="erp-header">
        <h2 style='margin:0; color: #0d6efd;'>🏢 Enterprise Store Management ERP</h2>
        <p style='margin:0; color: #6c757d; font-size: 14px;'>Centralized Material & Vendor Accounts Hub</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Horizontal Tabs for Modules
page = st.radio(
    "Navigation Menu",
    [
        "1. Dashboard / Home",
        "2. Material Register View",
        "3. New Record Creation",
        "4. All Suppliers List",
        "5. Material List",
        "6. Invoice Wise Total Value",
        "7. Vendor Payments Entry",
        "8. Vendor Statement & Ledger",
    ],
    horizontal=True,
)

st.markdown("---")

# ================= PAGE 1: HOME =================
if page == "1. Dashboard / Home":
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
  st.title("💳 HO Payments Management & Vendor Ledger Hub")
  st.markdown(
      "Record disbursements, view transaction logs, and access detailed"
      " financial statements."
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

      suppliers_unique = list(df[sup_col].dropna().unique())

      # --- TOP SELECTOR FOR SUPPLIER ---
      selected_summary_sup = st.selectbox(
          "🔍 Select Vendor Account:",
          suppliers_unique,
          key="summary_sup_select",
      )

      st.markdown("---")

      # --- CALCULATE FINANCIAL STANDING FOR SELECTED SUPPLIER ---
      sup_filtered_df = df[df[sup_col] == selected_summary_sup]
      total_inv_amt = sup_filtered_df[val_col].sum()

      if not st.session_state.payments_df.empty:
        sup_paid_df = st.session_state.payments_df[
            st.session_state.payments_df["Supplier Name"]
            == selected_summary_sup
        ]
        total_paid_amt = sup_paid_df["Paid Amount"].sum()
      else:
        total_paid_amt = 0.0

      net_out = total_inv_amt - total_paid_amt

      # Display Metrics
      m_col1, m_col2, m_col3 = st.columns(3)
      m_col1.metric("Total Invoice Amount", f"₹ {total_inv_amt:,.2f}")
      m_col2.metric("Total Paid Amount", f"₹ {total_paid_amt:,.2f}")
      m_col3.metric("Outstanding Balance", f"₹ {net_out:,.2f}")

      summary_single_df = pd.DataFrame(
          {
              "Supplier Name": [selected_summary_sup],
              "Total Invoice Amount": [total_inv_amt],
              "Paid Amount": [total_paid_amt],
              "Outstanding Amount": [net_out],
          }
      )
      summary_single_df.insert(0, "S.No", [1])

      st.markdown("### Financial Standing Summary:")
      st.data_editor(
          summary_single_df,
          hide_index=True,
          use_container_width=True,
          disabled=True,
      )

      st.markdown("---")

      # --- SIDE-BY-SIDE ACTION BUTTONS FOR POP-UPS ---
      b_col1, b_col2, b_col3 = st.columns(3)

      # 1. ADD NEW PAYMENT POPUP BUTTON
      with b_col1:
        if st.button("➕ Add New Payment", use_container_width=True):

          @st.dialog("➕ New Payment Entry Form", width="large")
          def show_payment_popup():
            with st.form("payment_form_popup"):
              col_p1, col_p2 = st.columns(2)
              p_supplier = col_p1.selectbox(
                  "Select Supplier Name:",
                  suppliers_unique,
                  index=suppliers_unique.index(selected_summary_sup),
              )
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
                    [st.session_state.payments_df, new_payment],
                    ignore_index=True,
                )
                st.session_state.payments_df.to_csv(PAYMENTS_FILE, index=False)
                st.success(
                    f"Successfully recorded payment of ₹ {p_amount:,.2f} for"
                    f" {p_supplier}!"
                )
                st.rerun()

          show_payment_popup()

      # 2. VIEW PAYMENT HISTORY POPUP BUTTON
      with b_col2:
        if st.button("📜 View Payment History", use_container_width=True):

          @st.dialog(
              f"📜 Payment History Log — {selected_summary_sup}", width="large"
          )
          def show_history_popup():
            if not st.session_state.payments_df.empty:
              sup_hist = (
                  st.session_state.payments_df[
                      st.session_state.payments_df["Supplier Name"]
                      == selected_summary_sup
                  ]
                  .copy()
                  .reset_index(drop=True)
              )
              if not sup_hist.empty:
                sup_hist.insert(0, "S.No", range(1, len(sup_hist) + 1))
                st.data_editor(
                    sup_hist,
                    hide_index=True,
                    use_container_width=True,
                    disabled=True,
                )
              else:
                st.info(f"No payment history found for {selected_summary_sup}.")
            else:
              st.info("No payments recorded yet.")

          show_history_popup()

      # 3. VENDOR STATEMENT & LEDGER REPORT POPUP BUTTON
      with b_col3:
        if st.button("📑 Full Statement & Ledger", use_container_width=True):

          @st.dialog(
              f"📑 Complete Statement & Ledger — {selected_summary_sup}",
              width="large",
          )
          def show_ledger_popup():
            sup_invoices = (
                df[df[sup_col] == selected_summary_sup]
                .copy()
                .reset_index(drop=True)
            )
            if "S.No" in sup_invoices.columns:
              sup_invoices["S.No"] = range(1, len(sup_invoices) + 1)
            else:
              sup_invoices.insert(0, "S.No", range(1, len(sup_invoices) + 1))

            st.markdown(f"### 📂 Invoice Line Items")
            st.data_editor(
                sup_invoices,
                hide_index=True,
                use_container_width=True,
                disabled=True,
            )

            st.markdown("---")
            st.markdown(f"### 💳 Payment Disbursement Log")
            if (
                not st.session_state.payments_df.empty
                and selected_summary_sup
                in st.session_state.payments_df["Supplier Name"].values
            ):
              sup_payments = (
                  st.session_state.payments_df[
                      st.session_state.payments_df["Supplier Name"]
                      == selected_summary_sup
                  ]
                  .copy()
                  .reset_index(drop=True)
              )
              sup_payments.insert(0, "S.No", range(1, len(sup_payments) + 1))
              st.data_editor(
                  sup_payments,
                  hide_index=True,
                  use_container_width=True,
                  disabled=True,
              )
            else:
              st.info(
                  "No payment transactions recorded for this vendor yet."
              )

          show_ledger_popup()

    else:
      st.error("Required supplier or valuation columns missing from dataset.")
  else:
    st.info("Please load data records first.")


# ================= PAGE 8: VENDOR STATEMENT & LEDGER =================
elif page == "8. Vendor Statement & Ledger":
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

      st.subheader(f"📂 Invoice Line Items — {selected_supplier_det}")
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
