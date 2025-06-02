# lines 236 

        # Buttons for Run Evaluation and the new combined button
        st.markdown("---") # Separator before action buttons
        col_run_eval, col_fetch_and_eval = st.columns(2)

        with col_run_eval:
            if st.button("🚀 Run Evaluation Only", help="Evaluates current data (assumes 'llm_output' is present).", use_container_width=True):
                if not st.session_state.df_original.empty:
                    evaluated_df = run_evaluation_logic(st.session_state.df_original, evaluator)
                    if evaluated_df is not None: st.rerun() # Rerun to show results
                else:
                    st.warning("Please upload data first.")
        
        with col_fetch_and_eval:
            if st.button("🎯 Fetch Responses & Evaluate", help="Fetches bot responses then immediately runs evaluation.", use_container_width=True):
                if not st.session_state.df_original.empty:
                    if 'query' not in st.session_state.df_original.columns:
                        st.error("Data needs a 'query' column to fetch responses.")
                    else:
                        # Step 1: Fetch responses
                        with st.spinner("Step 1/2: Fetching bot responses..."):
                            updated_df_for_eval = fetch_bot_responses_for_df_streamlit_with_progress(
                                st.session_state.df_original.copy(), 'query', st.session_state.selected_domain_key
                            )
                        # Update df_original with fetched responses *before* evaluation
                        st.session_state.df_original = updated_df_for_eval.copy() 
                        
                        # Step 2: Run evaluation on the updated data
                        if 'llm_output' in updated_df_for_eval.columns and not updated_df_for_eval['llm_output'].astype(str).str.strip().replace('', pd.NA).isnull().all():
                            st.info("Responses fetched. Now running evaluation...")
                            evaluated_df = run_evaluation_logic(updated_df_for_eval, evaluator) # Pass the df with fetched responses
                            if evaluated_df is not None: st.rerun() # Rerun to show results
                        else:
                            st.error("Fetching responses failed or resulted in empty outputs. Evaluation cannot proceed.")
                else:
                    st.warning("Please upload data first.")
