import datetime
import pandas as pd
import streamlit as st


def run():
  st.title("📊 SITE-CGD OFFICE BUILDING, MAHRESHWARAM")
  st.markdown(
      "### PROJECT : MCGDPL6111 (Movone Infrastructure Private Limited) —"
      " Store Inward Register"
  )

  st.markdown("---")

  # --- STORE INWARD REGISTER DATA TABLE ---
  st.subheader("📦 Store Inward Details")

  # మీరు ఇచ్చిన కాలమ్స్ తో డిఫాల్ట్ స్ట్రక్చర్
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

  # సాంపుల్ డేటా (ఒక రో ఉంచబడింది, అవసరమైతే ఎడిట్ చేసుకోవచ్చు)
  sample_data = {
      "Sl No": [1],
      "Store Inward No.": ["INW-001"],
      "Actual Received Date": [str(datetime.date.today())],
      "Supplier/Sender Name": ["ABC Suppliers"],
      "HSN Code": ["1234"],
      "DescriptionOfMaterial": ["Cement Bag"],
      "UOM": ["Bags"],
      "PO No.": ["PO-101"],
      "PO Date": [str(datetime.date.today())],
      "PO Qty.": [100],
      "Challan Qty.": [100],
      "Invoice Value": [35000],
      "Received Qty.": [100],
      "Received Value": [35000],
      "Unit Rate": [350],
      "CGST": [9.0],
      "SGST": [9.0],
      "Tax Value": [6300],
      "Freight": [500],
      "Invoice/DC No.": ["INV-999"],
      "Invoice/DC Date": [str(datetime.date.today())],
      "E-Way Bill No.": ["EWB12345"],
      "LR No.": ["LR-55"],
      "LR Date": [str(datetime.date.today())],
      "Vehicle No.": ["TS08AB1234"],
      "Location": ["Godown"],
      "Type of Receipt": ["Purchase"],
      "Remarks": ["Good Condition"],
  }

  # పాండాస్ డేటాఫ్రేమ్ క్రియేట్ చేయడం
  df = pd.DataFrame(columns=columns_list)

  # యూజర్ ఎడిట్ చేసుకునేలా టేబుల్ చూపించడం
  edited_df = st.data_editor(
      df,
      num_rows="dynamic",  # కొత్త రోస్ యాడ్ చేసుకోవడానికి అవకాశం ఉంటుంది
      hide_index=True,
      use_container_width=True,
      key="store_inward_table",
  )

  st.markdown("---")
  st.info(
      "💡 మీరు పైన ఉన్న టేబుల్‌లో నేరుగా డేటాను టైప్ చేయవచ్చు లేదా కొత్త రోస్"
      " (Rows) యాడ్ చేసుకోవచ్చు."
  )
