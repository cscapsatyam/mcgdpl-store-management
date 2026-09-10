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

      if "akg_std_rates" not in st.session_state:
        st.session_state.akg_std_rates = {}
      if "akg_rent_types" not in st.session_state:
        st.session_state.akg_rent_types = {}
      if "akg_bulk_qtys" not in st.session_state:
        st.session_state.akg_bulk_qtys = {}
      if "akg_bulk_returns" not in st.session_state:
        st.session_state.akg_bulk_returns = {}

      if not sup_invoices.empty:
        possible_qty_cols = ["Qty", "Quantity", "Nos", "Receiving Qty"]
        possible_rate_cols = ["Rate", "Unit Rate", "Rent Rate"]

        qty_col = next(
            (c for c in possible_qty_cols if c in sup_invoices.columns), "Qty"
        )
        rate_col = next(
            (c for c in possible_rate_cols if c in sup_invoices.columns),
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
                if c in sup_invoices.columns
            ),
            None,
        )

        if mat_desc_col:
          for mat_name, std_rate in st.session_state.akg_std_rates.items():
            sup_invoices.loc[
                sup_invoices[mat_desc_col] == mat_name, rate_col
            ] = std_rate
            df.loc[
                (df[sup_col] == target_supplier)
                & (df[mat_desc_col] == mat_name),
                rate_col,
            ] = std_rate

          for mat_name, b_qty in st.session_state.akg_bulk_qtys.items():
            sup_invoices.loc[sup_invoices[mat_desc_col] == mat_name, qty_col] = (
                b_qty
            )
            df.loc[
                (df[sup_col] == target_supplier)
                & (df[mat_desc_col] == mat_name),
                qty_col,
            ] = b_qty

          for mat_name, b_ret in st.session_state.akg_bulk_returns.items():
            sup_invoices.loc[sup_invoices[mat_desc_col] == mat_name, "Return Date"] = (
                b_ret
            )
            df.loc[
                (df[sup_col] == target_supplier)
                & (df[mat_desc_col] == mat_name),
                "Return Date",
            ] = b_ret

        if qty_col not in sup_invoices.columns:
          sup_invoices[qty_col] = 1.0
        if rate_col not in sup_invoices.columns:
          sup_invoices[rate_col] = 0.0

        sup_invoices[qty_col] = pd.to_numeric(
            sup_invoices[qty_col]
            .astype(str)
            .str.replace(r"[^\d.]", "", regex=True),
            errors="coerce",
        ).fillna(0)
        sup_invoices[rate_col] = pd.to_numeric(
            sup_invoices[rate_col]
            .astype(str)
            .str.replace(r"[^\d.]", "", regex=True),
            errors="coerce",
        ).fillna(0)

        if "Actualy Recived Date" in sup_invoices.columns:
          sup_invoices["Actualy Recived Date DT"] = pd.to_datetime(
              sup_invoices["Actualy Recived Date"], errors="coerce"
          )
          sup_invoices["Return Date DT"] = pd.to_datetime(
              sup_invoices["Return Date"], errors="coerce"
          )
          effective_return_dt = sup_invoices["Return Date DT"].fillna(
              pd.to_datetime("today")
          )

          sup_invoices["Total Days"] = (
              effective_return_dt - sup_invoices["Actualy Recived Date DT"]
          ).dt.days
          sup_invoices["Total Days"] = sup_invoices["Total Days"].fillna(1)
          sup_invoices["Total Days"] = sup_invoices["Total Days"].apply(
              lambda x: max(int(x), 1)
          )
          sup_invoices["Calculated Months"] = (
              sup_invoices["Total Days"] / 30.0
          ).round(2)

        def get_rent_basis(row):
          if mat_desc_col and row.get(mat_desc_col) in st.session_state.get(
              "akg_rent_types", {}
          ):
            return st.session_state["akg_rent_types"][row[mat_desc_col]]
          return "Monthly"

        sup_invoices["Rent Basis"] = sup_invoices.apply(get_rent_basis, axis=1)

        def calc_base_rent(row):
          qty = row[qty_col]
          rate = row[rate_col]
          if row["Rent Basis"] == "Day-wise":
            days = row.get("Total Days", 1)
            return round(qty * rate * days, 2)
          else:
            return round(qty * rate, 2)

        sup_invoices["Base Rent Value"] = sup_invoices.apply(
            calc_base_rent, axis=1
        )
        sup_invoices["CGST (9%)"] = (
            sup_invoices["Base Rent Value"] * 0.09
        ).round(2)
        sup_invoices["SGST (9%)"] = (
            sup_invoices["Base Rent Value"] * 0.09
        ).round(2)
        sup_invoices["Total Rent with 18% Tax"] = (
            sup_invoices["Base Rent Value"]
            + sup_invoices["CGST (9%)"]
            + sup_invoices["SGST (9%)"]
        ).round(2)

        if "S.No" in sup_invoices.columns:
          sup_invoices["S.No"] = range(1, len(sup_invoices) + 1)
        else:
          sup_invoices.insert(0, "S.No", range(1, len(sup_invoices) + 1))

        total_inv_amt = sup_invoices["Total Rent with 18% Tax"].sum()

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
            if "S.No" in sup_payments.columns:
              sup_payments["S.No"] = range(1, len(sup_payments) + 1)
            else:
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
            "✏️ Click Here to Manage Material Settings & Payments",
            expanded=False,
        ):
          tab_p1, tab_p2, tab_p3, tab_p4 = st.tabs(
              [
                  "⚙️ Bulk Rate & Basis",
                  "🔄 Update Return & Qty",
                  "✏️ Edit Material Data",
                  "💳 Add Payment",
              ]
          )

          with tab_p1:
            with st.form("akg_bulk_rate_form_v14"):
              st.subheader("Set Rent Rate & Calculation Basis")
              if mat_desc_col:
                unique_materials = list(
                    sup_invoices[mat_desc_col].dropna().unique()
                )
                if unique_materials:
                  selected_mat_1 = st.selectbox(
                      "Select Material Name / Description:",
                      unique_materials,
                      key="bulk_mat_select_1_v14",
                  )

                  default_bulk_rate = float(
                      st.session_state.akg_std_rates.get(selected_mat_1, 0.0)
                  )
                  default_basis = st.session_state.akg_rent_types.get(
                      selected_mat_1, "Monthly"
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

                  submitted_bulk_1 = st.form_submit_button(
                      "Apply Rate & Basis"
                  )
                  if submitted_bulk_1:
                    st.session_state.akg_std_rates[selected_mat_1] = (
                        bulk_rate_val
                    )
                    st.session_state.akg_rent_types[selected_mat_1] = (
                        rent_basis_val
                    )

                    if "Return Date" not in df.columns:
                      df["Return Date"] = None
                    df.loc[
                        (df[sup_col] == target_supplier)
                        & (df[mat_desc_col] == selected_mat_1),
                        rate_col,
                    ] = bulk_rate_val

                    st.session_state.current_df = df
                    st.success(
                        f"Rate & Basis updated for '{selected_mat_1}'"
                        " successfully!"
                    )
                    st.rerun()
                else:
                  st.warning("No materials found.")
              else:
                st.warning("Material description column not available.")

          with tab_p2:
            with st.form("akg_return_qty_form_v14"):
              st.subheader("Update Material Return & Quantity")
              if mat_desc_col:
                unique_materials = list(
                    sup_invoices[mat_desc_col].dropna().unique()
                )
                if unique_materials:
                  selected_mat_2 = st.selectbox(
                      "Select Material Name / Description:",
                      unique_materials,
                      key="bulk_mat_select_2_v14",
                  )

                  mat_rows_check = sup_invoices[
                      sup_invoices[mat_desc_col] == selected_mat_2
                  ]
                  def_qty = (
                      float(mat_rows_check[qty_col].iloc[0])
                      if not mat_rows_check.empty
                      else 1.0
                  )
                  if selected_mat_2 in st.session_state.akg_bulk_qtys:
                    def_qty = st.session_state.akg_bulk_qtys[selected_mat_2]

                  def_ret = (
                      mat_rows_check["Return Date"].iloc[0]
                      if not mat_rows_check.empty
                      else None
                  )
                  if selected_mat_2 in st.session_state.akg_bulk_returns:
                    def_ret = st.session_state.akg_bulk_returns[selected_mat_2]

                  default_date = (
                      pd.to_datetime(def_ret).date()
                      if pd.notnull(def_ret)
                      else datetime.date.today()
                  )

                  col_r1, col_r2 = st.columns(2)
                  with col_r1:
                    bulk_qty_val = st.number_input(
                        "Quantity Returned for this Material",
                        value=def_qty,
                        min_value=0.0,
                        format="%.2f",
                    )
                  with col_r2:
                    bulk_return_date = st.date_input(
                        "Material Return Date", value=default_date
                    )

                  submitted_bulk_2 = st.form_submit_button(
                      "Save Return Details"
                  )
                  if submitted_bulk_2:
                    final_ret_val = str(bulk_return_date)

                    st.session_state.akg_bulk_qtys[selected_mat_2] = (
                        bulk_qty_val
                    )
                    st.session_state.akg_bulk_returns[selected_mat_2] = (
                        final_ret_val
                    )

                    if "Return Date" not in df.columns:
                      df["Return Date"] = None

                    df.loc[
                        (df[sup_col] == target_supplier)
                        & (df[mat_desc_col] == selected_mat_2),
                        qty_col,
                    ] = bulk_qty_val
                    df.loc[
                        (df[sup_col] == target_supplier)
                        & (df[mat_desc_col] == selected_mat_2),
                        "Return Date",
                    ] = final_ret_val

                    st.session_state.current_df = df
                    st.success(
                        f"Return details updated for '{selected_mat_2}'"
                        " successfully!"
                    )
                    st.rerun()
                else:
                  st.warning("No materials found.")
              else:
                st.warning("Material description column not available.")

          with tab_p3:
            st.subheader("Modify Specific Material Records")
            editable_df = sup_invoices[
                [
                    "Store Entry No",
                    "Actualy Recived Date",
                    "Return Date",
                    mat_desc_col,
                    qty_col,
                    rate_col,
                ]
            ].copy()
            editable_df["Original_Index"] = sup_invoices.index

            edited_result_df = st.data_editor(
                editable_df,
                hide_index=True,
                use_container_width=True,
                key="specific_material_data_editor_v14",
            )

            if st.button("Save Modifications", key="save_mod_btn_v14"):
              for idx, row in edited_result_df.iterrows():
                orig_idx = row["Original_Index"]
                df.loc[orig_idx, qty_col] = row[qty_col]
                df.loc[orig_idx, rate_col] = row[rate_col]
                df.loc[orig_idx, "Return Date"] = row["Return Date"]

              st.session_state.current_df = df.copy()
              st.success("Modifications saved successfully!")
              st.rerun()

          with tab_p4:
            with st.form("akg_payment_form_v14"):
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
        st.subheader("📑 Month-wise & Material-wise Breakdown Report")

        if (
            "Actualy Recived Date" in sup_invoices.columns
            and mat_desc_col
            and not sup_invoices.empty
        ):
          months_list = [
              "January",
              "February",
              "March",
              "April",
              "May",
              "June",
              "July",
              "August",
              "September",
              "October",
              "November",
              "December",
          ]
          years_list = [2024, 2025, 2026, 2027, 2028]

          col_m_sel, col_y_sel = st.columns(2)
          with col_m_sel:
            current_month_name = datetime.datetime.now().strftime("%B")
            default_m_idx = (
                months_list.index(current_month_name)
                if current_month_name in months_list
                else 0
            )
            selected_month_name = st.selectbox(
                "📂 Select Month:",
                months_list,
                index=default_m_idx,
                key="akg_dropdown_month_v14",
            )
          with col_y_sel:
            current_year = datetime.datetime.now().year
            default_y_idx = (
                years_list.index(current_year)
                if current_year in years_list
                else 2
            )
            selected_year_val = st.selectbox(
                "📅 Select Year:",
                years_list,
                index=default_y_idx,
                key="akg_dropdown_year_v14",
            )

          selected_dropdown_month = f"{selected_month_name} {selected_year_val}"
          st.markdown(
              f"### Material-wise Active Rent for **{selected_dropdown_month}**"
          )

          sel_m_dt = pd.to_datetime(selected_dropdown_month, format="%B %Y")
          month_start = sel_m_dt
          month_end = (
              sel_m_dt + pd.offsets.MonthEnd(1)
          ).normalize()  # Last day of selected month

          active_rows = []
          for idx, row in sup_invoices.iterrows():
            r_dt = pd.to_datetime(
                row["Actualy Recived Date"], errors="coerce"
            ).normalize()
            ret_dt = (
                pd.to_datetime(row["Return Date"], errors="coerce").normalize()
                if pd.notnull(row["Return Date"])
                else pd.Timestamp("today").normalize()
            )

            if pd.notnull(r_dt):
              # Check if item is active during this specific month
              if r_dt <= month_end and ret_dt >= month_start:
                # Calculate active overlap days specifically for this selected month
                effective_start = max(r_dt, month_start)
                effective_end = min(ret_dt, month_end)
                days_in_month = (
                    (effective_end - effective_start).days + 1
                )  # Inclusive of start/end day

                qty = row[qty_col]
                rate = row[rate_col]
                basis = row["Rent Basis"]

                if basis == "Day-wise":
                  month_base_rent = round(qty * rate * max(days_in_month, 0), 2)
                else:
                  # Fixed monthly rent if active at any point during this month
                  month_base_rent = round(qty * rate, 2)

                row_copy = row.copy()
                row_copy["Month_Base_Rent"] = month_base_rent
                row_copy["Month_Tax_18"] = round(month_base_rent * 1.18, 2)
                active_rows.append(row_copy)

          if active_rows:
            month_sub_df = pd.DataFrame(active_rows)
            material_report = (
                month_sub_df.groupby(mat_desc_col)
                .agg(
                    Base_Rate=(rate_col, "first"),
                    Total_Qty=(qty_col, "sum"),
                    Base_Rent_Value=("Month_Base_Rent", "sum"),
                    Total_Tax_18=("Month_Tax_18", "sum"),
                )
                .reset_index()
            )

            material_report["Base_Rate"] = material_report["Base_Rate"].round(2)
            material_report["Base_Rent_Value"] = material_report[
                "Base_Rent_Value"
            ].round(2)
            material_report["Total_Tax_18"] = material_report[
                "Total_Tax_18"
            ].round(2)

            if "S.No" in material_report.columns:
              material_report["S.No"] = range(1, len(material_report) + 1)
            else:
              material_report.insert(
                  0, "S.No", range(1, len(material_report) + 1)
              )

            st.dataframe(
                material_report,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "S.No": st.column_config.NumberColumn("S.No", width="small"),
                    mat_desc_col: st.column_config.TextColumn(
                        "Material Description", width="large"
                    ),
                    "Base_Rate": st.column_config.NumberColumn(
                        "Base Rate (₹)", format="₹ %.2f", width="medium"
                    ),
                    "Total_Qty": st.column_config.NumberColumn(
                        "Total Qty", width="small"
                    ),
                    "Base_Rent_Value": st.column_config.NumberColumn(
                        "Base Rent (₹)", format="₹ %.2f", width="medium"
                    ),
                    "Total_Tax_18": st.column_config.NumberColumn(
                        "Total + 18% Tax (₹)",
                        format="₹ %.2f",
                        width="medium",
                    ),
                },
                key="mat_report_active_table_v14",
            )

            total_month_base_rent = material_report["Base_Rent_Value"].sum()
            total_month_tax_rent = material_report["Total_Tax_18"].sum()

            st.markdown(
                f"**📊 Total Rent Breakdown for {selected_dropdown_month}:**"
            )
            col_tot1, col_tot2 = st.columns(2)
            col_tot1.metric(
                "Total Base Rent (Without Tax)",
                f"₹ {total_month_base_rent:,.2f}",
            )
            col_tot2.metric(
                "Total Rent Value (With 18% Tax)",
                f"₹ {total_month_tax_rent:,.2f}",
            )

          else:
            st.info(
                f"No active materials found for {selected_dropdown_month}."
            )
        else:
          st.info("Insufficient data available.")

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
        existing_cols = [c for c in desired_cols if c and c in sup_invoices.columns]
        other_cols = [c for c in sup_invoices.columns if c not in existing_cols]
        ordered_sup_invoices = sup_invoices[existing_cols + other_cols]

        st.dataframe(
            ordered_sup_invoices,
            hide_index=True,
            use_container_width=True,
            key="akg_inv_table_v14",
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

          if "S.No" in stock_summary.columns:
            stock_summary["S.No"] = range(1, len(stock_summary) + 1)
          else:
            stock_summary.insert(0, "S.No", range(1, len(stock_summary) + 1))

          st.dataframe(
              stock_summary,
              hide_index=True,
              use_container_width=True,
              key="akg_stock_ledger_table_v14",
          )
        else:
          st.info("Material description column not found for stock ledger.")

        st.markdown("---")
        st.subheader("💳 Payment Disbursement Log — AKG Shutterings")
        if not sup_payments.empty:
          st.dataframe(
              sup_payments,
              hide_index=True,
              use_container_width=True,
              key="akg_pay_table_v14",
          )
        else:
          st.info("No payment transactions recorded for this vendor yet.")
      else:
        st.warning("No records found for 'AKG SHUTTERINGS PRIVATE LIMITED'.")
    else:
      st.error("Supplier column not detected in dataset.")
  else:
    st.info("Please load data records first from the main upload page.")
