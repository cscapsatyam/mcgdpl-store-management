import datetime
import io
import pandas as pd
import streamlit as st


# --- Excel Download Helper Function ---
def convert_df_to_excel(df):
  output = io.BytesIO()
  with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="Sheet1")
  processed_data = output.getvalue()
  return processed_data


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
        }
    ]

  if "material_master" not in st.session_state:
    st.session_state.material_master = [
        {
            "Sr No": 1,
            "Material Code": "MAT-001",
            "Material Description": "CEMENT OPC 53 GRADE",
            "Standard UOM": "Bags",
            "Category": "Cement & Binding",
        }
    ]

  if "subcontractor_master" not in st.session_state:
    st.session_state.subcontractor_master = [
        {
            "Sr No": 1,
            "Sub Contractor Name": "SRI VENKATA RAMANA WORKS",
            "Phone": "9888877777",
        }
    ]

  if "material_issue_records" not in st.session_state:
    st.session_state.material_issue_records = []

  if "site_transfer_records" not in st.session_state:
    st.session_state.site_transfer_records = []

  if "stock_audit_records" not in st.session_state:
    st.session_state.stock_audit_records = []

  # --- Navigation Tabs (11 Tabs) ---
  (
      tab_entry,
      tab_register,
      tab_summary,
      tab_po_status,
      tab_issue,
      tab_po,
      tab_sup_master,
      tab_mat_master,
      tab_sub_master,
      tab_transfer,
      tab_audit,
  ) = st.tabs(
      [
          "➕ Manual Entry",
          "📦 Inward Register",
          "📈 Stock Ledger",
          "📊 PO Status",
          "📤 Material Issue",
          "📋 Purchase Orders",
          "🏢 Supplier Master",
          "🧱 Material Master",
          "👷 Subcontractor Master",
          "🔄 Site Transfers",
          "📋 Stock Audit",
      ]
  )

  supplier_options = [s["Supplier Name"] for s in st.session_state.supplier_master]
  material_options = [
      m["Material Description"] for m in st.session_state.material_master
  ]
  subcontractor_options = [
      sc["Sub Contractor Name"]
      for sc in st.session_state.subcontractor_master
  ]
  po_options = ["None / Direct Receipt"] + [
      po["Purchase Order No"] for po in st.session_state.po_records
  ]

  # --- TAB 1: MANUAL ENTRY FORM ---
  with tab_entry:
    st.markdown("### 📝 Add New Store Inward Entry")
    selected_po = st.selectbox(
        "Select Purchase Order (Optional - Auto-fills Supplier & Material)",
        po_options,
    )

    default_supplier = supplier_options[0] if supplier_options else ""
    default_material = material_options[0] if material_options else ""

    if selected_po != "None / Direct Receipt":
      matched_po = next(
          (
              p
              for p in st.session_state.po_records
              if p["Purchase Order No"] == selected_po
          ),
          None,
      )
      if matched_po:
        if matched_po["Supplier Name"] in supplier_options:
          default_supplier = matched_po["Supplier Name"]
        if matched_po["Material Description"] in material_options:
          default_material = matched_po["Material Description"]

    with st.form("manual_entry_form", clear_on_submit=True):
      col1, col2, col3 = st.columns(3)

      with col1:
        store_inward_no = st.text_input("Store Inward No")
        supplier_name = st.selectbox(
            "Supplier/Sender Name",
            supplier_options,
            index=supplier_options.index(default_supplier)
            if default_supplier in supplier_options
            else 0,
        )
        invoice_no = st.text_input("Invoice/Delivery Challan No")
        entry_date = st.date_input("Date", datetime.date.today())

      with col2:
        material_desc = st.selectbox(
            "Description Of Material",
            material_options,
            index=material_options.index(default_material)
            if default_material in material_options
            else 0,
        )
        uom = st.selectbox(
            "UOM", ["Bags", "Cu.M", "MT", "Nos", "Kgs", "Litres", "Bundles"]
        )
        received_qty = st.number_input(
            "Received Qty", min_value=0.0, step=0.1, format="%.2f"
        )
        basic_rate = st.number_input(
            "Basic Rate", min_value=0.0, step=0.1, format="%.2f"
        )

      with col3:
        tax_percentage = st.number_input(
            "CGST + SGST (%)",
            min_value=0.0,
            max_value=100.0,
            step=0.5,
            value=18.0,
        )
        freight = st.number_input(
            "Freight", min_value=0.0, step=0.1, format="%.2f"
        )

        base_amount = received_qty * basic_rate
        tax_amount = base_amount * (tax_percentage / 100.0)
        calculated_total_value = base_amount + tax_amount + freight

        st.markdown(f"**Total Value:** ₹ {calculated_total_value:,.2f}")

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
            "Purchase Order No": selected_po,
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
    st.markdown("### 📦 Store Inward Register (Editable & Export)")
    if st.session_state.mipl_records:
      df = pd.DataFrame(st.session_state.mipl_records)
      edited_df = st.data_editor(
          df,
          hide_index=True,
          use_container_width=True,
          key="mipl_register_editor",
      )
      st.session_state.mipl_records = edited_df.to_dict("records")

      excel_data = convert_df_to_excel(edited_df)
      st.download_button(
          label="📥 Download Inward Register as Excel",
          data=excel_data,
          file_name=f"Store_Inward_Register_{datetime.date.today()}.xlsx",
          mime=(
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          ),
      )
    else:
      st.info("No records found.")

  # --- TAB 3: STOCK LEDGER SUMMARY ---
  with tab_summary:
    st.markdown("### 📈 Stock Ledger Summary & Export")
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

        excel_data = convert_df_to_excel(summary_df)
        st.download_button(
            label="📥 Download Stock Ledger as Excel",
            data=excel_data,
            file_name=f"Stock_Ledger_Summary_{datetime.date.today()}.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
        )
    else:
      st.warning("No data available.")

  # --- TAB 4: PO STATUS & TRACKING ---
  with tab_po_status:
    st.markdown("### 📊 Purchase Order Status & Tracking")
    if st.session_state.po_records:
      po_df = pd.DataFrame(st.session_state.po_records)
      if st.session_state.mipl_records:
        inward_df = pd.DataFrame(st.session_state.mipl_records)
        if "Purchase Order No" in inward_df.columns:
          received_summary = (
              inward_df.groupby("Purchase Order No")["Received Qty"]
              .sum()
              .reset_index()
          )
          po_status_df = pd.merge(
              po_df,
              received_summary,
              on="Purchase Order No",
              how="left",
          ).fillna({"Received Qty": 0.0})
        else:
          po_status_df = po_df.copy()
          po_status_df["Received Qty"] = 0.0
      else:
        po_status_df = po_df.copy()
        po_status_df["Received Qty"] = 0.0

      po_status_df["Pending Qty"] = (
          po_status_df["Qty of Order"] - po_status_df["Received Qty"]
      )
      po_status_df["Status"] = po_status_df.apply(
          lambda row: "Completed"
          if row["Pending Qty"] <= 0
          else ("Partially Received" if row["Received Qty"] > 0 else "Pending"),
          axis=1,
      )

      final_po_status_df = po_status_df[
          [
              "Purchase Order No",
              "Supplier Name",
              "Material Description",
              "Qty of Order",
              "Received Qty",
              "Pending Qty",
              "Status",
          ]
      ]
      st.dataframe(
          final_po_status_df, hide_index=True, use_container_width=True
      )

      excel_data = convert_df_to_excel(final_po_status_df)
      st.download_button(
          label="📥 Download PO Status as Excel",
          data=excel_data,
          file_name=f"PO_Status_Tracking_{datetime.date.today()}.xlsx",
          mime=(
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          ),
      )
    else:
      st.info("No Purchase Orders available to track.")

  # --- TAB 5: MATERIAL ISSUE ---
  with tab_issue:
    st.markdown("### 📤 Material Issue to Sub Contractors")
    with st.form("material_issue_form", clear_on_submit=True):
      ic1, ic2, ic3 = st.columns(3)
      with ic1:
        issue_date = st.date_input("Issue Date", datetime.date.today())
        subcontractor_name = (
            st.selectbox("Sub Contractor Name", subcontractor_options)
            if subcontractor_options
            else st.text_input("Sub Contractor Name")
        )
      with ic2:
        issue_material = (
            st.selectbox("Description Of Material", material_options)
            if material_options
            else st.text_input("Description Of Material")
        )
        issue_uom = st.selectbox(
            "UOM",
            ["Bags", "Cu.M", "MT", "Nos", "Kgs", "Litres", "Bundles"],
            key="issue_uom",
        )
      with ic3:
        issued_qty = st.number_input(
            "Issued Qty", min_value=0.0, step=0.1, format="%.2f"
        )
        purpose = st.text_input("Purpose / Work Description")
        st.write("")
        issue_submitted = st.form_submit_button("💾 Save Material Issue")

      if issue_submitted:
        new_issue_sr = len(st.session_state.material_issue_records) + 1
        st.session_state.material_issue_records.append({
            "Sr No": new_issue_sr,
            "Issue Date": issue_date,
            "Sub Contractor Name": subcontractor_name,
            "Description Of Material": issue_material,
            "UOM": issue_uom,
            "Issued Qty": issued_qty,
            "Purpose": purpose,
        })
        st.success("Material issued successfully!")

    if st.session_state.material_issue_records:
      issue_df = pd.DataFrame(st.session_state.material_issue_records)
      edited_issue_df = st.data_editor(
          issue_df, hide_index=True, use_container_width=True, key="issue_editor"
      )
      st.session_state.material_issue_records = edited_issue_df.to_dict(
          "records"
      )

      excel_data = convert_df_to_excel(edited_issue_df)
      st.download_button(
          label="📥 Download Material Issue as Excel",
          data=excel_data,
          file_name=f"Material_Issue_Register_{datetime.date.today()}.xlsx",
          mime=(
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          ),
      )

  # --- TAB 6: PURCHASE ORDERS ---
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

  # --- TAB 7: SUPPLIER MASTER ---
  with tab_sup_master:
    st.markdown("### 🏢 Supplier Master Management")
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
        s_submitted = st.form_submit_button("➕ Add New Supplier")

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

  # --- TAB 8: MATERIAL MASTER ---
  with tab_mat_master:
    st.markdown("### 🧱 Material Master Management")
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
        m_submitted = st.form_submit_button("➕ Add New Material")

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

  # --- TAB 9: SUBCONTRACTOR MASTER ---
  with tab_sub_master:
    st.markdown("### 👷 Subcontractor Master Management")
    with st.form("subcontractor_add_form", clear_on_submit=True):
      subc1, subc2 = st.columns(2)
      with subc1:
        sub_name = st.text_input("Sub Contractor Name")
      with subc2:
        sub_phone = st.text_input("Phone Number")

      sub_submitted = st.form_submit_button("➕ Add New Subcontractor")

      if sub_submitted:
        new_sub_sr = len(st.session_state.subcontractor_master) + 1
        st.session_state.subcontractor_master.append({
            "Sr No": new_sub_sr,
            "Sub Contractor Name": sub_name,
            "Phone": sub_phone,
        })
        st.success("Subcontractor added successfully!")

    if st.session_state.subcontractor_master:
      sub_df = pd.DataFrame(st.session_state.subcontractor_master)
      edited_sub_df = st.data_editor(
          sub_df,
          hide_index=True,
          use_container_width=True,
          key="subcontractor_master_editor",
      )
      st.session_state.subcontractor_master = edited_sub_df.to_dict("records")

  # --- TAB 10: SITE TRANSFERS ---
  with tab_transfer:
    st.markdown("### 🔄 Inter-Site Material Transfers")
    with st.form("site_transfer_form", clear_on_submit=True):
      tc1, tc2, tc3 = st.columns(3)
      with tc1:
        transfer_date = st.date_input("Transfer Date", datetime.date.today())
        from_site = st.text_input("From Site / Location")
      with tc2:
        to_site = st.text_input("To Site / Project")
        tr_material = (
            st.selectbox("Material Description", material_options)
            if material_options
            else st.text_input("Material Description")
        )
      with tc3:
        tr_qty = st.number_input(
            "Transferred Qty", min_value=0.0, step=0.1, format="%.2f"
        )
        tr_remarks = st.text_input("Transfer Remarks")
        st.write("")
        tr_submitted = st.form_submit_button("💾 Save Transfer Record")

      if tr_submitted:
        new_tr_sr = len(st.session_state.site_transfer_records) + 1
        st.session_state.site_transfer_records.append({
            "Sr No": new_tr_sr,
            "Date": transfer_date,
            "From Site": from_site,
            "To Site": to_site,
            "Material Description": tr_material,
            "Transferred Qty": tr_qty,
            "Remarks": tr_remarks,
        })
        st.success("Site transfer record saved successfully!")

    if st.session_state.site_transfer_records:
      tr_df = pd.DataFrame(st.session_state.site_transfer_records)
      edited_tr_df = st.data_editor(
          tr_df,
          hide_index=True,
          use_container_width=True,
          key="transfer_editor",
      )
      st.session_state.site_transfer_records = edited_tr_df.to_dict("records")

  # --- TAB 11: STOCK AUDIT ---
  with tab_audit:
    st.markdown("### 📋 Physical Stock Audit & Variance")
    with st.form("stock_audit_form", clear_on_submit=True):
      ac1, ac2, ac3 = st.columns(3)
      with ac1:
        audit_date = st.date_input("Audit Date", datetime.date.today())
        auditor_name = st.text_input("Auditor Name")
      with ac2:
        audit_material = (
            st.selectbox("Material Description", material_options)
            if material_options
            else st.text_input("Material Description")
        )
        system_qty = st.number_input(
            "System Stock Qty", min_value=0.0, step=0.1, format="%.2f"
        )
      with ac3:
        physical_qty = st.number_input(
            "Physical Count Qty", min_value=0.0, step=0.1, format="%.2f"
        )
        audit_remarks = st.text_input("Audit Remarks / Discrepancy Reason")
        st.write("")
        audit_submitted = st.form_submit_button("💾 Save Audit Record")

      if audit_submitted:
        variance = physical_qty - system_qty
        new_audit_sr = len(st.session_state.stock_audit_records) + 1
        st.session_state.stock_audit_records.append({
            "Sr No": new_audit_sr,
            "Date": audit_date,
            "Auditor Name": auditor_name,
            "Material Description": audit_material,
            "System Qty": system_qty,
            "Physical Qty": physical_qty,
            "Variance (Diff)": variance,
            "Remarks": audit_remarks,
        })
        st.success("Stock audit record added successfully!")

    if st.session_state.stock_audit_records:
      audit_df = pd.DataFrame(st.session_state.stock_audit_records)
      edited_audit_df = st.data_editor(
          audit_df, hide_index=True, use_container_width=True, key="audit_editor"
      )
      st.session_state.stock_audit_records = edited_audit_df.to_dict("records")

      excel_data = convert_df_to_excel(edited_audit_df)
      st.download_button(
          label="📥 Download Stock Audit as Excel",
          data=excel_data,
          file_name=f"Stock_Audit_Report_{datetime.date.today()}.xlsx",
          mime=(
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          ),
      )