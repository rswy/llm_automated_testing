# src/metrics/utils.py
import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.meteor_score import single_meteor_score
from nltk.tokenize import word_tokenize
import warnings

# Ensure NLTK data is downloaded (run this in interpreter once: nltk.download('punkt'), nltk.download('wordnet'), nltk.download('omw-1.4'))
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/wordnet')
    nltk.data.find('corpora/omw-1.4')
except Exception as e:
    print(f"NLTK data missing: {e}")
    print("Please run the following in a Python interpreter:")
    print("import nltk")
    print("nltk.download('punkt')")
    print("nltk.download('wordnet')")
    print("nltk.download('omw-1.4')")
    # You might want to exit or raise an error here depending on desired behavior
except LookupError as e:
     print(f"NLTK data lookup error: {e}. Ensure data is downloaded correctly.")


def safe_word_tokenize(text):
    """Tokenizes text using nltk.word_tokenize, handling potential errors and non-string input."""
    try:
        # Ensure text is a string
        if not isinstance(text, str):
             text = str(text)
        # Tokenize using NLTK (requires 'punkt' data)
        return word_tokenize(text.lower())
    except LookupError:
        # This error occurs if 'punkt' is needed but not found
        warnings.warn("NLTK 'punkt' tokenizer data not found. Falling back to simple split(). "
                      "Run nltk.download('punkt') for better tokenization.", RuntimeWarning)
        return text.lower().split() # Basic fallback
    except Exception as e:
        warnings.warn(f"Tokenization failed for text: '{text}'. Error: {e}. Returning empty list.", RuntimeWarning)
        return []