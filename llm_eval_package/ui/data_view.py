# llm_eval_package/ui/data_view.py
import streamlit as st
import pandas as pd

class DataManagementView:
    def __init__(self):
        pass

    def render_data_preview(self, df_to_edit: pd.DataFrame, key_suffix: str = "original_data_editor") -> pd.DataFrame:
        if not df_to_edit.empty:
            st.subheader("📄 Uploaded Data Preview & Editor")
            st.caption(f"Displaying {len(df_to_edit)} rows. Edits are applied immediately (page will refresh).")
            
            column_config = {col: st.column_config.TextColumn(width="medium") for col in df_to_edit.columns}
            
            # If 'initial_reviewer_verdict' column exists, make it a selectbox
            initial_verdict_col_name = "initial_reviewer_verdict" # Ensure this matches config.py
            if initial_verdict_col_name in df_to_edit.columns:
                column_config[initial_verdict_col_name] = st.column_config.SelectboxColumn(
                    label="Initial Reviewer Verdict", # Friendly name for the column header
                    options=['Pass', 'Fail'], # Allow empty/None as well [ 'N/A', 'Error', None, ""]
                    required=False, # Make it not required
                    width="medium",
                    help="Your pre-assessment for this test case (optional)."
                )
                # Ensure existing values are compatible or map them
                df_to_edit[initial_verdict_col_name] = df_to_edit[initial_verdict_col_name].apply(
                    lambda x: x if pd.isna(x) or x in ['Pass', 'Fail', 'N/A', 'Error', ""] else 'N/A'
                ).astype(object).where(df_to_edit[initial_verdict_col_name].notna(), None)


            edited_df = st.data_editor(
                df_to_edit,
                num_rows="dynamic", 
                use_container_width=True,
                key=key_suffix,
                height=400,
                column_config=column_config
            )
            return edited_df
        return df_to_edit