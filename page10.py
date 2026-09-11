import datetime
import pandas as pd
import streamlit as st


def run():
  st.title("📊 SITE-CGD OFFICE BUILDING, MAHESHWARAM")
  st.markdown(
      "**PROJECT : MCGDPL6111 (Movone Infrastructure Private Limited) — Store"
      " Inward Register & Stock Ledger**"
  )

  # Initialize session state for storing records if not already present
  if "mipl_records" not in st.session_state:
    st.session_state.mipl_records = [
        {
            "Sr No": 1,
            "Store Inward No": "700",
            "Supplier/Sender Name": "VENKATESHWARA TRADERS",
            "Invoice/Delivery Challan No": "INV-101",
            "Date": datetime.date(2026, 9, 8),
            "Description Of Material": "CEMENT OPC 53 GRADE",
            "UOM": "Bags",
            "Received Qty": 100.0,
            "Basic Rate": 350.0,
            "CGST+SGST": 63.0,
            "Freight": 10.0,
            "Total Invoice Value": 42300.0,
            "Vehicle No": "TS08AB1234",
            "Type of Receipt": "Purchase",
            "Remarks": "Good condition",
        }
    ]

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
        total_invoice_value = st.number_input(
            "Total Invoice Value", min_value=0.0, step=0.1, format="%.2f"
        )
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
            "Total Invoice Value": total_invoice_value,
            "Vehicle No": vehicle_no,
            "Type of Receipt": type_of_receipt,
            "Remarks": remarks,
        }
        st.session_state.mipl_records.append(new_entry)
        st.success("Entry added successfully!")

  # --- TAB 2: STORE INWARD REGISTER ---
  with tab_register:
    st.markdown("### 📦 Store Inward Register (Editable)")
    df = pd.DataFrame(st.session_state.mipl_records)

    edited_df = st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        key="mipl_register_editor",
    )
    # Update session state with any inline edits made in the table
    st.session_state.mipl_records = edited_df.to_dict("records")

  # --- TAB 3: STOCK LEDGER SUMMARY ---
  with tab_summary:
    st.markdown("### 📈 Stock Ledger Summary")

    current_df = pd.DataFrame(st.session_state.mipl_records)
    if not current_df.empty and "Description Of Material" in current_df.columns:
      if "Received Qty" in current_df.columns and "UOM" in current_df.columns:
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
      else:
        summary_df = (
            current_df["Description Of Material"].value_counts().reset_index()
        )
        summary_df.columns = ["Material Description", "Total Inward Entries"]

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
