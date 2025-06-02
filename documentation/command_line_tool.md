# Step 1: 
## - Save the code above as main.py in your project's root directory (next to streamlit_app.py).
# Step 2: 
## - Make sure your llm_eval_package is correctly set up as a Python package and all internal imports are resolved.
# Step 3: 
## - Run from your terminal (after activating your Conda environment):


# Examples: 
## Example 1: Run with mock data, default metrics for RAG FAQ, and save as CSV
```bash
python main.py --input_file data/llm_eval_mock_data_generated.csv --output_file cli_results.csv
```
## Example 2: Run with custom metrics and thresholds
```bash
python main.py --input_file data/llm_eval_mock_data_generated.json --metrics "Semantic Similarity,Completeness" --custom_thresholds "Semantic Similarity=0.8,Completeness=0.7" --output_file cli_results.json --report_format json
```
## Example 3: Run with Safety metric and custom keywords
```bash
python main.py --input_file data/llm_eval_mock_data_generated.csv --metrics "Semantic Similarity,Safety" --sensitive_keywords "badword,unsafe"
```