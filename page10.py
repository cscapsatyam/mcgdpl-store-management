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

  if "material_issue_records" not in st.session_state:
    st.session_state.material_issue_records = []

  # --- Navigation Tabs (Only 4 Essential Tabs) ---
  tab_entry, tab_register, tab_summary, tab_issue = st.tabs(
      [
          "➕ Manual Entry",
          "📦 Inward Register",
          "📈 Stock Ledger",
          "📤 Material Issue",
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

      with col2:
        material_desc = st.text_input("Description Of Material")
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

  # --- TAB 4: MATERIAL ISSUE ---
  with tab_issue:
    st.markdown("### 📤 Material Issue to Sub Contractors")
    with st.form("material_issue_form", clear_on_submit=True):
      ic1, ic2, ic3 = st.columns(3)
      with ic1:
        issue_date = st.date_input("Issue Date", datetime.date.today())
        subcontractor_name = st.text_input("Sub Contractor Name")
      with ic2:
        issue_material = st.text_input("Description Of Material")
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
