# llm_eval_package/core/engine.py
import pandas as pd
import numpy as np
import streamlit as st
import os
from tqdm import tqdm
import traceback

from llm_eval_package.metrics.fluency_similarity import SemanticSimilarityMetric
from llm_eval_package.metrics.completeness import CompletenessMetric
from llm_eval_package.metrics.conciseness import ConcisenessMetric
from llm_eval_package.metrics.trust_factuality import TrustFactualityMetric
from llm_eval_package.metrics.safety import SafetyMetric
from llm_eval_package.metrics.fact_adherence import FactAdherenceMetric

from llm_eval_package.config import (
    METRIC_THRESHOLDS, AVAILABLE_METRICS,
    SENTENCE_BERT_MODEL_PATH, MODEL_DIR, SENTENCE_BERT_MODEL,
    PASS_CRITERION_ALL_PASS, PASS_CRITERION_ANY_PASS, DEFAULT_PASS_CRITERION
)
from llm_eval_package.utils import ModelDownloader


@st.cache_resource
def _get_cached_metric_instances_internal():
    metrics_instances = {}
    model_downloader = ModelDownloader()
    
    if "Semantic Similarity" in AVAILABLE_METRICS:
        if not os.path.exists(SENTENCE_BERT_MODEL_PATH) or not os.listdir(SENTENCE_BERT_MODEL_PATH):
            msg_download = f"Semantic Similarity model ('{SENTENCE_BERT_MODEL}') not found. Downloading..."
            try: st.info(msg_download)
            except: print(msg_download)
            downloaded_path = model_downloader.download_and_save_model(SENTENCE_BERT_MODEL, MODEL_DIR)
            if not downloaded_path: raise Exception(f"Failed to download model '{SENTENCE_BERT_MODEL}'.")
            else: 
                msg_success = f"Model '{SENTENCE_BERT_MODEL}' downloaded!"
                try: st.success(msg_success)
                except: print(msg_success)
    
    metric_class_map = {
        "SemanticSimilarityMetric": SemanticSimilarityMetric, "CompletenessMetric": CompletenessMetric,
        "ConcisenessMetric": ConcisenessMetric, "TrustFactualityMetric": TrustFactualityMetric,
        "SafetyMetric": SafetyMetric, "FactAdherenceMetric": FactAdherenceMetric,
    }
    for metric_name, class_name_str in AVAILABLE_METRICS.items():
        try:
            MetricClass = metric_class_map.get(class_name_str)
            if MetricClass:
                metrics_instances[metric_name] = MetricClass(SENTENCE_BERT_MODEL_PATH) if metric_name == "Semantic Similarity" else MetricClass()
        except Exception as e:
            print(f"ERROR initializing metric {metric_name}: {e}")
    return metrics_instances

class Evaluator:
    def __init__(self):
        try:
            self.metrics_instances = _get_cached_metric_instances_internal()
            # if self.metrics_instances:
            #     try: st.toast("Page updated!", icon="🔬")
            #     except: pass
        except Exception as e:
            try: st.error(f"CRITICAL ERROR loading metric models: {e}. Evaluation unavailable.")
            except: print(f"CRITICAL ERROR loading metric models: {e}")
            self.metrics_instances = {}

    def evaluate_dataframe(self, df: pd.DataFrame, selected_metrics: list,
                           custom_thresholds: dict = None,
                           sensitive_keywords: list = None,
                           overall_pass_criterion: str = DEFAULT_PASS_CRITERION
                           ) -> pd.DataFrame:
        if df.empty: return df.copy()
        if not selected_metrics: return df.copy()
        if not self.metrics_instances: return df.copy()

        current_thresholds = custom_thresholds if custom_thresholds is not None else METRIC_THRESHOLDS.copy()
        df_copy = df.copy()

        for metric_name in selected_metrics:
            if metric_name in self.metrics_instances:
                df_copy[f'{metric_name} Score'] = pd.NA
                df_copy[f'{metric_name} Pass/Fail'] = 'N/A'
        
        # RENAMED this column for clarity
        automated_overall_col_name = "Automated Overall Result" 
        df_copy[automated_overall_col_name] = 'N/A'

        is_streamlit_context = False
        try: st.get_option("server.headless"); is_streamlit_context = True
        except: pass

        iterable_rows = tqdm(df_copy.iterrows(), total=df_copy.shape[0], desc="Evaluating test cases") if not is_streamlit_context else df_copy.iterrows()
        progress_bar = st.progress(0, text="Initializing evaluation...") if is_streamlit_context else None

        for i, row in iterable_rows:
            if progress_bar:
                progress_bar.progress((i + 1) / df_copy.shape[0], text=f"Processing test case {i+1}/{df_copy.shape[0]}...")

            query, llm_output, ref_answer, req_facts = str(row.get('query','')), str(row.get('llm_output','')), str(row.get('reference_answer','')), str(row.get('required_facts',''))
            row_metric_statuses = {}

            for metric_name in selected_metrics:
                if metric_name not in self.metrics_instances:
                    row_metric_statuses[metric_name] = 'Error (Not Initialized)'
                    continue
                
                metric_instance, score, individual_status = self.metrics_instances[metric_name], pd.NA, 'Error (Calculation)'
                try:
                    kwargs = {'llm_output': llm_output, 'reference_answer': ref_answer, 'query': query}
                    if metric_name == "Safety": kwargs['sensitive_keywords'] = sensitive_keywords
                    elif metric_name == "Fact Adherence": kwargs['required_facts'] = req_facts
                    
                    score_val = metric_instance.compute(**kwargs)
                    if not pd.isna(score_val):
                        score = float(score_val)
                        df_copy.loc[i, f'{metric_name} Score'] = round(score, 4)
                        threshold = current_thresholds.get(metric_name)
                        if threshold is not None:
                            individual_status = 'Pass' if (metric_name == "Safety" and score == threshold) or \
                                                        (metric_name != "Safety" and score >= threshold) else 'Fail'
                        else: individual_status = 'N/A (No Threshold)'
                    else: individual_status = 'Error (No Score)'
                except Exception as e:
                    print(f"ERROR evaluating {metric_name} for row {i}: {e}\n{traceback.format_exc()}")
                    df_copy.loc[i, f'{metric_name} Score'] = 'Calc Error'
                
                df_copy.loc[i, f'{metric_name} Pass/Fail'] = individual_status
                row_metric_statuses[metric_name] = individual_status

            # Calculate Automated Overall Result
            if selected_metrics:
                relevant_statuses = [s for m, s in row_metric_statuses.items() if m in selected_metrics]
                if not relevant_statuses: df_copy.loc[i, automated_overall_col_name] = 'Error (No Metrics Run)'
                elif overall_pass_criterion == PASS_CRITERION_ALL_PASS:
                    if all(s == 'Pass' for s in relevant_statuses): df_copy.loc[i, automated_overall_col_name] = 'Pass'
                    elif any(s.startswith('Error') for s in relevant_statuses): df_copy.loc[i, automated_overall_col_name] = 'Error'
                    else: df_copy.loc[i, automated_overall_col_name] = 'Fail'
                elif overall_pass_criterion == PASS_CRITERION_ANY_PASS:
                    if any(s == 'Pass' for s in relevant_statuses): df_copy.loc[i, automated_overall_col_name] = 'Pass'
                    elif all(s.startswith('Error') or s == 'N/A (No Threshold)' for s in relevant_statuses): df_copy.loc[i, automated_overall_col_name] = 'Error'
                    else: df_copy.loc[i, automated_overall_col_name] = 'Fail'
            else: df_copy.loc[i, automated_overall_col_name] = 'N/A (No Metrics Selected)'

        if progress_bar: progress_bar.empty()
        try: st.success("Evaluation process completed!")
        except: print("Evaluation process completed!")
        return df_copy

    def get_available_metrics(self) -> list: return list(AVAILABLE_METRICS.keys())
    def get_metric_thresholds(self) -> dict: return METRIC_THRESHOLDS.copy()