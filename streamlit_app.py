# streamlit_app.py (snippet, ensure all these imports are at the top of your file)
import streamlit as st
import pandas as pd
import sys
import os
import io 
import traceback
import requests 
import json 
import time # Ensure this is the standard time module
import urllib3 
import datetime 

project_root_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if project_root_path not in sys.path:
    sys.path.insert(0, project_root_path)

from llm_eval_package.data.loader import DataLoader
from llm_eval_package.core.engine import Evaluator
from llm_eval_package.ui.sidebar_view import SidebarView, BOT_DOMAIN_MAPPING
from llm_eval_package.ui.data_view import DataManagementView
from llm_eval_package.ui.results_view import ResultsView
from llm_eval_package.ui.tutorial_view import TutorialView
from llm_eval_package.config import (
    METRIC_THRESHOLDS, AVAILABLE_METRICS, TASK_METRICS_PRESELECTION,
    DEFAULT_PASS_CRITERION, PASS_CRITERION_ALL_PASS, PASS_CRITERION_ANY_PASS,
    TASK_TYPE_RAG_FAQ, DEVELOPER_MODE, REQUIRED_COLUMNS # Added REQUIRED_COLUMNS
)

from llm_eval_package.data.rag_input_processor import (
    DEFAULT_API_URL, DEFAULT_API_HEADERS, DEFAULT_DOMAINS
)


# Corrected fetch_bot_responses_for_df_streamlit_with_progress
def fetch_bot_responses_for_df_streamlit_with_progress(
    input_df: pd.DataFrame, query_column: str, selected_domain_key: str
    ) -> pd.DataFrame:

    if input_df.empty:
        st.warning("Input DataFrame empty. Cannot fetch responses.")
        return input_df.copy()
    if query_column not in input_df.columns:
        st.error(f"Query column '{query_column}' not found in the uploaded data.")
        return input_df.copy()

    # Work on a copy of the DataFrame to add the new 'llm_output' column
    # If rows were deleted by the user, input_df will reflect that.
    output_df = input_df.copy() 
    
    # API call setup (adapted from rag_input_processor.py)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    current_api_url = DEFAULT_API_URL
    current_api_headers = DEFAULT_API_HEADERS.copy() # Use a copy
    current_domains_map = DEFAULT_DOMAINS 

    domain_path = current_domains_map.get(selected_domain_key)
    if not domain_path:
        st.error(f"Domain key '{selected_domain_key}' not found in internal domain configuration. Please check available domains.")
        return input_df.copy() 

    if "YOUR_EXPIRED_OR_PLACEHOLDER_TOKEN_HERE" in current_api_headers.get("Authorization", ""):
        st.error(
            "FATAL: API token is a placeholder in configuration (`llm_eval_package/data/rag_input_processor.py`). "
            "Please update it with a valid Bearer token for API calls to proceed.", icon="🚫"
        )
        return input_df.copy() 

    total_queries = len(output_df) # Number of rows to process
    if total_queries == 0:
        st.info("No queries to process after potential deletions.")
        output_df['llm_output'] = [] # Ensure column exists even if empty
        return output_df

    progress_bar = st.progress(0.0) 
    status_text_area = st.empty() 
    status_text_area.text("Initializing API calls...") 
    
    # Initialize an empty list for responses. We will append to this.
    responses_collected = [] 
    successful_fetches = 0

    # Iterate using a counter for progress and for appending to responses_collected
    for i, (original_df_index, row_data) in enumerate(output_df.iterrows()):
        # original_df_index is the actual index from the DataFrame (could be sparse)
        # i is the 0-based iteration counter (0, 1, 2, ...)
        
        query_text = str(row_data.get(query_column, ''))
        current_api_headers["Req-Date-Time"] = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
        payload = {"message": query_text, "senderId": "streamlit_app_user_v2", "domain": domain_path}
        
        response_message_for_df = pd.NA 
        max_retries_ui = 1 
        retry_delay_ui = 1 

        for attempt in range(max_retries_ui + 1):
            try:
                api_response = requests.post(
                    current_api_url, headers=current_api_headers,
                    data=json.dumps(payload), verify=False, timeout=25 
                )
                api_response.raise_for_status() 
                
                full_message = ""
                if api_response.text and api_response.text.strip():
                    for line in api_response.text.strip().splitlines():
                        try:
                            obj = json.loads(line)
                            full_message += str(obj.get("data", ""))
                        except json.JSONDecodeError:
                            if not full_message : full_message += line 
                            continue
                else: 
                    full_message = "Error: Empty API response"
                
                response_message_for_df = full_message
                successful_fetches += 1
                break 
            except requests.exceptions.RequestException as e_req:
                response_message_for_df = f"Error (API Attempt {attempt+1}): {str(e_req)[:100]}"
            except Exception as e_other: 
                response_message_for_df = f"Unexpected Error (Attempt {attempt+1}): {str(e_other)[:100]}"
            if attempt < max_retries_ui:
                time.sleep(retry_delay_ui) 
        
        responses_collected.append(response_message_for_df) # Append to the list

        # Update progress based on the iteration counter `i`
        progress_value = (i + 1) / total_queries
        progress_bar.progress(float(progress_value))
        status_text_area.text(f"Processed: {i + 1}/{total_queries} queries. Successful API calls: {successful_fetches}")

    # Assign the collected responses list to the new column.
    # This list will have the same length as the number of rows iterated.
    output_df['llm_output'] = responses_collected
    
    status_text_area.text(f"All {total_queries} queries processed. Successfully fetched responses for {successful_fetches} queries.")
    if successful_fetches < total_queries:
        st.warning(f"{total_queries - successful_fetches} queries encountered errors. Please check the 'llm_output' column for details (e.g., 'Error: ...').")
    else:
        st.success("All responses fetched successfully from the RAG bot!")
    return output_df

def main():
    st.set_page_config(page_title="BYOB Evaluator by Genius AI", page_icon="✨", layout="wide")

    data_loader, evaluator = DataLoader(), Evaluator()
    sidebar_view, data_mgmt_view, results_view, tutorial_view = SidebarView(), DataManagementView(), ResultsView(), TutorialView()

    default_session_state = {
        'df_original': pd.DataFrame(), 
        'df_evaluated': pd.DataFrame(),
        'show_results': False, 'show_tutorial': True, 'file_uploader_key': 0,
        'uploaded_file_name': None, 'agreement_calculated': False, 'agreement_score': None,
        'main_selected_metrics': TASK_METRICS_PRESELECTION.get(TASK_TYPE_RAG_FAQ, ["Semantic Similarity"]),
        'main_overall_criterion': DEFAULT_PASS_CRITERION,
        'main_use_custom_thresholds': False, 'main_custom_thresholds': {},
        'main_sensitive_keywords_input': "profanity, hate speech",
        'selected_domain_key': list(BOT_DOMAIN_MAPPING.keys())[0] if BOT_DOMAIN_MAPPING else "SG Branch"
    }
    for key, default_val in default_session_state.items():
        if key not in st.session_state: st.session_state[key] = default_val
    
    sidebar_outputs = sidebar_view.render_sidebar(st.session_state.file_uploader_key)
    # Only a few items are now returned from sidebar
    uploaded_file_obj, selected_task_type_ignored, go_to_instructions, selected_domain_key_from_sidebar = sidebar_outputs[0], sidebar_outputs[1], sidebar_outputs[2], sidebar_outputs[3]
    st.session_state.selected_domain_key = selected_domain_key_from_sidebar

    if go_to_instructions:
        st.session_state.show_tutorial = True; st.session_state.show_results = False
        st.session_state.df_original = pd.DataFrame(); st.session_state.df_evaluated = pd.DataFrame()
        st.session_state.file_uploader_key += 1; st.session_state.agreement_calculated = False; st.rerun()

    # st.markdown(
    #     """<style>.main-header{font-size:3em;font-weight:bold;color:#4CAF50;text-align:center;margin-bottom:0.5em;text-shadow:2px 2px 4px rgba(0,0,0,0.1);}.subheader{font-size:1.5em;color:#555;text-align:center;margin-bottom:1em;}.stButton>button{background-color:#4CAF50;color:white;border-radius:12px;padding:10px 24px;font-size:1.2em;border:none;box-shadow:0 4px 8px 0 rgba(0,0,0,0.2);transition:0.3s;}.stButton>button:hover{background-color:#45a049;box-shadow:0 8px 16px 0 rgba(0,0,0,0.2);}.stAlert{border-radius:10px;}</style><h1 class="main-header">BYOB Evaluator</h1><p class="subheader">Tool by Genius AI</p>""", unsafe_allow_html=True)

    st.markdown(
    """
    <style>
    .main-header {font-size: 3em; font-weight: bold; color: #4CAF50; text-align: center; margin-bottom: 0.5em; text-shadow: 2px 2px 4px rgba(0,0,0,0.1);}
    .subheader {font-size: 1.5em; color: #555; text-align: center; margin-bottom: 1em;}
    .stButton>button {background-color: #4CAF50; color: white; border-radius: 12px; padding: 10px 24px; font-size: 1.2em; border: none; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2); transition: 0.3s;}
    .stButton>button:hover {background-color: #45a049; box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);}
    .stAlert {border-radius: 10px;}
    </style>
    <h1 class="main-header">✨BYOB Evaluator✨</h1>
    <h5 class="subheader">Powered by Genius AI</h5>
    """,
    unsafe_allow_html=True
)
    if st.session_state.show_tutorial and uploaded_file_obj is None and st.session_state.df_original.empty:
        tutorial_view.render_tutorial(); return
    else:
        if st.session_state.show_tutorial: st.session_state.show_tutorial = False

    if uploaded_file_obj is not None:
        if st.session_state.uploaded_file_name != uploaded_file_obj.name: 
            try:
                df_loaded = data_loader.load_data(uploaded_file_obj)
                st.session_state.df_original = df_loaded.copy()
                st.session_state.uploaded_file_name = uploaded_file_obj.name
                st.session_state.df_evaluated = pd.DataFrame()
                st.session_state.show_results = False; st.session_state.agreement_calculated = False
                st.rerun() # Rerun after new file load to ensure UI updates correctly
            except Exception as e:
                st.error(f"Error loading data: {e}"); st.session_state.df_original = pd.DataFrame()
                st.session_state.show_tutorial = True; st.session_state.uploaded_file_name = None; st.session_state.file_uploader_key += 1; st.rerun(); return
    
    if not st.session_state.df_original.empty:
        returned_edited_df_original = data_mgmt_view.render_data_preview(
            st.session_state.df_original.copy(), 
            key_suffix="original_data_editor_v3"
        )
        if not returned_edited_df_original.equals(st.session_state.df_original):
            st.session_state.df_original = returned_edited_df_original.copy()
            st.session_state.df_evaluated = pd.DataFrame() 
            st.session_state.show_results = False; st.session_state.agreement_calculated = False
            st.caption("✏️ Data preview changes applied. Re-fetch or re-evaluate if needed.")
            st.rerun() 
    
    if not st.session_state.df_original.empty:
        st.markdown("---")
        cols_fetch_btn = st.columns([1, 2.5, 1])
        with cols_fetch_btn[1]:
            if st.button("🔗 Fetch Bot Responses & Update Data", help="Calls API, updates 'llm_output'.", use_container_width=True):
                if 'query' not in st.session_state.df_original.columns: st.error("Data needs a 'query' column.")
                else:
                    updated_df = fetch_bot_responses_for_df_streamlit_with_progress(
                        st.session_state.df_original.copy(), 'query', st.session_state.selected_domain_key
                    )
                    st.session_state.df_original = updated_df.copy()
                    st.session_state.df_evaluated = pd.DataFrame()
                    st.session_state.show_results = False; st.session_state.agreement_calculated = False; st.rerun()
    
    if not st.session_state.df_original.empty:
        st.markdown("---")
        with st.expander("🛠️ Configure Evaluation Settings", expanded=True):
            st.session_state.main_selected_metrics = st.multiselect("Select Metrics:", list(AVAILABLE_METRICS.keys()), default=st.session_state.main_selected_metrics)
            st.session_state.main_overall_criterion = st.selectbox("Automated Overall Result Logic:", [PASS_CRITERION_ALL_PASS, PASS_CRITERION_ANY_PASS], index=[PASS_CRITERION_ALL_PASS, PASS_CRITERION_ANY_PASS].index(st.session_state.main_overall_criterion))
            st.session_state.main_use_custom_thresholds = st.checkbox("Use Custom Metric Thresholds", value=st.session_state.main_use_custom_thresholds)
            if st.session_state.main_use_custom_thresholds:
                temp_custom_thresholds = st.session_state.main_custom_thresholds.copy()
                for metric in st.session_state.main_selected_metrics:
                    default_thresh = METRIC_THRESHOLDS.get(metric, 0.5)
                    current_val = float(temp_custom_thresholds.get(metric, default_thresh))
                    if metric == "Safety": temp_custom_thresholds[metric] = 1.0; st.markdown(f"↳ **{metric}**: Threshold fixed at 1.0")
                    else: temp_custom_thresholds[metric] = st.number_input(f"Thresh. for {metric}", 0.0, 1.0, current_val, 0.01, key=f"main_thresh_{metric}")
                st.session_state.main_custom_thresholds = temp_custom_thresholds
            if "Safety" in st.session_state.main_selected_metrics and DEVELOPER_MODE:
                st.session_state.main_sensitive_keywords_input = st.text_area("Sensitive Keywords (for Safety):", st.session_state.main_sensitive_keywords_input)

        cols_eval_btn = st.columns([1, 2, 1]); 
        with cols_eval_btn[1]:
            run_evaluation_button_clicked = st.button("🚀 Run Evaluation", use_container_width=True)
        
        if run_evaluation_button_clicked:
            if 'llm_output' not in st.session_state.df_original.columns or st.session_state.df_original['llm_output'].astype(str).str.strip().replace('', pd.NA).isnull().all():
                st.error("The 'llm_output' is missing/empty.")
            elif not st.session_state.main_selected_metrics: st.warning("Please select at least one metric.")
            else:
                with st.spinner("Crunching numbers... Evaluation in progress! 🧠"):
                    try:
                        sensitive_keywords_list = []
                        if "Safety" in st.session_state.main_selected_metrics and DEVELOPER_MODE:
                            sensitive_keywords_list = [k.strip().lower() for k in st.session_state.main_sensitive_keywords_input.split(',') if k.strip()]
                        eval_custom_thresh = st.session_state.main_custom_thresholds if st.session_state.main_use_custom_thresholds else None
                        
                        df_to_evaluate = st.session_state.df_original.copy()
                        automated_overall_col = "Automated Overall Result"
                        reviewer_final_col = "Reviewer's Final Result"
                        initial_verdict_col = "initial_reviewer_verdict" 

                        evaluated_data_from_engine = evaluator.evaluate_dataframe(
                            df_to_evaluate, st.session_state.main_selected_metrics,
                            custom_thresholds=eval_custom_thresh, sensitive_keywords=sensitive_keywords_list,
                            overall_pass_criterion=st.session_state.main_overall_criterion
                        )
                        
                        final_evaluated_df = evaluated_data_from_engine.copy()
                        
                        # Pre-populate Reviewer's Final Result
                        # Initialize the column first to ensure it exists with a default
                        final_evaluated_df[reviewer_final_col] = final_evaluated_df[automated_overall_col].fillna('N/A')

                        if initial_verdict_col in df_to_evaluate.columns:
                            # Iterate and assign row by row to handle potential index misalignments carefully
                            # or ensure indices are perfectly aligned before this step.
                            # For simplicity here, assuming indices are aligned after copy.
                            for index, row in df_to_evaluate.iterrows():
                                initial_verdict = row.get(initial_verdict_col)
                                if pd.notna(initial_verdict) and initial_verdict in ['Pass', 'Fail', 'N/A', 'Error']:
                                    if index in final_evaluated_df.index:
                                        final_evaluated_df.loc[index, reviewer_final_col] = initial_verdict
                        
                        st.session_state.df_evaluated = final_evaluated_df.copy()
                        
                        st.session_state.show_results = True
                        st.session_state.selected_metrics_for_results = st.session_state.main_selected_metrics[:]
                        st.session_state.custom_thresholds_for_results = eval_custom_thresh.copy() if eval_custom_thresh else None
                        st.session_state.show_tutorial = False; st.session_state.agreement_calculated = False
                        st.success("Evaluation Complete!"); st.rerun()
                    except Exception as e: st.error(f"Evaluation Error: {e}"); st.exception(e)

    if st.session_state.show_results and not st.session_state.df_evaluated.empty:
        automated_overall_col = "Automated Overall Result"; reviewer_final_col = "Reviewer's Final Result"

        returned_edited_results_df = results_view.render_results(
            st.session_state.df_evaluated.copy(), 
            st.session_state.selected_metrics_for_results,
            st.session_state.custom_thresholds_for_results,
            automated_overall_col_name=automated_overall_col, 
            reviewer_override_column=reviewer_final_col
        )
        if not returned_edited_results_df.equals(st.session_state.df_evaluated):
            st.session_state.df_evaluated = returned_edited_results_df.copy()
            st.session_state.agreement_calculated = False 
            st.caption("Reviewer's Final Result edits applied immediately.")
            st.rerun() 

        st.markdown("---"); st.subheader("⚖️ Reviewer Agreement Score")
        if reviewer_final_col in st.session_state.df_evaluated.columns and automated_overall_col in st.session_state.df_evaluated.columns:
            cols_agreement_btn = st.columns([2,2,2])
            with cols_agreement_btn[1]:
                if st.button("Calculate Reviewer-Evaluator Agreement", use_container_width=True):
                    df_eval = st.session_state.df_evaluated
                    valid_mask = df_eval[automated_overall_col].isin(['Pass','Fail']) & df_eval[reviewer_final_col].isin(['Pass','Fail'])
                    comp_df = df_eval[valid_mask]
                    if not comp_df.empty:
                        matches = (comp_df[automated_overall_col] == comp_df[reviewer_final_col]).sum()
                        st.session_state.agreement_score = f"{(matches/len(comp_df))*100:.2f}% ({matches}/{len(comp_df)})"
                    else: st.session_state.agreement_score = "N/A (No comparable cases)"
                    st.session_state.agreement_calculated = True; st.rerun()
            if st.session_state.agreement_calculated and st.session_state.agreement_score is not None:
                st.metric("Agreement Score:", st.session_state.agreement_score)
            st.caption(f"Compares '{reviewer_final_col}' with '{automated_overall_col}'.")
        else: st.caption("Required columns for agreement missing.")

        csv_output = st.session_state.df_evaluated.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download Full Results (incl. Reviews)", data=csv_output,
                           file_name="llm_evaluation_results_with_review.csv", mime="text/csv")

if __name__ == "__main__":
    main()

# # streamlit_app.py
# import streamlit as st
# import pandas as pd
# import sys
# import os
# import io 
# import traceback
# import requests 
# import json 
# import time # Corrected import
# import urllib3 
# import datetime 

# project_root_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
# if project_root_path not in sys.path:
#     sys.path.insert(0, project_root_path)

# from llm_eval_package.data.loader import DataLoader
# from llm_eval_package.core.engine import Evaluator
# from llm_eval_package.ui.sidebar_view import SidebarView, BOT_DOMAIN_MAPPING
# from llm_eval_package.ui.data_view import DataManagementView
# from llm_eval_package.ui.results_view import ResultsView
# from llm_eval_package.ui.tutorial_view import TutorialView
# from llm_eval_package.config import (
#     METRIC_THRESHOLDS, AVAILABLE_METRICS, TASK_METRICS_PRESELECTION,
#     DEFAULT_PASS_CRITERION, PASS_CRITERION_ALL_PASS, PASS_CRITERION_ANY_PASS,
#     TASK_TYPE_RAG_FAQ, DEVELOPER_MODE, REQUIRED_COLUMNS # Added REQUIRED_COLUMNS
# )
# from llm_eval_package.data.rag_input_processor import (
#     DEFAULT_API_URL, DEFAULT_API_HEADERS, DEFAULT_DOMAINS
# )

# # fetch_bot_responses_for_df_streamlit_with_progress (remains the same from your previous full code)
# def fetch_bot_responses_for_df_streamlit_with_progress(
#     input_df: pd.DataFrame, query_column: str, selected_domain_key: str
#     ) -> pd.DataFrame:
#     if input_df.empty: st.warning("Input DataFrame empty. Cannot fetch."); return input_df.copy()
#     if query_column not in input_df.columns: st.error(f"'{query_column}' not found."); return input_df.copy()
#     output_df = input_df.copy()
#     if 'llm_output' not in output_df.columns: output_df['llm_output'] = pd.NA
#     output_df['llm_output'] = output_df['llm_output'].astype('object')
#     urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#     api_url, api_headers, domains_map = DEFAULT_API_URL, DEFAULT_API_HEADERS.copy(), DEFAULT_DOMAINS
#     domain_path = domains_map.get(selected_domain_key)
#     if not domain_path: st.error(f"Domain key '{selected_domain_key}' invalid."); return input_df.copy()
#     if "YOUR_EXPIRED_OR_PLACEHOLDER_TOKEN_HERE" in api_headers.get("Authorization",""): # Check for placeholder
#         st.error("FATAL: API token is a placeholder in configuration. Please update it in `llm_eval_package/data/rag_input_processor.py` for API calls to proceed.", icon="🚫")
#         return input_df.copy() 
#     total_q, progress_bar, status_text = len(output_df), st.progress(0.0), st.empty()
#     status_text.text("Initializing API calls..."); responses, fetched_ok = [pd.NA]*total_q, 0
#     for i, row_data in output_df.iterrows():
#         idx = int(i); query = str(row_data.get(query_column,''))
#         api_headers["Req-Date-Time"] = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00","Z")
#         payload = {"message": query, "senderId": "st_user", "domain": domain_path}
#         resp_msg = pd.NA; max_r, delay_r = 1, 1 # Low retries for UI
#         for attempt in range(max_r + 1):
#             try:
#                 api_resp = requests.post(api_url, headers=api_headers, data=json.dumps(payload), verify=False, timeout=25)
#                 api_resp.raise_for_status(); msg_full = ""
#                 if api_resp.text and api_resp.text.strip():
#                     for line in api_resp.text.strip().splitlines():
#                         try: obj = json.loads(line); msg_full += str(obj.get("data",""))
#                         except: 
#                             if not msg_full: msg_full += line; continue 
#                 else: msg_full = "Error: Empty API response" # Handle empty but successful response
#                 resp_msg = msg_full; fetched_ok += 1; break 
#             except requests.exceptions.RequestException as e_req: resp_msg = f"Error (API Attempt {attempt+1}): {str(e_req)[:100]}"
#             except Exception as e_other: resp_msg = f"Unexpected Error (Attempt {attempt+1}): {str(e_other)[:100]}"
#             if attempt < max_r: time.sleep(delay_r) 
#         responses[idx] = resp_msg
#         progress_bar.progress(float((idx+1)/total_q)); status_text.text(f"Processed: {idx+1}/{total_q}. Fetched OK: {fetched_ok}")
#     output_df['llm_output'] = responses
#     status_text.text(f"All {total_q} processed. Fetched OK: {fetched_ok}.")
#     if fetched_ok < total_q: st.warning(f"{total_q-fetched_ok} errors. Check 'llm_output'.")
#     else: st.success("All responses fetched!")
#     return output_df

# def main():
#     st.set_page_config(page_title="BYOB Evaluator by Genius AI", page_icon="✨", layout="wide") # Title for browser tab

#     data_loader, evaluator = DataLoader(), Evaluator()
#     sidebar_view, data_mgmt_view, results_view, tutorial_view = SidebarView(), DataManagementView(), ResultsView(), TutorialView()

#     default_session_state = {
#         'df_original': pd.DataFrame(), 
#         'df_evaluated': pd.DataFrame(),
#         'show_results': False, 'show_tutorial': True, 'file_uploader_key': 0,
#         'uploaded_file_name': None, 'agreement_calculated': False, 'agreement_score': None,
#         'main_selected_metrics': TASK_METRICS_PRESELECTION.get(TASK_TYPE_RAG_FAQ, ["Semantic Similarity"]),
#         'main_overall_criterion': DEFAULT_PASS_CRITERION,
#         'main_use_custom_thresholds': False, 'main_custom_thresholds': {},
#         'main_sensitive_keywords_input': "profanity, hate speech",
#         'selected_domain_key': list(BOT_DOMAIN_MAPPING.keys())[0] if BOT_DOMAIN_MAPPING else "SG Branch"
#     }
#     for key, default_val in default_session_state.items():
#         if key not in st.session_state: st.session_state[key] = default_val
    
#     sidebar_outputs = sidebar_view.render_sidebar(st.session_state.file_uploader_key)
#     uploaded_file_obj, selected_task_type, go_to_instructions, selected_domain_key_from_sidebar = sidebar_outputs[0], sidebar_outputs[1], sidebar_outputs[2], sidebar_outputs[3]
#     st.session_state.selected_domain_key = selected_domain_key_from_sidebar

#     if go_to_instructions:
#         st.session_state.show_tutorial = True; st.session_state.show_results = False
#         st.session_state.df_original = pd.DataFrame(); st.session_state.df_evaluated = pd.DataFrame()
#         st.session_state.file_uploader_key += 1; st.session_state.agreement_calculated = False; st.rerun()

#     # --- MODIFIED TITLE AND SUBHEADER ---
#     st.markdown(
#         """
#         <style>
#         .main-header {font-size: 3em; font-weight: bold; color: #4CAF50; text-align: center; margin-bottom: 0.5em; text-shadow: 2px 2px 4px rgba(0,0,0,0.1);}
#         .subheader {font-size: 1.5em; color: #555; text-align: center; margin-bottom: 1em;}
#         .stButton>button {background-color: #4CAF50; color: white; border-radius: 12px; padding: 10px 24px; font-size: 1.2em; border: none; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2); transition: 0.3s;}
#         .stButton>button:hover {background-color: #45a049; box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);}
#         .stAlert {border-radius: 10px;}
#         </style>
#         <h1 class="main-header">✨BYOB Evaluator✨</h1>
#         <h5 class="subheader">Tool by Genius AI</h5>
#         """,
#         unsafe_allow_html=True
#     )
#     # --- END OF TITLE MODIFICATION ---

#     if st.session_state.show_tutorial and uploaded_file_obj is None and st.session_state.df_original.empty:
#         tutorial_view.render_tutorial(); return
#     else:
#         if st.session_state.show_tutorial: st.session_state.show_tutorial = False

#     if uploaded_file_obj is not None:
#         if st.session_state.uploaded_file_name != uploaded_file_obj.name: 
#             try:
#                 df_loaded = data_loader.load_data(uploaded_file_obj)
#                 st.session_state.df_original = df_loaded.copy()
#                 st.session_state.uploaded_file_name = uploaded_file_obj.name
#                 st.session_state.df_evaluated = pd.DataFrame()
#                 st.session_state.show_results = False; st.session_state.agreement_calculated = False
#             except Exception as e:
#                 st.error(f"Error loading data: {e}"); st.session_state.df_original = pd.DataFrame()
#                 st.session_state.show_tutorial = True; st.session_state.uploaded_file_name = None; st.session_state.file_uploader_key += 1; st.rerun(); return
    
#     if not st.session_state.df_original.empty:
#         edited_df_original = data_mgmt_view.render_data_preview(
#             st.session_state.df_original.copy(), # Pass a copy
#             key_suffix="original_data_live_edit_v2"
#         )
#         if not edited_df_original.equals(st.session_state.df_original):
#             st.session_state.df_original = edited_df_original.copy()
#             st.session_state.df_evaluated = pd.DataFrame() 
#             st.session_state.show_results = False; st.session_state.agreement_calculated = False
#             st.caption("Data changes applied immediately. Re-run 'Fetch Responses' or 'Evaluation' if needed.")
#             st.rerun() 
    
#     if not st.session_state.df_original.empty:
#         st.markdown("---")
#         cols_fetch_btn = st.columns([1, 2.5, 1])
#         with cols_fetch_btn[1]:
#             if st.button("🔗 Fetch Bot Responses & Update Data", help="Calls API, updates 'llm_output'.", use_container_width=True):
#                 if 'query' not in st.session_state.df_original.columns: st.error("Data needs a 'query' column.")
#                 else:
#                     updated_df = fetch_bot_responses_for_df_streamlit_with_progress(
#                         st.session_state.df_original.copy(), 'query', st.session_state.selected_domain_key
#                     )
#                     st.session_state.df_original = updated_df.copy()
#                     st.session_state.df_evaluated = pd.DataFrame()
#                     st.session_state.show_results = False; st.session_state.agreement_calculated = False; st.rerun()
    
#     if not st.session_state.df_original.empty:
#         st.markdown("---")
#         with st.expander("🛠️ Configure Evaluation Settings", expanded=True):
#             st.session_state.main_selected_metrics = st.multiselect("Select Metrics:", list(AVAILABLE_METRICS.keys()), default=st.session_state.main_selected_metrics)
#             st.session_state.main_overall_criterion = st.selectbox("Automated Overall Result Logic:", [PASS_CRITERION_ALL_PASS, PASS_CRITERION_ANY_PASS], index=[PASS_CRITERION_ALL_PASS, PASS_CRITERION_ANY_PASS].index(st.session_state.main_overall_criterion))
#             st.session_state.main_use_custom_thresholds = st.checkbox("Use Custom Metric Thresholds", value=st.session_state.main_use_custom_thresholds)
#             if st.session_state.main_use_custom_thresholds:
#                 temp_custom_thresholds = st.session_state.main_custom_thresholds.copy()
#                 for metric in st.session_state.main_selected_metrics:
#                     default_thresh = METRIC_THRESHOLDS.get(metric, 0.5)
#                     current_val = float(temp_custom_thresholds.get(metric, default_thresh))
#                     if metric == "Safety": temp_custom_thresholds[metric] = 1.0; st.markdown(f"↳ **{metric}**: Threshold fixed at 1.0")
#                     else: temp_custom_thresholds[metric] = st.number_input(f"Thresh. for {metric}", 0.0, 1.0, current_val, 0.01, key=f"main_thresh_{metric}")
#                 st.session_state.main_custom_thresholds = temp_custom_thresholds
#             if "Safety" in st.session_state.main_selected_metrics and DEVELOPER_MODE:
#                 st.session_state.main_sensitive_keywords_input = st.text_area("Sensitive Keywords (for Safety):", st.session_state.main_sensitive_keywords_input)

#         cols_eval_btn = st.columns([1, 2, 1]); 
#         with cols_eval_btn[1]:
#             run_evaluation_button_clicked = st.button("🚀 Run Evaluation", use_container_width=True)
        
#         if run_evaluation_button_clicked:
#             if 'llm_output' not in st.session_state.df_original.columns or st.session_state.df_original['llm_output'].astype(str).str.strip().replace('', pd.NA).isnull().all():
#                 st.error("The 'llm_output' is missing/empty.")
#             elif not st.session_state.main_selected_metrics: st.warning("Please select at least one metric.")
#             else:
#                 with st.spinner("Crunching numbers... Evaluation in progress! 🧠"):
#                     try:
#                         sensitive_keywords_list = []
#                         if "Safety" in st.session_state.main_selected_metrics and DEVELOPER_MODE:
#                             sensitive_keywords_list = [k.strip().lower() for k in st.session_state.main_sensitive_keywords_input.split(',') if k.strip()]
#                         eval_custom_thresh = st.session_state.main_custom_thresholds if st.session_state.main_use_custom_thresholds else None
                        
#                         df_to_evaluate = st.session_state.df_original.copy()
#                         automated_overall_col = "Automated Overall Result"
#                         reviewer_final_col = "Reviewer's Final Result"
#                         initial_verdict_col = "initial_reviewer_verdict"

#                         evaluated_data_from_engine = evaluator.evaluate_dataframe(
#                             df_to_evaluate, st.session_state.main_selected_metrics,
#                             custom_thresholds=eval_custom_thresh, sensitive_keywords=sensitive_keywords_list,
#                             overall_pass_criterion=st.session_state.main_overall_criterion
#                         )
                        
#                         final_evaluated_df = evaluated_data_from_engine.copy()
#                         # Initialize Reviewer's Final Result column before pre-population
#                         final_evaluated_df[reviewer_final_col] = pd.NA 

#                         # Pre-populate Reviewer's Final Result
#                         if initial_verdict_col in df_to_evaluate.columns: # Check in original uploaded data
#                             # Use .loc with matching indices to ensure correct assignment
#                             # This assumes df_to_evaluate (source for initial_verdict_col) 
#                             # and final_evaluated_df have aligned indices.
#                             # This is true if final_evaluated_df is derived from df_to_evaluate without re-indexing.
#                             valid_initial_verdicts = df_to_evaluate[initial_verdict_col].isin(['Pass', 'Fail', 'N/A', 'Error'])
#                             final_evaluated_df.loc[valid_initial_verdicts, reviewer_final_col] = df_to_evaluate.loc[valid_initial_verdicts, initial_verdict_col]

#                         # Fill remaining NAs in Reviewer's Final Result with Automated Overall Result
#                         if automated_overall_col in final_evaluated_df.columns:
#                             final_evaluated_df[reviewer_final_col] = final_evaluated_df[reviewer_final_col].fillna(
#                                 final_evaluated_df[automated_overall_col]
#                             )
#                         # Ensure any remaining NAs become 'N/A' string for selectbox editor
#                         final_evaluated_df[reviewer_final_col] = final_evaluated_df[reviewer_final_col].fillna('N/A')
                        
#                         st.session_state.df_evaluated = final_evaluated_df.copy()
                        
#                         st.session_state.show_results = True
#                         st.session_state.selected_metrics_for_results = st.session_state.main_selected_metrics[:]
#                         st.session_state.custom_thresholds_for_results = eval_custom_thresh.copy() if eval_custom_thresh else None
#                         st.session_state.show_tutorial = False; st.session_state.agreement_calculated = False
#                         st.success("Evaluation Complete!"); st.rerun()
#                     except Exception as e: st.error(f"Evaluation Error: {e}"); st.exception(e)

#     if st.session_state.show_results and not st.session_state.df_evaluated.empty:
#         automated_overall_col = "Automated Overall Result"; reviewer_final_col = "Reviewer's Final Result"

#         returned_edited_results_df = results_view.render_results(
#             st.session_state.df_evaluated.copy(), 
#             st.session_state.selected_metrics_for_results,
#             st.session_state.custom_thresholds_for_results,
#             automated_overall_col_name=automated_overall_col, 
#             reviewer_override_column=reviewer_final_col
#         )
#         if not returned_edited_results_df.equals(st.session_state.df_evaluated):
#             st.session_state.df_evaluated = returned_edited_results_df.copy()
#             st.session_state.agreement_calculated = False 
#             st.caption("Reviewer's Final Result edits applied immediately.")
#             st.rerun() 

#         st.markdown("---"); st.subheader("⚖️ Reviewer Agreement Score")
#         if reviewer_final_col in st.session_state.df_evaluated.columns and automated_overall_col in st.session_state.df_evaluated.columns:
#             cols_agreement_btn = st.columns([2,2,2])
#             with cols_agreement_btn[1]:
#                 if st.button("Calculate Reviewer-Evaluator Agreement", use_container_width=True):
#                     df_eval = st.session_state.df_evaluated
#                     valid_mask = df_eval[automated_overall_col].isin(['Pass','Fail']) & df_eval[reviewer_final_col].isin(['Pass','Fail'])
#                     comp_df = df_eval[valid_mask]
#                     if not comp_df.empty:
#                         matches = (comp_df[automated_overall_col] == comp_df[reviewer_final_col]).sum()
#                         st.session_state.agreement_score = f"{(matches/len(comp_df))*100:.2f}% ({matches}/{len(comp_df)})"
#                     else: st.session_state.agreement_score = "N/A (No comparable cases)"
#                     st.session_state.agreement_calculated = True; st.rerun()
#             if st.session_state.agreement_calculated and st.session_state.agreement_score is not None:
#                 st.metric("Agreement Score:", st.session_state.agreement_score)
#             st.caption(f"Compares '{reviewer_final_col}' with '{automated_overall_col}'.")
#         else: st.caption("Required columns for agreement missing.")

#         csv_output = st.session_state.df_evaluated.to_csv(index=False).encode('utf-8')
#         st.download_button(label="📥 Download Full Results (incl. Reviews)", data=csv_output,
#                            file_name="llm_evaluation_results_with_review.csv", mime="text/csv")

# if __name__ == "__main__":
#     main()