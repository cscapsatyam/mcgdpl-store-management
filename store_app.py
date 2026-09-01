import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Store Management System", layout="wide")

# Initialize Session State variables
if "current_df" not in st.session_state:
  st.session_state.current_df = pd.DataFrame()
if "payments_df" not in st.session_state:
  st.session_state.payments_df = pd.DataFrame(
      columns=[
          "Supplier Name",
          "Payment Date",
          "Reference No",
          "Paid Amount",
          "Remarks",
      ]
  )

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
        "7. Vendor Payments Entry",
        "8. Vendor Outstanding Detailed Report",  # కొత్తగా యాడ్ చేసిన ప్రత్యేక పేజీ
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

        st.data_editor(
            summary_df, hide_index=True, use_container_width=True, disabled=True
        )
      else:
        st.warning("⚠️ ఎక్సెల్ ఫైల్‌లో వాల్యూ కాలమ్ కనుగొనబడలేదు.")
    else:
      st.error("ఎక్సెల్ ఫైల్‌లో 'Supplier / Sendor Name' లేదా 'Invoice No' కాలమ్స్ లేవు.")
  else:
    st.info("దయచేసి ముందుగా డాటా లోడ్ చేయండి.")

# ================= PAGE 7: VENDOR PAYMENTS ENTRY =================
elif page == "7. Vendor Payments Entry":
  st.title("💳 HO Payments Entry & Summary")

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

      st.subheader("➕ HO నుండి చేసిన పేమెంట్ వివరాలను నమోదు చేయండి:")
      suppliers_unique = list(df[sup_col].dropna().unique())

      with st.form("payment_form"):
        col_p1, col_p2 = st.columns(2)
        p_supplier = col_p1.selectbox("సప్లయర్ పేరు ఎంచుకోండి:", suppliers_unique)
        p_date = col_p2.date_input("పేమెంట్ తేదీ:")

        col_p3, col_p4 = st.columns(2)
        p_ref = col_p3.text_input("రెఫరెన్స్ నంబర్ (UTR / Cheque No):")
        p_amount = col_p4.number_input(
            "చెల్లించిన మొత్తం (Paid Amount):", min_value=0.0, step=100.0
        )
        p_remarks = st.text_input("గమనికలు (Remarks / Notes):")

        submitted = st.form_submit_button("పేమెంట్ సేవ్ చేయండి")
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
          st.success(
              f"✅ {p_supplier} గారికి చేసిన రూ. {p_amount} పేమెంట్ విజయవంతంగా"
              " సేవ్ చేయబడింది!"
          )

      st.markdown("---")
      st.subheader("📋 సప్లయర్ వారీగా అవుట్‌స్టాండింగ్ సమ్మరీ:")

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

      st.data_editor(
          outstanding_df,
          hide_index=True,
          use_container_width=True,
          disabled=True,
      )

      if not st.session_state.payments_df.empty:
        st.markdown("---")
        st.subheader("📜 చేసిన అన్ని పేమెంట్స్ చరిత్ర (Payment History):")
        st.data_editor(
            st.session_state.payments_df,
            hide_index=True,
            use_container_width=True,
            disabled=True,
        )
    else:
      st.error("ఎక్సెల్ ఫైల్‌లో సప్లయర్ లేదా అమౌంట్ కాలమ్ కనుగొనబడలేదు.")
  else:
    st.info("దయచేసి ముందుగా డాటా లోడ్ చేయండి.")

# ================= PAGE 8: VENDOR OUTSTANDING DETAILED REPORT =================
elif page == "8. Vendor Outstanding Detailed Report":
  st.title("📑 Vendor Outstanding Detailed Ledger & Report")

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
          "🔍 ఏ సప్లయర్ యొక్క పూర్తి అవుట్‌స్టాండింగ్ వివరాలు కావాలో ఎంచుకోండి:",
          suppliers_list,
          key="det_sup_select",
      )

      st.markdown("---")

      # సెలెక్ట్ చేసిన సప్లయర్ ఇన్వాయిస్ వివరాలు
      sup_invoices = df[df[sup_col] == selected_supplier_det].copy()
      total_inv_amt = sup_invoices[val_col].sum()

      # సెలెక్ట్ చేసిన సప్లయర్ పేమెంట్స్ వివరాలు
      if not st.session_state.payments_df.empty:
        sup_payments = st.session_state.payments_df[
            st.session_state.payments_df["Supplier Name"] == selected_supplier_det
        ].copy()
        total_paid_amt = sup_payments["Paid Amount"].sum()
      else:
        sup_payments = pd.DataFrame()
        total_paid_amt = 0.0

      net_outstanding = total_inv_amt - total_paid_amt

      # మెట్రిక్స్ కార్డ్స్ డిస్ప్లే
      col_m1, col_m2, col_m3 = st.columns(3)
      col_m1.metric("📦 మొత్తం ఇన్వాయిస్ విలువ (Total Invoices)", f"₹ {total_inv_amt:,.2f}")
      col_m2.metric("💳 చెల్లించిన మొత్తం (Total Paid)", f"₹ {total_paid_amt:,.2f}")
      col_m3.metric("⚠️ బాకీ ఉండవలసిన మొత్తం (Outstanding)", f"₹ {net_outstanding:,.2f}")

      st.markdown("---")

      # ప్రింట్ / PDF ఆప్షన్ కోసం బటన్
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

      st.subheader(f"📂 {selected_supplier_det} - ఇన్వాయిస్ వివరాలు:")
      st.data_editor(
          sup_invoices,
          hide_index=True,
          use_container_width=True,
          disabled=True,
          key="det_inv_table",
      )

      st.markdown("---")
      st.subheader(f"💳 {selected_supplier_det} - జరిపిన పేమెంట్స్ చరిత్ర:")
      if not sup_payments.empty:
        st.data_editor(
            sup_payments,
            hide_index=True,
            use_container_width=True,
            disabled=True,
            key="det_pay_table",
        )
      else:
        st.info("ఈ సప్లయర్‌కి ఇప్పటివరకు ఎటువంటి పేమెంట్స్ ఎంట్రీ చేయలేదు.")

    else:
      st.error("ఎక్సెల్ ఫైల్‌లో సప్లయర్ లేదా అమౌంట్ కాలమ్ కనుగొనబడలేదు.")
  else:
    st.info("దయచేసి ముందుగా డాటా లోడ్ చేయండి.")
