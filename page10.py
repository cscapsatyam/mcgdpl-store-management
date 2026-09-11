import datetime
import pandas as pd
import streamlit as st


def run():
  st.title("📊 SITE-CGD OFFICE BUILDING, MAHESHWARAM")
  st.markdown(
      "**PROJECT : MCGDPL6111 (Movone Infrastructure Private Limited) — Store"
      " Inward Register & Stock Ledger**"
  )

  if "mipl_records" not in st.session_state:
    st.session_state.mipl_records = []

  supplier_options = (
      [s["Supplier Name"] for s in st.session_state.get("supplier_master", [])]
      if "supplier_master" in st.session_state
      else ["VENKATESHWARA TRADERS"]
  )
  material_options = (
      [
          m["Material Description"]
          for m in st.session_state.get("material_master", [])
      ]
      if "material_master" in st.session_state
      else ["CEMENT OPC 53 GRADE"]
  )

  tab_entry, tab_register, tab_summary = st.tabs(
      [
          "➕ Manual Entry Form",
          "📦 Store Inward Register",
          "📈 Stock Ledger Summary",
      ]
  )

  # --- TAB 1: MANUAL ENTRY FORM ---
  with tab_entry:
    st.markdown("### 📝 Add New Store Inward Entry")

    with st.form("manual_entry_form", clear_on_submit=True):
      col1, col2, col3 = st.columns(3)

      with col1:
        store_inward_no = st.text_input("Store Inward No", value="800")
        supplier_name = st.selectbox("Supplier/Sender Name", supplier_options)
        invoice_no = st.text_input("Invoice/Delivery Challan No")
        entry_date = st.date_input("Date", datetime.date.today())
        material_desc = st.selectbox("Description Of Material", material_options)

      with col2:
        uom = st.selectbox(
            "UOM", ["Bags", "Cu.M", "MT", "Nos", "Kgs", "Litres", "Bundles"]
        )
        received_qty = st.number_input(
            "Received Qty", min_value=0.0, step=0.1, value=50.0, format="%.2f"
        )
        basic_rate = st.number_input(
            "Basic Rate", min_value=0.0, step=0.1, value=255.0, format="%.2f"
        )

        # CGST + SGST Percentage Input
        tax_percentage = st.number_input(
            "CGST + SGST (%)",
            min_value=0.0,
            max_value=100.0,
            step=0.5,
            value=18.0,
        )

      with col3:
        freight = st.number_input(
            "Freight", min_value=0.0, step=0.1, value=500.0, format="%.2f"
        )

        # CORRECT CALCULATION LOGIC
        base_amount = received_qty * basic_rate
        tax_amount = base_amount * (tax_percentage / 100.0)
        calculated_total_value = base_amount + tax_amount + freight

        st.markdown(f"**Calculation Breakdown:**")
        st.text(f"Base Amount: ₹ {base_amount:,.2f}")
        st.text(f"Tax Value ({tax_percentage}%): ₹ {tax_amount:,.2f}")
        st.info(f"**Total Invoice Value: ₹ {calculated_total_value:,.2f}**")

        vehicle_no = st.text_input("Vehicle No")
        type_of_receipt = st.selectbox(
            "Type of Receipt", ["Purchase", "Return", "Transfer", "Sample"]
        )
        remarks = st.text_input("Remarks")

      submitted = st.form_submit_button("💾 Save Entry")

      if submitted:
        new_sr_no = len(st.session_state.mipl_records) + 1
        new_entry = {
            "Sr No": new_sr_no,
            "Store Inward No": store_inward_no,
            "Supplier/Sender Name": supplier_name,
            "Invoice/Delivery Challan No": invoice_no,
            "Date": entry_date,
            "Description Of Material": material_desc,
            "UOM": uom,
            "Received Qty": received_qty,
            "Basic Rate": basic_rate,
            "CGST+SGST (%)": tax_percentage,
            "Tax Amount": tax_amount,
            "Freight": freight,
            "Total Invoice Value": calculated_total_value,
            "Vehicle No": vehicle_no,
            "Type of Receipt": type_of_receipt,
            "Remarks": remarks,
        }
        st.session_state.mipl_records.append(new_entry)
        st.success("Entry added successfully!")

  # --- TAB 2: STORE INWARD REGISTER ---
  with tab_register:
    st.markdown("### 📦 Store Inward Register (Editable)")
    if st.session_state.mipl_records:
      df = pd.DataFrame(st.session_state.mipl_records)
      edited_df = st.data_editor(
          df,
          hide_index=True,
          use_container_width=True,
          key="mipl_register_editor",
      )
      st.session_state.mipl_records = edited_df.to_dict("records")
    else:
      st.info("No records added yet.")

  # --- TAB 3: STOCK LEDGER SUMMARY ---
  with tab_summary:
    st.markdown("### 📈 Stock Ledger Summary")
    if st.session_state.mipl_records:
      current_df = pd.DataFrame(st.session_state.mipl_records)
      if (
          not current_df.empty
          and "Description Of Material" in current_df.columns
      ):
        summary_df = (
            current_df.groupby(["Description Of Material", "UOM"])[
                "Received Qty"
            ]
            .sum()
            .reset_index()
        )
        summary_df.columns = [
            "Material Description",
            "UOM",
            "Total Received Qty",
        ]
        st.dataframe(summary_df, hide_index=True, use_container_width=True)
    else:
      st.warning("No data available.")
