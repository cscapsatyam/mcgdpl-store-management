import datetime
import pandas as pd
import streamlit as st


def run():
  st.title("📊 SITE-CGD OFFICE BUILDING, MAHESHWARAM")
  st.markdown(
      "### PROJECT : MCGDPL6111 (Movone Infrastructure Private Limited) —"
      " Store Inward Register"
  )

  st.markdown("---")

  # --- EXCEL FILE LOADING SECTION ---
  st.subheader("📦 MIPL-Reciepts Data Import")

  excel_file_path = "MIPL-Reciepts.xlsx"

  try:
    # ఎక్సెల్ ఫైల్ లోని షీట్ పేర్లను ముందుగా చెక్ చేయడం కోసం
    xl_file = pd.ExcelFile(excel_file_path)
    sheet_names = xl_file.sheet_names

    # ఒకవేళ ఒకటి కంటే ఎక్కువ షీట్లు ఉంటే యూజర్ సెలెక్ట్ చేసుకోవడానికి
    if len(sheet_names) > 1:
      selected_sheet = st.selectbox("📂 Select Sheet from Excel:", sheet_names)
    else:
      selected_sheet = sheet_names[0]

    # ఎక్సెల్ ఫైల్ నుండి డేటా రీడ్ చేయడం
    df = pd.read_excel(excel_file_path, sheet_name=selected_sheet)
    st.success(f"Successfully loaded data from sheet: `{selected_sheet}`")

  except FileNotFoundError:
    st.error(
        f"⚠️ `{excel_file_path}` file not found in the repository. Please upload"
        " it."
    )
    # ఫైల్ లేకపోతే మీరు ఇచ్చిన డిఫాల్ట్ కాలమ్స్‌తో ఖాళీ టేబుల్ చూపించడం
    columns_list = [
        "Sl No",
        "Store Inward No.",
        "Actual Received Date",
        "Supplier/Sender Name",
        "HSN Code",
        "Description Of Material",
        "UOM",
        "PO No.",
        "PO Date",
        "PO Qty.",
        "Challan Qty.",
        "Invoice Value",
        "Received Qty.",
        "Received Value",
        "Unit Rate",
        "CGST",
        "SGST",
        "Tax Value",
        "Freight",
        "Invoice/DC No.",
        "Invoice/DC Date",
        "E-Way Bill No.",
        "LR No.",
        "LR Date",
        "Vehicle No.",
        "Location",
        "Type of Receipt",
        "Remarks",
    ]
    df = pd.DataFrame(columns=columns_list)
  except Exception as e:
    st.error(f"Error reading Excel file: {e}")
    df = pd.DataFrame()

  st.markdown("---")

  # --- DATA EDITOR TABLE ---
  if not df.empty:
    st.info(
        "💡 మీరు కింద ఉన్న టేబుల్‌లో డేటాను ఎడిట్ చేసుకోవచ్చు లేదా కొత్త రోస్"
        " (Rows) యాడ్ చేయవచ్చు."
    )
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        hide_index=True,
        use_container_width=True,
        key="mipl_receipts_table",
    )
  else:
    st.warning("No data available to display.")
