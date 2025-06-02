# This file defines task types and their associated properties.
# It's kept separate for easy configuration and extension.

# Define task types
RAG_FAQ = "rag_faq"
SUMMARIZATION = "summarization"
CLASSIFICATION = "classification"
CHATBOT = "chatbot" # A more generic task type for conversational agents
GENERIC = "generic" # For tasks that don't fit specific categories

# Mapping of task types to their display names
TASK_TYPE_MAPPING = {
    RAG_FAQ: "RAG FAQ",
    SUMMARIZATION: "Summarization",
    CLASSIFICATION: "Classification",
    CHATBOT: "Chatbot",
    GENERIC: "Generic Text Generation"
}

# Define which metrics are relevant for each task type.
# These are the *internal* metric names used in the system, not necessarily display names.
TASK_METRICS = {
    RAG_FAQ: ["Semantic Similarity", "Completeness", "Trust & Factuality", "Conciseness", "Safety"],
    SUMMARIZATION: ["Semantic Similarity", "Completeness", "Conciseness", "Safety"],
    CLASSIFICATION: ["Accuracy", "Precision", "Recall", "F1 Score", "Safety"], # Placeholder metrics
    CHATBOT: ["Semantic Similarity", "Fluency", "Coherence", "Safety"], # Placeholder metrics
    GENERIC: ["Semantic Similarity", "Completeness", "Conciseness", "Safety"]
}

# Define the primary reference column for each task type.
# This column contains the ground truth or target for evaluation.
PRIMARY_REFERENCE_COLUMNS = {
    RAG_FAQ: "reference_answer",
    SUMMARIZATION: "reference_answer",
    CLASSIFICATION: "ground_truth", # For classification, ground_truth is the label
    CHATBOT: "reference_answer",
    GENERIC: "reference_answer"
}

# Define the primary prediction column for each task type.
# This column contains the LLM's output to be evaluated.
PRIMARY_PREDICTION_COLUMNS = {
    RAG_FAQ: "llm_output",
    SUMMARIZATION: "llm_output",
    CLASSIFICATION: "llm_output", # For classification, llm_output is the predicted label
    CHATBOT: "llm_output",
    GENERIC: "llm_output"
}

# Define custom keyword arguments for specific metrics that need additional data from the test case.
# This maps a metric name to a dictionary of {kwarg_name_for_metric: data_column_name_in_test_case}.
# Example: For a 'Fact Presence' metric, it might need a list of 'facts' from the reference.
CUSTOM_METRIC_KWARG_MAP = {
    "Trust & Factuality": {"reference_facts": "ref_facts"}, # Metric expects 'reference_facts', data has 'ref_facts'
    "Completeness": {"reference_key_points": "ref_key_points"}, # Metric expects 'reference_key_points', data has 'ref_key_points'
    # "Safety": {"sensitive_keywords": "sensitive_keywords_column_in_data"} # If sensitive keywords were in data
}


def get_metrics_for_task(task_type: str) -> list:
    """Returns a list of metric names relevant for a given task type."""
    return TASK_METRICS.get(task_type, [])

def get_primary_reference_col(task_type: str) -> str:
    """Returns the name of the primary reference column for a given task type."""
    return PRIMARY_REFERENCE_COLUMNS.get(task_type)

def get_primary_prediction_col(task_type: str) -> str:
    """Returns the name of the primary prediction column for a given task type."""
    return PRIMARY_PREDICTION_COLUMNS.get(task_type)