
def run_evaluation_logic(df_input_for_eval: pd.DataFrame, evaluator: Evaluator):
    """
    Encapsulates the evaluation running logic, including pre-populating reviewer's result.
    Returns the evaluated DataFrame or None if prerequisites are not met.
    """
    if 'llm_output' not in df_input_for_eval.columns or df_input_for_eval['llm_output'].astype(str).str.strip().replace('', pd.NA).isnull().all():
        st.error("The 'llm_output' column is missing or empty. Fetch responses or ensure your data includes it.")
        return None
    if not st.session_state.main_selected_metrics:
        st.warning("Please select at least one metric for evaluation in the 'Configure Evaluation Settings' section.")
        return None

    with st.spinner("Crunching the numbers... Evaluation in progress! 🧠"):
        try:
            sensitive_keywords_list = []
            if "Safety" in st.session_state.main_selected_metrics and DEVELOPER_MODE:
                sensitive_keywords_list = [k.strip().lower() for k in st.session_state.main_sensitive_keywords_input.split(',') if k.strip()]
            eval_custom_thresh = st.session_state.main_custom_thresholds if st.session_state.main_use_custom_thresholds else None
            
            automated_overall_col = "Automated Overall Result"
            reviewer_final_col = "Reviewer's Final Result"
            initial_verdict_col = "initial_reviewer_verdict" 

            evaluated_data_from_engine = evaluator.evaluate_dataframe(
                df_input_for_eval.copy(), # Pass a copy to evaluator
                st.session_state.main_selected_metrics,
                custom_thresholds=eval_custom_thresh, 
                sensitive_keywords=sensitive_keywords_list,
                overall_pass_criterion=st.session_state.main_overall_criterion
            )
            
            final_evaluated_df = evaluated_data_from_engine.copy()
            final_evaluated_df[reviewer_final_col] = pd.NA 

            # Pre-populate Reviewer's Final Result from initial_reviewer_verdict in df_input_for_eval (which is original_df)
            if initial_verdict_col in df_input_for_eval.columns:
                for index, row in df_input_for_eval.iterrows():
                    initial_verdict = row.get(initial_verdict_col)
                    if pd.notna(initial_verdict) and initial_verdict in ['Pass', 'Fail', 'N/A', 'Error']:
                        if index in final_evaluated_df.index:
                            final_evaluated_df.loc[index, reviewer_final_col] = initial_verdict
            
            if automated_overall_col in final_evaluated_df.columns:
                final_evaluated_df[reviewer_final_col] = final_evaluated_df[reviewer_final_col].fillna(
                    final_evaluated_df[automated_overall_col]
                )
            final_evaluated_df[reviewer_final_col] = final_evaluated_df[reviewer_final_col].fillna('N/A')
            
            st.session_state.df_evaluated = final_evaluated_df.copy()
            st.session_state.show_results = True
            st.session_state.selected_metrics_for_results = st.session_state.main_selected_metrics[:]
            st.session_state.custom_thresholds_for_results = eval_custom_thresh.copy() if eval_custom_thresh else None
            st.session_state.show_tutorial = False; st.session_state.agreement_calculated = False
            st.success("Evaluation Complete!")
            return st.session_state.df_evaluated
        except Exception as e: 
            st.error(f"Evaluation Error: {e}"); st.exception(e)
            return None


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
