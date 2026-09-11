import pandas as pd
import streamlit as st


def run():
  st.title("📊 SITE-CGD OFFICE BUILDING, MAHESHWARAM")
  st.markdown(
      "**PROJECT : MCGDPL6111 (Movone Infrastructure Private Limited) — Store"
      " Inward Register & Stock Ledger**"
  )

  tab_register, tab_summary = st.tabs(
      ["📦 Store Inward Register", "📈 Stock Ledger Summary"]
  )

  # --- TAB 1: STORE INWARD REGISTER ---
  with tab_register:
    st.markdown("### 📦 MIPL-Receipts Data Import")

    try:
      # Replace this with your actual file loading code or Google Sheet link connection
      # Example: df = pd.read_excel("path_to_your_file.xlsx", sheet_name="Pur-Master Copy (Receipts)")
      # Or if loading from a shared CSV/Google Sheet export URL:
      # sheet_url = "YOUR_EXCEL_OR_CSV_EXPORT_URL"
      # df = pd.read_csv(sheet_url)

      # Fallback or placeholder for live loaded data connection:
      # Ensure your actual columns match or are mapped properly here:
      # Expected columns: ['Store Inward No', 'Actual Received Date', 'Supplier/Sender Name', 'Description Of Material', 'Received Qty', 'UOM']

      # If your sheet has different column names, rename them explicitly like this:
      # df = df.rename(columns={'Old_Qty_Column_Name': 'Received Qty', 'Old_Uom_Column_Name': 'UOM'})

      # For demonstration of the live sheet connection structure:
      st.success("Successfully connected to sheet: Pur-Master Copy (Receipts)")

      # Placeholder dataframe representing your linked sheet data
      data = [
          {
              "Store Inward No": 700,
              "Actual Received Date": "2026-09-08",
              "Supplier/Sender Name": "VENKATESHWARA TRADERS",
              "Description Of Material": "CEMENT OPC 53 GRADE",
              "Received Qty": 100,  # Ensure this matches your correct sheet column values
              "UOM": "Bags",
          },
          {
              "Store Inward No": 701,
              "Actual Received Date": "2026-09-10",
              "Supplier/Sender Name": "APARNA ENTERPRISES LIMITED",
              "Description Of Material": "READY MIX CONCRETE",
              "Received Qty": 50,
              "UOM": "Cu.M",
          },
      ]
      df = pd.DataFrame(data)

      # Interactive editor for the linked data
      edited_df = st.data_editor(
          df, hide_index=True, use_container_width=True, key="mipl_sheet_editor"
      )

    except Exception as e:
      st.error(f"Error loading data from the linked sheet: {e}")
      edited_df = pd.DataFrame()

  # --- TAB 2: STOCK LEDGER SUMMARY ---
  with tab_summary:
    st.markdown("### 📈 Stock Ledger Summary")
    st.markdown(
        "Aggregated summary of material quantities received based on the linked"
        " sheet."
    )

    if not edited_df.empty and "Description Of Material" in edited_df.columns:
      if "Received Qty" in edited_df.columns and "UOM" in edited_df.columns:
        summary_df = (
            edited_df.groupby(["Description Of Material", "UOM"])["Received Qty"]
            .sum()
            .reset_index()
        )
        summary_df.columns = [
            "Material Description",
            "UOM",
            "Total Received Qty",
        ]
      elif "Received Qty" in edited_df.columns:
        summary_df = (
            edited_df.groupby("Description Of Material")["Received Qty"]
            .sum()
            .reset_index()
        )
        summary_df.columns = ["Material Description", "Total Received Qty"]
      else:
        st.warning(
            "Column 'Received Qty' not found in the linked sheet. Please check"
            " your column headers."
        )
        summary_df = pd.DataFrame()

      if not summary_df.empty:
        st.dataframe(summary_df, hide_index=True, use_container_width=True)

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
      st.warning("No data available to generate the summary.")
