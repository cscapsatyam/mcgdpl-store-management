import os
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Enterprise Store Management System", layout="wide"
)

# Custom ERP Styling with Sticky Headers & Clean Layout
st.markdown(
    """
    <style>
    .main {
        background-color: #f4f6f9;
    }
    
    /* Streamlit డిఫాల్ట్ హెడర్‌ని స్టికీగా మరియు టాప్‌లో ఫిక్స్‌డ్‌గా ఉంచడానికి */
    header[data-testid="stHeader"] {
        background-color: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(5px);
        z-index: 999;
    }

    /* మెయిన్ పేజీ టైటిల్స్ కదలకుండా ఒకే చోట ఫిక్స్‌డ్‌గా ఉండేలా (Sticky Headers) */
    h1, h2, h3 {
        position: sticky;
        top: 0rem;
        background-color: #f4f6f9;
        z-index: 99;
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
    }

    /* ERP స్టైల్ బటన్లు */
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
    </style>
    """,
    unsafe_allow_html=True,
)

# --- FILE PATHS FOR PERSISTENCE ---
PAYMENTS_FILE = "vendor_payments.csv"

# Initialize Session States
if "payments_df" not in st.session_state:
  if os.path.exists(PAYMENTS_FILE):
    try:
      st.session_state.payments_df = pd.read_csv(PAYMENTS_FILE)
    except Exception:
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

if "current_df" not in st.session_state:
  st.session_state.current_df = pd.DataFrame()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🏢 Enterprise ERP Navigation")
page = st.sidebar.selectbox(
    "Select Module:",
    [
        "1. Data Upload & Hub",
        "2. Inventory Dashboard",
        "3. Material Summary",
        "4. Store Operations",
        "5. Supplier Analytics",
        "6. Export & Reports",
        "7. Vendor Payments Entry",
    ],
)

st.sidebar.markdown("---")
st.sidebar.info("System Status: 🟢 Online (ERP Active)")


# ================= PAGE 1: DATA UPLOAD & HUB =================
if page == "1. Data Upload & Hub":
  st.title("📂 Enterprise Data Ingestion Hub")
  st.markdown(
      "Upload your master Excel or CSV files to synchronize inventory and"
      " financial records."
  )

  uploaded_file = st.file_uploader(
      "Choose an Excel or CSV file", type=["xlsx", "csv"]
  )

  if uploaded_file is not None:
    try:
      if uploaded_file.name.endswith(".csv"):
        st.session_state.current_df = pd.read_csv(uploaded_file)
      else:
        st.session_state.current_df = pd.read_excel(uploaded_file)

      st.success("File successfully uploaded and loaded into ERP memory!")
    except Exception as e:
      st.error(f"Error loading file: {e}")

  if not st.session_state.current_df.empty:
    st.markdown("### 📊 Preview Loaded Dataset")
    with st.container(height=400):
      st.dataframe(
          st.session_state.current_df, use_container_width=True, hide_index=True
      )
  else:
    st.info(
        "No dataset loaded yet. Please upload a file to begin operations."
    )


# ================= PAGE 2: INVENTORY DASHBOARD =================
elif page == "2. Inventory Dashboard":
  st.title("📈 Inventory Performance Dashboard")
  st.markdown(
      "High-level metrics and stock distribution across active store segments."
  )

  if not st.session_state.current_df.empty:
    df = st.session_state.current_df.copy()
    st.metric("Total Records Loaded", len(df))
    with st.container(height=450):
      st.dataframe(df, use_container_width=True, hide_index=True)
  else:
    st.warning("Please upload data in Module 1 first.")


# ================= PAGE 3: MATERIAL SUMMARY =================
elif page == "3. Material Summary":
  st.title("📦 Material Master Summary")
  st.markdown("Consolidated material stock levels and pricing reports.")

  if not st.session_state.current_df.empty:
    with st.container(height=450):
      st.dataframe(
          st.session_state.current_df, use_container_width=True, hide_index=True
      )
  else:
    st.info("No data available.")


# ================= PAGE 4: STORE OPERATIONS =================
elif page == "4. Store Operations":
  st.title("🏭 Store Operations & Logs")
  st.markdown("Daily inwards, outwards, and site movement registers.")

  if not st.session_state.current_df.empty:
    with st.container(height=450):
      st.dataframe(
          st.session_state.current_df, use_container_width=True, hide_index=True
      )
  else:
    st.info("No operational data loaded.")


# ================= PAGE 5: SUPPLIER ANALYTICS =================
elif page == "5. Supplier Analytics":
  st.title("📊 Supplier Performance & Ledger Analytics")
  st.markdown("Analyze supplier fulfillment rates, values, and standing.")

  if not st.session_state.current_df.empty:
    with st.container(height=450):
      st.dataframe(
          st.session_state.current_df, use_container_width=True, hide_index=True
      )
  else:
    st.info("Please load dataset first.")


# ================= PAGE 6: EXPORT & REPORTS =================
elif page == "6. Export & Reports":
  st.title("📑 Enterprise Reporting & Export Center")
  st.markdown("Download formatted statements and financial summaries.")

  if not st.session_state.current_df.empty:
    st.success("Data ready for export generation.")
  else:
    st.info("No data available for export.")


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

      # --- TWO ACTION BUTTONS FOR POP-UPS ---
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

      # 2. VENDOR STATEMENT & LEDGER REPORT POPUP BUTTON
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

            # --- INVOICE-WISE CONSOLIDATED VIEW ---
            sup_invoices_raw = df[df[sup_col] == selected_summary_sup].copy()

            if inv_col in sup_invoices_raw.columns:
              optional_cols = [
                  "Store Entry No",
                  "Invoice Date",
                  "GRN No",
                  "GRN Date",
                  "Vechile Number",
                  "Type Reciept",
              ]
              available_extra = [
                  c for c in optional_cols if c in sup_invoices_raw.columns
              ]
              group_cols = [inv_col] + available_extra

              sup_invoices = (
                  sup_invoices_raw.groupby(group_cols)[val_col]
                  .sum()
                  .reset_index()
                  .rename(columns={val_col: "Total Invoice Value"})
              )
            else:
              sup_invoices = sup_invoices_raw

            sup_invoices = sup_invoices.reset_index(drop=True)
            sup_invoices.insert(0, "S.No", range(1, len(sup_invoices + 1)))

            st.markdown(f"### 📂 Invoice-Wise Summary")
            with st.container(height=350):
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
              with st.container(height=250):
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
