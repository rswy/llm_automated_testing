# llm_eval_package/ui/sidebar_view.py
import streamlit as st
from pathlib import Path
import sys

from llm_eval_package.config import (
    TASK_TYPE_MAPPING, DEVELOPER_MODE, TASK_TYPE_RAG_FAQ, ENABLE_TASK_SELECTION
    # Removed metric/threshold/criteria specific imports as they are moved to main panel
)

# Bot domain mapping
BOT_DOMAIN_MAPPING = {
    'Finance': '/dmofinance-122',
    'HR': '/hr-161',
    'SG Branch': '/branch-ops-181',
    'TH Branch': '/thailand-101',
    'GWB': 'gwb-25',
    'DMO': '/dmo-61'
}

class SidebarView:
    def __init__(self):
        pass

    def render_sidebar(self, file_uploader_key: int):
        # --- Logo ---
        # Replace this URL with the path to your actual logo file or its URL
        # For local files, ensure the path is relative to your Streamlit app's root directory
        # e.g., if your logo is in an 'assets' folder: "assets/logo.png"
        # For a transparent background logo, ensure it's a PNG.
        
        
        # A more professional placeholder:
        # https://www.gstatic.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png
        # logo_url = "https://placehold.co/250x80/FFFFFF/000000/png?text=Genius+AI+%26+Innovation+Group&font=raleway"
        logo_url = "logo/genius_ai_7.png" # Placeholder

 

        # Display the logo
        # Use columns to center the logo if desired, or adjust width
        # col1, col2, col3 = st.sidebar.columns([1,3,1])
        # with col2:
        st.sidebar.image(logo_url, use_container_width='auto')
        
        # Simpler logo display:
        # st.sidebar.image(logo_url, width=200) # Adjust width as needed
        # st.sidebar.caption("Genius AI - Innovation Group") # Text caption if not in logo image

        st.sidebar.title("⚙️ Configuration")
        st.sidebar.markdown("---")

        go_to_instructions = st.sidebar.button("📖 View Instructions/Help", help="Learn how to use the tool.", use_container_width=True)
        st.sidebar.markdown("---")

        st.sidebar.header("1. Data Input")
        uploaded_file = st.sidebar.file_uploader(
            "Upload Dataset (CSV or JSON)", type=["csv", "json"],
            key=f"file_uploader_{file_uploader_key}",
            help="Upload your test data. See 'Instructions' for required format."
        )

        st.sidebar.header("2. Bot API Settings (Optional)")
        domain_display_names = list(BOT_DOMAIN_MAPPING.keys())
        default_domain_index = domain_display_names.index('SG Branch') if 'SG Branch' in domain_display_names else 0
        selected_domain_display_name = st.sidebar.selectbox(
            "Bot Domain:", options=domain_display_names, index=default_domain_index,
            help="Select bot domain for the 'Fetch Bot Responses' feature."
        )
        selected_domain_key = selected_domain_display_name

        selected_task_type = TASK_TYPE_RAG_FAQ 
        if ENABLE_TASK_SELECTION and DEVELOPER_MODE: 
            st.sidebar.header("Task Type (Dev Mode)")
            task_options = list(TASK_TYPE_MAPPING.values())
            current_task_display = TASK_TYPE_MAPPING.get(selected_task_type, task_options[0])
            selected_task_type_display = st.sidebar.selectbox(
                "Task Type:", options=task_options,
                index=task_options.index(current_task_display) if current_task_display in task_options else 0
            )
            selected_task_type = next((k for k, v in TASK_TYPE_MAPPING.items() if v == selected_task_type_display), TASK_TYPE_RAG_FAQ)
        elif DEVELOPER_MODE and not ENABLE_TASK_SELECTION:
             st.sidebar.caption(f"Task Type fixed to: {TASK_TYPE_MAPPING[selected_task_type]}")

        return (
            uploaded_file,
            selected_task_type, 
            go_to_instructions,
            selected_domain_key
        )


# # # # # import streamlit as st
# # # # # from pathlib import Path
# # # # # import sys
# # # # # import time # Import time for sleep

# # # # # # Ensure tasks module can be found for mock data generation (if not already in sys.path)
# # # # # try:
# # # # #     # This path assumes llm_eval_package is one level up from ui/sidebar_view.py
# # # # #     project_root_for_mock_data = Path(__file__).resolve().parent.parent.parent
# # # # #     if str(project_root_for_mock_data) not in sys.path:
# # # # #         sys.sys.path.insert(0, str(project_root_for_mock_data))
    
# # # # #     # Import mock data functions from their new location
# # # # #     from llm_eval_package.data.generator import generate_mock_data_flat, save_mock_data
# # # # #     MOCK_DATA_GENERATOR_AVAILABLE = True
# # # # # except ImportError as e:
# # # # #     st.warning(f"Could not import mock data generator: {e}. Mock data generation button will be disabled.")
# # # # #     MOCK_DATA_GENERATOR_AVAILABLE = False


# # # # # from llm_eval_package.config import ( # Updated import path
# # # # #     AVAILABLE_METRICS, METRIC_THRESHOLDS, TASK_TYPE_MAPPING, 
# # # # #     TASK_METRICS_PRESELECTION, ENABLE_TASK_SELECTION, ENABLE_METRIC_SELECTION, DEVELOPER_MODE # Import new flags
# # # # # )

# # # # # class SidebarView:
# # # # #     """
# # # # #     Manages the display and interaction of the sidebar in the Streamlit application.
# # # # #     This includes data upload, metric selection, and evaluation controls.
# # # # #     """

# # # # #     def __init__(self):
# # # # #         """
# # # # #         Initializes the SidebarView.
# # # # #         """
# # # # #         pass

# # # # #     def render_sidebar(self, file_uploader_key: int):
# # # # #         """
# # # # #         Renders the sidebar components and returns the user's selections.

# # # # #         Args:
# # # # #             file_uploader_key (int): A key used to manage the state of the file uploader.

# # # # #         Returns:
# # # # #             tuple: A tuple containing:
# # # # #                 - uploaded_file (streamlit.runtime.uploaded_file_manager.UploadedFile or None): The uploaded data file.
# # # # #                 - selected_metrics (list): A list of metric names selected by the user.
# # # # #                 - run_evaluation (bool): True if the 'Run Evaluation' button was clicked, False otherwise.
# # # # #                 - custom_thresholds (dict or None): A dictionary of custom thresholds if enabled, else None.
# # # # #                 - sensitive_keywords (list): A list of user-defined sensitive keywords.
# # # # #                 - selected_task_type (str): The selected task type.
# # # # #                 - go_to_instructions (bool): True if 'Go to Instructions' button was clicked.
# # # # #         """
# # # # #         st.sidebar.title("LLM Evaluation Tool")
# # # # #         # Add a small logo/icon
# # # # #         # st.sidebar.image("path/to/your/logo.png", use_column_width=True) # If you have a logo image
# # # # #         st.sidebar.markdown("---")

# # # # #         # Go to Instructions Button
# # # # #         go_to_instructions = st.sidebar.button("💡 Go to Instructions", help="Learn how to use the tool.")
# # # # #         st.sidebar.markdown("---") # Separator

# # # # #         # 1. Data Upload Section
# # # # #         st.sidebar.header("1. Upload Data")
# # # # #         # Pass the key to the file uploader
# # # # #         uploaded_file = st.sidebar.file_uploader("Upload your dataset (CSV or JSON)", type=["csv", "json"], key=f"file_uploader_{file_uploader_key}")

# # # # #         # Add Mock Data Generation Button
# # # # #         if MOCK_DATA_GENERATOR_AVAILABLE:
# # # # #             if st.sidebar.button("✨ Generate Mock Data", help="Generate a sample dataset for testing."):
# # # # #                 with st.spinner("Generating mock data..."):
# # # # #                     try:
# # # # #                         # Define output directory relative to project root dynamically
# # # # #                         # This path assumes the 'data' folder is at the project root
# # # # #                         project_root = Path(__file__).resolve().parent.parent.parent
# # # # #                         data_dir = project_root / "data"

# # # # #                         mock_data = generate_mock_data_flat(num_samples_per_task=3)
# # # # #                         save_mock_data(mock_data, output_dir=data_dir, base_filename="llm_eval_mock_data_generated")
# # # # #                         st.toast("Mock data generated and saved to 'data/' folder! Please upload the generated file.", icon="✅") # Changed to st.toast
# # # # #                         time.sleep(3) # Keep toast visible for 3 seconds
# # # # #                         st.rerun() # Rerun to allow user to immediately load the new data
# # # # #                     except Exception as e:
# # # # #                         st.sidebar.error(f"Error generating mock data: {e}")
# # # # #         else:
# # # # #             st.sidebar.info("Mock data generator not available. Check dependencies/imports.")


# # # # #         # 2. Task Type Selection (Conditional based on ENABLE_TASK_SELECTION)
# # # # #         selected_task_type = None
# # # # #         if ENABLE_TASK_SELECTION:
# # # # #             st.sidebar.header("2. Select Task Type")
# # # # #             selected_task_type_display = st.sidebar.selectbox(
# # # # #                 "Choose the task type for evaluation:",
# # # # #                 options=list(TASK_TYPE_MAPPING.values()),
# # # # #                 format_func=lambda x: x, # The format_func is applied to the options
# # # # #                 help="Select the type of task your LLM performs to get relevant metric suggestions."
# # # # #             )
# # # # #             selected_task_type = next(key for key, value in TASK_TYPE_MAPPING.items() if value == selected_task_type_display)
# # # # #         else:
# # # # #             # If disabled (end-user mode), fix to RAG FAQ
# # # # #             selected_task_type = "rag_faq" # Fixed for end-user mode
# # # # #             st.sidebar.info(f"Task Type fixed to: **{TASK_TYPE_MAPPING[selected_task_type]}** (Developer Mode Off)")


# # # # #         # 3. Metric Selection Section (Conditional based on ENABLE_METRIC_SELECTION)
# # # # #         selected_metrics = []
# # # # #         if ENABLE_METRIC_SELECTION:
# # # # #             st.sidebar.header("3. Select Metrics")
# # # # #             preselected_metrics = TASK_METRICS_PRESELECTION.get(selected_task_type, [])
# # # # #             preselected_metrics = [
# # # # #                 metric for metric in preselected_metrics if metric in AVAILABLE_METRICS
# # # # #             ]
# # # # #             all_metric_names = list(AVAILABLE_METRICS.keys())

# # # # #             selected_metrics = st.sidebar.multiselect(
# # # # #                 "Choose metrics for evaluation:",
# # # # #                 options=all_metric_names,
# # # # #                 default=preselected_metrics,
# # # # #                 help="Select the metrics to evaluate your LLM's performance."
# # # # #             )
# # # # #         else:
# # # # #             # If disabled (end-user mode), fix to Semantic Similarity
# # # # #             selected_metrics = ["Semantic Similarity"] # Fixed for end-user mode
# # # # #             st.sidebar.info(f"Metrics fixed to: **{', '.join(selected_metrics)}** (Developer Mode Off)")


# # # # #         # 4. Threshold Settings
# # # # #         st.sidebar.header("4. Threshold Settings")
# # # # #         # In end-user mode, this is the only adjustable setting
# # # # #         use_custom_thresholds = st.sidebar.checkbox(
# # # # #             "Use Custom Thresholds", 
# # # # #             value=True if not DEVELOPER_MODE else False, # Default to True for end-user
# # # # #             help="Toggle to define your own pass/fail cut-off scores for each metric."
# # # # #         )

# # # # #         custom_thresholds = {}
# # # # #         if use_custom_thresholds:
# # # # #             st.sidebar.write("Set custom thresholds for selected metrics:")
# # # # #             for metric_name in selected_metrics:
# # # # #                 default_threshold = METRIC_THRESHOLDS.get(metric_name, 0.5) # Default to 0.5 if not found
# # # # #                 # For Safety metric, the threshold is typically 1.0 (pass if 1.0)
# # # # #                 if metric_name == "Safety":
# # # # #                     st.sidebar.markdown(f"**{metric_name}**: Output is considered safe if score is 1.0 (no sensitive keywords detected).")
# # # # #                     custom_thresholds[metric_name] = 1.0 # Fixed threshold for Safety
# # # # #                 else:
# # # # #                     custom_thresholds[metric_name] = st.sidebar.number_input(
# # # # #                         f"{metric_name} Threshold",
# # # # #                         min_value=0.0,
# # # # #                         max_value=1.0,
# # # # #                         value=float(default_threshold),
# # # # #                         step=0.01,
# # # # #                         key=f"custom_threshold_{metric_name}", # Unique key for each input
# # # # #                         help=f"Set the minimum score for '{metric_name}' to be considered 'Pass'."
# # # # #                     )
# # # # #         else:
# # # # #             custom_thresholds = None # Indicate that default thresholds should be used
# # # # #             st.sidebar.info("Using default thresholds for all metrics.")


# # # # #         # 5. Safety Keyword Input (if Safety metric is selected and in developer mode)
# # # # #         sensitive_keywords = []
# # # # #         if "Safety" in selected_metrics and DEVELOPER_MODE: # Only show in developer mode
# # # # #             st.sidebar.header("5. Safety Keywords")
# # # # #             keywords_input = st.sidebar.text_area(
# # # # #                 "Enter sensitive keywords (comma-separated):",
# # # # #                 "profanity, hate speech, violence, explicit, harmful", # Example defaults
# # # # #                 help="Define keywords that, if found in LLM output, will flag the response as 'unsafe'."
# # # # #             )
# # # # #             if keywords_input:
# # # # #                 sensitive_keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
            
# # # # #             if not sensitive_keywords:
# # # # #                 st.sidebar.warning("No sensitive keywords entered for Safety metric. It will always pass.")

# # # # #         # Removed Run Evaluation button from sidebar_view
# # # # #         run_evaluation = False 

# # # # #         return (
# # # # #             uploaded_file,
# # # # #             selected_metrics,
# # # # #             run_evaluation, # This will always be False now
# # # # #             custom_thresholds,
# # # # #             sensitive_keywords,
# # # # #             selected_task_type,
# # # # #             go_to_instructions
# # # # #         )



# # # # import streamlit as st
# # # # from pathlib import Path
# # # # import sys
# # # # import time 

# # # # # Ensure tasks module can be found (if not already in sys.path)
# # # # try:
# # # #     project_root_for_mock_data = Path(__file__).resolve().parent.parent.parent
# # # #     if str(project_root_for_mock_data) not in sys.path:
# # # #         sys.path.insert(0, str(project_root_for_mock_data))
# # # #     from llm_eval_package.data.generator import generate_mock_data_flat, save_mock_data
# # # #     MOCK_DATA_GENERATOR_AVAILABLE = True
# # # # except ImportError as e:
# # # #     # st.warning(f"Could not import mock data generator: {e}. Mock data generation button will be disabled.")
# # # #     print(f"Warning: Could not import mock data generator from sidebar_view: {e}") # Print for non-Streamlit context
# # # #     MOCK_DATA_GENERATOR_AVAILABLE = False


# # # # from llm_eval_package.config import (
# # # #     AVAILABLE_METRICS, METRIC_THRESHOLDS, TASK_TYPE_MAPPING,
# # # #     TASK_METRICS_PRESELECTION, ENABLE_TASK_SELECTION, # <-- This flag will control visibility
# # # #     ENABLE_METRIC_SELECTION, DEVELOPER_MODE,
# # # #     PASS_CRITERION_ALL_PASS, PASS_CRITERION_ANY_PASS, DEFAULT_PASS_CRITERION
# # # # )

# # # # # Bot domain mapping as provided by the user
# # # # BOT_DOMAIN_MAPPING = {
# # # #     'Finance': '/dmofinance-122',
# # # #     'HR': '/hr-161',
# # # #     'SG Branch': '/branch-ops-181',
# # # #     'TH Branch': '/thailand-101',
# # # #     'GWB': 'gwb-25',
# # # #     'DMO': '/dmo-61'
# # # # }

# # # # class SidebarView:
# # # #     def __init__(self):
# # # #         pass

# # # #     def render_sidebar(self, file_uploader_key: int):
# # # #         st.sidebar.title("LLM Evaluation Tool")
# # # #         st.sidebar.markdown("---")

# # # #         go_to_instructions = st.sidebar.button("💡 Go to Instructions", help="Learn how to use the tool.")
# # # #         st.sidebar.markdown("---")

# # # #         st.sidebar.header("1. Upload Data")
# # # #         uploaded_file = st.sidebar.file_uploader("Upload your dataset (CSV or JSON)", type=["csv", "json"], key=f"file_uploader_{file_uploader_key}")

# # # #         if MOCK_DATA_GENERATOR_AVAILABLE:
# # # #             if st.sidebar.button("✨ Generate Mock Data", help="Generate a sample dataset for testing."):
# # # #                 with st.spinner("Generating mock data..."):
# # # #                     try:
# # # #                         project_root = Path(__file__).resolve().parent.parent.parent
# # # #                         data_dir = project_root / "data"
# # # #                         mock_data = generate_mock_data_flat(num_samples_per_task=3) # Using flat mock data
# # # #                         save_mock_data(mock_data, output_dir=data_dir, base_filename="llm_eval_mock_data_generated")
# # # #                         st.toast("Mock data generated and saved to 'data/' folder! Please upload the generated file.", icon="✅")
# # # #                         time.sleep(3) 
# # # #                         # st.rerun() # Rerun can sometimes cause issues if not handled carefully
# # # #                     except Exception as e:
# # # #                         st.sidebar.error(f"Error generating mock data: {e}")
# # # #         # else:
# # # #             # st.sidebar.info("Mock data generator not available. Check dependencies/imports.")


# # # #         # New Section: Bot Domain Selection
# # # #         st.sidebar.header("1b. Bot Domain Config") 
# # # #         domain_display_names = list(BOT_DOMAIN_MAPPING.keys())
# # # #         default_domain_index = domain_display_names.index('SG Branch') if 'SG Branch' in domain_display_names else 0
# # # #         selected_domain_display_name = st.sidebar.selectbox(
# # # #             "Choose Bot Domain for Fetching Responses:",
# # # #             options=domain_display_names,
# # # #             index=default_domain_index,
# # # #             help="Select the bot domain if you intend to fetch live responses for queries in the uploaded file."
# # # #         )
# # # #         selected_domain_key = selected_domain_display_name 

# # # #         selected_task_type = None # Default to None
# # # #         if ENABLE_TASK_SELECTION:
# # # #             st.sidebar.header("2. Select Task Type")
# # # #             task_options = list(TASK_TYPE_MAPPING.values())
# # # #             # Ensure a default is selected if session state hasn't initialized one
# # # #             # This part might need adjustment based on how selected_task_type is managed in session_state
# # # #             # For simplicity, let's assume a default or that it's handled in main app logic.
# # # #             selected_task_type_display = st.sidebar.selectbox(
# # # #                 "Choose the task type for evaluation:",
# # # #                 options=task_options,
# # # #                 index = 0, # Default to first option if not otherwise set
# # # #                 format_func=lambda x: x, 
# # # #                 help="Select the type of task your LLM performs to get relevant metric suggestions."
# # # #             )
# # # #             selected_task_type = next((key for key, value in TASK_TYPE_MAPPING.items() if value == selected_task_type_display), "rag_faq")

# # # #         else:
# # # #             selected_task_type = "rag_faq" 
# # # #             # if DEVELOPER_MODE: # Only show this info if dev mode is on, but selection is off
# # # #             #      st.sidebar.info(f"Task Type fixed to: **{TASK_TYPE_MAPPING[selected_task_type]}** (Task Selection Disabled)")

# # # #             if ENABLE_TASK_SELECTION: # This will be False after config change
# # # #                 st.sidebar.header("2. Select Task Type")
# # # #                 task_options = list(TASK_TYPE_MAPPING.values())
# # # #                 selected_task_type_display = st.sidebar.selectbox(
# # # #                     "Choose the task type for evaluation:",
# # # #                     options=task_options,
# # # #                     index = 0,
# # # #                     format_func=lambda x: x,
# # # #                     help="Select the type of task your LLM performs to get relevant metric suggestions."
# # # #                 )
# # # #                 selected_task_type = next((key for key, value in TASK_TYPE_MAPPING.items() if value == selected_task_type_display), "rag_faq")
# # # #             # else:
# # # #             #     # When ENABLE_TASK_SELECTION is False, this section won't be shown.
# # # #             #     # We still pass back a default selected_task_type.
# # # #             #     if DEVELOPER_MODE: # Optionally show info if in developer mode but selection is off
# # # #             #         st.sidebar.info(f"Task Type fixed to: **{TASK_TYPE_MAPPING[selected_task_type]}** (Task Selection Disabled by Config)")


# # # #         selected_metrics = []
# # # #         if ENABLE_METRIC_SELECTION:
# # # #             st.sidebar.header("3. Select Metrics")
# # # #             preselected_metrics_keys = TASK_METRICS_PRESELECTION.get(selected_task_type, [])
# # # #             # Ensure preselected are valid metric names (keys of AVAILABLE_METRICS)
# # # #             preselected_metrics = [
# # # #                 metric for metric in preselected_metrics_keys if metric in AVAILABLE_METRICS
# # # #             ]
# # # #             all_metric_names = list(AVAILABLE_METRICS.keys())

# # # #             selected_metrics = st.sidebar.multiselect(
# # # #                 "Choose metrics for evaluation:",
# # # #                 options=all_metric_names,
# # # #                 default=preselected_metrics,
# # # #                 help="Select the metrics to evaluate your LLM's performance."
# # # #             )
# # # #         else:
# # # #             selected_metrics = ["Semantic Similarity"] 
# # # #             if DEVELOPER_MODE: # Only show this info if dev mode is on, but selection is off
# # # #                 st.sidebar.info(f"Metrics fixed to: **{', '.join(selected_metrics)}** (Metric Selection Disabled)")



# # # #         st.sidebar.header("4. Evaluation Configuration") # Renumbering to group eval settings

# # # #         # --- NEW: Overall Pass/Fail Criterion ---
# # # #         st.sidebar.subheader("Overall Pass/Fail Logic")
# # # #         overall_pass_criteria_options = [PASS_CRITERION_ALL_PASS, PASS_CRITERION_ANY_PASS]
# # # #         selected_overall_criterion = st.sidebar.selectbox(
# # # #             "Define overall pass/fail for a test case:",
# # # #             options=overall_pass_criteria_options,
# # # #             index=overall_pass_criteria_options.index(DEFAULT_PASS_CRITERION),
# # # #             help="How should the final pass/fail status be determined if multiple metrics are used?"
# # # #         )

# # # #         st.sidebar.header("4. Threshold Settings")
# # # #         use_custom_thresholds = st.sidebar.checkbox(
# # # #             "Use Custom Thresholds", 
# # # #             value=True if not DEVELOPER_MODE else False, 
# # # #             help="Toggle to define your own pass/fail cut-off scores for each metric."
# # # #         )

# # # #         custom_thresholds = {}
# # # #         if use_custom_thresholds:
# # # #             st.sidebar.write("Set custom thresholds for selected metrics:")
# # # #             for metric_name in selected_metrics:
# # # #                 default_threshold = METRIC_THRESHOLDS.get(metric_name, 0.5) 
# # # #                 if metric_name == "Safety":
# # # #                     st.sidebar.markdown(f"**{metric_name}**: Output is safe if score is 1.0.")
# # # #                     custom_thresholds[metric_name] = 1.0 
# # # #                 else:
# # # #                     custom_thresholds[metric_name] = st.sidebar.number_input(
# # # #                         f"{metric_name} Threshold",
# # # #                         min_value=0.0, max_value=1.0,
# # # #                         value=float(default_threshold), step=0.01,
# # # #                         key=f"custom_threshold_{metric_name}", 
# # # #                         help=f"Min score for '{metric_name}' to be 'Pass'."
# # # #                     )
# # # #         else:
# # # #             custom_thresholds = None 
# # # #             st.sidebar.info("Using default thresholds.")


# # # #         sensitive_keywords = []
# # # #         if "Safety" in selected_metrics and DEVELOPER_MODE: 
# # # #             st.sidebar.header("5. Safety Keywords")
# # # #             keywords_input = st.sidebar.text_area(
# # # #                 "Enter sensitive keywords (comma-separated):",
# # # #                 "profanity, hate speech, violence, explicit, harmful", 
# # # #                 help="Keywords that flag LLM output as 'unsafe'."
# # # #             )
# # # #             if keywords_input:
# # # #                 sensitive_keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
# # # #             if not sensitive_keywords:
# # # #                 st.sidebar.warning("No sensitive keywords for Safety metric. It will always pass.")
        
# # # #         run_evaluation = False 

# # # #         return (
# # # #             uploaded_file,
# # # #             selected_metrics, # This now uses the default task_type for preselection
# # # #             run_evaluation,
# # # #             custom_thresholds,
# # # #             sensitive_keywords,
# # # #             selected_task_type, # Will be the default one
# # # #             go_to_instructions,
# # # #             selected_domain_key
# # # #         )






# # # import streamlit as st
# # # from pathlib import Path
# # # import sys
# # # import time

# # # # Ensure tasks module can be found (if not already in sys.path) for mock data generator
# # # # This path assumes llm_eval_package is one level up from ui/sidebar_view.py
# # # # and the main project root is one level above llm_eval_package.
# # # try:
# # #     project_root_for_mock_data = Path(__file__).resolve().parent.parent.parent
# # #     if str(project_root_for_mock_data) not in sys.path:
# # #         sys.path.insert(0, str(project_root_for_mock_data))
# # #     from llm_eval_package.data.generator import generate_mock_data_flat, save_mock_data
# # #     MOCK_DATA_GENERATOR_AVAILABLE = True
# # # except ImportError as e:
# # #     # Using print for non-Streamlit contexts (like initial import checks)
# # #     print(f"Warning (from sidebar_view.py): Could not import mock data generator: {e}.")
# # #     MOCK_DATA_GENERATOR_AVAILABLE = False


# # # from llm_eval_package.config import (
# # #     AVAILABLE_METRICS, METRIC_THRESHOLDS, TASK_TYPE_MAPPING,
# # #     # TASK_METRICS_PRESELECTION, # Will use default task_type for preselection
# # #     ENABLE_TASK_SELECTION, # This will be False
# # #     ENABLE_METRIC_SELECTION, DEVELOPER_MODE,
# # #     PASS_CRITERION_ALL_PASS, PASS_CRITERION_ANY_PASS, DEFAULT_PASS_CRITERION # Import pass criteria
# # # )

# # # # Bot domain mapping (can also be moved to config.py if globally needed)
# # # BOT_DOMAIN_MAPPING = {
# # #     'Finance': '/dmofinance-122',
# # #     'HR': '/hr-161',
# # #     'SG Branch': '/branch-ops-181',
# # #     'TH Branch': '/thailand-101',
# # #     'GWB': 'gwb-25',
# # #     'DMO': '/dmo-61'
# # # }

# # # class SidebarView:
# # #     def __init__(self):
# # #         pass

# # #     def render_sidebar(self, file_uploader_key: int):
# # #         st.sidebar.title("⚙️ Configuration")
# # #         st.sidebar.markdown("---")

# # #         # Go to Instructions Button
# # #         go_to_instructions = st.sidebar.button("💡 How to Use This Tool", help="Learn how to use the LLM Evaluator.", use_container_width=True)
# # #         st.sidebar.markdown("---")

# # #         # 1. Data Upload Section
# # #         st.sidebar.header("1. Load Your Data")
# # #         uploaded_file = st.sidebar.file_uploader("Upload dataset (CSV or JSON)", type=["csv", "json"], key=f"file_uploader_{file_uploader_key}")

# # #         # Add Mock Data Generation Button
# # #         if MOCK_DATA_GENERATOR_AVAILABLE:
# # #             if st.sidebar.button("✨ Generate Sample Data", help="Generate a sample dataset for testing.", use_container_width=True):
# # #                 with st.spinner("Generating sample data..."):
# # #                     try:
# # #                         # Define output directory relative to project root dynamically
# # #                         project_root = Path(__file__).resolve().parent.parent.parent
# # #                         data_dir = project_root / "data" # Standard "data" folder at project root

# # #                         mock_data = generate_mock_data_flat(num_samples_per_task=3) # Using flat mock data
# # #                         save_mock_data(mock_data, output_dir=data_dir, base_filename="llm_eval_mock_data_generated")
# # #                         st.toast("Sample data saved to 'data/' folder! Please upload the 'llm_eval_mock_data_generated.csv' or '.json' file.", icon="✅")
# # #                         time.sleep(3) # Keep toast visible
# # #                     except Exception as e:
# # #                         st.sidebar.error(f"Error generating sample data: {e}")
# # #         # else:
# # #             # st.sidebar.info("Mock data generator not available.")


# # #         # 2. Bot API Configuration (for fetching live responses)
# # #         st.sidebar.header("2. Bot API Settings")
# # #         domain_display_names = list(BOT_DOMAIN_MAPPING.keys())
# # #         # Default to 'SG Branch' or the first available if 'SG Branch' isn't in the list
# # #         default_domain_index = domain_display_names.index('SG Branch') if 'SG Branch' in domain_display_names else 0
# # #         selected_domain_display_name = st.sidebar.selectbox(
# # #             "Bot Domain for Fetching Responses:",
# # #             options=domain_display_names,
# # #             index=default_domain_index,
# # #             help="Select the bot domain if using the 'Fetch Bot Responses' feature."
# # #         )
# # #         selected_domain_key = selected_domain_display_name # In this case, display name is the key


# # #         # 3. Evaluation Settings
# # #         st.sidebar.header("3. Evaluation Settings")

# # #         # Task Type Selection (Hidden as per request by setting ENABLE_TASK_SELECTION=False in config)
# # #         selected_task_type = "rag_faq" # Default to rag_faq as selection is removed for user
# # #         if ENABLE_TASK_SELECTION: # This block will not be shown if False in config
# # #             st.sidebar.subheader("Task Type") # Retained subheader for consistency if re-enabled
# # #             task_options = list(TASK_TYPE_MAPPING.values())
# # #             selected_task_type_display = st.sidebar.selectbox(
# # #                 "Primary Task of your LLM:",
# # #                 options=task_options,
# # #                 index = task_options.index(TASK_TYPE_MAPPING.get(selected_task_type, task_options[0])),
# # #                 format_func=lambda x: x,
# # #                 help="This helps in suggesting relevant metrics (Developer Mode)."
# # #             )
# # #             selected_task_type = next((key for key, value in TASK_TYPE_MAPPING.items() if value == selected_task_type_display), "rag_faq")
# # #         # else: # Info message if selection is disabled but in dev mode (optional)
# # #         #     if DEVELOPER_MODE:
# # #         #         st.sidebar.caption(f"Task Type fixed to: {TASK_TYPE_MAPPING[selected_task_type]} (Configured)")


# # #         # Metric Selection
# # #         st.sidebar.subheader("Metrics for Evaluation")
# # #         selected_metrics = []
# # #         # In config.py, TASK_METRICS_PRESELECTION can be updated for 'rag_faq'
# # #         # For example: TASK_METRICS_PRESELECTION = { "rag_faq": ["Semantic Similarity", "Fact Adherence", ...], }
# # #         from llm_eval_package.config import TASK_METRICS_PRESELECTION # Re-import for safety
        
# # #         # Use the default task_type for preselection logic
# # #         preselected_metrics_keys = TASK_METRICS_PRESELECTION.get(selected_task_type, ["Semantic Similarity"])

# # #         if ENABLE_METRIC_SELECTION:
# # #             preselected_metrics = [metric for metric in preselected_metrics_keys if metric in AVAILABLE_METRICS]
# # #             all_metric_names = list(AVAILABLE_METRICS.keys())
# # #             selected_metrics = st.sidebar.multiselect(
# # #                 "Choose metrics:",
# # #                 options=all_metric_names,
# # #                 default=preselected_metrics,
# # #                 help="Select the metrics to evaluate your LLM's performance."
# # #             )
# # #         else: # Metric selection disabled (e.g. for standard UAT)
# # #             selected_metrics = [metric for metric in preselected_metrics_keys if metric in AVAILABLE_METRICS]
# # #             if not selected_metrics and AVAILABLE_METRICS: # Fallback if preselection is empty
# # #                 selected_metrics = [list(AVAILABLE_METRICS.keys())[0]]
# # #             st.sidebar.caption(f"Metrics fixed to: {', '.join(selected_metrics)} (Configured)")


# # #         # Overall Pass/Fail Criterion
# # #         st.sidebar.subheader("Overall Pass/Fail Logic")
# # #         overall_pass_criteria_options = [PASS_CRITERION_ALL_PASS, PASS_CRITERION_ANY_PASS]
# # #         try:
# # #             default_criterion_index = overall_pass_criteria_options.index(DEFAULT_PASS_CRITERION)
# # #         except ValueError:
# # #             default_criterion_index = 0 # Fallback to first option if default isn't in options

# # #         selected_overall_criterion = st.sidebar.selectbox(
# # #             "Define overall pass/fail for a test case:",
# # #             options=overall_pass_criteria_options,
# # #             index=default_criterion_index,
# # #             help="How is the final pass/fail status determined if multiple metrics are used?"
# # #         )

# # #         # Threshold Settings
# # #         st.sidebar.subheader("Metric Thresholds")
# # #         use_custom_thresholds = st.sidebar.checkbox(
# # #             "Use Custom Thresholds",
# # #             value=False, # Default to False, encouraging use of standard thresholds first
# # #             help="Toggle to define your own pass/fail cut-off scores for each metric."
# # #         )
# # #         custom_thresholds = {}
# # #         if use_custom_thresholds:
# # #             st.sidebar.caption("Set custom thresholds (0.0 to 1.0):")
# # #             for metric_name in selected_metrics:
# # #                 default_threshold = METRIC_THRESHOLDS.get(metric_name, 0.5)
# # #                 if metric_name == "Safety": # Safety usually has fixed logic (1.0 = pass)
# # #                     st.sidebar.text(f"{metric_name}: Passes if score is 1.0")
# # #                     custom_thresholds[metric_name] = 1.0
# # #                 else:
# # #                     custom_thresholds[metric_name] = st.sidebar.number_input(
# # #                         f"{metric_name}",
# # #                         min_value=0.0, max_value=1.0,
# # #                         value=float(default_threshold), step=0.01,
# # #                         key=f"custom_threshold_{metric_name}"
# # #                     )
# # #         else:
# # #             custom_thresholds = None # Indicates default thresholds should be used
# # #             st.sidebar.caption("Using default thresholds for all metrics.")


# # #         # Safety Keyword Input (Only if Safety metric is selected and in developer mode)
# # #         sensitive_keywords = []
# # #         if "Safety" in selected_metrics and DEVELOPER_MODE:
# # #             st.sidebar.subheader("Safety Configuration")
# # #             keywords_input = st.sidebar.text_area(
# # #                 "Sensitive keywords (comma-separated):",
# # #                 # "profanity, hate speech, violence, explicit, harmful", # Example defaults
# # #                 placeholder="e.g., confidential, internal_code, competitor_name",
# # #                 help="Define keywords that, if found in LLM output, will flag the response as 'unsafe'."
# # #             )
# # #             if keywords_input:
# # #                 sensitive_keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
# # #             if not sensitive_keywords and "Safety" in selected_metrics : # Added check if safety is actually selected
# # #                 st.sidebar.warning("Safety metric is selected, but no sensitive keywords entered. It will likely always pass.")

# # #         # The 'Run Evaluation' button is now in the main app area, so this is always False from sidebar.
# # #         run_evaluation_from_sidebar = False

# # #         return (
# # #             uploaded_file,
# # #             selected_metrics,
# # #             run_evaluation_from_sidebar,
# # #             custom_thresholds,
# # #             sensitive_keywords,
# # #             selected_task_type, # This is now a fixed default if ENABLE_TASK_SELECTION is False
# # #             go_to_instructions,
# # #             selected_domain_key,
# # #             selected_overall_criterion # New return value
# # #         )



# # # llm_eval_package/ui/sidebar_view.py
# # import streamlit as st
# # from pathlib import Path # Path can still be useful for other things
# # import sys
# # # import time # No longer needed as mock data toast is removed

# # # --- Mock data generator imports and related logic are completely removed ---

# # from llm_eval_package.config import (
# #     AVAILABLE_METRICS, METRIC_THRESHOLDS, TASK_TYPE_MAPPING,
# #     TASK_METRICS_PRESELECTION, ENABLE_TASK_SELECTION,
# #     ENABLE_METRIC_SELECTION, DEVELOPER_MODE,
# #     PASS_CRITERION_ALL_PASS, PASS_CRITERION_ANY_PASS, DEFAULT_PASS_CRITERION,
# #     TASK_TYPE_RAG_FAQ # For default task type if task selection is disabled
# # )

# # # Bot domain mapping
# # BOT_DOMAIN_MAPPING = {
# #     'Finance': '/dmofinance-122',
# #     'HR': '/hr-161',
# #     'SG Branch': '/branch-ops-181',
# #     'TH Branch': '/thailand-101',
# #     'GWB': 'gwb-25',
# #     'DMO': '/dmo-61'
# # }

# # class SidebarView:
# #     """
# #     Manages the display and interaction of the sidebar in the Streamlit application.
# #     """

# #     def __init__(self):
# #         pass

# #     def render_sidebar(self, file_uploader_key: int):
# #         """
# #         Renders the sidebar components and returns the user's selections.
# #         """
# #         st.sidebar.title("⚙️ Configuration")
# #         st.sidebar.markdown("---")

# #         # 0. Go to Instructions Button
# #         go_to_instructions = st.sidebar.button("📖 View Instructions/Help", help="Learn how to use the tool and understand the metrics.", use_container_width=True)
# #         st.sidebar.markdown("---")

# #         # 1. Data Input Section
# #         st.sidebar.header("1. Data Input")
# #         uploaded_file = st.sidebar.file_uploader(
# #             "Upload Dataset (CSV or JSON)",
# #             type=["csv", "json"],
# #             key=f"file_uploader_{file_uploader_key}",
# #             help="Upload your test data. See 'Instructions' for required format."
# #         )

# #         # --- "Generate Mock Data" button and its logic have been completely removed ---

# #         # 2. Bot API Configuration (for fetching live responses)
# #         st.sidebar.header("2. Bot API Settings (Optional)")
# #         domain_display_names = list(BOT_DOMAIN_MAPPING.keys())
# #         # Default to 'SG Branch' or the first available if 'SG Branch' isn't in the list
# #         default_domain_index = domain_display_names.index('SG Branch') if 'SG Branch' in domain_display_names else 0
# #         selected_domain_display_name = st.sidebar.selectbox(
# #             "Bot Domain:",
# #             options=domain_display_names,
# #             index=default_domain_index,
# #             help="Select the bot domain if you use the 'Fetch Bot Responses' feature in the main panel."
# #         )
# #         selected_domain_key = selected_domain_display_name # Key is the same as display name here

# #         # Task Type Selection (Controlled by ENABLE_TASK_SELECTION in config.py)
# #         # Default to RAG_FAQ as per UAT feedback to remove selection from user view.
# #         selected_task_type = TASK_TYPE_RAG_FAQ
# #         if ENABLE_TASK_SELECTION: # This block will not execute if False in config
# #             st.sidebar.header("Task Type (Dev Mode)") # Should be renumbered if shown
# #             task_options = list(TASK_TYPE_MAPPING.values())
# #             selected_task_type_display = st.sidebar.selectbox(
# #                 "Task Type:",
# #                 options=task_options,
# #                 # Ensure default selection is robust
# #                 index=task_options.index(TASK_TYPE_MAPPING[selected_task_type]) if selected_task_type in TASK_TYPE_MAPPING and TASK_TYPE_MAPPING[selected_task_type] in task_options else 0,
# #                 format_func=lambda x: x,
# #                 help="Select the type of task your LLM performs. This may influence default metric suggestions."
# #             )
# #             # Find the key corresponding to the selected display name
# #             selected_task_type = next((key for key, value in TASK_TYPE_MAPPING.items() if value == selected_task_type_display), TASK_TYPE_RAG_FAQ)
# #         elif DEVELOPER_MODE and not ENABLE_TASK_SELECTION: # Info for developers if selection is off
# #              st.sidebar.caption(f"Task Type fixed to: {TASK_TYPE_MAPPING[selected_task_type]} (Selection disabled in config)")


# #         # 3. Evaluation Settings
# #         st.sidebar.header("3. Evaluation Metrics & Logic")

# #         # Metric Selection (Controlled by ENABLE_METRIC_SELECTION)
# #         selected_metrics = []
# #         if ENABLE_METRIC_SELECTION:
# #             st.sidebar.subheader("Select Metrics")
# #             # Metric pre-selection now uses the (potentially fixed) selected_task_type
# #             preselected_metrics_keys = TASK_METRICS_PRESELECTION.get(selected_task_type, [])
# #             # Ensure preselected are valid metric names (keys of AVAILABLE_METRICS)
# #             preselected_metrics = [metric for metric in preselected_metrics_keys if metric in AVAILABLE_METRICS]
# #             all_metric_names = list(AVAILABLE_METRICS.keys())

# #             selected_metrics = st.sidebar.multiselect(
# #                 "Metrics for Evaluation:",
# #                 options=all_metric_names,
# #                 default=preselected_metrics,
# #                 help="Choose the metrics to evaluate the LLM's performance."
# #             )
# #         else: # Metric selection disabled, use a default set
# #             # Ensure default task type is used for preselection
# #             selected_metrics = TASK_METRICS_PRESELECTION.get(selected_task_type, ["Semantic Similarity"])
# #             if DEVELOPER_MODE and not ENABLE_METRIC_SELECTION: # Info for developers
# #                 st.sidebar.caption(f"Metrics fixed to: {', '.join(selected_metrics)} (Selection disabled in config)")


# #         # Overall Pass/Fail Criterion
# #         st.sidebar.subheader("Overall Test Case Pass/Fail")
# #         overall_pass_criteria_options = [PASS_CRITERION_ALL_PASS, PASS_CRITERION_ANY_PASS]
# #         selected_overall_criterion = st.sidebar.selectbox(
# #             "Logic for Overall Pass/Fail:",
# #             options=overall_pass_criteria_options,
# #             index=overall_pass_criteria_options.index(DEFAULT_PASS_CRITERION) if DEFAULT_PASS_CRITERION in overall_pass_criteria_options else 0,
# #             help="Determines how a test case passes/fails based on individual metric results."
# #         )

# #         # Threshold Settings
# #         st.sidebar.subheader("Metric Thresholds")
# #         use_custom_thresholds = st.sidebar.checkbox(
# #             "Use Custom Thresholds",
# #             value=False, # Default to False for simplicity, user can enable
# #             help="Define your own pass/fail scores for each metric. Otherwise, defaults are used."
# #         )
# #         custom_thresholds = {}
# #         if use_custom_thresholds:
# #             st.sidebar.caption("Set custom thresholds (0.0 to 1.0):")
# #             for metric_name in selected_metrics: # Iterate over actually selected metrics
# #                 default_threshold = METRIC_THRESHOLDS.get(metric_name, 0.5) # Get default from config
# #                 if metric_name == "Safety":
# #                     st.sidebar.markdown(f"↳ **{metric_name}**: Passes if score is 1.0 (No sensitive keywords).")
# #                     custom_thresholds[metric_name] = 1.0 # Safety threshold is typically fixed
# #                 else:
# #                     custom_thresholds[metric_name] = st.sidebar.number_input(
# #                         f"↳ {metric_name}",
# #                         min_value=0.0, max_value=1.0,
# #                         value=float(default_threshold), step=0.01,
# #                         key=f"custom_threshold_{metric_name}", # Unique key for each input
# #                         help=f"Minimum score for '{metric_name}' to be considered 'Pass'."
# #                     )
# #         else:
# #             custom_thresholds = None # Indicates default thresholds from config.py should be used
# #             st.sidebar.caption("Using default thresholds for all metrics.")


# #         # Safety Keyword Input (if Safety metric is selected and in developer mode)
# #         sensitive_keywords = []
# #         if "Safety" in selected_metrics and DEVELOPER_MODE: # Only show in developer mode
# #             st.sidebar.subheader("Safety Metric Settings")
# #             keywords_input = st.sidebar.text_area(
# #                 "Sensitive Keywords (comma-separated):",
# #                 "profanity, hate speech, internal_code_alpha", # Example defaults
# #                 help="Define keywords that, if found in LLM output, will flag the response as 'unsafe'."
# #             )
# #             if keywords_input:
# #                 # Ensure keywords are lowercased for case-insensitive matching later
# #                 sensitive_keywords = [k.strip().lower() for k in keywords_input.split(',') if k.strip()]
            
# #             if not sensitive_keywords and "Safety" in selected_metrics : # Check again if Safety is still selected
# #                  st.sidebar.warning("No sensitive keywords entered for Safety. It will pass unless specific checks for empty keywords are implemented in the metric itself.")
        
# #         # Run Evaluation button was moved to the main panel in streamlit_app.py
# #         run_evaluation_from_sidebar = False # This is no longer triggered from sidebar

# #         return (
# #             uploaded_file,
# #             selected_metrics,
# #             run_evaluation_from_sidebar, # Will always be False
# #             custom_thresholds,
# #             sensitive_keywords,
# #             selected_task_type, # Defaulted if UI selection is off
# #             go_to_instructions,
# #             selected_domain_key,
# #             selected_overall_criterion # New return value
# #         )



# # llm_eval_package/ui/sidebar_view.py
# import streamlit as st
# from pathlib import Path
# import sys

# from llm_eval_package.config import (
#     TASK_TYPE_MAPPING, DEVELOPER_MODE, TASK_TYPE_RAG_FAQ, ENABLE_TASK_SELECTION
#     # Removed metric/threshold/criteria specific imports as they are moved to main panel
# )

# # Bot domain mapping
# BOT_DOMAIN_MAPPING = {
#     'Finance': '/dmofinance-122',
#     'HR': '/hr-161',
#     'SG Branch': '/branch-ops-181',
#     'TH Branch': '/thailand-101',
#     'GWB': 'gwb-25',
#     'DMO': '/dmo-61'
# }

# class SidebarView:
#     def __init__(self):
#         pass

#     def render_sidebar(self, file_uploader_key: int):
#         st.sidebar.title("⚙️ Configuration")
#         st.sidebar.markdown("---")

#         go_to_instructions = st.sidebar.button("📖 View Instructions/Help", help="Learn how to use the tool.", use_container_width=True)
#         st.sidebar.markdown("---")

#         st.sidebar.header("1. Data Input")
#         uploaded_file = st.sidebar.file_uploader(
#             "Upload Dataset (CSV or JSON)", type=["csv", "json"],
#             key=f"file_uploader_{file_uploader_key}",
#             help="Upload your test data. See 'Instructions' for required format."
#         )

#         st.sidebar.header("2. Bot API Settings (Optional)")
#         domain_display_names = list(BOT_DOMAIN_MAPPING.keys())
#         default_domain_index = domain_display_names.index('SG Branch') if 'SG Branch' in domain_display_names else 0
#         selected_domain_display_name = st.sidebar.selectbox(
#             "Bot Domain:", options=domain_display_names, index=default_domain_index,
#             help="Select bot domain for the 'Fetch Bot Responses' feature."
#         )
#         selected_domain_key = selected_domain_display_name

#         # Task Type is effectively fixed as selection UI is removed/disabled by default config
#         selected_task_type = TASK_TYPE_RAG_FAQ # Default
#         if ENABLE_TASK_SELECTION and DEVELOPER_MODE: # Only if explicitly enabled for devs
#             st.sidebar.header("Task Type (Dev Mode)")
#             task_options = list(TASK_TYPE_MAPPING.values())
#             current_task_display = TASK_TYPE_MAPPING.get(selected_task_type, task_options[0])
#             selected_task_type_display = st.sidebar.selectbox(
#                 "Task Type:", options=task_options,
#                 index=task_options.index(current_task_display) if current_task_display in task_options else 0
#             )
#             selected_task_type = next((k for k, v in TASK_TYPE_MAPPING.items() if v == selected_task_type_display), TASK_TYPE_RAG_FAQ)
#         elif DEVELOPER_MODE and not ENABLE_TASK_SELECTION:
#              st.sidebar.caption(f"Task Type fixed to: {TASK_TYPE_MAPPING[selected_task_type]}")


#         # Evaluation metrics, thresholds, overall criteria, and safety keywords are now in the main panel.
#         # The sidebar now only returns these core items.
#         return (
#             uploaded_file,
#             selected_task_type, # Still pass the (potentially fixed) task type
#             go_to_instructions,
#             selected_domain_key
#         )
