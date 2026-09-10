import datetime
import pandas as pd
import streamlit as st


def run():
  st.title("📊 SITE-CGD OFFICE BUILDING, MAHESHWARAM")
  st.markdown("### PROJECT : MCGDPL6111 (MIPL) — Daily Staff & Manpower Report")

  # టాప్ డేట్ మరియు డే డిస్‌ప్లే
  col_h1, col_h2 = st.columns([2, 1])
  with col_h1:
    report_date = st.date_input("📅 Select Report Date:", datetime.date.today())
  with col_h2:
    day_name = report_date.strftime("%A")
    st.info(f"**Day:** {day_name}")

  st.markdown("---")

  # టేబుల్స్ క్లియర్‌గా కనిపించడానికి టూ కాలమ్స్ లేఅవుట్
  col1, col2 = st.columns([1, 1])

  # --- 1. STAFF REPORT SECTION ---
  with col1:
    st.subheader("👥 STAFF REPORT")

    default_staff_data = [
        {
            "S.No": 1,
            "Employee Name": "Mr. M.Sridhar Reddy",
            "Department": "Site Incharge",
            "Status": "Present",
        },
        {
            "S.No": 2,
            "Employee Name": "Mr. Ch.Satish Reddy",
            "Department": "Stores",
            "Status": "Present",
        },
        {
            "S.No": 3,
            "Employee Name": "Mr. J.Srikanth Reddy",
            "Department": "Admin",
            "Status": "Present",
        },
        {
            "S.No": 4,
            "Employee Name": "Mr. G.Laxmana Rao - Sr.Engr",
            "Department": "Civil",
            "Status": "Present",
        },
        {
            "S.No": 5,
            "Employee Name": "Mr. A.Satyanarayana - Executive",
            "Department": "Stores",
            "Status": "Present",
        },
        {
            "S.No": 6,
            "Employee Name": "Mr. D.Veeraiah - GET",
            "Department": "Civil",
            "Status": "Present",
        },
        {
            "S.No": 7,
            "Employee Name": "Mr. B.Shiva - Supervisor",
            "Department": "Stores",
            "Status": "Present",
        },
        {
            "S.No": 8,
            "Employee Name": "Mr. G.Kurma Rao - Electrician",
            "Department": "Electrician",
            "Status": "Present",
        },
        {
            "S.No": 9,
            "Employee Name": "Mr. B.Ramesh -(Tower Crane)",
            "Department": "Operator",
            "Status": "Present",
        },
    ]

    staff_df = pd.DataFrame(default_staff_data)

    edited_staff_df = st.data_editor(
        staff_df,
        hide_index=True,
        use_container_width=True,
        height=380,  # టేబుల్ సైజ్ పర్ఫెక్ట్ గా కనిపించడానికి హైట్ సెట్ చేశాం
        key="staff_report_table",
    )

    staff_total = len(edited_staff_df[edited_staff_df["Status"] == "Present"])
    st.markdown(f"**STAFF TOTAL (Present):** `{staff_total}`")

  # --- 2. MANPOWER REPORT SECTION ---
  with col2:
    st.subheader("👷 MANPOWER REPORT")

    st.markdown("##### 1. Sub-Contractor Manpower Details")
    sub_data = [
        {
            "Sub-Contractor Details": (
                "Steel reinforcement, shuttering, concreting & shifting"
            ),
            "Mr. NVVS Murthi": 13,
            "Mr. Keshava": 0,
        }
    ]
    sub_df = pd.DataFrame(sub_data)
    edited_sub_df = st.data_editor(
        sub_df,
        hide_index=True,
        use_container_width=True,
        height=100,
        key="sub_contractor_table",
    )

    st.markdown("##### 2. NMR Manpower Details")
    nmr_data = [
        {
            "NMR Type": "A. NMR Regular Staff (MD Murshad)",
            "Mestri": 1,
            "Helper": 2,
        },
        {
            "NMR Type": "B. NMR Daily Wage (Local Labour)",
            "Mestri": 0,
            "Helper": 0,
        },
    ]
    nmr_df = pd.DataFrame(nmr_data)
    edited_nmr_df = st.data_editor(
        nmr_df,
        hide_index=True,
        use_container_width=True,
        height=120,
        key="nmr_table",
    )

    st.markdown("##### 3. Hired Vehicle Details")
    vehicle_data = [
        {"Vehicle Type": "A. Hydra", "Helper": 0, "Operator": 0},
        {"Vehicle Type": "B. JCB", "Helper": 0, "Operator": 0},
        {"Vehicle Type": "C. Tractor", "Helper": 0, "Operator": 0},
        {"Vehicle Type": "D. Rollers", "Helper": 0, "Operator": 0},
    ]
    vehicle_df = pd.DataFrame(vehicle_data)
    edited_vehicle_df = st.data_editor(
        vehicle_df,
        hide_index=True,
        use_container_width=True,
        height=170,
        key="vehicle_table",
    )

    st.markdown("##### 4. Security Details")
    security_data = [
        {"Security Details": "A. Supervisor (Day/Night)", "Day": 1, "Night": 1},
        {
            "Security Details": "B. Security Guards (Day/Night)",
            "Day": 1,
            "Night": 1,
        },
    ]
    security_df = pd.DataFrame(security_data)
    edited_security_df = st.data_editor(
        security_df,
        hide_index=True,
        use_container_width=True,
        height=110,
        key="security_table",
    )

    sub_manpower_total = (
        edited_sub_df["Mr. NVVS Murthi"].sum()
        + edited_sub_df["Mr. Keshava"].sum()
        + edited_nmr_df["Mestri"].sum()
        + edited_nmr_df["Helper"].sum()
        + edited_security_df["Day"].sum()
        + edited_security_df["Night"].sum()
    )
    st.markdown(f"**MANPOWER SUBTOTAL:** `{sub_manpower_total}`")

  st.markdown("---")

  # --- TOTAL HEADCOUNT SUMMARY ---
  total_headcount = staff_total + sub_manpower_total

  st.success(
      f"### 🎯 TOTAL HEADCOUNT (STAFF & MANPOWER): **{total_headcount}**"
  )
