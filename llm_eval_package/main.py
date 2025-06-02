# main.py (at the root of your project)

import argparse
import pandas as pd
import sys
import os
from pathlib import Path
import json
import traceback # For detailed error logging

# Add the project root to sys.path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import components from the llm_eval_package
from llm_eval_package.core.engine import Evaluator
from llm_eval_package.config import (
    METRIC_THRESHOLDS, AVAILABLE_METRICS, TASK_METRIC_PRESELECTION, TASK_TYPE_RAG_FAQ, REQUIRED_COLUMNS
)

def parse_custom_thresholds(s):
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
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=True)

    eval_parser = subparsers.add_parser("evaluate", help="Run evaluation on a dataset with LLM outputs.")
    eval_parser.add_argument(
        "--input_file", type=str, required=True,
        help="Path to the input data file (CSV or JSON) containing 'query', 'llm_output', 'reference_answer'."
    )
    eval_parser.add_argument(
        "--output_file", type=str, default="llm_evaluation_results.csv",
        help="Path to save the evaluation results. Supports .csv and .json extensions."
    )
    eval_parser.add_argument(
        "--task_type", type=str, default=TASK_TYPE_RAG_FAQ,
        choices=list(TASK_METRIC_PRESELECTION.keys()),
        help="Specify the task type for evaluation. Used for preselecting metrics if --metrics is not provided."
    )
    eval_parser.add_argument(
        "--metrics", type=str,
        help=(f"Comma-separated list of metrics to run. "
              f"Available: {', '.join(AVAILABLE_METRICS.keys())}. "
              "If not provided, defaults based on --task_type.")
    )
    eval_parser.add_argument(
        "--custom_thresholds", type=parse_custom_thresholds,
        help=("Comma-separated custom thresholds (e.g., 'Semantic Similarity=0.8,Completeness=0.75'). "
              "Overrides default thresholds for specified metrics.")
    )
    eval_parser.add_argument(
        "--sensitive_keywords", type=str,
        help="Comma-separated list of sensitive keywords for the 'Safety' metric."
    )
    eval_parser.add_argument(
        "--report_format", type=str, default="csv", choices=["csv", "json"],
        help="Output format for the results file (determines extension if not in output_file)."
    )

    fetch_parser = subparsers.add_parser("fetch-responses", help="Fetch responses from an RAG bot for a list of queries and prepare for evaluation.")
    fetch_parser.add_argument(
        "--input_queries_csv", type=str, required=True,
        help="Path to the input CSV file containing queries and other desired passthrough columns (e.g. 'reference_answer', 'id')."
    )
    fetch_parser.add_argument(
        "--output_eval_data_csv", type=str, required=True,
        help="Path to save the output CSV file. This file will include original columns plus the fetched 'llm_output'."
    )
    fetch_parser.add_argument(
        "--query_column", type=str, default="query",
        help="Name of the column in --input_queries_csv that contains the queries."
    )
    fetch_parser.add_argument(
        "--domain_key", type=str, default="SG Branch",
        help="Domain key for RAG bot API. Check llm_eval_package/data/rag_input_processor.py for defaults."
    )
    fetch_parser.add_argument(
        "--api_url", type=str, default=None,
        help="Custom API URL for the RAG bot. Overrides default in rag_input_processor.py."
    )
    fetch_parser.add_argument(
        "--api_token", type=str, default=None,
        help="Bearer token for API authorization. Overrides default/placeholder in rag_input_processor.py."
    )

    args = parser.parse_args()

    if args.command == "evaluate":
        evaluator_instance = Evaluator() 

        print(f"Loading data from {args.input_file} for evaluation...")
        try:
            input_file_path = Path(args.input_file)
            file_extension = input_file_path.suffix.lower().lstrip('.')
            if file_extension == 'csv':
                df_original = pd.read_csv(input_file_path)
            elif file_extension == 'json':
                with open(input_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                df_original = pd.DataFrame(data)
            else:
                print(f"Error: Unsupported file format: '{file_extension}'. Please use .csv or .json.")
                sys.exit(1)

            if df_original.empty:
                print(f"Error: Input file '{args.input_file}' is empty or could not be parsed.")
                sys.exit(1)

            mandatory_cols_eval = ['query', 'llm_output', 'reference_answer']
            missing_columns_eval = [col for col in mandatory_cols_eval if col not in df_original.columns]
            if missing_columns_eval:
                print(f"Error: Missing required columns in '{args.input_file}' for evaluation: {', '.join(missing_columns_eval)}. "
                      f"Ensure your file contains at least: {', '.join(mandatory_cols_eval)}.")
                print("If 'llm_output' is missing, you might need to run the 'fetch-responses' command first.")
                sys.exit(1)
            
            for col in REQUIRED_COLUMNS: 
                if col not in df_original.columns:
                    df_original[col] = '' 

            print(f"Successfully loaded {len(df_original)} records for evaluation.")

        except FileNotFoundError:
            print(f"Error: Input file not found: {args.input_file}")
            sys.exit(1)
        except Exception as e:
            print(f"Error loading data for evaluation: {e}")
            print(traceback.format_exc())
            sys.exit(1)

        selected_metrics = []
        if args.metrics:
            selected_metrics = [m.strip() for m in args.metrics.split(',') if m.strip() in AVAILABLE_METRICS]
            invalid_metrics = [m.strip() for m in args.metrics.split(',') if m.strip() not in AVAILABLE_METRICS]
            if invalid_metrics:
                print(f"Warning: Ignoring invalid metrics: {', '.join(invalid_metrics)}")
            if not selected_metrics: 
                print(f"Warning: No valid metrics found in '{args.metrics}'. Using default metrics for task type '{args.task_type}'.")
                selected_metrics = TASK_METRIC_PRESELECTION.get(args.task_type, ["Semantic Similarity"])
        else:
            selected_metrics = TASK_METRIC_PRESELECTION.get(args.task_type, ["Semantic Similarity"])
        
        if not selected_metrics:
            print(f"Error: No metrics selected or defaulted for task type '{args.task_type}'.")
            sys.exit(1)
        print(f"Selected metrics for evaluation: {', '.join(selected_metrics)}")

        sensitive_keywords_list = []
        if args.sensitive_keywords:
            sensitive_keywords_list = [k.strip() for k in args.sensitive_keywords.split(',') if k.strip()]
            print(f"Sensitive keywords for Safety metric: {sensitive_keywords_list}")
        elif "Safety" in selected_metrics:
            print("Warning: 'Safety' metric selected but no --sensitive_keywords provided.")

        print("Running evaluation...")
        try:
            df_evaluated = evaluator_instance.evaluate_dataframe(
                df_original.copy(), 
                selected_metrics,
                custom_thresholds=args.custom_thresholds,
                sensitive_keywords=sensitive_keywords_list
            )
            print("Evaluation complete.")
        except Exception as e:
            print(f"Error during evaluation: {e}")
            print(traceback.format_exc())
            sys.exit(1)

        output_path = Path(args.output_file)
        output_format_from_ext = output_path.suffix.lower().lstrip('.')
        
        final_report_format = args.report_format
        if output_format_from_ext in ["csv", "json"]:
            final_report_format = output_format_from_ext
            if output_format_from_ext != args.report_format:
                 print(f"Info: Output format inferred as '{final_report_format}' from --output_file extension.")
        elif not output_path.suffix: 
            output_path = output_path.with_suffix(f".{args.report_format}")

        print(f"Saving results to '{output_path}' in {final_report_format} format...")
        try:
            if final_report_format == "csv":
                df_evaluated.to_csv(output_path, index=False, encoding='utf-8')
            elif final_report_format == "json":
                df_evaluated.to_json(output_path, orient="records", indent=4, force_ascii=False)
            print(f"Results saved successfully to '{output_path}'")
        except Exception as e:
            print(f"Error saving results: {e}")
            print(traceback.format_exc())
            sys.exit(1)

    elif args.command == "fetch-responses":
        print("Fetching RAG bot responses...")
        try:
            from llm_eval_package.data.rag_input_processor import fetch_bot_responses, DEFAULT_API_HEADERS

            headers_for_fetch = DEFAULT_API_HEADERS.copy()
            if args.api_token:
                headers_for_fetch["Authorization"] = f"Bearer {args.api_token}"
                print("Using API token from --api_token argument.")
            elif "YOUR_EXPIRED_OR_PLACEHOLDER_TOKEN_HERE" in headers_for_fetch.get("Authorization", "") :
                 print("Warning: Using default placeholder API token. Update it in llm_eval_package/data/rag_input_processor.py or use --api_token CLI argument.")

            fetch_bot_responses(
                input_csv_path=args.input_queries_csv,
                output_csv_path=args.output_eval_data_csv,
                query_column=args.query_column,
                domain_key=args.domain_key,
                api_url=args.api_url, 
                api_headers=headers_for_fetch
            )
            print(f"\nSuccessfully fetched responses and saved to '{args.output_eval_data_csv}'")
            print(f"This file can now be used as --input_file for the 'evaluate' command.")
        except FileNotFoundError as e:
            print(f"Error: Input queries file not found: {e}")
            sys.exit(1)
        except ValueError as e: 
            print(f"Configuration error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred during fetch-responses: {e}")
            print(traceback.format_exc())
            sys.exit(1)

if __name__ == "__main__":
    main()