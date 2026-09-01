import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Store Management System", layout="wide")

# Initialize Session State variables
if 'current_df' not in st.session_state:
    st.session_state.current_df = pd.DataFrame()
if 'custom_suppliers' not in st.session_state:
    st.session_state.custom_suppliers = []
if 'custom_materials' not in st.session_state:
    st.session_state.custom_materials = []

standard_columns = [
    'S.No', 'Store Entry No', 'Actualy Recived Date', 'GRN No', 
    'GRN Date', 'Supplier / Sendor Name', 'Description Of material', 
    'UOM', 'PO No', 'Invoice No', 'date', 'Receiving Qty', 'unit rate', 
    'CGST', 'SGST', 'Fright', 'Inovice value', 
    'Vechile Number', 'Type Reciept', 'Remarks'
]

# Sidebar Navigation
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("పేజీని ఎంచుకోండి:", [
    "1. Home / Dashboard", 
    "2. Material Register View", 
    "3. New Record Creation", 
    "4. All Suppliers List", 
    "5. Material List"
])

# ================= PAGE 1: HOME =================
if page == "1. Home / Dashboard":
    st.title("📦 Store Management System")
    st.markdown("### స్వాగతం! దయచేసి ఎక్సెల్ ఫైల్‌ను అప్‌లోడ్ చేయండి లేదా సైడ్‌బార్ ద్వారా ఇతర పేజీలకు వెళ్లండి.")
    
    uploaded_file = st.file_uploader("📁 మీ ఎక్సెల్ ఫైల్‌ని ఇక్కడ అప్‌లోడ్ చేయండి", type=["xlsx", "xls"])
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file, sheet_name=0)
            mapped_data = pd.DataFrame()
            
            # Map columns safely
            qty_excel_col = None
            for c in df.columns:
                c_lower = str(c).strip().lower()
                if 'qty' in c_lower or 'quantity' in c_lower or 'recieved' in c_lower or 'receiving' in c_lower:
                    qty_excel_col = c
                    break

            for std_col in standard_columns:
                if std_col == 'S.No':
                    continue
                if std_col == 'Receiving Qty' and qty_excel_col:
                    mapped_data[std_col] = df[qty_excel_col]
                    continue

                found_col = None
                for excel_col in df.columns:
                    if str(excel_col).strip().lower() == std_col.strip().lower():
                        found_col = excel_col
                        break
                
                if found_col:
                    mapped_data[std_col] = df[found_col]
                else:
                    mapped_data[std_col] = 0.0 if std_col in ['unit rate', 'CGST', 'SGST', 'Fright', 'Inovice value', 'Receiving Qty'] else ""

            mapped_data = mapped_data.replace({np.nan: "", "nan": "", "NaN": ""})
            mapped_data.insert(0, 'S.No', range(1, len(mapped_data) + 1))
            
            st.session_state.current_df = mapped_data
            st.success("ఎక్సెల్ డేటా విజయవంతంగా లోడ్ చేయబడింది!")
        except Exception as e:
            st.error(f"ఎర్రర్: {e}")

# ================= PAGE 2: REGISTER VIEW =================
elif page == "2. Material Register View":
    st.title("📊 Page 2: Material Inward Register")
    
    if st.session_state.current_df.empty:
        st.warning("దయచేసి ముందుగా హోమ్ పేజీలో ఎక్సెల్ ఫైల్ అప్‌లోడ్ చేయండి.")
    else:
        df_show = st.session_state.current_df.copy()
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            suppliers = ['All'] + list(df_show['Supplier / Sendor Name'].dropna().unique())
            sel_supp = st.selectbox("Supplier Filter", suppliers)
        with col2:
            pos = ['All'] + list(df_show['PO No'].dropna().unique())
            sel_po = st.selectbox("PO No Filter", pos)
        with col3:
            receipts = ['All'] + list(df_show['Type Reciept'].dropna().unique())
            sel_rec = st.selectbox("Receipt Type Filter", receipts)

        # Apply filtering
        if sel_supp != 'All':
            df_show = df_show[df_show['Supplier / Sendor Name'] == sel_supp]
        if sel_po != 'All':
            df_show = df_show[df_show['PO No'] == sel_po]
        if sel_rec != 'All':
            df_show = df_show[df_show['Type Reciept'] == sel_rec]

        st.dataframe(df_show, use_container_width=True)

# ================= PAGE 3: NEW ENTRY =================
elif page == "3. New Record Creation":
    st.title("➕ Page 3: New Material Inward Creation")
    
    with st.form("new_entry_form"):
        new_row = {}
        cols_to_input = [col for col in standard_columns if col not in ['S.No', 'Inovice value']]
        
        for col in cols_to_input:
            new_row[col] = st.text_input(f"{col}")
            
        submitted = st.form_submit_button("💾 సేవ్ చేయండి (Save Record)")
        if submitted:
            new_row['S.No'] = len(st.session_state.current_df) + 1
            # Calculate invoice value
            try:
                qty = float(new_row.get('Receiving Qty', 1) or 1)
                u_rate = float(new_row.get('unit rate', 0) or 0)
                cgst = float(new_row.get('CGST', 0) or 0)
                sgst = float(new_row.get('SGST', 0) or 0)
                fright = float(new_row.get('Fright', 0) or 0)
                new_row['Inovice value'] = (u_rate * qty) + cgst + sgst + fright
            except:
                new_row['Inovice value'] = 0.0

            new_df = pd.DataFrame([new_row])
            st.session_state.current_df = pd.concat([st.session_state.current_df, new_df], ignore_index=True)
            st.success("కొత్త రికార్డు విజయవంతంగా జోడించబడింది!")

# ================= PAGE 4: SUPPLIERS =================
elif page == "4. All Suppliers List":
    st.title("🏢 Page 4: All Suppliers Record List")
    
    new_supp = st.text_input("➕ కొత్త Supplier పేరు జోడించండి:")
    if st.button("Add Supplier"):
        if new_supp and new_supp not in st.session_state.custom_suppliers:
            st.session_state.custom_suppliers.append(new_supp)
            st.success(f"Supplier '{new_supp}' జోడించబడింది!")

    if not st.session_state.current_df.empty and 'Supplier / Sendor Name' in st.session_state.current_df.columns:
        suppliers = list(st.session_state.current_df['Supplier / Sendor Name'].dropna().unique()) + st.session_state.custom_suppliers
        st.write(list(set(suppliers)))
    else:
        st.info("డేటా అందుబాటులో లేదు.")

# ================= PAGE 5: MATERIALS =================
elif page == "5. Material List":
    st.title("📦 Page 5: All Materials Record List")
    
    new_mat = st.text_input("➕ కొత్త Material Description జోడించండి:")
    if st.button("Add Material"):
        if new_mat and new_mat not in st.session_state.custom_materials:
            st.session_state.custom_materials.append(new_mat)
            st.success(f"Material '{new_mat}' జోడించబడింది!")

    if not st.session_state.current_df.empty and 'Description Of material' in st.session_state.current_df.columns:
        materials = list(st.session_state.current_df['Description Of material'].dropna().unique()) + st.session_state.custom_materials
        st.write(list(set(materials)))
    else:
        st.info("డేటా అందుబాటులో లేదు.")