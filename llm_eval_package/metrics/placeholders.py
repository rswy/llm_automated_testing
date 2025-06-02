# src/metrics/placeholders.py
from .base_metric import BaseMetric
import warnings
import numpy as np # For float('nan')

class NLIScoreMetric(BaseMetric):
    """
    Placeholder for NLI-based fact checking. 
    This metric is not yet implemented and will return NaN.
    Full implementation requires an NLI model.
    """
    def compute(self, references, predictions, **kwargs):
        # warnings.warn("NLIScoreMetric is a placeholder and returns NaN. Called for single instance.", RuntimeWarning)
        return {"nli_entailment_score": np.nan}

class LLMAsJudgeFactualityMetric(BaseMetric):
    """
    Placeholder for using an LLM to judge factuality.
    This metric is not yet implemented and will return NaN.
    Full implementation requires LLM API access and prompt engineering.
    """
    def compute(self, references, predictions, **kwargs):
        # warnings.warn("LLMAsJudgeFactualityMetric is a placeholder and returns NaN. Called for single instance.", RuntimeWarning)
        return {"llm_judge_factuality": np.nan}

class ProfessionalToneMetric(BaseMetric):
    """
    Placeholder for evaluating professional tone.
    This metric is not yet implemented and will return NaN.
    Full implementation requires a dedicated classifier, LLM-as-judge, or human evaluation.
    """
    def compute(self, references, predictions, **kwargs):
        # warnings.warn("ProfessionalToneMetric is a placeholder and returns NaN. Called for single instance.", RuntimeWarning)
        return {"professional_tone_score": np.nan}

class RefusalQualityMetric(BaseMetric):
    """
    Placeholder for evaluating refusal appropriateness.
    This metric is not yet implemented and will return NaN.
    Full implementation requires specific test cases, logic, or human evaluation.
    """
    def compute(self, references, predictions, **kwargs):
        # warnings.warn("RefusalQualityMetric is a placeholder and returns NaN. Called for single instance.", RuntimeWarning)
        return {"refusal_quality_score": np.nan}

# Semantic Similarity was moved to its own file: semantic_similarity.py
