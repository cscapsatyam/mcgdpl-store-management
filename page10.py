import datetime
import pandas as pd
import streamlit as st


def run():
  st.title("📊 SITE-CGD OFFICE BUILDING, MAHESHWARAM")
  st.markdown(
      "**PROJECT : MCGDPL6111 (Movone Infrastructure Private Limited) — Store"
      " Inward Register & Stock Ledger**"
  )

  # Initialize session states if not present
  if "mipl_records" not in st.session_state:
    st.session_state.mipl_records = []

  if "po_records" not in st.session_state:
    st.session_state.po_records = [
        {
            "Sr No": 1,
            "Purchase Order No": "PO-2026-001",
            "Date": datetime.date(2026, 9, 1),
            "Supplier Name": "VENKATESHWARA TRADERS",
            "Material Description": "CEMENT OPC 53 GRADE",
            "Qty of Order": 500.0,
        }
    ]

  # Navigation tabs including the new Supplier Order List tab
  tab_entry, tab_register, tab_summary, tab_po = st.tabs(
      [
          "➕ Manual Entry Form",
          "📦 Store Inward Register",
          "📈 Stock Ledger Summary",
          "📋 Supplier Order List",
      ]
  )

  # --- TAB 1: MANUAL ENTRY FORM ---
  with tab_entry:
    st.markdown("### 📝 Add New Store Inward Entry")

    with st.form("manual_entry_form", clear_on_submit=True):
      col1, col2, col3 = st.columns(3)

      with col1:
        store_inward_no = st.text_input("Store Inward No")
        supplier_name = st.text_input("Supplier/Sender Name")
        invoice_no = st.text_input("Invoice/Delivery Challan No")
        entry_date = st.date_input("Date", datetime.date.today())
        material_desc = st.text_input("Description Of Material")

      with col2:
        uom = st.selectbox(
            "UOM", ["Bags", "Cu.M", "MT", "Nos", "Kgs", "Litres", "Bundles"]
        )
        received_qty = st.number_input(
            "Received Qty", min_value=0.0, step=0.1, format="%.2f"
        )
        basic_rate = st.number_input(
            "Basic Rate", min_value=0.0, step=0.1, format="%.2f"
        )
        cgst_sgst = st.number_input(
            "CGST + SGST", min_value=0.0, step=0.1, format="%.2f"
        )

      with col3:
        freight = st.number_input(
            "Freight", min_value=0.0, step=0.1, format="%.2f"
        )
        calculated_total_value = (received_qty * basic_rate) + cgst_sgst + freight
        st.markdown(f"**Calculated Total Invoice Value:**")
        st.info(f"₹ {calculated_total_value:,.2f}")

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
            "CGST+SGST": cgst_sgst,
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
      st.info("No records added yet. Please use the Manual Entry Form tab.")

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

        col1, col2 = st.columns(2)
        with col1:
          st.metric(
              label="Total Inward Transactions", value=len(current_df)
          )
        with col2:
          st.metric(
              label="Unique Materials",
              value=current_df["Description Of Material"].nunique(),
          )
    else:
      st.warning("No data available to generate summary.")

  # --- TAB 4: SUPPLIER ORDER LIST ---
  with tab_po:
    st.markdown("### 📋 Supplier Order List")
    st.info("Manage and view purchase orders placed with suppliers.")

    # Sub-form or inline editor to add new purchase orders
    with st.form("po_entry_form", clear_on_submit=True):
      c1, c2, c3 = st.columns(3)
      with c1:
        po_no = st.text_input("Purchase Order No")
        po_date = st.date_input("PO Date", datetime.date.today())
      with c2:
        po_supplier = st.text_input("Supplier Name")
        po_material = st.text_input("Material Description")
      with c3:
        po_qty = st.number_input(
            "Qty of Order", min_value=0.0, step=0.1, format="%.2f"
        )
        st.write("")  # Spacing alignment
        po_submitted = st.form_submit_button("➕ Add Purchase Order")

      if po_submitted:
        new_po_sr = len(st.session_state.po_records) + 1
        new_po = {
            "Sr No": new_po_sr,
            "Purchase Order No": po_no,
            "Date": po_date,
            "Supplier Name": po_supplier,
            "Material Description": po_material,
            "Qty of Order": po_qty,
        }
        st.session_state.po_records.append(new_po)
        st.success("Purchase order added successfully!")

    # Display editable table for PO records
    if st.session_state.po_records:
      po_df = pd.DataFrame(st.session_state.po_records)
      edited_po_df = st.data_editor(
          po_df, hide_index=True, use_container_width=True, key="po_editor"
      )
      st.session_state.po_records = edited_po_df.to_dict("records")
