# Tab 3: Edit Specific Material Data (Fixed Saving Issue)
          with tab_p3:
            st.subheader("Modify Specific Material Records")
            st.markdown(
                "ఇక్కడ మీరు నేరుగా టేబుల్‌లో క్వాంటిటీ, రేట్ లేదా రిటర్న్ డేట్ మార్చి"
                " **Save Modifications** బటన్ నొక్కండి."
            )

            # ఎడిట్ చేయడానికి అవసరమైన కాలమ్స్‌తో టేబుల్ తయారు చేయడం
            editable_df = filtered_sup_invoices[
                [
                    "Store Entry No",
                    "Actualy Recived Date",
                    "Return Date",
                    mat_desc_col,
                    qty_col,
                    rate_col,
                ]
            ].copy()

            # Unique identification కోసం తాత్కాలికంగా ఇండెక్స్ యాడ్ చేయడం
            editable_df["Original_Index"] = filtered_sup_invoices.index

            edited_result_df = st.data_editor(
                editable_df,
                hide_index=True,
                use_container_width=True,
                key="specific_material_data_editor",
            )

            if st.button("Save Modifications", key="save_mod_btn"):
              # యూజర్ చేసిన మార్పులను మెయిన్ df లోకి అప్‌డేట్ చేయడం
              for idx, row in edited_result_df.iterrows():
                orig_idx = row["Original_Index"]

                # మెయిన్ df లో వాల్యూస్ అప్‌డేట్ చేయడం
                df.loc[orig_idx, qty_col] = row[qty_col]
                df.loc[orig_idx, rate_col] = row[rate_col]
                df.loc[orig_idx, "Return Date"] = row["Return Date"]

              # సెషన్ స్టేట్‌లో సేవ్ చేయడం
              st.session_state.current_df = df.copy()
              st.success("మార్పులు విజయవంతంగా సేవ్ చేయబడ్డాయి!")
              st.rerun()
