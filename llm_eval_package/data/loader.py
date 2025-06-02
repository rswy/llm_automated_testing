# llm_eval_package/data/loader.py
import pandas as pd
import json
from llm_eval_package.config import REQUIRED_COLUMNS # Ensure this is correctly imported
import streamlit as st

class DataLoader:
    def __init__(self):
        pass

    def _load_csv_internal(self, file_uploader) -> pd.DataFrame: # Renamed for internal consistency
        """
        Internal helper to load and process CSV data, ensuring 'id' is string.
        """
        df = pd.DataFrame() # Initialize
        try:
            # Attempt to read with 'id' specifically as string.
            # Peek at columns first to see if 'id' exists, to avoid error if dtype applied to non-existent col
            if hasattr(file_uploader, 'seek'): file_uploader.seek(0)
            temp_df_for_cols_check = pd.read_csv(file_uploader, nrows=0) # Read only header
            if hasattr(file_uploader, 'seek'): file_uploader.seek(0) # Reset pointer

            dtype_spec = {}
            if 'id' in temp_df_for_cols_check.columns:
                dtype_spec['id'] = str 
            
            df = pd.read_csv(file_uploader, dtype=dtype_spec if dtype_spec else None)

        except ValueError as ve: 
             st.warning(f"Initial CSV load with specific 'id' dtype failed (this is okay if 'id' is missing or not strictly numeric): {ve}. Retrying generic load.")
             if hasattr(file_uploader, 'seek'): file_uploader.seek(0)
             df = pd.read_csv(file_uploader)
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")
            return pd.DataFrame() # Return empty on critical error
        
        # Post-load conversion to ensure 'id' is string if it exists
        if 'id' in df.columns and not pd.api.types.is_string_dtype(df['id']):
            df['id'] = df['id'].astype(str).fillna('')
        return df

    def load_data(self, file_uploader) -> pd.DataFrame:
        """
        Loads data from an uploaded file (CSV or JSON) and performs validation and preparation.
        """
        if file_uploader is not None:
            file_extension = file_uploader.name.split('.')[-1].lower()
            df = pd.DataFrame() # Initialize df

            if file_extension == 'csv':
                df = self._load_csv_internal(file_uploader) # Corrected method call
            elif file_extension == 'json':
                try:
                    if hasattr(file_uploader, 'seek'): file_uploader.seek(0) # Ensure reading from start
                    json_data = file_uploader.read().decode('utf-8')
                    data = json.loads(json_data)
                    df = pd.DataFrame(data)
                except Exception as e:
                    st.error(f"Error processing JSON file: {e}")
                    return pd.DataFrame() 
            else:
                st.error("Unsupported file format. Please upload a CSV or JSON file.")
                return pd.DataFrame() 

            if not df.empty:
                self._validate_and_prepare_columns(df) 
            return df
        return pd.DataFrame()

    def _validate_and_prepare_columns(self, df: pd.DataFrame):
        """
        Ensures all REQUIRED_COLUMNS exist, standardized casing and values for specific columns.
        """
        df_columns_lower_map = {col.lower().replace(" ", "_").replace("-", "_"): col for col in df.columns}

        for req_col_from_config in REQUIRED_COLUMNS: 
            req_col_lower_standard = req_col_from_config.lower().replace(" ", "_").replace("-", "_")
            actual_df_col_name = None

            if req_col_lower_standard in df_columns_lower_map:
                actual_df_col_name = df_columns_lower_map[req_col_lower_standard]
                if actual_df_col_name != req_col_from_config:
                    df.rename(columns={actual_df_col_name: req_col_from_config}, inplace=True)
                current_col_name_for_processing = req_col_from_config
            else: 
                df[req_col_from_config] = pd.NA 
                current_col_name_for_processing = req_col_from_config
            
            if current_col_name_for_processing == 'id':
                df[current_col_name_for_processing] = df[current_col_name_for_processing].astype(str).fillna('')
            
            elif current_col_name_for_processing == 'initial_reviewer_verdict':
                allowed_verdicts_standard = ['Pass', 'Fail', 'N/A', 'Error'] 
                
                def standardize_verdict(value):
                    if pd.isna(value): return 'N/A' 
                    s_value = str(value).strip().title() 
                    if s_value in allowed_verdicts_standard: return s_value
                    if not s_value: return 'N/A' 
                    return 'N/A' 

                df[current_col_name_for_processing] = df[current_col_name_for_processing].apply(standardize_verdict)
                df[current_col_name_for_processing] = df[current_col_name_for_processing].astype(object) 

        essential_for_app = ['query'] 
        for ecol_config_case in essential_for_app:
            if ecol_config_case not in df.columns or df[ecol_config_case].isnull().all():
                error_message = f"Essential data column '{ecol_config_case}' is missing or entirely empty. Please check your uploaded file."
                st.error(error_message)
                raise ValueError(error_message)

# import pandas as pd
# import json
# from llm_eval_package.config import REQUIRED_COLUMNS # Updated import path
# import streamlit as st

# class DataLoader:
#     """
#     Handles loading and validating input data for LLM evaluation.
#     Supports CSV and JSON file formats.
#     """

#     def __init__(self):
#         """
#         Initializes the DataLoader.
#         """
#         pass

 
#     def _load_csv(self, file_uploader) -> pd.DataFrame:
#         """
#         Loads data from a CSV file, ensuring 'id' is string.
#         """
#         # Define dtypes for specific columns, especially 'id'
#         # You can add other columns here if they need specific type handling
#         dtype_map = {'id': str} 
#         try:
#             # Try reading with specified dtypes
#             df = pd.read_csv(file_uploader, dtype=dtype_map)
#         except Exception:
#             # Fallback if dtype specification causes issues (e.g., id column not present)
#             # Reset file_uploader's cursor to read again
#             if hasattr(file_uploader, 'seek'):
#                 file_uploader.seek(0)
#             df = pd.read_csv(file_uploader)
#             # If 'id' column exists after fallback, try to convert it to string
#             if 'id' in df.columns:
#                 df['id'] = df['id'].astype(str)
#         return df

#     def load_data(self, file_uploader) -> pd.DataFrame:
#         if file_uploader is not None:
#             file_extension = file_uploader.name.split('.')[-1].lower()
#             df = pd.DataFrame() # Initialize df

#             if file_extension == 'csv':
#                 df = self._load_csv(file_uploader)
#             elif file_extension == 'json':
#                 # For JSON, type conversion might need to happen after loading into DataFrame
#                 json_data = file_uploader.read().decode('utf-8')
#                 data = json.loads(json_data)
#                 df = pd.DataFrame(data)
#                 if 'id' in df.columns:
#                     df['id'] = df['id'].astype(str) # Ensure 'id' is string for JSON too
#             else:
#                 st.error("Unsupported file format. Please upload a CSV or JSON file.")
#                 st.stop()

#             self._validate_columns(df) # Ensure this method exists and is appropriate
#             return df
#         return pd.DataFrame()

#     def _validate_columns(self, df: pd.DataFrame):
#         mandatory_cols = ['query', 'llm_output', 'reference_answer'] # Adjust as per your true mandatory cols
#         # Check for the truly mandatory columns for evaluation
#         # initial_reviewer_verdict is optional in input, created by app if not present

#         # Add all columns defined in REQUIRED_COLUMNS from config if they are missing
#         # This includes 'id', 'initial_reviewer_verdict', etc., ensuring they exist
#         for col in REQUIRED_COLUMNS: # From config.py
#             if col not in df.columns:
#                 df[col] = pd.NA # Or appropriate default like "" or None
#             # Ensure 'id' column is string if it was just added or to be safe
#             if col == 'id':
#                 df[col] = df[col].astype(str).fillna("") # Ensure string and handle NaNs if any

#         # Now check for core mandatory fields needed for any processing to begin
#         # This check is more about preventing crashes than strict data validation for every possible column
#         # For example, 'query' is essential for fetching responses or evaluation.
#         essential_cols_for_processing = ['query'] # Adjust based on minimum needed to proceed
#         missing_essential_columns = [col for col in essential_cols_for_processing if col not in df.columns or df[col].isnull().all()]

#         if missing_essential_columns:
#             st.error(f"Missing essential data in column(s): {', '.join(missing_essential_columns)}. "
#                      f"Please ensure your file contains data for these.")
#             st.stop() 

#     def _load_json(self, file_uploader) -> pd.DataFrame:
#         """
#         Loads data from a JSON file.

#         Args:
#             file_uploader: The Streamlit file uploader object for the JSON file.

#         Returns:
#             pd.DataFrame: A pandas DataFrame containing the JSON data.
#         """
#         # Read the file content as a string
#         json_data = file_uploader.read().decode('utf-8')
#         # Parse the JSON string into a Python object
#         data = json.loads(json_data)
#         return pd.DataFrame(data)
