import argparse
import pandas as pd
import sys
import os
from pathlib import Path
import json

# Add the project root to sys.path so Python can find 'llm_eval_package'
# This assumes main.py is in the project root directory.
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import components from the llm_eval_package
from llm_eval_package.data.loader import DataLoader
from llm_eval_package.core.engine import Evaluator
from llm_eval_package.core.reporting import Reporter
from llm_eval_package.config import METRIC_THRESHOLDS, AVAILABLE_METRICS, TASK_METRIC_PRESELECTION, TASK_TYPE_RAG_FAQ

def parse_custom_thresholds(s):
    """
    Parses a string of custom thresholds (e.g., "Metric1=0.8,Metric2=0.9") into a dictionary.
    """
    if not s:
        return None
    thresholds = {}
    for item in s.split(','):
        if '=' in item:
            key, value = item.split('=', 1)
            try:
                thresholds[key.strip()] = float(value.strip())
            except ValueError:
                raise argparse.ArgumentTypeError(f"Invalid threshold format: '{item}'. Must be 'MetricName=Value'.")
        else:
            raise argparse.ArgumentTypeError(f"Invalid threshold format: '{item}'. Must be 'MetricName=Value'.")
    return thresholds

def main():
    parser = argparse.ArgumentParser(
        description="LLM Evaluation Tool - Command Line Interface",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Required arguments
    parser.add_argument(
        "--input_file",
        type=str,
        required=True,
        help="Path to the input data file (CSV or JSON) containing 'query', 'llm_output', 'reference_answer'."
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default="llm_evaluation_results.csv",
        help="Path to save the evaluation results. Supports .csv and .json extensions."
    )

    # Optional arguments
    parser.add_argument(
        "--task_type",
        type=str,
        default=TASK_TYPE_RAG_FAQ, # Default to RAG FAQ as per user request
        choices=list(TASK_METRIC_PRESELECTION.keys()), # Use available task types from config
        help="Specify the task type for evaluation. Used for preselecting metrics if --metrics is not provided."
    )
    parser.add_argument(
        "--metrics",
        type=str,
        help=f"Comma-separated list of metrics to run. Available: {', '.join(AVAILABLE_METRICS.keys())}. "
             "If not provided, defaults based on --task_type (e.g., 'Semantic Similarity' for RAG FAQ)."
    )
    parser.add_argument(
        "--custom_thresholds",
        type=parse_custom_thresholds,
        help="Comma-separated custom thresholds (e.g., 'Semantic Similarity=0.8,Completeness=0.75'). "
             "Overrides default thresholds for specified metrics."
    )
    parser.add_argument(
        "--sensitive_keywords",
        type=str,
        help="Comma-separated list of sensitive keywords for the 'Safety' metric."
    )
    parser.add_argument(
        "--report_format",
        type=str,
        default="csv",
        choices=["csv", "json"],
        help="Output format for the results file."
    )

    args = parser.parse_args()

    # --- Initialize Components ---
    data_loader = DataLoader()
    evaluator = Evaluator()
    reporter = Reporter()

    # --- Load Data ---
    print(f"Loading data from {args.input_file}...")
    try:
        # For CLI, we need to open the file and pass a file-like object or path
        # Assuming DataLoader can take a path or file-like object directly
        # For simplicity, let's adapt DataLoader to take a path for CLI
        df_original = data_loader.load_data_from_path(args.input_file)
        if df_original.empty:
            print("Error: Input file is empty or could not be parsed.")
            sys.exit(1)
        print(f"Successfully loaded {len(df_original)} records.")
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)

    # --- Determine Metrics to Run ---
    selected_metrics = []
    if args.metrics:
        selected_metrics = [m.strip() for m in args.metrics.split(',') if m.strip() in AVAILABLE_METRICS]
        if not selected_metrics:
            print(f"Warning: No valid metrics found in '{args.metrics}'. Using default metrics for task type '{args.task_type}'.")
            selected_metrics = TASK_METRIC_PRESELECTION.get(args.task_type, ["Semantic Similarity"])
    else:
        selected_metrics = TASK_METRIC_PRESELECTION.get(args.task_type, ["Semantic Similarity"])
    
    if not selected_metrics:
        print("Error: No metrics selected for evaluation. Please specify metrics or a valid task type.")
        sys.exit(1)
    
    print(f"Selected metrics for evaluation: {', '.join(selected_metrics)}")

    # --- Prepare Sensitive Keywords ---
    sensitive_keywords_list = []
    if args.sensitive_keywords:
        sensitive_keywords_list = [k.strip() for k in args.sensitive_keywords.split(',') if k.strip()]
        print(f"Sensitive keywords for Safety metric: {sensitive_keywords_list}")
    elif "Safety" in selected_metrics:
        print("Warning: 'Safety' metric selected but no sensitive keywords provided. It will always pass.")

    # --- Run Evaluation ---
    print("Running evaluation...")
    try:
        df_evaluated = evaluator.evaluate_dataframe(
            df_original.copy(),
            selected_metrics,
            custom_thresholds=args.custom_thresholds,
            sensitive_keywords=sensitive_keywords_list
        )
        print("Evaluation complete.")
    except Exception as e:
        print(f"Error during evaluation: {e}")
        sys.exit(1)

    # --- Save Results ---
    print(f"Saving results to {args.output_file} in {args.report_format} format...")
    try:
        # Adapt Reporter to save directly from CLI
        if args.report_format == "csv":
            df_evaluated.to_csv(args.output_file, index=False, encoding='utf-8')
        elif args.report_format == "json":
            df_evaluated.to_json(args.output_file, orient="records", indent=4, force_ascii=False)
        print(f"Results saved successfully to {args.output_file}")
    except Exception as e:
        print(f"Error saving results: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Temporarily modify DataLoader to accept path for CLI
    # This is a quick adaptation for CLI; a more robust design might
    # have DataLoader.load_data handle both file_uploader and path.
    original_load_data = DataLoader.load_data
    def load_data_from_path_adapter(self, path):
        file_extension = Path(path).suffix.lower().lstrip('.')
        if file_extension == 'csv':
            df = pd.read_csv(path)
        elif file_extension == 'json':
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}. Please use .csv or .json.")
        self._validate_columns(df)
        return df
    DataLoader.load_data_from_path = load_data_from_path_adapter

    main()

    # Restore original method if needed (though not critical for script exit)
    DataLoader.load_data = original_load_data
