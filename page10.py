import datetime
import pandas as pd
import streamlit as st


def run():
  st.title("📊 SITE-CGD OFFICE BUILDING, MAHESHWARAM")
  st.markdown(
      "**PROJECT : MCGDPL6111 (Movone Infrastructure Private Limited) — Store"
      " Inward Register & Stock Ledger**"
  )

  # --- Initialize Session States ---
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

  if "supplier_master" not in st.session_state:
    st.session_state.supplier_master = [
        {
            "Sr No": 1,
            "Supplier Name": "VENKATESHWARA TRADERS",
            "Contact Person": "Ramesh",
            "Phone": "9876543210",
            "GSTIN": "36AAAAA0000A1Z5",
        },
        {
            "Sr No": 2,
            "Supplier Name": "APARNA ENTERPRISES LIMITED",
            "Contact Person": "Sales Desk",
            "Phone": "9123456789",
            "GSTIN": "36BBBBB1111B1Z6",
        },
    ]

  if "material_master" not in st.session_state:
    st.session_state.material_master = [
        {
            "Sr No": 1,
            "Material Code": "MAT-001",
            "Material Description": "CEMENT OPC 53 GRADE",
            "Standard UOM": "Bags",
            "Category": "Cement & Binding",
        },
        {
            "Sr No": 2,
            "Material Code": "MAT-002",
            "Material Description": "READY MIX CONCRETE",
            "Standard UOM": "Cu.M",
            "Category": "Concrete",
        },
    ]

  # --- All 6 Navigation Tabs ---
  (
      tab_entry,
      tab_register,
      tab_summary,
      tab_po,
      tab_supplier_master,
      tab_material_master,
  ) = st.tabs(
      [
          "➕ Manual Entry Form",
          "📦 Store Inward Register",
          "📈 Stock Ledger Summary",
          "📋 Supplier Order List",
          "🏢 Supplier Master",
          "🧱 Material Master",
      ]
  )

  # Dropdown options extracted from masters
  supplier_options = [s["Supplier Name"] for s in st.session_state.supplier_master]
  material_options = [
      m["Material Description"] for m in st.session_state.material_master
  ]

  # --- TAB 1: MANUAL ENTRY FORM ---
  with tab_entry:
    st.markdown("### 📝 Add New Store Inward Entry")

    with st.form("manual_entry_form", clear_on_submit=True):
      col1, col2, col3 = st.columns(3)

      with col1:
        store_inward_no = st.text_input("Store Inward No")
        supplier_name = st.selectbox("Supplier/Sender Name", supplier_options)
        invoice_no = st.text_input("Invoice/Delivery Challan No")
        entry_date = st.date_input("Date", datetime.date.today())
        material_desc = st.selectbox("Description Of Material", material_options)

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
        tax_percentage = st.number_input(
            "CGST + SGST (%)",
            min_value=0.0,
            max_value=100.0,
            step=0.5,
            value=18.0,
        )

      with col3:
        freight = st.number_input(
            "Freight", min_value=0.0, step=0.1, format="%.2f"
        )

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
      st.info("No records found.")

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

  # --- TAB 4: SUPPLIER ORDER LIST ---
  with tab_po:
    st.markdown("### 📋 Supplier Order List (Purchase Orders)")
    with st.form("po_entry_form", clear_on_submit=True):
      c1, c2, c3 = st.columns(3)
      with c1:
        po_no = st.text_input("Purchase Order No")
        po_date = st.date_input("PO Date", datetime.date.today())
      with c2:
        po_supplier = st.selectbox("Supplier Name", supplier_options)
        po_material = st.selectbox("Material Description", material_options)
      with c3:
        po_qty = st.number_input(
            "Qty of Order", min_value=0.0, step=0.1, format="%.2f"
        )
        st.write("")
        po_submitted = st.form_submit_button("➕ Add Purchase Order")

      if po_submitted:
        new_po_sr = len(st.session_state.po_records) + 1
        st.session_state.po_records.append({
            "Sr No": new_po_sr,
            "Purchase Order No": po_no,
            "Date": po_date,
            "Supplier Name": po_supplier,
            "Material Description": po_material,
            "Qty of Order": po_qty,
        })
        st.success("Purchase order added successfully!")

    if st.session_state.po_records:
      po_df = pd.DataFrame(st.session_state.po_records)
      edited_po_df = st.data_editor(
          po_df, hide_index=True, use_container_width=True, key="po_editor"
      )
      st.session_state.po_records = edited_po_df.to_dict("records")

  # --- TAB 5: SUPPLIER MASTER ---
  with tab_supplier_master:
    st.markdown("### 🏢 Supplier Master Data")
    with st.form("supplier_add_form", clear_on_submit=True):
      sc1, sc2, sc3 = st.columns(3)
      with sc1:
        s_name = st.text_input("Supplier Name")
        s_contact = st.text_input("Contact Person")
      with sc2:
        s_phone = st.text_input("Phone Number")
        s_gstin = st.text_input("GSTIN")
      with sc3:
        st.write("")
        s_submitted = st.form_submit_button("➕ Add Supplier")

      if s_submitted:
        new_s_sr = len(st.session_state.supplier_master) + 1
        st.session_state.supplier_master.append({
            "Sr No": new_s_sr,
            "Supplier Name": s_name,
            "Contact Person": s_contact,
            "Phone": s_phone,
            "GSTIN": s_gstin,
        })
        st.success("Supplier added successfully!")

    if st.session_state.supplier_master:
      sup_df = pd.DataFrame(st.session_state.supplier_master)
      edited_sup_df = st.data_editor(
          sup_df,
          hide_index=True,
          use_container_width=True,
          key="supplier_master_editor",
      )
      st.session_state.supplier_master = edited_sup_df.to_dict("records")

  # --- TAB 6: MATERIAL MASTER ---
  with tab_material_master:
    st.markdown("### 🧱 Material Master Data")
    with st.form("material_add_form", clear_on_submit=True):
      mc1, mc2, mc3 = st.columns(3)
      with mc1:
        m_code = st.text_input("Material Code")
        m_desc = st.text_input("Material Description")
      with mc2:
        m_uom = st.selectbox(
            "Standard UOM",
            ["Bags", "Cu.M", "MT", "Nos", "Kgs", "Litres", "Bundles"],
        )
        m_cat = st.text_input("Category")
      with mc3:
        st.write("")
        m_submitted = st.form_submit_button("➕ Add Material")

      if m_submitted:
        new_m_sr = len(st.session_state.material_master) + 1
        st.session_state.material_master.append({
            "Sr No": new_m_sr,
            "Material Code": m_code,
            "Material Description": m_desc,
            "Standard UOM": m_uom,
            "Category": m_cat,
        })
        st.success("Material added successfully!")

    if st.session_state.material_master:
      mat_df = pd.DataFrame(st.session_state.material_master)
      edited_mat_df = st.data_editor(
          mat_df,
          hide_index=True,
          use_container_width=True,
          key="material_master_editor",
      )
      st.session_state.material_master = edited_mat_df.to_dict("records")
