# src/metrics/classification.py
from .base_metric import BaseMetric
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import numpy as np
import warnings

class ClassificationMetrics(BaseMetric):
    """
    Computes classification metrics for a single reference and prediction label.
    Note: For metrics like precision, recall, F1 to be meaningful, they are
    typically calculated over a dataset. Here, we'll calculate them for the
    single prediction, which implies a micro-average perspective if aggregated later,
    or more simply, treating the single prediction as its own tiny dataset.
    Accuracy for a single instance is 1.0 if match, 0.0 otherwise.
    Precision/Recall/F1 for a single instance are less standard but can be 1 or 0.
    """


    
    def compute(self, references, predictions, **kwargs):
        # references is a single ground truth label
        # predictions is a single predicted label
        
        ref_label = str(references).strip() if references is not None else ""
        pred_label = str(predictions).strip() if predictions is not None else ""

        if not ref_label or not pred_label:
            warnings.warn(f"ClassificationMetrics: Empty reference or prediction label. Ref: '{ref_label}', Pred: '{pred_label}'. Returning NaNs.", RuntimeWarning)
            return {"accuracy": float('nan'), "precision": float('nan'), "recall": float('nan'), "f1_score": float('nan')}

        # For a single instance:
        accuracy = 1.0 if ref_label == pred_label else 0.0
        
        # Precision, Recall, F1 for a single instance:
        # If we consider this single instance, and assume it's positive if predicted positive:
        # This interpretation is tricky for single instances. A common approach for per-instance
        # "correctness" contribution to these metrics is binary (correct or not).
        # Let's return 1 if correct for the class, 0 if incorrect.
        # This means precision/recall/F1 will be 1 if correct, 0 if incorrect, assuming the class of interest is the predicted class.
        # This is a simplification. True P/R/F1 are dataset-level.
        # The evaluator's aggregation step will correctly calculate dataset-level P/R/F1 if it
        # collects all true labels and predicted labels and then calls sklearn.metrics functions.

        # The current evaluator will average these 0/1 values, which is NOT standard P/R/F1.
        # A better approach is for this method to return the raw prediction and reference
        # and let the evaluator handle the final P/R/F1 calculation after collecting all pairs.
        # However, to stick to the "return score dict" pattern:
        
        is_correct = (ref_label == pred_label)
        
        # Simplistic per-instance view (can be debated):
        # If a prediction is made for a class, and it's correct, P/R/F1 for that instance regarding that class is 1.
        # If it's incorrect, it's 0.
        # This is not how sklearn calculates it globally. We might need to adjust evaluator
        # or accept these are instance-level correctness flags.
        # For now, let's calculate as if the single prediction is the entire dataset for these.
        
        try:
            # This calculates P/R/F1 as if this single pair is the entire dataset.
            # This will result in 1.0 or 0.0 for P/R/F1 for the *specific class predicted/referenced*.
            # To get overall P/R/F1 (e.g. macro), the evaluator would need to aggregate all pairs first.
            # Let's provide instance-level accuracy, and let global P/R/F1 be computed by evaluator.
            # For now, to fit the pattern, we can calculate sklearn metrics on this single pair,
            # but the averaging in the evaluator will be of these 0/1 scores.
            
            # For binary case (e.g. if predicted_label is considered 'positive class')
            # TP: ref_label == pred_label (and pred_label is the class of interest)
            # FP: ref_label != pred_label (and pred_label is the class of interest)
            # FN: ref_label == class_of_interest and pred_label != class_of_interest
            # This is too complex for the simple return. Let's stick to simpler 0/1 values for "correctness"
            # and the evaluator can do the main sklearn call.
            #
            # The current `evaluator.py` will average these.
            # To make the aggregated scores correct, ClassificationMetrics should be called *once*
            # by the evaluator with *all* references and predictions for a model/task.
            # This conflicts with the "per-instance score" goal for *these specific metrics*.
            #
            # Resolution: We will calculate instance accuracy. For P/R/F1, this class is not
            # the right place to calculate per-instance scores that average to the global scores.
            # The evaluator should collect all ref/pred pairs and call sklearn.metrics once for P/R/F1.
            #
            # For now, let's have this metric return accuracy for the instance.
            # And return 0/1 for P/R/F1 based on correctness, with a heavy caveat.
            
            # We need to provide all labels to precision_recall_fscore_support.
            # For a single instance, this means the ref_label and pred_label.
            # It's better if the evaluator handles global P/R/F1.
            # For individual scores, we'll report accuracy.
            # And placeholder P/R/F1 (which will be instance correctness).

            # If we must return P/R/F1 from here for the per-instance report:
            # Assume the positive label is ref_label.
            # This is not standard.
            precision, recall, f1, _ = precision_recall_fscore_support(
                [ref_label], [pred_label], average='macro', labels=[ref_label, pred_label] if ref_label != pred_label else [ref_label], zero_division=0
            )

        except Exception as e:
            warnings.warn(f"ClassificationMetrics: Calculation Error for instance: {e}. Returning 0s for P/R/F1.", RuntimeWarning)
            precision, recall, f1 = 0.0, 0.0, 0.0
            if accuracy == float('nan'): # if accuracy also failed
                 accuracy = 0.0


        return {
            "accuracy": accuracy,
            "precision": precision, # This will be 1.0 or 0.0 based on the pair
            "recall": recall,     # This will be 1.0 or 0.0
            "f1_score": f1        # This will be 1.0 or 0.0
        }