# llm_eval_package/ui/tutorial_view.py
import streamlit as st
import pandas as pd

class TutorialView:
    def __init__(self):
        pass

    def render_tutorial(self):
        st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🚀 LLM Evaluation Guide 🚀</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Your one-stop guide to evaluating LLMs effectively for banking!</p>", unsafe_allow_html=True)
        st.markdown("---")

        st.info("🎯 **Goal**: Evaluate your bank's LLMs. Fetch live responses or use pre-existing ones. Review and override automated results.")

        with st.expander("💾 Step 1: Preparing & Uploading Your Input Data", expanded=True):
            st.markdown("Your foundation is a **CSV or JSON file**. Here's the column structure:")
            
            cols_data = {
                "Column Name": ["`query`", "`reference_answer`", "`llm_output`", 
                                "`initial_reviewer_verdict`", "`required_facts`", 
                                "`test_description`", "`test_config`"],
                "Requirement": ["**Required**", "**Required** (for most metrics)", "Required (can be auto-fetched)",
                                "*Optional*", "*Optional* (for Fact Adherence)", 
                                "*Optional*", "*Optional*"],
                "Purpose": [
                    "The question/prompt for the LLM (e.g., 'What are current home loan rates?').",
                    "The ideal/correct answer.",
                    "LLM's actual response. (Leave empty if using 'Fetch Bot Responses').",
                    "Your pre-assessment (Pass/Fail/N/A/Error). This will pre-fill 'Reviewer's Final Result'.",
                    "Critical facts LLM *must* mention (semicolon-separated; e.g., `Rate 4.5%;Lock-in 2yr`).",
                    "Brief description of the test case.",
                    "Category for grouping results (e.g., `HomeLoan_Rates`, `AccountOpening_Policy`)."
                ]
            }
            st.table(pd.DataFrame(cols_data))
            st.markdown("- **Uploading**: Use the sidebar 'Upload Dataset' button.")
            st.markdown("- **Editing**: The data table displayed after upload is editable. Changes are applied immediately when you click out of a cell or press Enter. The page will refresh, but your edits are saved to the current session.")

            
            st.markdown("---")
            st.markdown("##### 🏦 Banking Scenario Examples (Illustrative Data):")
            
            tab_branch, tab_finance, tab_wholesale, tab_hr = st.tabs(["🏢 Branch Ops", "💰 Finance/Investments", "🌍 Wholesale Banking", "👥 HR Policy"])

            with tab_branch:
                st.caption("Example: Bank Branch Operations")
                branch_data = {
                    'query': ["Orchard branch Saturday hours?", "How to open a current account?"],
                    'llm_output': ["The Orchard branch is open from 9 AM to 1 PM on Saturdays.", "To open a new current account, you need NRIC, proof of address, and a $500 initial deposit. Apply online or at any branch."],
                    'reference_answer': ["Orchard branch Saturday hours are 9:00 AM - 1:00 PM.", "Provide NRIC/passport, proof of address, min. $500 deposit. Apply online or visit."],
                    'initial_reviewer_verdict': ["Pass", ""], # Example: One pre-filled, one not
                    'required_facts': ["9 AM to 1 PM;Saturdays", "NRIC;proof of address;$500 deposit"],
                    'test_description': ["Check Orchard Sat hours", "Verify current account opening steps"],
                    'test_config': ["Branch_Hours_Orchard", "AccountOpening_Current"]
                }
                st.dataframe(pd.DataFrame(branch_data), use_container_width=True)

            with tab_finance:
                st.caption("Example: Finance/Investment Products")
                finance_data = {
                    'query': ["12-month FD rate?", "Risks of unit trusts?"],
                    'llm_output': ["12-month FD is 3.5% p.a. for >$10k.", "Unit trusts are subject to market fluctuations; no guaranteed returns; potential principal loss."],
                    'reference_answer': ["12-month FD promotional rate is 3.50% p.a. for $10k+ deposits.", "Unit trusts involve market risk (value can fall), past performance not indicative of future, potential principal loss. Read prospectus."],
                    'initial_reviewer_verdict': ["Pass", "Fail"],
                    'required_facts': ["3.5% p.a.;12-month", "market fluctuations;no guarantee;lose principal"],
                    'test_description': ["Verify 12m FD rate", "Explain unit trust risks"],
                    'test_config': ["FixedDeposit_Rates_12M", "UnitTrust_RiskDisclosure"]
                }
                st.dataframe(pd.DataFrame(finance_data), use_container_width=True)

            with tab_wholesale:
                st.caption("Example: Wholesale Banking (Trade Finance)")
                wholesale_data = {
                    'query': ["Documents for Letter of Credit?", "Import LC processing time?"],
                    'llm_output': ["Application form, proforma invoice, transport documents.", "Usually 2-3 business days."],
                    'reference_answer': ["Completed LC application, proforma invoice/sales contract, shipping details. Other docs may be needed.", "Standard processing is 2-3 working days after correct document submission."],
                    'initial_reviewer_verdict': ["", "Pass"],
                    'required_facts': ["application form;proforma invoice", "2-3 business days"],
                    'test_description': ["Check LC application docs", "Verify import LC processing time"],
                    'test_config': ["TradeFinance_LC_Docs", "TradeFinance_LC_ProcessingTime"]
                }
                st.dataframe(pd.DataFrame(wholesale_data), use_container_width=True)

            with tab_hr:
                st.caption("Example: HR Policy (Internal)")
                hr_data = {
                    'query': ["Paternity leave policy?", "Annual medical leave?"],
                    'llm_output': ["Eligible males get 2 weeks paternity leave.", "14 days outpatient, 60 days hospitalization leave annually."],
                    'reference_answer': ["Eligible male employees get 2 weeks GPPL + 2 weeks shared parental leave (subject to criteria).", "14 days paid outpatient sick leave, up to 60 days paid hospitalisation leave (inclusive of outpatient)."],
                    'initial_reviewer_verdict': ["N/A", "Pass"],
                    'required_facts': ["2 weeks paternity leave", "14 days outpatient;60 days hospitalization"],
                    'test_description': ["Verify paternity leave", "Verify medical leave days"],
                    'test_config': ["HR_Leave_Paternity", "HR_Leave_Medical"]
                }
                st.dataframe(pd.DataFrame(hr_data), use_container_width=True)


        with st.expander("🔗 Step 2: Fetching Live Bot Responses (Optional)", expanded=False):
            st.markdown(
                """
                If your `llm_output` column is empty:
                1.  **Select Bot Domain**: In the sidebar ("2. Bot API Settings"), choose the bot (e.g., 'SG Branch').
                2.  **Click Fetch**: In the main panel, click "🔗 **Fetch Bot Responses & Update Data**".
                    - A progress bar will show status.
                    - This populates the `llm_output` column.
                **Note**: Ensure the API token in the backend configuration (`llm_eval_package/data/rag_input_processor.py`) is valid. This tool no longer asks for the token in the UI.
                """
            )

        with st.expander("🛠️ Step 3: Configuring Evaluation Settings", expanded=False):
            st.markdown(
                """
                Before running the evaluation, configure settings in the **main panel** (this section appears after data is loaded):
                1.  **Select Metrics**: Choose which quality aspects to measure (e.g., `Semantic Similarity`, `Fact Adherence`).
                2.  **Automated Overall Result Logic**: Decide how the system determines an overall pass/fail based on the selected metrics (e.g., "All selected metrics must pass").
                3.  **Metric Thresholds**: Optionally, set custom pass/fail scores for each metric.
                4.  **Safety Keywords** (if "Safety" metric is chosen & Developer Mode is active): List words that make a response unsafe.
                """
            )
            st.markdown("###### Mapping Bank UAT Goals to Metrics:")
            # ... (Metric mapping examples from previous response can be kept here) ...
            st.markdown(
            """
            * **"Is the bot's answer relevant and correct in meaning?"** ➡️ Use `Semantic Similarity`.
            * **"Did the bot provide all critical pieces of information?"** ➡️ Use `Fact Adherence` (for specific facts from `required_facts`) and/or `Completeness` (general coverage against `reference_answer`).
            * **"Is the answer concise, no fluff?"** ➡️ Use `Conciseness`.
            * **"Is the answer factually accurate?"** ➡️ Use `Trust & Factuality` (vs. `reference_answer`) and `Fact Adherence` (vs. `required_facts`).
            * **"Does the bot avoid restricted terms?"** ➡️ Use `Safety`.
            """
            )


        with st.expander("🚀 Step 4: Running the Evaluation", expanded=False):
            st.markdown(
                """
                - Click the "🚀 **Run Evaluation**" button in the main panel.
                - The tool calculates scores and determines an "Automated Overall Result" for each test case.
                """
            )

        with st.expander("📝 Step 5: Reviewing Results & Overriding", expanded=False):
            st.markdown(
                """
                1.  **View Summaries**: Check the "Overall Summary" and "Summary by Test Configuration".
                2.  **Detailed Table**:
                    - Shows key data, metric scores (as progress bars), the "Automated Overall Result", and an editable "**Reviewer's Final Result**" column.
                    - The "Reviewer's Final Result" is pre-filled from your `initial_reviewer_verdict` (if provided) or the "Automated Overall Result".
                    - You can **edit** the "Reviewer's Final Result" directly in the table. Edits are applied immediately.
                3.  **Agreement Score**: Click "⚖️ Calculate Reviewer-Evaluator Agreement" to see how your final verdicts match the system's automated results.
                4.  **Download**: Get the full detailed report as a CSV.
                """
            )
        
        with st.expander("🗂️ Power of `test_config` for Bank Testers", expanded=False):
            # ... (test_config examples from previous response - this section can remain largely the same) ...
            st.markdown(
            """
            The `test_config` column helps categorize tests for targeted analysis.
            **Bank Branch Examples for `test_config`**:
            - `AccountOpening_Savings`, `CardServices_LostCard`, `BranchInfo_Jurong_Hours`, `LoanProduct_HomeLoan_Rates`
            This allows filtering/grouping results to see performance for specific banking areas.
            """
            )

        with st.expander("⌨️ Using the Command Line (CLI)", expanded=False):
            # ... (CLI instructions from previous response - this section can remain largely the same) ...
             st.markdown("##### **Part 1: Fetch Live Bot Responses**")
             st.code("python main.py fetch-responses --input_queries_csv data/queries.csv --output_eval_data_csv data/responses.csv --domain_key \"SG Branch\"", "bash")
             st.caption("Ensure API token in `rag_input_processor.py` is valid.")
             st.markdown("##### **Part 2: Evaluate Responses**")
             st.code("python main.py evaluate --input_file data/responses.csv --output_file results/report.csv --metrics \"Semantic Similarity,Fact Adherence\"", "bash")

        st.markdown("---"); st.success("You're all set! Happy Evaluating! 🎉")
        
# # llm_eval_package/ui/tutorial_view.py
# import streamlit as st
# import pandas as pd

# class TutorialView:
#     def __init__(self):
#         pass

#     def render_tutorial(self):
#         st.markdown("<h2 style='text-align: center; color: #4CAF50;'>🚀 LLM Evaluation Guide 🚀</h2>", unsafe_allow_html=True)
#         st.markdown("<p style='text-align: center;'>Your one-stop guide to evaluating LLMs effectively!</p>", unsafe_allow_html=True)
#         st.markdown("---")

#         st.info("🎯 **Goal**: This tool helps assess your LLM's performance. You can use pre-existing LLM responses or fetch live ones from your RAG chatbot for evaluation against various quality metrics.")

#         # Section 1: Input Data
#         with st.expander("💾 Step 1: Preparing Your Input Data", expanded=True):
#             st.markdown(
#                 """
#                 Your foundation for evaluation is a **CSV or JSON file**. Here's what it needs:
#                 """
#             )
#             # Using columns for better layout of field definitions
#             col1, col2 = st.columns(2)
#             with col1:
#                 st.markdown("##### **Required Fields** ✨")
#                 st.markdown("- **`query`**: The question/prompt for the LLM.")
#                 st.markdown("- **`reference_answer`**: The ideal/correct answer.")

#             with col2:
#                 st.markdown("##### *Optional Fields* (Recommended) 📝")
#                 st.markdown("- **`llm_output`**: The LLM's actual response. *(Can be empty if using 'Fetch Bot Responses' feature)*")
#                 st.markdown("- **`required_facts`**: Critical facts the LLM *must* mention. Separate with semicolons (`;`). *Used by the 'Fact Adherence' metric.* (e.g., `Interest is 3.5%; Min. deposit $1000`)")
#                 st.markdown("- **`test_description`**: What this test case aims to verify.")
#                 st.markdown("- **`test_config`**: Category for grouping (e.g., `SavingsAccount`, `HR_Policy_Leave`).")

#             st.markdown("---")
#             st.markdown("##### 🏦 Banking Scenario Examples:")
#             # Tabs for different banking examples
#             tab_branch, tab_finance, tab_hr = st.tabs(["🏢 Branch Ops", "💰 Finance/Investments", "👥 HR Policy"])

#             with tab_branch:
#                 st.caption("Example: Bank Branch Operations")
#                 branch_data = {
#                     'query': ["Orchard branch Saturday hours?", "How to open a current account?"],
#                     'llm_output': ["Open 9 AM - 1 PM Saturdays.", "Provide NRIC, address proof, $500 deposit. Apply online or at branch."],
#                     'reference_answer': ["Orchard branch is open 9:00 AM - 1:00 PM on Saturdays.", "Provide NRIC/passport, proof of address, min. $500 deposit. Apply online or visit."],
#                     'required_facts': ["9 AM to 1 PM;Saturdays", "NRIC;proof of address;$500 deposit"],
#                     'test_description': ["Check Orchard Sat hours", "Verify current account opening steps"],
#                     'test_config': ["Branch_Hours_Orchard", "AccountOpening_Current"]
#                 }
#                 st.dataframe(pd.DataFrame(branch_data), use_container_width=True)

#             with tab_finance:
#                 st.caption("Example: Finance/Investment Products")
#                 finance_data = {
#                     'query': ["12-month FD rate?", "Risks of unit trusts?"],
#                     'llm_output': ["12-month FD is 3.5% p.a. for >$10k.", "Unit trusts subject to market fluctuations, no guaranteed returns, potential principal loss."],
#                     'reference_answer': ["12-month FD promotional rate is 3.50% p.a. for $10k+ deposits.", "Unit trusts involve market risk (value can fall), past performance not indicative of future, potential principal loss. Read prospectus."],
#                     'required_facts': ["3.5% p.a.;12-month", "market fluctuations;no guarantee;lose principal"],
#                     'test_description': ["Verify 12m FD rate", "Explain unit trust risks"],
#                     'test_config': ["FixedDeposit_Rates_12M", "UnitTrust_RiskDisclosure"]
#                 }
#                 st.dataframe(pd.DataFrame(finance_data), use_container_width=True)

#             with tab_hr:
#                 st.caption("Example: HR Policy (Internal)")
#                 hr_data = {
#                     'query': ["Paternity leave policy?", "Annual medical leave entitlement?"],
#                     'llm_output': ["Eligible males get 2 weeks paternity leave.", "14 days outpatient, 60 days hospitalization leave annually."],
#                     'reference_answer': ["Eligible male employees get 2 weeks GPPL + 2 weeks shared parental leave (subject to criteria).", "14 days paid outpatient sick leave, up to 60 days paid hospitalisation leave (inclusive of outpatient)."],
#                     'required_facts': ["2 weeks paternity leave", "14 days outpatient;60 days hospitalization"],
#                     'test_description': ["Verify paternity leave", "Verify medical leave days"],
#                     'test_config': ["HR_Leave_Paternity", "HR_Leave_Medical"]
#                 }
#                 st.dataframe(pd.DataFrame(hr_data), use_container_width=True)

#         # Section 2: GUI Workflow
#         with st.expander("🖥️ Using the Dashboard (GUI Workflow)", expanded=False):
#             st.markdown(
#                 """
#                 **1. Upload Data**: Use the sidebar "Upload Dataset" button.
#                 """
#             )
#             st.image("https://storage.googleapis.com/gemini-prod/images/2024/05/29/18_00_00_000000_BQAE.png", caption="Sidebar: Upload & Bot Config", width=300) # Placeholder - replace with actual image if possible

#             st.markdown(
#                 """
#                 **2. Configure Bot (If Fetching Live Responses)**:
#                    - **Bot Domain**: Select in sidebar (e.g., 'SG Branch').
#                    - **API Token**: Optionally enter in the main panel (field appears after data upload).
#                 """
#             )
#             st.markdown(
#                 """
#                 **3. Fetch Live Responses (Optional)**:
#                    - Click "🔗 **Fetch Bot Responses & Update Data**" in the main panel.
#                    - This populates/updates the `llm_output` column in your data table.
#                 """
#             )
#             st.markdown(
#                 """
#                 **4. Configure Evaluation**:
#                    - **Metrics**: Select in sidebar (e.g., Semantic Similarity, Fact Adherence). *(Developer Mode may show more options)*
#                    - **Overall Pass/Fail Logic**: Choose how a test case passes based on multiple metrics (e.g., "All metrics must pass").
#                    - **Thresholds**: Set pass/fail scores for each metric.
#                    - **Safety Keywords**: If using "Safety" metric, define sensitive terms. *(Developer Mode)*
#                 """
#             )
#             st.image("https://storage.googleapis.com/gemini-prod/images/2024/05/29/18_05_00_000000_BQAE.png", caption="Main Panel: Fetch & Evaluate Buttons", width=400) # Placeholder

#             st.markdown(
#                 """
#                 **5. Run Evaluation**: Click "🚀 **Run Evaluation**".
#                 **6. View Results**: Analyze summaries, detailed tables, and download reports.
#                 """
#             )

#         # Section 3: Mapping Business Needs to Metrics
#         with st.expander("💡 Mapping Bank UAT Goals to Metrics", expanded=False):
#             st.markdown(
#                 """
#                 Connect your testing goals to the tool's metrics:

#                 - **"Is the bot's answer relevant and correct in meaning?"**
#                   ➡️ Use `Semantic Similarity`.
#                   *Example*: Bot gives PayNow info for a FAST transfer query. Low similarity expected.

#                 - **"Did the bot provide all critical pieces of information?"**
#                   ➡️ Use `Fact Adherence` (for specific, must-have facts from your `required_facts` column).
#                   ➡️ Use `Completeness` (for general coverage against the `reference_answer`).
#                   *Example*: For a loan query, `Fact Adherence` checks if "Interest 3.5%" and "Min. loan $10k" are stated.

#                 - **"Is the answer concise, no fluff?"**
#                   ➡️ Use `Conciseness`.
#                   *Example*: Bot gives a lengthy intro before answering a simple phone number query. Lower score.

#                 - **"Is the answer factually accurate against our gold standard?"**
#                   ➡️ Use `Trust & Factuality` (compares to `reference_answer`).
#                   ➡️ Reinforce with `Fact Adherence` for key data points.

#                 - **"Does the bot avoid restricted terms or harmful language?"**
#                   ➡️ Use `Safety` (define keywords like "internal_code_xyz", "competitor_promo").
#                 """
#             )

#         # Section 4: Using `test_config`
#         with st.expander("🗂️ Power of `test_config` for Bank Testers", expanded=False):
#             st.markdown(
#                 """
#                 The `test_config` column helps you categorize tests. This is invaluable for analyzing results for specific banking areas.
#                 After evaluation, the "Results" page will show a "Summary by Test Configuration" section.

#                 **Bank Branch Examples for `test_config`**:
#                 - `AccountOpening_Savings`: Queries about opening savings accounts.
#                 - `CardServices_LostCard`: Procedures for lost/stolen cards.
#                 - `BranchInfo_Jurong_Hours`: Specific branch operating hours.
#                 - `LoanProduct_HomeLoan_Rates`: Inquiries about home loan interest rates.
#                 - `DigitalBanking_PayNow_Setup`: Questions on setting up PayNow.
#                 - `CustomerFeedback_Complaints`: How the bot handles complaint-like queries.

#                 This allows you to see, for example, if the bot excels at `BranchInfo` but struggles with `LoanProduct` details.
#                 """
#             )


#         # Section 5: CLI Workflow
#         with st.expander("⌨️ Using the Command Line (CLI)", expanded=False):
#             st.markdown(
#                 """
#                 For automation or batch processing:
#                 **Important**: First, ensure a valid API token is in `llm_eval_package/data/rag_input_processor.py` or use the `--api_token` argument.
#                 """
#             )
#             st.markdown("##### **Part 1: Fetch Live Responses**")
#             st.code(
#                 """
# python main.py fetch-responses \\
#     --input_queries_csv data/my_bank_queries.csv \\
#     --output_eval_data_csv data/bank_queries_with_responses.csv \\
#     --domain_key "SG Branch" \\
#     # --api_token "YOUR_TOKEN_IF_NOT_IN_SCRIPT"
#                 """, language="bash"
#             )
#             st.caption("This adds `llm_output` to your query file.")

#             st.markdown("##### **Part 2: Evaluate Responses**")
#             st.code(
#                 """
# python main.py evaluate \\
#     --input_file data/bank_queries_with_responses.csv \\
#     --output_file results/bank_evaluation_report.csv \\
#     --metrics "Semantic Similarity,Fact Adherence,Safety" \\
#     # --custom_thresholds "Fact Adherence=1.0,Safety=1.0" \\
#     # --sensitive_keywords "internal_use_only,competitor_xyz"
#                 """, language="bash"
#             )
#             st.caption("This generates your evaluation report.")

#         st.markdown("---")
#         st.success("You're all set! Happy Evaluating! 🎉")