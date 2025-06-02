# # llm_eval_package/ui/results_view.py
# import streamlit as st
# import pandas as pd
# from llm_eval_package.config import METRIC_THRESHOLDS, INTERPRETATION_CONFIG

# class ResultsView:
#     def __init__(self):
#         pass

#     def render_results(self, df_evaluated_to_edit: pd.DataFrame, selected_metrics: list, 
#                        custom_thresholds: dict = None, 
#                        automated_overall_col_name: str = "Automated Overall Result",
#                        reviewer_override_column: str = "Reviewer's Final Result"
#                        ) -> pd.DataFrame: 
#         if df_evaluated_to_edit.empty:
#             st.warning("No evaluation results to display.")
#             return df_evaluated_to_edit.copy()

#         st.header("📊 Evaluation Results")
#         current_thresholds = custom_thresholds if custom_thresholds is not None else METRIC_THRESHOLDS.copy()
        
#         df_display_and_edit = df_evaluated_to_edit.copy()

#         # Ensure essential result columns exist
#         if automated_overall_col_name not in df_display_and_edit.columns:
#             df_display_and_edit[automated_overall_col_name] = pd.NA 
        
#         allowed_override_values = ['Pass', 'Fail', 'N/A', 'Error']
#         if reviewer_override_column not in df_display_and_edit.columns:
#             df_display_and_edit[reviewer_override_column] = df_display_and_edit[automated_overall_col_name].fillna('N/A')
#         df_display_and_edit[reviewer_override_column] = df_display_and_edit[reviewer_override_column].apply(
#             lambda x: str(x) if pd.notna(x) and str(x) in allowed_override_values else 'N/A'
#         )

#         summary_col_for_display = reviewer_override_column
#         self._display_overall_summary(df_display_and_edit, 
#                                       summary_pass_fail_col=summary_col_for_display, 
#                                       evaluator_pass_fail_col=automated_overall_col_name)
        
#         self._display_metric_performance_and_insights(df_display_and_edit, selected_metrics, current_thresholds)

#         edited_df_from_editor = self._display_detailed_results_editable( # Renamed method
#             df_display_and_edit, selected_metrics, current_thresholds, 
#             automated_overall_col_name=automated_overall_col_name,
#             reviewer_override_column=reviewer_override_column
#         )

#         if 'test_config' in edited_df_from_editor.columns:
#             valid_configs = edited_df_from_editor['test_config'].dropna().unique()
#             if len(valid_configs) > 0 :
#                 st.markdown("---"); st.subheader("📋 Summary by Test Configuration")
#                 df_for_configs = edited_df_from_editor.copy()
#                 df_for_configs['test_config_filled'] = df_for_configs['test_config'].fillna("Uncategorized")
#                 unique_test_configs_display = sorted(df_for_configs['test_config_filled'].unique())
#                 for config_name_display in unique_test_configs_display:
#                     config_df_subset = df_for_configs[df_for_configs['test_config_filled'] == config_name_display]
#                     if not config_df_subset.empty:
#                         with st.expander(f"Results for: **{config_name_display}** ({len(config_df_subset)} test cases)"):
#                             self._display_overall_summary(config_df_subset, 
#                                                           summary_pass_fail_col=summary_col_for_display,
#                                                           evaluator_pass_fail_col=automated_overall_col_name, 
#                                                           is_group_summary=True)
#         return edited_df_from_editor

#     def _display_overall_summary(self, df_summary: pd.DataFrame, 
#                                  summary_pass_fail_col: str, 
#                                  evaluator_pass_fail_col: str, 
#                                  is_group_summary: bool = False):
#         # ... (This method remains the same as provided in the previous response) ...
#         if not is_group_summary: st.subheader("Overall Summary")
#         total_rows = len(df_summary)
#         st.write(f"Total test cases in this group: **{total_rows}**")
#         if total_rows > 0 and summary_pass_fail_col in df_summary.columns:
#             valid_mask = df_summary[summary_pass_fail_col].isin(['Pass', 'Fail'])
#             num_valid = valid_mask.sum()
#             passed = (df_summary.loc[valid_mask, summary_pass_fail_col] == 'Pass').sum()
#             failed = num_valid - passed
#             other = total_rows - num_valid
#             pass_rate = (passed / num_valid) * 100 if num_valid > 0 else 0.0
#             summary_col_label = "Reviewer's Final" if summary_pass_fail_col == "Reviewer's Final Result" else "Automated"
#             st.metric(label=f"**{summary_col_label} Test Case Pass Rate**", value=f"{pass_rate:.2f}%")
#             st.caption(f"Passed: {passed}, Failed: {failed}, Other (Error/N/A): {other} out of {total_rows}")
#             if summary_pass_fail_col == "Reviewer's Final Result" and evaluator_pass_fail_col in df_summary.columns and evaluator_pass_fail_col != summary_pass_fail_col:
#                 eval_valid_mask = df_summary[evaluator_pass_fail_col].isin(['Pass', 'Fail'])
#                 eval_num_valid = eval_valid_mask.sum()
#                 eval_passed = (df_summary.loc[eval_valid_mask, evaluator_pass_fail_col] == 'Pass').sum()
#                 eval_rate = (eval_passed / eval_num_valid) * 100 if eval_num_valid > 0 else 0.0
#                 st.caption(f"(Automated Overall Pass Rate: {eval_rate:.2f}%)")
#             st.markdown("---")
#         elif total_rows > 0 : 
#              st.caption(f"Note: Summary column '{summary_pass_fail_col}' not found or had no valid 'Pass'/'Fail' values.")
#              st.markdown("---")

#     def _display_metric_performance_and_insights(self, df_evaluated: pd.DataFrame, selected_metrics: list, current_thresholds: dict):
#         # ... (This method remains the same - it uses the full df_evaluated which has all metric P/F and scores) ...
#         st.subheader("💡 Metric Performance & Explanations")
#         if not selected_metrics: st.caption("No metrics selected."); return
#         st.markdown("##### Detailed Metric Breakdown (Across All Data):")
#         cols_per_row = min(len(selected_metrics), 3)
#         metric_cols_display = st.columns(cols_per_row)
#         col_idx = 0
#         for metric in selected_metrics:
#             with metric_cols_display[col_idx % cols_per_row]:
#                 st.markdown(f"**{metric}**")
#                 pf_col = f'{metric} Pass/Fail' # This column exists in df_evaluated
#                 if pf_col in df_evaluated.columns:
#                     counts = df_evaluated[pf_col].value_counts()
#                     pass_m, fail_m = counts.get('Pass', 0), counts.get('Fail', 0)
#                     other_m = len(df_evaluated) - (pass_m + fail_m)
#                     rate_m = (pass_m / (pass_m + fail_m)) * 100 if (pass_m + fail_m) > 0 else 0.0
#                     st.markdown(f"Pass Rate: **{rate_m:.1f}%** (P:{pass_m}, F:{fail_m}, O:{other_m})")
#                 score_col = f'{metric} Score' # This column also exists in df_evaluated
#                 if score_col in df_evaluated.columns:
#                     num_scores = pd.to_numeric(df_evaluated[score_col], errors='coerce').dropna()
#                     avg_s = num_scores.mean() if not num_scores.empty else "N/A"
#                     thresh = current_thresholds.get(metric, "N/A")
#                     avg_s_display = f"{avg_s:.3f}" if isinstance(avg_s, float) else avg_s
#                     thresh_display = f"{thresh:.2f}" if isinstance(thresh, float) else thresh
#                     st.markdown(f"Avg Score: **{avg_s_display}** (Th: {thresh_display})")
#                 insight_key = f"{metric.lower().replace(' ', '_').replace('&', '').strip()}_insight"
#                 st.caption(INTERPRETATION_CONFIG.get(insight_key, "No insight available."))
#                 if col_idx < len(selected_metrics) - 1 : st.markdown("---") 
#             col_idx += 1
#         st.markdown("---")


#     def _display_detailed_results_editable(self, df_to_edit: pd.DataFrame, selected_metrics: list, 
#                                            current_thresholds: dict, 
#                                            automated_overall_col_name: str,
#                                            reviewer_override_column: str
#                                            ) -> pd.DataFrame:
#         st.subheader("📝 Detailed Results (Review & Override)")
#         st.caption(f"Individual metric scores are shown below. Edit '{reviewer_override_column}'. Edits will be automatically saved 💾.")

#         df_for_editing_view = df_to_edit.copy()
        
#         # Define the order and selection of columns for the st.data_editor view
#         key_info_cols = ['id', 'query', 'llm_output', 'reference_answer', 'test_description', 'test_config', 'required_facts']
#         result_cols = [automated_overall_col_name, reviewer_override_column]
        
#         metric_score_cols_to_display = []
#         for metric in selected_metrics:
#             metric_score_cols_to_display.append(f'{metric} Score')
#             # Individual Metric Pass/Fail columns are NOT displayed here as per user request

#         # Construct the final order of columns for display in data_editor
#         display_order_for_editor = [col for col in key_info_cols if col in df_for_editing_view.columns]
#         display_order_for_editor.extend([col for col in result_cols if col in df_for_editing_view.columns])
#         display_order_for_editor.extend([col for col in metric_score_cols_to_display if col in df_for_editing_view.columns])
#         # Add any other columns that might have been in df_evaluated but not explicitly ordered (should be rare)
#         display_order_for_editor.extend([col for col in df_for_editing_view.columns if col not in display_order_for_editor])
        
#         df_for_editor_view_subset = df_for_editing_view[display_order_for_editor].copy()


#         column_config_dict = {
#             reviewer_override_column: st.column_config.SelectboxColumn(
#                 label=f"🧑‍⚖️ {reviewer_override_column}",
#                 options=['Pass', 'Fail'], required=False, width="medium"
#             ),
#             automated_overall_col_name: st.column_config.TextColumn(label=f"🤖 {automated_overall_col_name}", width="medium"),
#             "query": st.column_config.TextColumn(width="large"),
#             "llm_output": st.column_config.TextColumn(width="large"),
#             "reference_answer": st.column_config.TextColumn(width="large"),
#             "id": st.column_config.TextColumn(width="small"),
#             "test_config": st.column_config.TextColumn(width="small"),
#             "required_facts": st.column_config.TextColumn(width="medium"),
#             "test_description": st.column_config.TextColumn(width="medium"),
#         }

#         for metric in selected_metrics:
#             score_col = f'{metric} Score'
#             if score_col in df_for_editor_view_subset.columns: # Check if column exists in the subset
#                  # Ensure scores are numeric for ProgressColumn; coerce errors to NaN
#                  df_for_editor_view_subset[score_col] = pd.to_numeric(df_for_editor_view_subset[score_col], errors='coerce')
#                  column_config_dict[score_col] = st.column_config.ProgressColumn(
#                     label=score_col, format="%.3f", width="medium",
#                     min_value=0.0, max_value=1.0,
#                     help=f"Score (0-1). Threshold: {current_thresholds.get(metric, 'N/A'):.2f}"
#                 )
#             # MetricX Pass/Fail columns are intentionally omitted from column_config_dict
        
#         # All columns except reviewer_override_column should be disabled
#         disabled_cols = [col for col in df_for_editor_view_subset.columns if col != reviewer_override_column]

#         edited_df_subset = st.data_editor(
#             df_for_editor_view_subset, # Pass the subset with correct column order
#             column_config=column_config_dict,
#             disabled=disabled_cols,
#             use_container_width=True,
#             key="detailed_results_editor_simplified", # New key for this version
#             height=600,
#             num_rows="fixed"
#         )
        
#         # IMPORTANT: The `edited_df_subset` only contains the columns that were displayed.
#         # We need to update the original full DataFrame (`df_to_edit`) with the changes 
#         # from the `reviewer_override_column` if it was edited.
#         # This ensures that columns not shown in the editor are preserved.
#         if reviewer_override_column in edited_df_subset.columns:
#             # Assuming row indices are preserved and aligned
#             df_to_edit.loc[edited_df_subset.index, reviewer_override_column] = edited_df_subset[reviewer_override_column]
            
#         return df_to_edit # Return the original full DataFrame with the override column potentially updated


# llm_eval_package/ui/results_view.py
import streamlit as st
import pandas as pd
from llm_eval_package.config import METRIC_THRESHOLDS, INTERPRETATION_CONFIG

class ResultsView:
    def __init__(self):
        pass

    def render_results(self, df_evaluated_to_edit: pd.DataFrame, selected_metrics: list, 
                       custom_thresholds: dict = None, 
                       automated_overall_col_name: str = "Automated Overall Result",
                       reviewer_override_column: str = "Reviewer's Final Result"
                       ) -> pd.DataFrame: 
        # ... (render_results logic from previous full response largely unchanged, calls _display_detailed_table_with_scores) ...
        if df_evaluated_to_edit.empty:
            st.warning("No evaluation results to display.")
            return df_evaluated_to_edit.copy()

        st.header("📊 Evaluation Results")
        current_thresholds = custom_thresholds if custom_thresholds is not None else METRIC_THRESHOLDS.copy()
        
        df_display_and_edit = df_evaluated_to_edit.copy()

        if automated_overall_col_name not in df_display_and_edit.columns:
            df_display_and_edit[automated_overall_col_name] = pd.NA 
        
        allowed_override_values = ['Pass', 'Fail']#, 'N/A', 'Error'
        if reviewer_override_column not in df_display_and_edit.columns:
            df_display_and_edit[reviewer_override_column] = df_display_and_edit[automated_overall_col_name].fillna('N/A')
        df_display_and_edit[reviewer_override_column] = df_display_and_edit[reviewer_override_column].apply(
            lambda x: str(x) if pd.notna(x) and str(x) in allowed_override_values else 'N/A'
        )

        summary_col_for_display = reviewer_override_column
        self._display_overall_summary(df_display_and_edit, 
                                      summary_pass_fail_col=summary_col_for_display, 
                                      evaluator_pass_fail_col=automated_overall_col_name)
        
        self._display_metric_performance_and_insights(df_display_and_edit, selected_metrics, current_thresholds)

        edited_df_from_editor = self._display_detailed_table_with_scores( 
            df_display_and_edit, selected_metrics, current_thresholds, 
            automated_overall_col_name=automated_overall_col_name,
            reviewer_override_column=reviewer_override_column
        )

        if 'test_config' in edited_df_from_editor.columns:
            valid_configs = edited_df_from_editor['test_config'].dropna().unique()
            if len(valid_configs) > 0 :
                st.markdown("---"); st.subheader("📋 Summary by Test Configuration")
                df_for_configs = edited_df_from_editor.copy()
                df_for_configs['test_config_filled'] = df_for_configs['test_config'].fillna("Uncategorized")
                unique_test_configs_display = sorted(df_for_configs['test_config_filled'].unique())
                for config_name_display in unique_test_configs_display:
                    config_df_subset = df_for_configs[df_for_configs['test_config_filled'] == config_name_display]
                    if not config_df_subset.empty:
                        with st.expander(f"Results for: **{config_name_display}** ({len(config_df_subset)} test cases)"):
                            self._display_overall_summary(config_df_subset, 
                                                          summary_pass_fail_col=summary_col_for_display,
                                                          evaluator_pass_fail_col=automated_overall_col_name, 
                                                          is_group_summary=True)
        return edited_df_from_editor


    def _display_overall_summary(self, df_summary: pd.DataFrame, 
                                 summary_pass_fail_col: str, 
                                 evaluator_pass_fail_col: str, 
                                 is_group_summary: bool = False):
        # ... (This method from previous response remains unchanged) ...
        if not is_group_summary: st.subheader("Overall Summary")
        total_rows = len(df_summary)
        st.write(f"Total test cases in this group: **{total_rows}**")
        if total_rows > 0 and summary_pass_fail_col in df_summary.columns:
            valid_mask = df_summary[summary_pass_fail_col].isin(['Pass', 'Fail'])
            num_valid = valid_mask.sum()
            passed = (df_summary.loc[valid_mask, summary_pass_fail_col] == 'Pass').sum()
            failed = num_valid - passed
            other = total_rows - num_valid
            pass_rate = (passed / num_valid) * 100 if num_valid > 0 else 0.0
            summary_col_label = "Reviewer's Final" if summary_pass_fail_col == "Reviewer's Final Result" else "Automated"
            st.metric(label=f"**{summary_col_label} Test Case Pass Rate**", value=f"{pass_rate:.2f}%")
            st.caption(f"Passed: {passed}, Failed: {failed}, Other (Error/N/A): {other} out of {total_rows}")
            if summary_pass_fail_col == "Reviewer's Final Result" and evaluator_pass_fail_col in df_summary.columns and evaluator_pass_fail_col != summary_pass_fail_col:
                eval_valid_mask = df_summary[evaluator_pass_fail_col].isin(['Pass', 'Fail'])
                eval_num_valid = eval_valid_mask.sum()
                eval_passed = (df_summary.loc[eval_valid_mask, evaluator_pass_fail_col] == 'Pass').sum()
                eval_rate = (eval_passed / eval_num_valid) * 100 if eval_num_valid > 0 else 0.0
                st.caption(f"(Automated Overall Pass Rate: {eval_rate:.2f}%)")
            st.markdown("---")
        elif total_rows > 0 : 
             st.caption(f"Note: Summary column '{summary_pass_fail_col}' not found or had no valid 'Pass'/'Fail' values.")
             st.markdown("---")


    def _display_metric_performance_and_insights(self, df_evaluated: pd.DataFrame, selected_metrics: list, current_thresholds: dict):
        # ... (This method from previous response remains unchanged) ...
        st.subheader("💡 Metric Performance & Explanations")
        if not selected_metrics: st.caption("No metrics selected."); return
        st.markdown("##### Detailed Metric Breakdown (Across All Data):")
        cols_per_row = min(len(selected_metrics), 3)
        metric_cols_display = st.columns(cols_per_row)
        col_idx = 0
        for metric in selected_metrics:
            with metric_cols_display[col_idx % cols_per_row]:
                st.markdown(f"**{metric}**")
                pf_col = f'{metric} Pass/Fail' 
                if pf_col in df_evaluated.columns:
                    counts = df_evaluated[pf_col].value_counts()
                    pass_m, fail_m = counts.get('Pass', 0), counts.get('Fail', 0)
                    other_m = len(df_evaluated) - (pass_m + fail_m)
                    rate_m = (pass_m / (pass_m + fail_m)) * 100 if (pass_m + fail_m) > 0 else 0.0
                    st.markdown(f"Pass Rate: **{rate_m:.1f}%** (P:{pass_m}, F:{fail_m}, O:{other_m})")
                score_col = f'{metric} Score' 
                if score_col in df_evaluated.columns:
                    num_scores = pd.to_numeric(df_evaluated[score_col], errors='coerce').dropna()
                    avg_s = num_scores.mean() if not num_scores.empty else "N/A"
                    thresh = current_thresholds.get(metric, "N/A")
                    avg_s_display = f"{avg_s:.3f}" if isinstance(avg_s, float) else avg_s
                    thresh_display = f"{thresh:.2f}" if isinstance(thresh, float) else thresh
                    st.markdown(f"Avg Score: **{avg_s_display}** (Th: {thresh_display})")
                insight_key = f"{metric.lower().replace(' ', '_').replace('&', '').strip()}_insight"
                st.caption(INTERPRETATION_CONFIG.get(insight_key, "No insight available."))
                if col_idx < len(selected_metrics) - 1 : st.markdown("---") 
            col_idx += 1
        st.markdown("---")

    def _display_detailed_table_with_scores(self, df_to_edit: pd.DataFrame, selected_metrics: list, 
                                           current_thresholds: dict, 
                                           automated_overall_col_name: str,
                                           reviewer_override_column: str
                                           ) -> pd.DataFrame:
        st.subheader("📝 Detailed Results (Review & Override)")
        st.caption(f"Individual metric scores are shown as progress bars. Edit '{reviewer_override_column}'. Changes are applied immediately (page will refresh).")

        df_for_editing_view = df_to_edit.copy()
        
        # Define column order for better UX when editing Reviewer's Final Result
        key_info_cols = ['id', 'query'] # Start with essential identifiers
        result_cols = [automated_overall_col_name, reviewer_override_column] # Put results early
        context_cols = ['llm_output', 'reference_answer', 'required_facts'] # Context for review
        metric_score_cols_to_display = [f'{metric} Score' for metric in selected_metrics] # Only scores
        other_info_cols = ['test_description', 'test_config']
        
        # Construct the final order
        display_order = []
        for col_group in [key_info_cols, result_cols, context_cols, metric_score_cols_to_display, other_info_cols]:
            display_order.extend([col for col in col_group if col in df_for_editing_view.columns and col not in display_order])
        display_order.extend([col for col in df_for_editing_view.columns if col not in display_order]) # Add any remaining
        
        df_for_editor_view_subset = df_for_editing_view[display_order].copy()

        column_config_dict = {
            reviewer_override_column: st.column_config.SelectboxColumn(
                label=f"🧑‍⚖️ {reviewer_override_column}",
                options=['Pass', 'Fail', 'N/A', 'Error'], required=False, width="medium" # Medium width
            ),
            automated_overall_col_name: st.column_config.TextColumn(label=f"🤖 {automated_overall_col_name}", width="medium"),
            "query": st.column_config.TextColumn(width="medium"), # Keep query accessible
            "id": st.column_config.TextColumn(width="small"),
            "llm_output": st.column_config.TextColumn(width="large"), # Make these large for readability
            "reference_answer": st.column_config.TextColumn(width="large"),
            "required_facts": st.column_config.TextColumn(width="medium"),
        }

        for metric in selected_metrics:
            score_col = f'{metric} Score'
            if score_col in df_for_editor_view_subset.columns:
                 df_for_editor_view_subset[score_col] = pd.to_numeric(df_for_editor_view_subset[score_col], errors='coerce')
                 column_config_dict[score_col] = st.column_config.ProgressColumn(
                    label=score_col, format="%.3f", width="medium",
                    min_value=0.0, max_value=1.0,
                    help=f"Score (0-1). Threshold: {current_thresholds.get(metric, 'N/A'):.2f}"
                )
        
        disabled_cols = [col for col in df_for_editor_view_subset.columns if col != reviewer_override_column]

        edited_df_subset = st.data_editor(
            df_for_editor_view_subset,
            column_config=column_config_dict,
            disabled=disabled_cols,
            use_container_width=True,
            key="detailed_results_editor_scores_override", # Changed key for this specific editor
            height=600,
            num_rows="fixed"
        )
        
        # Update the original full DataFrame (`df_to_edit`) with changes from `reviewer_override_column`
        if reviewer_override_column in edited_df_subset.columns:
            # Ensure indices are aligned for the update. data_editor preserves original index.
            df_to_edit.loc[edited_df_subset.index, reviewer_override_column] = edited_df_subset[reviewer_override_column]
            
        return df_to_edit