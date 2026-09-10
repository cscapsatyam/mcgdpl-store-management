import datetime
import pandas as pd
import streamlit as st


def run():
  st.title("📑 AKG SHUTTERINGS PRIVATE LIMITED - Rental, Stock Ledger & Tax")
  st.markdown(
      "Exclusive statement breakdown including Store Entry, Return Dates,"
      " Monthly/Day-wise Rent, Stock Ledger, and 18% Tax Calculation."
  )

  if "current_df" in st.session_state and not st.session_state.current_df.empty:
    df = st.session_state.current_df.copy()
    sup_col = "Supplier / Sendor Name"

    if sup_col in df.columns:
      target_supplier = "AKG SHUTTERINGS PRIVATE LIMITED"
      sup_invoices = (
          df[df[sup_col] == target_supplier].copy().reset_index(drop=True)
      )

      if "Return Date" not in sup_invoices.columns:
        sup_invoices["Return Date"] = None
      if "Return Date" not in df.columns:
        df["Return Date"] = None

      # Session state for standard/bulk material rates and rent types
      if "akg_std_rates" not in st.session_state:
        st.session_state.akg_std_rates = {}
      if "akg_rent_types" not in st.session_state:
        st.session_state.akg_rent_types = {}

      if not sup_invoices.empty:
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
              m
              for m in sup_invoices["Month_Year"].dropna().unique()
              if pd.notnull(m)
          ]

          col_f1, _ = st.columns([2, 4])
          with col_f1:
            selected_month = st.selectbox(
                "📅 Filter by Month & Year (Rent Table Only):",
                months_list,
                key="akg_month_filter",
            )

          filtered_sup_invoices = sup_invoices.copy()
          if selected_month != "All Months":
            filtered_sup_invoices = filtered_sup_invoices[
                filtered_sup_invoices["Month_Year"] == selected_month
            ]
        else:
          filtered_sup_invoices = sup_invoices.copy()

        possible_qty_cols = ["Qty", "Quantity", "Nos", "Receiving Qty"]
        possible_rate_cols = ["Rate", "Unit Rate", "Rent Rate"]

        qty_col = next(
            (
                c
                for c in possible_qty_cols
                if c in filtered_sup_invoices.columns
            ),
            "Qty",
        )
        rate_col = next(
            (
                c
                for c in possible_rate_cols
                if c in filtered_sup_invoices.columns
            ),
            "Rate",
        )
        mat_desc_col = next(
            (
                c
                for c in [
                    "Description Of material",
                    "Material Name",
                    "Item Description",
                ]
                if c in filtered_sup_invoices.columns
            ),
            None,
        )

        # Apply Standard/Bulk rates if set
        if mat_desc_col and st.session_state.akg_std_rates:
          for mat_name, std_rate in st.session_state.akg_std_rates.items():
            filtered_sup_invoices.loc[
                filtered_sup_invoices[mat_desc_col] == mat_name, rate_col
            ] = std_rate
            sup_invoices.loc[sup_invoices[mat_desc_col] == mat_name, rate_col] = (
                std_rate
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

        if "Actualy Recived Date" in filtered_sup_invoices.columns:
          filtered_sup_invoices["Actualy Recived Date DT"] = pd.to_datetime(
              filtered_sup_invoices["Actualy Recived Date"], errors="coerce"
          )
          filtered_sup_invoices["Return Date DT"] = pd.to_datetime(
              filtered_sup_invoices["Return Date"], errors="coerce"
          )
          effective_return_dt = filtered_sup_invoices["Return Date DT"].fillna(
              pd.to_datetime("today")
          )

          filtered_sup_invoices["Total Days"] = (
              effective_return_dt
              - filtered_sup_invoices["Actualy Recived Date DT"]
          ).dt.days
          filtered_sup_invoices["Total Days"] = filtered_sup_invoices[
              "Total Days"
          ].fillna(1)
          filtered_sup_invoices["Total Days"] = filtered_sup_invoices[
              "Total Days"
          ].apply(lambda x: max(int(x), 1))

          filtered_sup_invoices["Calculated Months"] = (
              filtered_sup_invoices["Total Days"] / 30.0
          ).round(2)

        # Assign Rent Type Column (Monthly vs Day-wise)
        def get_rent_basis(row):
          if mat_desc_col and row.get(mat_desc_col) in st.session_state.get(
              "akg_rent_types", {}
          ):
            return st.session_state["akg_rent_types"][row[mat_desc_col]]
          return "Monthly"  # Default

        filtered_sup_invoices["Rent Basis"] = filtered_sup_invoices.apply(
            get_rent_basis, axis=1
        )

        # Calculate Base Rent Value based on Basis (Monthly or Day-wise)
        def calc_base_rent(row):
          qty = row[qty_col]
          rate = row[rate_col]
          if row["Rent Basis"] == "Day-wise":
            return round(qty * rate * row["Total Days"], 2)
          else:
            return round(qty * rate * row["Calculated Months"], 2)

        filtered_sup_invoices["Base Rent Value"] = filtered_sup_invoices.apply(
            calc_base_rent, axis=1
        )
        filtered_sup_invoices["CGST (9%)"] = (
            filtered_sup_invoices["Base Rent Value"] * 0.09
        ).round(2)
        filtered_sup_invoices["SGST (9%)"] = (
            filtered_sup_invoices["Base Rent Value"] * 0.09
        ).round(2)
        filtered_sup_invoices["Total Rent with 18% Tax"] = (
            filtered_sup_invoices["Base Rent Value"]
            + filtered_sup_invoices["CGST (9%)"]
            + filtered_sup_invoices["SGST (9%)"]
        ).round(2)

        if "S.No" in filtered_sup_invoices.columns:
          filtered_sup_invoices["S.No"] = range(
              1, len(filtered_sup_invoices) + 1
          )
        else:
          filtered_sup_invoices.insert(
              0, "S.No", range(1, len(filtered_sup_invoices) + 1)
          )

        if qty_col in sup_invoices.columns:
          sup_invoices[qty_col] = pd.to_numeric(
              sup_invoices[qty_col]
              .astype(str)
              .str.replace(r"[^\d.]", "", regex=True),
              errors="coerce",
          ).fillna(0)
        else:
          sup_invoices[qty_col] = 0.0

        full_calc_df = sup_invoices.copy()
        if "Actualy Recived Date" in full_calc_df.columns:
          full_calc_df["Actualy Recived Date DT"] = pd.to_datetime(
              full_calc_df["Actualy Recived Date"], errors="coerce"
          )
          full_calc_df["Return Date DT"] = pd.to_datetime(
              full_calc_df["Return Date"], errors="coerce"
          )
          eff_ret = full_calc_df["Return Date DT"].fillna(
              pd.to_datetime("today")
          )
          full_calc_df["Total Days"] = (
              eff_ret - full_calc_df["Actualy Recived Date DT"]
          ).dt.days.apply(lambda x: max(int(x), 1))
          full_calc_df["Calculated Months"] = (
              full_calc_df["Total Days"] / 30.0
          ).round(2)
        else:
          full_calc_df["Calculated Months"] = 1.0

        if rate_col in full_calc_df.columns:
          full_calc_df[rate_col] = pd.to_numeric(
              full_calc_df[rate_col]
              .astype(str)
              .str.replace(r"[^\d.]", "", regex=True),
              errors="coerce",
          ).fillna(0)
        else:
          full_calc_df[rate_col] = 0.0

        full_calc_df["Rent Basis"] = full_calc_df.apply(get_rent_basis, axis=1)
        full_calc_df["Base Rent Value"] = full_calc_df.apply(
            lambda r: (
                round(r[qty_col] * r[rate_col] * r["Total Days"], 2)
                if r["Rent Basis"] == "Day-wise"
                else round(r[qty_col] * r[rate_col] * r["Calculated Months"], 2)
            ),
            axis=1,
        )
        full_calc_df["Total Rent with 18% Tax"] = (
            full_calc_df["Base Rent Value"] * 1.18
        ).round(2)

        total_inv_amt = full_calc_df["Total Rent with 18% Tax"].sum()

        if (
            "payments_df" in st.session_state
            and not st.session_state.payments_df.empty
        ):
          sup_payments = (
              st.session_state.payments_df[
                  st.session_state.payments_df["Supplier Name"]
                  == target_supplier
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

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric(
            "📦 Total Rent Value (inc. 18% Tax)", f"₹ {total_inv_amt:,.2f}"
        )
        col_m2.metric("💳 Total Paid Value", f"₹ {total_paid_amt:,.2f}")
        col_m3.metric("⚠️ Net Outstanding Balance", f"₹ {net_outstanding:,.2f}")

        st.markdown("---")

        with st.expander(
            "✏️ Click Here to Update Return Date, Qty & Rates / Set Bulk"
            " Material Rate & Rent Basis / Add Payment",
            expanded=False,
        ):
          tab_p1, tab_p2, tab_p3 = st.tabs(
              [
                  "📦 Update Single Entry",
                  "⚙️ Bulk Material Rate & Rent Basis",
                  "💳 Add Payment",
              ]
          )

          with tab_p1:
            with st.form("akg_rent_form"):
              st.subheader("Update Individual Store Entry Return Date, Qty & Rate")
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
                      "Rent Rate (₹)",
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
            with st.form("akg_bulk_rate_form"):
              st.subheader("Set Rate and Rent Basis (Monthly / Day-wise)")
              if mat_desc_col:
                unique_materials = list(
                    sup_invoices[mat_desc_col].dropna().unique()
                )
                if unique_materials:
                  selected_mat = st.selectbox(
                      "Select Material Name / Description:", unique_materials
                  )
                  default_bulk_rate = float(
                      st.session_state.akg_std_rates.get(selected_mat, 0.0)
                  )
                  default_basis = st.session_state.akg_rent_types.get(
                      selected_mat, "Monthly"
                  )

                  col_b1, col_b2 = st.columns(2)
                  with col_b1:
                    bulk_rate_val = st.number_input(
                        "Rent Rate for this Material (₹)",
                        value=default_bulk_rate,
                        min_value=0.0,
                        format="%.2f",
                    )
                  with col_b2:
                    rent_basis_val = st.selectbox(
                        "Rent Calculation Basis:",
                        ["Monthly", "Day-wise"],
                        index=(
                            0
                            if default_basis == "Monthly"
                            else (1 if default_basis == "Day-wise" else 0)
                        ),
                    )

                  submitted_bulk = st.form_submit_button(
                      "Apply Rate & Basis to All Entries of this Material"
                  )
                  if submitted_bulk:
                    st.session_state.akg_std_rates[selected_mat] = bulk_rate_val
                    st.session_state.akg_rent_types[selected_mat] = (
                        rent_basis_val
                    )
                    st.success(
                        f"Updated '{selected_mat}' -> Rate: ₹{bulk_rate_val},"
                        f" Basis: {rent_basis_val} successfully!"
                    )
                    st.rerun()
                else:
                  st.warning("No materials found.")
              else:
                st.warning("Material description column not available.")

          with tab_p3:
            with st.form("akg_payment_form"):
              st.subheader("Add Payment Entry")
              st.text_input(
                  "Vendor Name", value=target_supplier, disabled=True
              )
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
        st.subheader("📦 AKG Shutterings Material Receiving Status")

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
            "Rent Basis",
            "Total Days",
            "Calculated Months",
            "Base Rent Value",
            "CGST (9%)",
            "SGST (9%)",
            "Total Rent with 18% Tax",
        ]
        existing_cols = [
            c
            for c in desired_cols
            if c and c in filtered_sup_invoices.columns
        ]
        other_cols = [
            c for c in filtered_sup_invoices.columns if c not in existing_cols
        ]
        ordered_sup_invoices = filtered_sup_invoices[
            existing_cols + other_cols
        ]

        st.data_editor(
            ordered_sup_invoices,
            hide_index=True,
            use_container_width=True,
            disabled=True,
            key="akg_inv_table",
        )

        st.markdown("---")
        st.subheader(
            "📦 Material Stock Ledger Summary (All Months / Cumulative Up to"
            " Date)"
        )

        if mat_desc_col:
          sup_invoices["Is Returned Flag"] = (
              sup_invoices["Return Date"].notnull()
          )

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
    st.info("Please load data records first from the main upload page.")
