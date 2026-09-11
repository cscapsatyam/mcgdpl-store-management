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
      # Load your live sheet/file data here:
      # df = pd.read_excel("your_path.xlsx", sheet_name="Pur-Master Copy (Receipts)")
      # or
      # df = pd.read_csv("your_csv_link")

      # Placeholder dataframe reflecting your actual sheet structure
      data = [
          {
              "Store Inward No": 700,
              "Actual Received Date": "2026-09-08",
              "Supplier/Sender Name": "VENKATESHWARA TRADERS",
              "Description Of Material": "CEMENT OPC 53 GRADE",
              "Received Qty": 100,  # Ensure this matches your correct quantity
              "UOM": "Bags",
          },
          {
              "Store Inward No": 701,
              "Actual Received Date": "2026-09-10",
              "Supplier/Sender Name": "APARNA ENTERPRISES LIMITED",
              "Description Of Material": "READY MIX CONCRETE",
              "Received Qty": 50,  # Ensure this matches your correct quantity
              "UOM": "Cu.M",
          },
      ]
      df = pd.DataFrame(data)

      # FIX: If your linked Excel file has a different column name for quantity (e.g., 'Qty' or 'Quantity'),
      # rename it dynamically to 'Received Qty' so it works seamlessly:
      if (
          "Quantity" in df.columns
          and "Received Qty" not in df.columns
      ):
        df = df.rename(columns={"Quantity": "Received Qty"})
      elif "Qty" in df.columns and "Received Qty" not in df.columns:
        df = df.rename(columns={"Qty": "Received Qty"})

      st.success("Successfully connected to sheet: Pur-Master Copy (Receipts)")

      # Data editor allows you to view and make live manual corrections if needed
      edited_df = st.data_editor(
          df,
          hide_index=True,
          use_container_width=True,
          key="mipl_sheet_editor_fixed",
      )

    except Exception as e:
      st.error(f"Error loading sheet data: {e}")
      edited_df = pd.DataFrame()

  # --- TAB 2: STOCK LEDGER SUMMARY ---
  with tab_summary:
    st.markdown("### 📈 Stock Ledger Summary")
    st.markdown("Aggregated summary based on verified received quantities.")

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
        summary_df = pd.DataFrame()
        st.warning(
            "Column 'Received Qty' not found. Please check your Excel column"
            " headers."
        )

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
      st.warning("No data available to generate summary.")
