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
            
            column_config_build = {} 

            # Standardize 'initial_reviewer_verdict' for SelectboxColumn
            initial_verdict_col_name = "initial_reviewer_verdict" # Exact name from config
            if initial_verdict_col_name in df_to_edit.columns:
                # Options for the selectbox. Empty string allows user to "clear" to blank if desired.
                # 'N/A' is a good default for truly missing/unspecified.
                selectbox_options = ['Pass', 'Fail', 'N/A', 'Error', ''] 
                
                # Ensure existing values are in options or default to 'N/A' for editor
                # DataLoader already standardizes to 'Pass', 'Fail', 'N/A', 'Error'.
                # This just makes sure if something else slipped through or was pd.NA, it becomes 'N/A' string.
                df_to_edit[initial_verdict_col_name] = df_to_edit[initial_verdict_col_name].fillna('N/A').astype(str)
                df_to_edit[initial_verdict_col_name] = df_to_edit[initial_verdict_col_name].apply(
                    lambda x: x if x in selectbox_options else 'N/A'
                )

                column_config_build[initial_verdict_col_name] = st.column_config.SelectboxColumn(
                    label="Initial Reviewer Verdict",
                    options=selectbox_options, 
                    required=False, # If True, editor won't allow blank/None from options
                    width="medium",
                    help="Your pre-assessment (optional). Choose blank or N/A if not set."
                )
            
            if 'id' in df_to_edit.columns:
                column_config_build['id'] = st.column_config.TextColumn(
                    label="ID (Read-Only)", disabled=True, width="small",
                    help="Unique identifier for the test case."
                )
            
            for col in df_to_edit.columns:
                if col not in column_config_build:
                    # Infer type for st.data_editor for other columns
                    if pd.api.types.is_numeric_dtype(df_to_edit[col]) and not pd.api.types.is_bool_dtype(df_to_edit[col]):
                        column_config_build[col] = st.column_config.NumberColumn(width="medium", format="%g") # General number format
                    elif pd.api.types.is_datetime64_any_dtype(df_to_edit[col]):
                         column_config_build[col] = st.column_config.DatetimeColumn(width="medium")
                    elif pd.api.types.is_bool_dtype(df_to_edit[col]):
                         column_config_build[col] = st.column_config.CheckboxColumn(width="small")
                    else: # Default to TextColumn
                        column_config_build[col] = st.column_config.TextColumn(width="medium")
            
            edited_df = st.data_editor(
                df_to_edit,
                num_rows="dynamic", 
                use_container_width=True,
                key=key_suffix,
                height=400,
                column_config=column_config_build
            )
            return edited_df
        return df_to_edit

# # llm_eval_package/ui/data_view.py
# import streamlit as st
# import pandas as pd

# class DataManagementView:
#     def __init__(self):
#         pass

#     def render_data_preview(self, df_to_edit: pd.DataFrame, key_suffix: str = "original_data_editor") -> pd.DataFrame:
#         if not df_to_edit.empty:
#             st.subheader("📄 Uploaded Data Preview & Editor")
#             st.caption(f"Displaying {len(df_to_edit)} rows. Edits are applied immediately (page will refresh).")
            
#             column_config = {col: st.column_config.TextColumn(width="medium") for col in df_to_edit.columns}
            
#             # If 'initial_reviewer_verdict' column exists, make it a selectbox
#             initial_verdict_col_name = "initial_reviewer_verdict" # Ensure this matches config.py
#             if initial_verdict_col_name in df_to_edit.columns:
#                 column_config[initial_verdict_col_name] = st.column_config.SelectboxColumn(
#                     label="Initial Reviewer Verdict", # Friendly name for the column header
#                     options=['Pass', 'Fail'], # Allow empty/None as well [ 'N/A', 'Error', None, ""]
#                     required=False, # Make it not required
#                     width="medium",
#                     help="Your pre-assessment for this test case (optional)."
#                 )
#                 # Ensure existing values are compatible or map them
#                 df_to_edit[initial_verdict_col_name] = df_to_edit[initial_verdict_col_name].apply(
#                     lambda x: x if pd.isna(x) or x in ['Pass', 'Fail', 'N/A', 'Error', ""] else 'N/A'
#                 ).astype(object).where(df_to_edit[initial_verdict_col_name].notna(), None)


#             edited_df = st.data_editor(
#                 df_to_edit,
#                 num_rows="dynamic", 
#                 use_container_width=True,
#                 key=key_suffix,
#                 height=400,
#                 column_config=column_config
#             )
#             return edited_df
#         return df_to_edit