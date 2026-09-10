st.markdown("---")
        st.subheader("📅 Month-wise Rental & Invoice Breakdown Report")

        # నెలవారీగా రెంట్ లెక్కించే లాజిక్
        if "Actualy Recived Date DT" in filtered_sup_invoices.columns:
          # ఏ నెలకి ఆ నెల రెంట్ లెక్కించడానికి మంత్ కాలమ్ ఉపయోగించడం
          filtered_sup_invoices["Billing Month"] = pd.to_datetime(
              filtered_sup_invoices["Actualy Recived Date"], errors="coerce"
          ).dt.strftime("%B %Y")

          # నెలవారీ సమ్మరీ గ్రూపింగ్
          monthly_report = (
              filtered_sup_invoices.groupby("Billing Month")
              .agg(
                  Total_Items=("Description Of material", "count"),
                  Total_Base_Rent=("Base Rent Value", "sum"),
                  Total_Tax_18=("Total Rent with 18% Tax", "sum"),
              )
              .reset_index()
          )

          # అమౌంట్‌లను రౌండ్ ఆఫ్ చేయడం
          monthly_report["Total_Base_Rent"] = monthly_report[
              "Total_Base_Rent"
          ].round(2)
          monthly_report["Total_Tax_18"] = monthly_report[
              "Total_Tax_18"
          ].round(2)

          st.dataframe(monthly_report, use_container_width=True, hide_index=True)
        else:
          st.info("సరిపడా డేటా అందుబాటులో లేదు.")

        st.markdown("---")
        st.subheader("📦 AKG Shutterings Material Receiving Status")

        # (ఇక్కడ పాత టేబుల్ కోడ్ అలాగే ఉంటుంది)
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
