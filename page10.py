import pandas as pd
import streamlit as st


def run():
  st.title("📊 SITE-CGD OFFICE BUILDING, MAHESHWARAM")
  st.markdown(
      "**PROJECT : MCGDPL6111 (Movone Infrastructure Private Limited) — Store"
      " Inward Register & Stock Ledger**"
  )

  # Create navigation tabs for Page 10
  tab_register, tab_summary = st.tabs(
      ["📦 Store Inward Register", "📈 Stock Ledger Summary"]
  )

  # --- TAB 1: STORE INWARD REGISTER ---
  with tab_register:
    st.markdown("### 📦 MIPL-Receipts Data Import")
    st.success("Successfully loaded data from sheet: Pur-Master Copy (Receipts)")
    st.info("You can edit data in the table below or add new rows.")

    # Sample DataFrame mirroring your live columns
    data = [
        {
            "Sl No": 1,
            "Store Inward No": 700,
            "Actual Received Date": "2026-09-08",
            "Supplier/Sender Name": "VENKATESHWARA TRADERS",
            "HSN Code": "None",
            "Description Of Material": "CEMENT OPC 53 GRADE",
            "Quantity": 100,
        },
        {
            "Sl No": 2,
            "Store Inward No": 701,
            "Actual Received Date": "2026-09-10",
            "Supplier/Sender Name": "APARNA ENTERPRISES LIMITED",
            "HSN Code": "None",
            "Description Of Material": "READY MIX CONCRETE",
            "Quantity": 50,
        },
        {
            "Sl No": 3,
            "Store Inward No": 702,
            "Actual Received Date": "2026-09-10",
            "Supplier/Sender Name": "APARNA ENTERPRISES LIMITED",
            "HSN Code": "None",
            "Description Of Material": "READY MIX CONCRETE",
            "Quantity": 75,
        },
        {
            "Sl No": 4,
            "Store Inward No": 703,
            "Actual Received Date": "2026-09-10",
            "Supplier/Sender Name": "APARNA ENTERPRISES LIMITED",
            "HSN Code": "None",
            "Description Of Material": "READY MIX CONCRETE",
            "Quantity": 60,
        },
    ]
    df = pd.DataFrame(data)

    edited_df = st.data_editor(
        df, hide_index=True, use_container_width=True, key="store_inward_editor"
    )

  # --- TAB 2: STOCK LEDGER SUMMARY ---
  with tab_summary:
    st.markdown("### 📈 Stock Ledger Summary")
    st.markdown("Aggregated summary of material quantities received.")

    if not edited_df.empty and "Description Of Material" in edited_df.columns:
      if "Quantity" in edited_df.columns:
        summary_df = (
            edited_df.groupby("Description Of Material")["Quantity"]
            .sum()
            .reset_index()
        )
        summary_df.columns = ["Material Description", "Total Quantity Received"]
      else:
        summary_df = (
            edited_df["Description Of Material"].value_counts().reset_index()
        )
        summary_df.columns = ["Material Description", "Total Inward Entries"]

      st.dataframe(summary_df, hide_index=True, use_container_width=True)

      # Summary Metrics Display
      col1, col2 = st.columns(2)
      with col1:
        st.metric(
            label="Total Inward Transactions", value=len(edited_df)
        )
      with col2:
        st.metric(
            label="Unique Materials",
            value=edited_df["Description Of Material"].nunique(),
        )
    else:
      st.warning("No data available for summary calculation.")
