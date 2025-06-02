import os
from pathlib import Path
from sentence_transformers import SentenceTransformer

class ModelDownloader:
    """
    Utility class to download and save Sentence-Transformer models locally.
    """
    def __init__(self):
        pass

    def download_and_save_model(self, model_name: str, output_directory: str):
        """
        Downloads a Sentence-Transformer model from the Hugging Face Hub
        and saves it to the specified local directory.

        Args:
            model_name (str): The name of the model to download (e.g., 'all-MiniLM-L6-v2').
            output_directory (str): The base directory where the model will be saved.
                                    A subdirectory named after the model_name will be created.
        Returns:
            str: The full path to the saved model directory if successful, None otherwise.
        """
        save_path = os.path.join(output_directory, model_name)
        os.makedirs(save_path, exist_ok=True)

        print(f"Attempting to download and save model '{model_name}' to '{save_path}'...")

        try:
            # Initialize the model from the Hub (this will trigger download if not cached)
            model = SentenceTransformer(model_name)
            # Save the model to the specified path
            model.save(save_path)
            print(f"Model '{model_name}' successfully saved to '{save_path}'.")
            print("This directory contains all necessary files for the model.")
            return save_path
        except Exception as e:
            print(f"An error occurred while downloading or saving the model: {e}")
            return None

# How to run this from command line (for testing/pre-downloading):
# Navigate to your project's root directory.
# Ensure your Conda environment is activated.
# python -c "from llm_eval_package.utils import ModelDownloader; md = ModelDownloader(); md.download_and_save_model('all-MiniLM-L6-v2', './models')"
# Or, if you want to integrate this as a separate CLI command in main.py, you could.


# python -c "from llm_eval_package.utils import ModelDownloader; from llm_eval_package.config import SENTENCE_BERT_MODEL, MODEL_DIR; md = ModelDownloader(); md.download_and_save_model(SENTENCE_BERT_MODEL, MODEL_DIR)"