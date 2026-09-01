import os
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Enterprise Store Management System", layout="wide"
)

# Custom Styling with Professional ERP Look & A4 Border Print Layout
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

    /* --- A4 SIZE PDF & PRINT STYLING WITH BORDER DESIGN --- */
    @media print {
        @page {
            size: A4 portrait;
            margin: 10mm;
        }
        
        header, footer, nav, .stSidebar, div[data-testid="stSidebar"], button {
            display: none !important;
        }
        
        body {
            background: white !important;
            color: black !important;
            font-family: Arial, sans-serif !important;
            font-size: 11pt;
        }
        
        .main, .block-container {
            padding: 15px !important;
            margin: 0 !important;
            width: 100% !important;
            border: 3px double #333333 !important;
            box-sizing: border-box;
        }

        div[data-baseweb="modal"] {
            position: absolute !important;
            left: 0 !important;
            top: 0 !important;
            width: 100% !important;
            background: white !important;
            border: 3px double #333333 !important;
            padding: 20px !important;
        }

        table {
            width: 100% !important;
            border-collapse: collapse !important;
            margin-top: 10px;
        }
        th, td {
            border: 1px solid #666666 !important;
            padding: 6px 8px !important;
            text-align: left;
            font-size: 10pt;
        }
        th {
            background-color: #e9ecef !important;
            color: black !important;
            -webkit-print-color-adjust: exact;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Session State variables
if "current_df" not in st.session_state:
  st.session_state.current_df = pd.DataFrame()

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
        "9. AKG Shutterings Ledger",
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
                setTimeout(function() {
                    window.print();
                }, 500);
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
                    setTimeout(function() {
                        window.print();
                    }, 500);
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

      # --- TWO ACTION BUTTONS FOR POP-UPS (View Payment History removed) ---
      b_col1, b_col2 = st.columns(2)

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

      # 2. VENDOR STATEMENT & LEDGER REPORT POPUP BUTTON (WITH PDF / PRINT OPTION)
      with b_col2:
        if st.button("📑 Full Statement & Ledger", use_container_width=True):

          @st.dialog(
              f"📑 Complete Statement & Ledger — {selected_summary_sup}",
              width="large",
          )
          def show_ledger_popup():
            if st.button("🖨️ Print / Save as PDF", key="print_ledger_popup"):
              st.markdown(
                  """
                            <script>
                            setTimeout(function() {
                                window.print();
                            }, 500);
                            </script>
                            """,
                  unsafe_allow_html=True,
              )

            st.markdown("---")
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
                  setTimeout(function() {
                      window.print();
                  }, 500);
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
    
  
# ================= PAGE 9: AKG SHUTTERINGS DEDICATED LEDGER =================
elif page == "9. AKG Shutterings Ledger":
  st.title(
      "📑 AKG SHUTTERINGS PRIVATE LIMITED - Rental, Stock Ledger & Tax"
  )
  st.markdown(
      "Exclusive statement breakdown including Store Entry, Return Dates,"
      " Monthly Stock Rent, Stock Ledger, and 18% Tax Calculation."
  )

  if "current_df" in st.session_state and not st.session_state.current_df.empty:
    df = st.session_state.current_df.copy()
    sup_col = "Supplier / Sendor Name"

    if sup_col in df.columns:
      target_supplier = "AKG SHUTTERINGS PRIVATE LIMITED"
      sup_invoices = (
          df[df[sup_col] == target_supplier].copy().reset_index(drop=True)
      )

      if not sup_invoices.empty:
        # 1. Month-wise Value Filter (rent breakdown కోసం మాత్రమే ఫిల్టర్)
        date_col = (
            "Actualy Recived Date"
            if "Actualy Recived Date" in sup_invoices.columns
            else None
        )
        if date_col:
          sup_invoices["Month_Year"] = pd.to_datetime(
              sup_invoices[date_col], errors="coerce"
          ).dt.strftime("%B %Y")
          months_list = ["All Months"] + [
              m for m in sup_invoices["Month_Year"].dropna().unique() if pd.notnull(m)
          ]

          col_f1, _ = st.columns([2, 4])
          with col_f1:
            selected_month = st.selectbox(
                "📅 Filter by Month & Year (Rent Table Only):", months_list, key="akg_month_filter"
            )

          filtered_sup_invoices = sup_invoices.copy()
          if selected_month != "All Months":
            filtered_sup_invoices = filtered_sup_invoices[
                filtered_sup_invoices["Month_Year"] == selected_month
            ]
        else:
          filtered_sup_invoices = sup_invoices.copy()

        # 2. డే-వైస్, మంత్లీ రెంట్ మరియు 18% టాక్స్ కాలిక్యులేషన్ లాజిక్
        if "Actualy Recived Date" in filtered_sup_invoices.columns:
          filtered_sup_invoices["Actualy Recived Date DT"] = pd.to_datetime(
              filtered_sup_invoices["Actualy Recived Date"], errors="coerce"
          )

          if "Return Date" not in filtered_sup_invoices.columns:
            filtered_sup_invoices["Return Date"] = None

          filtered_sup_invoices["Return Date DT"] = pd.to_datetime(
              filtered_sup_invoices["Return Date"], errors="coerce"
          )
          effective_return_dt = filtered_sup_invoices["Return Date DT"].fillna(
              pd.to_datetime("today")
          )

          filtered_sup_invoices["Total Days"] = (
              effective_return_dt - filtered_sup_invoices["Actualy Recived Date DT"]
          ).dt.days
          filtered_sup_invoices["Total Days"] = filtered_sup_invoices["Total Days"].fillna(1)
          filtered_sup_invoices["Total Days"] = filtered_sup_invoices["Total Days"].apply(
              lambda x: max(int(x), 1)
          )

          filtered_sup_invoices["Calculated Months"] = (
              filtered_sup_invoices["Total Days"] / 30.0
          ).round(2)

        possible_qty_cols = ["Qty", "Quantity", "Nos"]
        possible_rate_cols = ["Rate", "Unit Rate", "Rent Rate"]

        qty_col = next(
            (c for c in possible_qty_cols if c in filtered_sup_invoices.columns), "Qty"
        )
        rate_col = next(
            (c for c in possible_rate_cols if c in filtered_sup_invoices.columns), "Rate"
        )

        if qty_col not in filtered_sup_invoices.columns:
          filtered_sup_invoices[qty_col] = 1.0
        if rate_col not in filtered_sup_invoices.columns:
          filtered_sup_invoices[rate_col] = 0.0

        filtered_sup_invoices[qty_col] = pd.to_numeric(
            filtered_sup_invoices[qty_col]
            .astype(str)
            .str.replace(r"[^\d.]", "", regex=True),
            errors="coerce",
        ).fillna(0)
        filtered_sup_invoices[rate_col] = pd.to_numeric(
            filtered_sup_invoices[rate_col]
            .astype(str)
            .str.replace(r"[^\d.]", "", regex=True),
            errors="coerce",
        ).fillna(0)

        filtered_sup_invoices["Base Rent Value"] = (
            filtered_sup_invoices[qty_col]
            * filtered_sup_invoices[rate_col]
            * filtered_sup_invoices["Calculated Months"]
        ).round(2)
        filtered_sup_invoices["CGST (9%)"] = (filtered_sup_invoices["Base Rent Value"] * 0.09).round(2)
        filtered_sup_invoices["SGST (9%)"] = (filtered_sup_invoices["Base Rent Value"] * 0.09).round(2)
        filtered_sup_invoices["Total Rent with 18% Tax"] = (
            filtered_sup_invoices["Base Rent Value"]
            + filtered_sup_invoices["CGST (9%)"]
            + filtered_sup_invoices["SGST (9%)"]
        ).round(2)

        if "S.No" in filtered_sup_invoices.columns:
          filtered_sup_invoices["S.No"] = range(1, len(filtered_sup_invoices) + 1)
        else:
          filtered_sup_invoices.insert(0, "S.No", range(1, len(filtered_sup_invoices) + 1))

        # మొత్తం ఇన్‌వాయిస్ అమౌంట్ అన్ని నెలలకి కలిపి లెక్కింపు
        sup_invoices[qty_col] = pd.to_numeric(
            sup_invoices[qty_col].astype(str).str.replace(r"[^\d.]", "", regex=True), errors="coerce"
        ).fillna(0)
        
        # అన్ని నెలల టోటల్ రెంట్ వాల్యూ కోసం పూర్తి డేటాను లెక్కించడం
        full_calc_df = sup_invoices.copy()
        if "Actualy Recived Date" in full_calc_df.columns:
          full_calc_df["Actualy Recived Date DT"] = pd.to_datetime(full_calc_df["Actualy Recived Date"], errors="coerce")
          if "Return Date" not in full_calc_df.columns:
            full_calc_df["Return Date"] = None
          full_calc_df["Return Date DT"] = pd.to_datetime(full_calc_df["Return Date"], errors="coerce")
          eff_ret = full_calc_df["Return Date DT"].fillna(pd.to_datetime("today"))
          full_calc_df["Total Days"] = (eff_ret - full_calc_df["Actualy Recived Date DT"]).dt.days.apply(lambda x: max(int(x), 1))
          full_calc_df["Calculated Months"] = (full_calc_df["Total Days"] / 30.0).round(2)
        else:
          full_calc_df["Calculated Months"] = 1.0

        if rate_col in full_calc_df.columns:
          full_calc_df[rate_col] = pd.to_numeric(
              full_calc_df[rate_col].astype(str).str.replace(r"[^\d.]", "", regex=True), errors="coerce"
          ).fillna(0)
        else:
          full_calc_df[rate_col] = 0.0

        full_calc_df["Base Rent Value"] = (full_calc_df[qty_col] * full_calc_df[rate_col] * full_calc_df["Calculated Months"]).round(2)
        full_calc_df["Total Rent with 18% Tax"] = (full_calc_df["Base Rent Value"] * 1.18).round(2)
        
        total_inv_amt = full_calc_df["Total Rent with 18% Tax"].sum()

        if "payments_df" in st.session_state and not st.session_state.payments_df.empty:
          sup_payments = (
              st.session_state.payments_df[
                  st.session_state.payments_df["Supplier Name"] == target_supplier
              ]
              .copy()
              .reset_index(drop=True)
          )
          if not sup_payments.empty:
            sup_payments.insert(0, "S.No", range(1, len(sup_payments) + 1))
            total_paid_amt = sup_payments["Paid Amount"].sum()
          else:
            total_paid_amt = 0.0
        else:
          sup_payments = pd.DataFrame()
          total_paid_amt = 0.0

        net_outstanding = total_inv_amt - total_paid_amt

        # మెట్రిక్స్ డిస్‌ప్లే
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("📦 Total Rent Value (inc. 18% Tax)", f"₹ {total_inv_amt:,.2f}")
        col_m2.metric("💳 Total Paid Value", f"₹ {total_paid_amt:,.2f}")
        col_m3.metric("⚠️ Net Outstanding Balance", f"₹ {net_outstanding:,.2f}")

        st.markdown("---")

        # Expander for Updates
        with st.expander(
            "✏️ Click Here to Update Return Date, Qty & Rates / Add Payment",
            expanded=False,
        ):
          tab_p1, tab_p2 = st.tabs(["📦 Update Material & Return", "💳 Add Payment"])

          with tab_p1:
            with st.form("akg_rent_form"):
              st.subheader("Update Material Return Date, Qty & Rate")
              entry_col_name = (
                  "Store Entry No"
                  if "Store Entry No" in sup_invoices.columns
                  else sup_invoices.columns[0]
              )
              entry_list = list(sup_invoices[entry_col_name].dropna().unique())

              if entry_list:
                selected_entry = st.selectbox(
                    "Select Store Entry No:", entry_list
                )

                curr_row = sup_invoices[
                    sup_invoices[entry_col_name] == selected_entry
                ].iloc[0]
                curr_qty = float(curr_row.get(qty_col, 1.0))
                curr_rate = float(curr_row.get(rate_col, 0.0))

                existing_ret_date = curr_row.get("Return Date")
                default_date = (
                    pd.to_datetime(existing_ret_date).date()
                    if pd.notnull(existing_ret_date)
                    else datetime.date.today()
                )

                col_e1, col_e2 = st.columns(2)
                with col_e1:
                  new_qty = st.number_input(
                      "Quantity", value=curr_qty, min_value=0.0, format="%.2f"
                  )
                  is_returned = st.checkbox(
                      "Has Material Been Returned?",
                      value=True if pd.notnull(existing_ret_date) else False,
                  )
                with col_e2:
                  new_rate = st.number_input(
                      "Monthly Rent Rate (₹)",
                      value=curr_rate,
                      min_value=0.0,
                      format="%.2f",
                  )
                  new_return_date = st.date_input(
                      "Material Return Date", value=default_date
                  )

                submitted_rent = st.form_submit_button(
                    "Save & Recalculate Rent"
                )
                if submitted_rent:
                  final_ret_val = (
                      str(new_return_date) if is_returned else None
                  )

                  if "Return Date" not in df.columns:
                    df["Return Date"] = None

                  df.loc[
                      (df[sup_col] == target_supplier)
                      & (df[entry_col_name] == selected_entry),
                      qty_col,
                  ] = new_qty
                  df.loc[
                      (df[sup_col] == target_supplier)
                      & (df[entry_col_name] == selected_entry),
                      rate_col,
                  ] = new_rate
                  df.loc[
                      (df[sup_col] == target_supplier)
                      & (df[entry_col_name] == selected_entry),
                      "Return Date",
                  ] = final_ret_val

                  st.session_state.current_df = df
                  st.success("Updated successfully!")
                  st.rerun()
              else:
                st.warning("No store entries found.")

          with tab_p2:
            with st.form("akg_payment_form"):
              st.subheader("Add Payment Entry")
              st.text_input("Vendor Name", value=target_supplier, disabled=True)
              p_date = st.date_input("Payment Date")
              p_amount = st.number_input(
                  "Paid Amount (₹)", min_value=0.0, format="%.2f"
              )
              p_mode = st.selectbox(
                  "Payment Mode", ["Bank Transfer", "Cheque", "UPI", "Cash"]
              )
              p_ref = st.text_input("Reference / Transaction ID")

              submitted_pay = st.form_submit_button("Save Payment")
              if submitted_pay:
                new_pay_row = {
                    "Supplier Name": target_supplier,
                    "Payment Date": str(p_date),
                    "Paid Amount": p_amount,
                    "Payment Mode": p_mode,
                    "Reference No": p_ref,
                }
                if "payments_df" not in st.session_state:
                  st.session_state.payments_df = pd.DataFrame(
                      columns=[
                          "Supplier Name",
                          "Payment Date",
                          "Paid Amount",
                          "Payment Mode",
                          "Reference No",
                      ]
                  )
                st.session_state.payments_df = pd.concat(
                    [
                        st.session_state.payments_df,
                        pd.DataFrame([new_pay_row]),
                    ],
                    ignore_index=True,
                )
                st.success("Payment saved successfully!")
                st.rerun()

        st.markdown("---")
        st.subheader(
            "📂 Monthly Stock Rent, Return Date & 18% Tax Breakdown — AKG"
            " Shutterings"
        )

        desired_cols = [
            "S.No",
            "Store Entry No",
            "Actualy Recived Date",
            "Return Date",
            "Work Order No",
            "Description Of material",
            "UOM",
            qty_col,
            rate_col,
            "Total Days",
            "Calculated Months",
            "Base Rent Value",
            "CGST (9%)",
            "SGST (9%)",
            "Total Rent with 18% Tax",
        ]
        existing_cols = [c for c in desired_cols if c and c in filtered_sup_invoices.columns]
        other_cols = [
            c for c in filtered_sup_invoices.columns if c not in existing_cols
        ]
        ordered_sup_invoices = filtered_sup_invoices[existing_cols + other_cols]

        st.data_editor(
            ordered_sup_invoices,
            hide_index=True,
            use_container_width=True,
            disabled=True,
            key="akg_inv_table",
        )

        # ================= STOCK LEDGER SUMMARY (ALL MONTHS / UP TO DATE) =================
        st.markdown("---")
        st.subheader("📦 Material Stock Ledger Summary (All Months / Cumulative Up to Date)")

        mat_desc_col = next(
            (
                c
                for c in [
                    "Description Of material",
                    "Material Name",
                    "Item Description",
                ]
                if c in sup_invoices.columns
            ),
            None,
        )

        if mat_desc_col:
          # మొత్తం sup_invoices (అన్ని నెలలు కలిపి) డేటా ఆధారంగా స్టాక్ లెడ్జర్‌ను లెక్కించడం
          sup_invoices["Is Returned Flag"] = sup_invoices["Return Date"].notnull()

          stock_summary = (
              sup_invoices.groupby(mat_desc_col)
              .agg(
                  Total_Received_Qty=(qty_col, "sum"),
                  Returned_Qty=(
                      qty_col,
                      lambda x: sum(
                          x[sup_invoices.loc[x.index, "Is Returned Flag"]]
                      ),
                  ),
              )
              .reset_index()
          )

          stock_summary["Running Stock At Site"] = (
              stock_summary["Total_Received_Qty"]
              - stock_summary["Returned_Qty"]
          )
          stock_summary.insert(0, "S.No", range(1, len(stock_summary) + 1))

          st.data_editor(
              stock_summary,
              hide_index=True,
              use_container_width=True,
              disabled=True,
              key="akg_stock_ledger_table",
          )
        else:
          st.info("Material description column not found for stock ledger.")

        st.markdown("---")
        st.subheader("💳 Payment Disbursement Log — AKG Shutterings")
        if not sup_payments.empty:
          st.data_editor(
              sup_payments,
              hide_index=True,
              use_container_width=True,
              disabled=True,
              key="akg_pay_table",
          )
        else:
          st.info("No payment transactions recorded for this vendor yet.")
      else:
        st.warning("No records found for 'AKG SHUTTERINGS PRIVATE LIMITED'.")
    else:
      st.error("Supplier column not detected in dataset.")
  else:
    st.info("Please load data records first.")
