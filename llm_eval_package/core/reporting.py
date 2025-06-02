import pandas as pd
import streamlit as st

class Reporter:
    """
    Handles the generation and display of evaluation reports.
    This class can be extended to create various types of reports (e.g., HTML, PDF).
    """

    def __init__(self):
        """
        Initializes the Reporter.
        """
        pass

    def generate_summary_report(self, df_evaluated: pd.DataFrame, selected_metrics: list, custom_thresholds: dict = None):
        """
        Generates and displays a summary report of the evaluation results.

        Args:
            df_evaluated (pd.DataFrame): The DataFrame containing evaluation results.
            selected_metrics (list): List of metrics that were evaluated.
            custom_thresholds (dict, optional): Custom thresholds used for evaluation.
        """
        if df_evaluated.empty:
            st.warning("No evaluation results to report.")
            return

        st.subheader("Evaluation Summary")

        total_rows = len(df_evaluated)
        st.write(f"Total test cases evaluated: **{total_rows}**")

        # Display overall pass/fail rates for each metric
        st.markdown("### Metric Pass/Fail Rates")
        summary_data = []
        for metric in selected_metrics:
            pass_col = f'{metric} Pass/Fail'
            if pass_col in df_evaluated.columns:
                pass_count = (df_evaluated[pass_col] == 'Pass').sum()
                fail_count = (df_evaluated[pass_col] == 'Fail').sum()
                error_count = (df_evaluated[pass_col] == 'Error').sum()
                
                pass_rate = (pass_count / total_rows) * 100 if total_rows > 0 else 0
                
                summary_data.append({
                    "Metric": metric,
                    "Pass Count": pass_count,
                    "Fail Count": fail_count,
                    "Error Count": error_count,
                    "Pass Rate (%)": f"{pass_rate:.2f}%"
                })
            else:
                summary_data.append({
                    "Metric": metric,
                    "Pass Count": "N/A",
                    "Fail Count": "N/A",
                    "Error Count": "N/A",
                    "Pass Rate (%)": "N/A"
                })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True)
        else:
            st.info("No metrics were selected for evaluation, or no results available.")

        # Display average scores for numerical metrics
        st.markdown("### Average Metric Scores")
        avg_scores_data = []
        for metric in selected_metrics:
            score_col = f'{metric} Score'
            if score_col in df_evaluated.columns:
                # Filter out 'Error' or non-numeric values before calculating mean
                numeric_scores = pd.to_numeric(df_evaluated[score_col], errors='coerce').dropna()
                if not numeric_scores.empty:
                    avg_score = numeric_scores.mean()
                    threshold = custom_thresholds.get(metric) if custom_thresholds else None
                    avg_scores_data.append({
                        "Metric": metric,
                        "Average Score": f"{avg_score:.4f}",
                        "Threshold": f"{threshold:.4f}" if threshold is not None else "Default"
                    })
                else:
                    avg_scores_data.append({
                        "Metric": metric,
                        "Average Score": "N/A (No numeric scores)",
                        "Threshold": "N/A"
                    })
            else:
                avg_scores_data.append({
                    "Metric": metric,
                    "Average Score": "N/A",
                    "Threshold": "N/A"
                })
        
        if avg_scores_data:
            avg_scores_df = pd.DataFrame(avg_scores_data)
            st.dataframe(avg_scores_df, use_container_width=True)
        else:
            st.info("No average scores to display.")

    def export_report(self, df_evaluated: pd.DataFrame, file_format: str = "csv"):
        """
        Exports the evaluation results to a specified file format.

        Args:
            df_evaluated (pd.DataFrame): The DataFrame containing evaluation results.
            file_format (str): The desired export format (e.g., "csv", "json").
        """
        if df_evaluated.empty:
            st.warning("No data to export.")
            return

        if file_format == "csv":
            csv_output = df_evaluated.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Results as CSV",
                data=csv_output,
                file_name="llm_evaluation_results.csv",
                mime="text/csv",
            )
        elif file_format == "json":
            json_output = df_evaluated.to_json(orient="records", indent=4).encode('utf-8')
            st.download_button(
                label="Download Results as JSON",
                data=json_output,
                file_name="llm_evaluation_results.json",
                mime="application/json",
            )
        else:
            st.error(f"Unsupported export format: {file_format}")

