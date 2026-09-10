import datetime
import io
import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import streamlit as st


def generate_akg_pdf_invoice(
    report_df,
    selected_month_str,
    target_supplier,
    total_basic,
    total_with_tax,
    start_date_str,
    end_date_str,
):
  buffer = io.BytesIO()
  doc = SimpleDocTemplate(
      buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
  )
  elements = []
  styles = getSampleStyleSheet()

  title_style = ParagraphStyle(
      'InvoiceTitle',
      parent=styles['Heading1'],
      fontSize=16,
      alignment=1,
      textColor=colors.HexColor('#1f2937'),
      spaceAfter=4,
  )
  sub_style = ParagraphStyle(
      'InvoiceSub',
      parent=styles['Normal'],
      fontSize=9,
      alignment=1,
      textColor=colors.HexColor('#4b5563'),
      spaceAfter=12,
  )
  cell_style = ParagraphStyle(
      'TableCell', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#1f2937')
  )
  header_style = ParagraphStyle(
      'TableHeader',
      parent=styles['Normal'],
      fontSize=9,
      fontName='Helvetica-Bold',
      textColor=colors.white,
  )

  elements.append(Paragraph("<b>AKG SHUTTERINGS PRIVATE LIMITED</b>", title_style))
  elements.append(
      Paragraph(
          f"Rental & Tax Statement — <b>{selected_month_str}</b><br/>"
          f"Billed to: {target_supplier}<br/>"
          f"<b>Period:</b> {start_date_str} to {end_date_str}",
          sub_style,
      )
  )

  table_data = [[
      Paragraph("S.No", header_style),
      Paragraph("Material Description", header_style),
      Paragraph("Basic Rate (₹)", header_style),
      Paragraph("Total Qty", header_style),
      Paragraph("Basic Rent (₹)", header_style),
      Paragraph("Total + 18% Tax (₹)", header_style),
  ]]

  for _, row in report_df.iterrows():
    table_data.append([
        Paragraph(str(row.get("S.No", "")), cell_style),
        Paragraph(str(row.get("Description Of material", "")), cell_style),
        Paragraph(f"{row.get('basic_Rate', 0):,.2f}", cell_style),
        Paragraph(str(row.get("Total_Qty", 0)), cell_style),
        Paragraph(f"{row.get('basic_Rent_Value', 0):,.2f}", cell_style),
        Paragraph(f"{row.get('Total_Tax_18', 0):,.2f}", cell_style),
    ])

  t = Table(table_data, colWidths=[35, 210, 70, 55, 75, 95])
  t.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
          ("ALIGN", (0, 0), (-1, -1), "CENTER"),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
          ("TOPPADDING", (0, 0), (-1, -1), 6),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
      ])
  )
  elements.append(t)
  elements.append(Spacer(1, 15))

  summary_style = ParagraphStyle(
      'SummaryStyle',
      parent=styles['Normal'],
      fontSize=10,
      fontName='Helvetica-Bold',
      textColor=colors.HexColor('#1f2937'),
  )
  elements.append(
      Paragraph(
          f"Total Basic Rent (Without Tax): ₹ {total_basic:,.2f}", summary_style
      )
  )
  elements.append(
      Paragraph(
          f"Total Rent Value (With 18% Tax): ₹ {total_with_tax:,.2f}",
          summary_style,
      )
  )

  doc.build(elements)
  buffer.seek(0)
  return buffer.getvalue()


def generate_stock_ledger_pdf(stock_df, target_supplier, upto_date_str):
  buffer = io.BytesIO()
  doc = SimpleDocTemplate(
      buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
  )
  elements = []
  styles = getSampleStyleSheet()

  title_style = ParagraphStyle(
      'LedgerTitle',
      parent=styles['Heading1'],
      fontSize=16,
      alignment=1,
      textColor=colors.HexColor('#1f2937'),
      spaceAfter=4,
  )
  sub_style = ParagraphStyle(
      'LedgerSub',
      parent=styles['Normal'],
      fontSize=9,
      alignment=1,
      textColor=colors.HexColor('#4b5563'),
      spaceAfter=15,
  )
  cell_style = ParagraphStyle(
      'TableCell', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#1f2937')
  )
  header_style = ParagraphStyle(
      'TableHeader',
      parent=styles['Normal'],
      fontSize=9,
      fontName='Helvetica-Bold',
      textColor=colors.white,
  )

  elements.append(Paragraph("<b>AKG SHUTTERINGS PRIVATE LIMITED</b>", title_style))
  elements.append(
      Paragraph(
          f"Material Stock Ledger Summary (Up to: {upto_date_str})<br/><b>Supplier:</b> {target_supplier}",
          sub_style,
      )
  )

  table_data = [[
      Paragraph("S.No", header_style),
      Paragraph("Material Description", header_style),
      Paragraph("First Received Date", header_style),
      Paragraph("Total Received Qty", header_style),
      Paragraph("Returned Qty", header_style),
      Paragraph("Running Stock At Site", header_style),
  ]]

  for _, row in stock_df.iterrows():
    table_data.append([
        Paragraph(str(row.get("S.No", "")), cell_style),
        Paragraph(str(row.get("Description Of material", "")), cell_style),
        Paragraph(str(row.get("First_Received_Date", "")), cell_style),
        Paragraph(str(row.get("Total_Received_Qty", 0)), cell_style),
        Paragraph(str(row.get("Returned_Qty", 0)), cell_style),
        Paragraph(str(row.get("Running Stock At Site", 0)), cell_style),
    ])

  t = Table(table_data, colWidths=[35, 195, 85, 75, 75, 75])
  t.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
          ("ALIGN", (0, 0), (-1, -1), "CENTER"),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
          ("TOPPADDING", (0, 0), (-1, -1), 6),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
      ])
  )
  elements.append(t)

  doc.build(elements)
  buffer.seek(0)
  return buffer.getvalue()


def generate_receiving_status_landscape_pdf(receiving_df, target_supplier):
  buffer = io.BytesIO()
  # Landscape orientation కోసం landscape(letter) వాడటం జరిగింది
  doc = SimpleDocTemplate(
      buffer, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30
  )
  elements = []
  styles = getSampleStyleSheet()

  title_style = ParagraphStyle(
      'RecTitle',
      parent=styles['Heading1'],
      fontSize=14,
      alignment=1,
      textColor=colors.HexColor('#1f2937'),
      spaceAfter=4,
  )
  sub_style = ParagraphStyle(
      'RecSub',
      parent=styles['Normal'],
      fontSize=9,
      alignment=1,
      textColor=colors.HexColor('#4b5563'),
      spaceAfter=10,
  )
  cell_style = ParagraphStyle(
      'TableCell', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#1f2937')
  )
  header_style = ParagraphStyle(
      'TableHeader',
      parent=styles['Normal'],
      fontSize=8,
      fontName='Helvetica-Bold',
      textColor=colors.white,
  )

  elements.append(Paragraph("<b>AKG SHUTTERINGS PRIVATE LIMITED</b>", title_style))
  elements.append(
      Paragraph(f"Material Receiving Status Report — <b>{target_supplier}</b>", sub_style)
  )

  # టేబుల్ హెడర్స్ తయారీ
  columns_to_show = [
      "S.No",
      "Store Entry No",
      "Actualy Recived Date",
      "Return Date",
      "Description Of material",
      "UOM",
      "Qty",
      "Rate",
      "Total Days",
      "basic Rent Value",
      "Total Rent with 18% Tax",
  ]
  active_cols = [c for c in columns_to_show if c in receiving_df.columns]

  header_row = [Paragraph(str(col), header_style) for col in active_cols]
  table_data = [header_row]

  for _, row in receiving_df.iterrows():
    row_data = [Paragraph(str(row.get(col, "")), cell_style) for col in active_cols]
    table_data.append(row_data)

  # Landscape width కి తగినట్లుగా కాలమ్ విడ్త్స్ సెట్ చేయడం (Total width ~ 730)
  col_widths = [30, 65, 75, 75, 150, 40, 45, 55, 55, 70, 75][:len(active_cols)]
  
  t = Table(table_data, colWidths=col_widths)
  t.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
          ("ALIGN", (0, 0), (-1, -1), "CENTER"),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
          ("TOPPADDING", (0, 0), (-1, -1), 4),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
      ])
  )
  elements.append(t)

  doc.build(elements)
  buffer.seek(0)
  return buffer.getvalue()


def run():
  st.title("📑 AKG SHUTTERINGS PRIVATE LIMITED - Rental, Stock Ledger & Tax")
  st.markdown(
      "Exclusive statement breakdown including Store Entry, Return Dates,"
      " Day-wise Rent, Stock Ledger, and 18% Tax Calculation."
  )

  if "current_df" in st.session_state and not st.session_state.current_df.empty:
    df = st.session_state.current_df.copy()
    sup_col = "Supplier / Sendor Name"

    if sup_col in df.columns:
      target_supplier = "AKG SHUTTERINGS PRIVATE LIMITED"
      sup_invoices = (
          df[df[sup_col] == target_supplier].copy().reset_index(drop=True)
      )

      if "Return Date" not in sup_invoices.columns:
        sup_invoices["Return Date"] = None
      if "Return Date" not in df.columns:
        df["Return Date"] = None

      if "akg_std_rates" not in st.session_state:
        st.session_state.akg_std_rates = {}
      if "akg_bulk_qtys" not in st.session_state:
        st.session_state.akg_bulk_qtys = {}
      if "akg_bulk_returns" not in st.session_state:
        st.session_state.akg_bulk_returns = {}

      if not sup_invoices.empty:
        possible_qty_cols = ["Qty", "Quantity", "Nos", "Receiving Qty"]
        possible_rate_cols = ["Rate", "Unit Rate", "Rent Rate"]

        qty_col = next(
            (c for c in possible_qty_cols if c in sup_invoices.columns), "Qty"
        )
        rate_col = next(
            (c for c in possible_rate_cols if c in sup_invoices.columns),
            "Rate",
        )
        mat_desc_col = next(
            (
                c
                for c in [
                    "Description Of material",
                    "Material Name",
                    "Item Description",
                ]
                if c in sup_invoices.columns
            ),
            None,
        )

        if mat_desc_col:
          for mat_name, std_rate in st.session_state.akg_std_rates.items():
            sup_invoices.loc[
                sup_invoices[mat_desc_col] == mat_name, rate_col
            ] = std_rate
            df.loc[
                (df[sup_col] == target_supplier)
                & (df[mat_desc_col] == mat_name),
                rate_col,
            ] = std_rate

          for mat_name, b_qty in st.session_state.akg_bulk_qtys.items():
            sup_invoices.loc[sup_invoices[mat_desc_col] == mat_name, qty_col] = (
                b_qty
            )
            df.loc[
                (df[sup_col] == target_supplier)
                & (df[mat_desc_col] == mat_name),
                qty_col,
            ] = b_qty

          for mat_name, b_ret in st.session_state.akg_bulk_returns.items():
            sup_invoices.loc[sup_invoices[mat_desc_col] == mat_name, "Return Date"] = (
                b_ret
            )
            df.loc[
                (df[sup_col] == target_supplier)
                & (df[mat_desc_col] == mat_name),
                "Return Date",
            ] = b_ret

        if qty_col not in sup_invoices.columns:
          sup_invoices[qty_col] = 1.0
        if rate_col not in sup_invoices.columns:
          sup_invoices[rate_col] = 0.0

        sup_invoices[qty_col] = pd.to_numeric(
            sup_invoices[qty_col]
            .astype(str)
            .str.replace(r"[^\d.]", "", regex=True),
            errors="coerce",
        ).fillna(0)
        sup_invoices[rate_col] = pd.to_numeric(
            sup_invoices[rate_col]
            .astype(str)
            .str.replace(r"[^\d.]", "", regex=True),
            errors="coerce",
        ).fillna(0)

        if "Actualy Recived Date" in sup_invoices.columns:
          sup_invoices["Actualy Recived Date DT"] = pd.to_datetime(
              sup_invoices["Actualy Recived Date"], errors="coerce"
          )
          sup_invoices["Return Date DT"] = pd.to_datetime(
              sup_invoices["Return Date"], errors="coerce"
          )
          effective_return_dt = sup_invoices["Return Date DT"].fillna(
              pd.to_datetime("today")
          )

          sup_invoices["Total Days"] = (
              effective_return_dt - sup_invoices["Actualy Recived Date DT"]
          ).dt.days
          sup_invoices["Total Days"] = sup_invoices["Total Days"].fillna(1)
          sup_invoices["Total Days"] = sup_invoices["Total Days"].apply(
              lambda x: max(int(x), 1)
          )
          sup_invoices["Calculated Months"] = (
              sup_invoices["Total Days"] / 30.0
          ).round(2)

        sup_invoices["Rent Basis"] = "Day-wise"

        def calc_basic_rent(row):
          qty = row[qty_col]
          rate = row[rate_col]
          days = row.get("Total Days", 1)
          return round(qty * rate * days, 2)

        sup_invoices["basic Rent Value"] = sup_invoices.apply(
            calc_basic_rent, axis=1
        )
        sup_invoices["CGST (9%)"] = (
            sup_invoices["basic Rent Value"] * 0.09
        ).round(2)
        sup_invoices["SGST (9%)"] = (
            sup_invoices["basic Rent Value"] * 0.09
        ).round(2)
        sup_invoices["Total Rent with 18% Tax"] = (
            sup_invoices["basic Rent Value"]
            + sup_invoices["CGST (9%)"]
            + sup_invoices["SGST (9%)"]
        ).round(2)

        if "S.No" in sup_invoices.columns:
          sup_invoices["S.No"] = range(1, len(sup_invoices) + 1)
        else:
          sup_invoices.insert(0, "S.No", range(1, len(sup_invoices) + 1))

        total_inv_amt = sup_invoices["Total Rent with 18% Tax"].sum()

        if (
            "payments_df" in st.session_state
            and not st.session_state.payments_df.empty
        ):
          sup_payments = (
              st.session_state.payments_df[
                  st.session_state.payments_df["Supplier Name"]
                  == target_supplier
              ]
              .copy()
              .reset_index(drop=True)
          )
          if not sup_payments.empty:
            if "S.No" in sup_payments.columns:
              sup_payments["S.No"] = range(1, len(sup_payments) + 1)
            else:
              sup_payments.insert(0, "S.No", range(1, len(sup_payments) + 1))
            total_paid_amt = sup_payments["Paid Amount"].sum()
          else:
            total_paid_amt = 0.0
        else:
          sup_payments = pd.DataFrame()
          total_paid_amt = 0.0

        net_outstanding = total_inv_amt - total_paid_amt

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric(
            "📦 Total Rent Value (inc. 18% Tax)", f"₹ {total_inv_amt:,.2f}"
        )
        col_m2.metric("💳 Total Paid Value", f"₹ {total_paid_amt:,.2f}")
        col_m3.metric("⚠️ Net Outstanding Balance", f"₹ {net_outstanding:,.2f}")

        st.markdown("---")

        with st.expander(
            "✏️ Click Here to Manage Material Settings & Payments",
            expanded=True,
        ):
          tab_p1, tab_p2, tab_p3, tab_p4, tab_p5, tab_p6 = st.tabs(
              [
                  "⚙️ Set Rent Rate",
                  "🔄 Update Return & Qty",
                  "✏️ Edit Material Data",
                  "💳 Add Payment",
                  "📊 Month-wise Report",
                  "📦 Receiving Status",
              ]
          )

          with tab_p1:
            with st.form("akg_bulk_rate_form_v21"):
              st.subheader("Set Rent Rate (Day-wise Basis)")
              if mat_desc_col:
                unique_materials = list(
                    sup_invoices[mat_desc_col].dropna().unique()
                )
                if unique_materials:
                  selected_mat_1 = st.selectbox(
                      "Select Material Name / Description:",
                      unique_materials,
                      key="bulk_mat_select_1_v21",
                  )

                  default_bulk_rate = float(
                      st.session_state.akg_std_rates.get(selected_mat_1, 0.0)
                  )

                  bulk_rate_val = st.number_input(
                      "Rent Rate for this Material (₹ per day)",
                      value=default_bulk_rate,
                      min_value=0.0,
                      format="%.2f",
                  )

                  submitted_bulk_1 = st.form_submit_button("Apply Rate")
                  if submitted_bulk_1:
                    st.session_state.akg_std_rates[selected_mat_1] = (
                        bulk_rate_val
                    )

                    if "Return Date" not in df.columns:
                      df["Return Date"] = None
                    df.loc[
                        (df[sup_col] == target_supplier)
                        & (df[mat_desc_col] == selected_mat_1),
                        rate_col,
                    ] = bulk_rate_val

                    st.session_state.current_df = df
                    st.success(
                        f"Rate updated for '{selected_mat_1}' successfully!"
                    )
                    st.rerun()
                else:
                  st.warning("No materials found.")
              else:
                st.warning("Material description column not available.")

          with tab_p2:
            with st.form("akg_return_qty_form_v21"):
              st.subheader("Update Material Return & Quantity")
              if mat_desc_col:
                unique_materials = list(
                    sup_invoices[mat_desc_col].dropna().unique()
                )
                if unique_materials:
                  selected_mat_2 = st.selectbox(
                      "Select Material Name / Description:",
                      unique_materials,
                      key="bulk_mat_select_2_v21",
                  )

                  mat_rows_check = sup_invoices[
                      sup_invoices[mat_desc_col] == selected_mat_2
                  ]
                  def_qty = (
                      float(mat_rows_check[qty_col].iloc[0])
                      if not mat_rows_check.empty
                      else 1.0
                  )
                  if selected_mat_2 in st.session_state.akg_bulk_qtys:
                    def_qty = st.session_state.akg_bulk_qtys[selected_mat_2]

                  def_ret = (
                      mat_rows_check["Return Date"].iloc[0]
                      if not mat_rows_check.empty
                      else None
                  )
                  if selected_mat_2 in st.session_state.akg_bulk_returns:
                    def_ret = st.session_state.akg_bulk_returns[selected_mat_2]

                  default_date = (
                      pd.to_datetime(def_ret).date()
                      if pd.notnull(def_ret)
                      else datetime.date.today()
                  )

                  col_r1, col_r2 = st.columns(2)
                  with col_r1:
                    bulk_qty_val = st.number_input(
                        "Quantity Returned for this Material",
                        value=def_qty,
                        min_value=0.0,
                        format="%.2f",
                    )
                  with col_r2:
                    bulk_return_date = st.date_input(
                        "Material Return Date", value=default_date
                    )

                  submitted_bulk_2 = st.form_submit_button(
                      "Save Return Details"
                  )
                  if submitted_bulk_2:
                    final_ret_val = str(bulk_return_date)

                    st.session_state.akg_bulk_qtys[selected_mat_2] = (
                        bulk_qty_val
                    )
                    st.session_state.akg_bulk_returns[selected_mat_2] = (
                        final_ret_val
                    )

                    if "Return Date" not in df.columns:
                      df["Return Date"] = None

                    df.loc[
                        (df[sup_col] == target_supplier)
                        & (df[mat_desc_col] == selected_mat_2),
                        qty_col,
                    ] = bulk_qty_val
                    df.loc[
                        (df[sup_col] == target_supplier)
                        & (df[mat_desc_col] == selected_mat_2),
                        "Return Date",
                    ] = final_ret_val

                    st.session_state.current_df = df
                    st.success(
                        f"Return details updated for '{selected_mat_2}'"
                        " successfully!"
                    )
                    st.rerun()
                else:
                  st.warning("No materials found.")
              else:
                st.warning("Material description column not available.")

          with tab_p3:
            st.subheader("Modify Specific Material Records")
            editable_df = sup_invoices[
                [
                    "Store Entry No",
                    "Actualy Recived Date",
                    "Return Date",
                    mat_desc_col,
                    qty_col,
                    rate_col,
                ]
            ].copy()
            editable_df["Original_Index"] = sup_invoices.index

            edited_result_df = st.data_editor(
                editable_df,
                hide_index=True,
                use_container_width=True,
                key="specific_material_data_editor_v21",
            )

            if st.button("Save Modifications", key="save_mod_btn_v21"):
              for idx, row in edited_result_df.iterrows():
                orig_idx = row["Original_Index"]
                df.loc[orig_idx, qty_col] = row[qty_col]
                df.loc[orig_idx, rate_col] = row[rate_col]
                df.loc[orig_idx, "Return Date"] = row["Return Date"]

              st.session_state.current_df = df.copy()
              st.success("Modifications saved successfully!")
              st.rerun()

          with tab_p4:
            with st.form("akg_payment_form_v21"):
              st.subheader("Add Payment Entry")
              st.text_input(
                  "Vendor Name", value=target_supplier, disabled=True
              )
              p_date = st.date_input("Payment Date")
              p_amount = st.number_input(
                  "Paid Amount (₹)", min_value=0.0, format="%.2f"
              )
              p_mode = st.selectbox(
                  "Payment Mode", ["Bank Transfer", "Cheque", "UPI", "Cash"]
              )
              p_ref = st.text_input("Reference / Transaction ID")

              submitted_pay = st.form_submit_button("Save Payment")
              if submitted_pay:
                new_pay_row = {
                    "Supplier Name": target_supplier,
                    "Payment Date": str(p_date),
                    "Paid Amount": p_amount,
                    "Payment Mode": p_mode,
                    "Reference No": p_ref,
                }
                if "payments_df" not in st.session_state:
                  st.session_state.payments_df = pd.DataFrame(
                      columns=[
                          "Supplier Name",
                          "Payment Date",
                          "Paid Amount",
                          "Payment Mode",
                          "Reference No",
                      ]
                  )
                st.session_state.payments_df = pd.concat(
                    [
                        st.session_state.payments_df,
                        pd.DataFrame([new_pay_row]),
                    ],
                    ignore_index=True,
                )
                st.success("Payment saved successfully!")
                st.rerun()

          with tab_p5:
            st.subheader("Month-wise & Material-wise Breakdown Report")

            if (
                "Actualy Recived Date" in sup_invoices.columns
                and mat_desc_col
                and not sup_invoices.empty
            ):
              months_list = [
                  "January",
                  "February",
                  "March",
                  "April",
                  "May",
                  "June",
                  "July",
                  "August",
                  "September",
                  "October",
                  "November",
                  "December",
              ]
              years_list = [2024, 2025, 2026, 2027, 2028]

              col_m_sel, col_y_sel = st.columns(2)
              with col_m_sel:
                current_month_name = datetime.datetime.now().strftime("%B")
                default_m_idx = (
                    months_list.index(current_month_name)
                    if current_month_name in months_list
                    else 0
                )
                selected_month_name = st.selectbox(
                    "📂 Select Month:",
                    months_list,
                    index=default_m_idx,
                    key="akg_dropdown_month_v21",
                )
              with col_y_sel:
                current_year = datetime.datetime.now().year
                default_y_idx = (
                    years_list.index(current_year)
                    if current_year in years_list
                    else 2
                )
                selected_year_val = st.selectbox(
                    "📅 Select Year:",
                    years_list,
                    index=default_y_idx,
                    key="akg_dropdown_year_v21",
                )

              selected_dropdown_month = (
                  f"{selected_month_name} {selected_year_val}"
              )
              st.markdown(
                  f"### Material-wise Active Day-wise Rent for **{selected_dropdown_month}**"
              )

              sel_m_dt = pd.to_datetime(
                  selected_dropdown_month, format="%B %Y"
              )
              month_start = sel_m_dt
              month_end = (sel_m_dt + pd.offsets.MonthEnd(1)).normalize()

              active_rows = []
              for idx, row in sup_invoices.iterrows():
                r_dt = pd.to_datetime(
                    row["Actualy Recived Date"], errors="coerce"
                ).normalize()
                ret_dt = (
                    pd.to_datetime(row["Return Date"], errors="coerce").normalize()
                    if pd.notnull(row["Return Date"])
                    else pd.Timestamp("today").normalize()
                )

                if pd.notnull(r_dt):
                  if r_dt <= month_end and ret_dt >= month_start:
                    effective_start = max(r_dt, month_start)
                    effective_end = min(ret_dt, month_end)
                    days_in_month_overlap = (
                        effective_end - effective_start
                    ).days + 1

                    qty = row[qty_col]
                    rate = row[rate_col]
                    total_days_in_sel_month = (month_end - month_start).days + 1

                    if r_dt <= month_start and ret_dt >= month_end:
                      active_billing_days = total_days_in_sel_month
                    else:
                      active_billing_days = max(days_in_month_overlap, 0)

                    month_basic_rent = round(
                        qty * rate * active_billing_days, 2
                    )

                    row_copy = row.copy()
                    row_copy["Month_basic_Rent"] = month_basic_rent
                    row_copy["Month_Tax_18"] = round(
                        month_basic_rent * 1.18, 2
                    )
                    row_copy["Effective_Start_Date"] = effective_start.strftime(
                        "%d-%m-%Y"
                    )
                    row_copy["Effective_End_Date"] = effective_end.strftime(
                        "%d-%m-%Y"
                    )
                    active_rows.append(row_copy)

              if active_rows:
                month_sub_df = pd.DataFrame(active_rows)
                material_report = (
                    month_sub_df.groupby(mat_desc_col)
                    .agg(
                        basic_Rate=(rate_col, "first"),
                        Total_Qty=(qty_col, "sum"),
                        basic_Rent_Value=("Month_basic_Rent", "sum"),
                        Total_Tax_18=("Month_Tax_18", "sum"),
                        Min_Start=("Effective_Start_Date", "min"),
                        Max_End=("Effective_End_Date", "max"),
                    )
                    .reset_index()
                )

                material_report["basic_Rate"] = material_report[
                    "basic_Rate"
                ].round(2)
                material_report["basic_Rent_Value"] = material_report[
                    "basic_Rent_Value"
                ].round(2)
                material_report["Total_Tax_18"] = material_report[
                    "Total_Tax_18"
                ].round(2)

                if "S.No" in material_report.columns:
                  material_report["S.No"] = range(1, len(material_report) + 1)
                else:
                  material_report.insert(
                      0, "S.No", range(1, len(material_report) + 1)
                  )

                st.dataframe(
                    material_report,
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "S.No": st.column_config.NumberColumn(
                            "S.No", width="small"
                        ),
                        mat_desc_col: st.column_config.TextColumn(
                            "Material Description", width="large"
                        ),
                        "basic_Rate": st.column_config.NumberColumn(
                            "Basic Rate (₹)", format="₹ %.2f", width="medium"
                        ),
                        "Total_Qty": st.column_config.NumberColumn(
                            "Total Qty", width="small"
                        ),
                        "basic_Rent_Value": st.column_config.NumberColumn(
                            "Basic Rent (₹)", format="₹ %.2f", width="medium"
                        ),
                        "Total_Tax_18": st.column_config.NumberColumn(
                            "Total + 18% Tax (₹)",
                            format="₹ %.2f",
                            width="medium",
                        ),
                        "Min_Start": st.column_config.TextColumn("Start Date"),
                        "Max_End": st.column_config.TextColumn("Up-to Date"),
                    },
                    key="mat_report_active_table_v21",
                )

                total_month_basic_rent = material_report[
                    "basic_Rent_Value"
                ].sum()
                total_month_tax_rent = material_report["Total_Tax_18"].sum()

                overall_start_str = (
                    material_report["Min_Start"].min()
                    if not material_report.empty
                    else month_start.strftime("%d-%m-%Y")
                )
                overall_end_str = (
                    material_report["Max_End"].max()
                    if not material_report.empty
                    else month_end.strftime("%d-%m-%Y")
                )

                st.markdown(
                    f"**📊 Total Rent Breakdown for {selected_dropdown_month}:**"
                )
                col_tot1, col_tot2 = st.columns(2)
                col_tot1.metric(
                    "Total Basic Rent (Without Tax)",
                    f"₹ {total_month_basic_rent:,.2f}",
                )
                col_tot2.metric(
                    "Total Rent Value (With 18% Tax)",
                    f"₹ {total_month_tax_rent:,.2f}",
                )

                st.markdown("")
                pdf_bytes = generate_akg_pdf_invoice(
                    material_report,
                    selected_dropdown_month,
                    target_supplier,
                    total_month_basic_rent,
                    total_month_tax_rent,
                    overall_start_str,
                    overall_end_str,
                )
                st.download_button(
                    label="📥 Download Active Rent Invoice (PDF)",
                    data=pdf_bytes,
                    file_name=f"AKG_Invoice_{selected_month_name}_{selected_year_val}.pdf",
                    mime="application/pdf",
                    key="download_pdf_invoice_btn_v21",
                )

              else:
                st.info(
                    f"No active materials found for {selected_dropdown_month}."
                )
            else:
              st.info("Insufficient data available.")

          with tab_p6:
            st.subheader("📦 AKG Shutterings Material Receiving Status")
            desired_cols = [
                "S.No",
                "Store Entry No",
                "Actualy Recived Date",
                "Return Date",
                "Work Order No",
                "Description Of material",
                "UOM",
                qty_col,
                rate_col,
                "Rent Basis",
                "Total Days",
                "Calculated Months",
                "basic Rent Value",
                "CGST (9%)",
                "SGST (9%)",
                "Total Rent with 18% Tax",
            ]
            existing_cols = [c for c in desired_cols if c and c in sup_invoices.columns]
            other_cols = [c for c in sup_invoices.columns if c not in existing_cols]
            ordered_sup_invoices = sup_invoices[existing_cols + other_cols]

            st.dataframe(
                ordered_sup_invoices,
                hide_index=True,
                use_container_width=True,
                key="akg_inv_table_v21",
            )

            st.markdown("")
            # మెటీరియల్ రిసీవింగ్ స్టేటస్ కోసం హారిజాంటల్ (Landscape) PDF డౌన్‌లోడ్ బటన్
            rec_pdf_bytes = generate_receiving_status_landscape_pdf(ordered_sup_invoices, target_supplier)
            st.download_button(
                label="📥 Download Material Receiving Status (Landscape PDF)",
                data=rec_pdf_bytes,
                file_name="AKG_Material_Receiving_Status_Landscape.pdf",
                mime="application/pdf",
                key="download_receiving_status_landscape_pdf_v21",
            )

        st.markdown("---")
        st.subheader(
            "📦 Material Stock Ledger Summary (Cumulative Up to Date)"
        )

        col_d1, col_d2 = st.columns([2, 2])
        with col_d1:
          ledger_upto_date = st.date_input(
              "📅 Select Ledger Up to Date:",
              value=datetime.date.today(),
              key="ledger_calendar_upto_date_v21",
          )

        ledger_upto_ts = pd.to_datetime(ledger_upto_date).normalize()

        if mat_desc_col:
          filtered_stock_df = sup_invoices.copy()
          filtered_stock_df["Parsed_Recv_Date"] = pd.to_datetime(
              filtered_stock_df["Actualy Recived Date"], errors="coerce"
          ).dt.normalize()

          filtered_stock_df = filtered_stock_df[
              filtered_stock_df["Parsed_Recv_Date"] <= ledger_upto_ts
          ]

          if not filtered_stock_df.empty:
            filtered_stock_df["Is Returned Flag"] = filtered_stock_df[
                "Return Date"
            ].notnull()

            stock_summary = (
                filtered_stock_df.groupby(mat_desc_col)
                .agg(
                    First_Received_Date=("Parsed_Recv_Date", "min"),
                    Total_Received_Qty=(qty_col, "sum"),
                    Returned_Qty=(
                        qty_col,
                        lambda x: sum(
                            x[filtered_stock_df.loc[x.index, "Is Returned Flag"]]
                        ),
                    ),
                )
                .reset_index()
            )

            stock_summary["First_Received_Date"] = pd.to_datetime(
                stock_summary["First_Received_Date"]
            ).dt.strftime("%d-%m-%Y")

            stock_summary["Running Stock At Site"] = (
                stock_summary["Total_Received_Qty"]
                - stock_summary["Returned_Qty"]
            )

            if "S.No" in stock_summary.columns:
              stock_summary["S.No"] = range(1, len(stock_summary) + 1)
            else:
              stock_summary.insert(
                  0, "S.No", range(1, len(stock_summary) + 1)
              )

            st.dataframe(
                stock_summary,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "S.No": st.column_config.NumberColumn("S.No", width="small"),
                    mat_desc_col: st.column_config.TextColumn(
                        "Material Description", width="large"
                    ),
                    "First_Received_Date": st.column_config.TextColumn(
                        "First Received Date", width="medium"
                    ),
                    "Total_Received_Qty": st.column_config.NumberColumn(
                        "Total Received Qty", width="small"
                    ),
                    "Returned_Qty": st.column_config.NumberColumn(
                        "Returned Qty", width="small"
                    ),
                    "Running Stock At Site": st.column_config.NumberColumn(
                        "Running Stock At Site", width="small"
                    ),
                },
                key="akg_stock_ledger_table_v21",
            )

            st.markdown("")
            stock_pdf_bytes = generate_stock_ledger_pdf(
                stock_summary, target_supplier, ledger_upto_date.strftime("%d-%m-%Y")
            )
            st.download_button(
                label="📥 Download Stock Ledger Summary (PDF)",
                data=stock_pdf_bytes,
                file_name=f"AKG_Material_Stock_Ledger_Up_To_{ledger_upto_date}.pdf",
                mime="application/pdf",
                key="download_stock_ledger_pdf_btn_v21",
            )
          else:
            st.info("No records found up to the selected date.")
        else:
          st.info("Material description column not found for stock ledger.")

        st.markdown("---")
        st.subheader("💳 Payment Disbursement Log — AKG Shutterings")
        if not sup_payments.empty:
          st.dataframe(
              sup_payments,
              hide_index=True,
              use_container_width=True,
              key="akg_pay_table_v21",
          )
        else:
          st.info("No payment transactions recorded for this vendor yet.")
      else:
        st.warning("No records found for 'AKG SHUTTERINGS PRIVATE LIMITED'.")
    else:
      st.error("Supplier column not detected in dataset.")
  else:
    st.info("Please load data records first from the main upload page.")
