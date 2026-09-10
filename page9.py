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

          # Tab 1: Bulk Rate & Rent Basis
          with tab_p1:
            with st.form("akg_bulk_rate_form"):
              st.subheader("Set Rent Rate & Calculation Basis")
              if mat_desc_col:
                unique_materials = list(
                    sup_invoices[mat_desc_col].dropna().unique()
                )
                if unique_materials:
                  selected_mat_1 = st.selectbox(
                      "Select Material Name / Description:",
                      unique_materials,
                      key="bulk_mat_select_1",
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

          # Tab 2: Update Return Date & Qty
          with tab_p2:
            with st.form("akg_return_qty_form"):
              st.subheader("Update Material Return & Quantity")
              if mat_desc_col:
                unique_materials = list(
                    sup_invoices[mat_desc_col].dropna().unique()
                )
                if unique_materials:
                  selected_mat_2 = st.selectbox(
                      "Select Material Name / Description:",
                      unique_materials,
                      key="bulk_mat_select_2",
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

          # Tab 3: Edit Specific Material Data (New Modification Tab)
          with tab_p3:
            st.subheader("Modify Specific Material Records")
            st.markdown(
                "ఇక్కడ మీరు నేరుగా టేబుల్‌లో ఉన్న డేటాను ఎడిట్ చేసుకోవచ్చు"
                " (సవరించవచ్చు)."
            )

            # ఎడిట్ చేయడానికి వీలుగా ఒక కాపీ టేబుల్ చూపించడం
            editable_df = filtered_sup_invoices[
                [
                    "Store Entry No",
                    "Actualy Recived Date",
                    "Return Date",
                    mat_desc_col,
                    qty_col,
                    rate_col,
                ]
            ].copy()

            edited_result_df = st.data_editor(
                editable_df,
                hide_index=True,
                use_container_width=True,
                key="specific_material_data_editor",
            )

            if st.button("Save Modifications"):
              # యూజర్ మార్చిన మార్పులను మెయిన్ డేటాఫ్రేమ్‌కు అప్లై చేయడం
              for idx, row in edited_result_df.iterrows():
                original_index = filtered_sup_invoices.index[idx]
                # మెయిన్ df లో అప్‌డేట్ చేయడం
                df.loc[
                    df.index == original_index, qty_col
                ] = row[qty_col]
                df.loc[
                    df.index == original_index, rate_col
                ] = row[rate_col]
                df.loc[
                    df.index == original_index, "Return Date"
                ] = row["Return Date"]

              st.session_state.current_df = df
              st.success("మార్పులు విజయవంతంగా సేవ్ చేయబడ్డాయి!")
              st.rerun()

          # Tab 4: Add Payment
          with tab_p4:
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
