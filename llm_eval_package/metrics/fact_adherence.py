# llm_eval_package/metrics/fact_adherence.py
from llm_eval_package.metrics.base import BaseMetric
import numpy as np
import warnings
import pandas as pd
import string # For punctuation

try:
    import nltk
    from nltk.stem import WordNetLemmatizer
    from nltk.tokenize import word_tokenize
    from nltk.corpus import wordnet # For POS tag mapping

    _NLTK_AVAILABLE = True
    # Check for necessary NLTK data and offer to download if missing
    # This is a simplified check; a more robust check might try nltk.download()
    # within a try-except block if permissions allow, or guide the user.
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/wordnet')
        nltk.data.find('corpora/omw-1.4')
        nltk.data.find('taggers/averaged_perceptron_tagger') # For nltk.pos_tag
    except LookupError:
        warnings.warn(
            "One or more NLTK data packages (punkt, wordnet, omw-1.4, averaged_perceptron_tagger) "
            "not found. Fact Adherence may fall back to simpler matching or be less accurate.\n"
            "Please run the following in a Python interpreter:\n"
            "import nltk\n"
            "nltk.download('punkt')\n"
            "nltk.download('wordnet')\n"
            "nltk.download('omw-1.4')\n"
            "nltk.download('averaged_perceptron_tagger')"
        )
        _NLTK_AVAILABLE = False # If essential data is missing, treat NLTK as not fully ready

except ImportError:
    _NLTK_AVAILABLE = False
    warnings.warn("NLTK library not found. FactAdherenceMetric will use simple substring matching.")

class FactAdherenceMetric(BaseMetric):
    def __init__(self):
        super().__init__("Fact Adherence")
        self.nltk_ready = False
        if _NLTK_AVAILABLE:
            try:
                self.lemmatizer = WordNetLemmatizer()
                word_tokenize("test") 
                nltk.pos_tag(word_tokenize("test")) 
                self.lemmatizer.lemmatize("tests", pos=wordnet.VERB) 
                self.nltk_ready = True
                print("DEBUG (FactAdherence): NLTK with POS-aware lemmatization is READY.")
            except Exception as e:
                warnings.warn(f"FactAdherenceMetric: NLTK components failed ({e}). Falling back.")
                self.nltk_ready = False
        else:
            print("DEBUG (FactAdherence): NLTK not available, falling back.")

    def _get_wordnet_pos(self, nltk_tag):
        if nltk_tag.startswith('J'): return wordnet.ADJ
        elif nltk_tag.startswith('V'): return wordnet.VERB
        elif nltk_tag.startswith('N'): return wordnet.NOUN
        elif nltk_tag.startswith('R'): return wordnet.ADV
        else: return wordnet.NOUN 

    def _process_text_for_matching(self, text: str):
        """Tokenizes, cleans (keeps alphanumeric, specific symbols like $), and lemmatizes text."""
        if not self.nltk_ready or not text or not isinstance(text, str):
            if not text or not isinstance(text, str): return []
            # Basic fallback: lower, split, remove common punctuation but try to keep $ and numbers
            # This fallback is less precise than NLTK path.
            processed_tokens = []
            # Allow specific symbols like $ and % to be part of tokens if attached to numbers
            # This regex attempts to keep currency/percentages and words.
            raw_tokens = re.findall(r'[\$€£¥]?\d+[.,\d]*%?|\w+', str(text).lower())
            for token in raw_tokens:
                # Remove standalone punctuation that might have been captured if not part of word/currency
                if token in string.punctuation and len(token) == 1: 
                    continue
                processed_tokens.append(token)
            return processed_tokens

        tokens = word_tokenize(text.lower())
        
        # Filter out most punctuation but keep $, %, and numbers as part of tokens if possible
        # and ensure tokens are not just standalone punctuation.
        # This also aims to handle cases like "$500" becoming ['$', '500'] by word_tokenize
        # and then tries to treat them as individual items or re-combine if necessary for facts.
        # For "all words must match", it's better if "$500" is treated as "500" and fact has "500".
        # Or if fact has "$500", it should tokenize to ['$','500'].
        
        # Let's simplify: keep alphanumeric, and specific symbols if they are part of what users might consider a "word" or value.
        # word_tokenize will separate '$' from '500'. We want to keep both if they are in the fact.
        # The previous filter `token.isalnum()` was too aggressive, removing '$'.

        cleaned_tokens = []
        for token in tokens:
            if token in string.punctuation: # Skip common standalone punctuation
                continue
            cleaned_tokens.append(token) 
            # Numbers will be kept as strings here. Lemmatizer doesn't change them.
            # Symbols like '$' will also be kept if word_tokenize treats them as tokens.

        if not cleaned_tokens: return []

        pos_tags = nltk.pos_tag(cleaned_tokens)
        lemmatized_tokens = [self.lemmatizer.lemmatize(token, self._get_wordnet_pos(tag)) for token, tag in pos_tags]
        
        # print(f"    Processed '{text}' -> {lemmatized_tokens}") # Debug individual processing
        return lemmatized_tokens

    def compute(self, llm_output: str, reference_answer: str = None, query: str = None, required_facts: str = None, **kwargs) -> float:
        if pd.isna(required_facts) or not str(required_facts).strip(): return np.nan 
        facts_list_phrases = [fact.strip() for fact in str(required_facts).split(';') if fact.strip()]
        if not facts_list_phrases: return np.nan
        if pd.isna(llm_output) or not str(llm_output).strip(): return 0.0
        
        llm_output_str = str(llm_output)
        found_count = 0

        # print(f"\nDEBUG (FactAdherence): Evaluating LLM Output: '{llm_output_str}'")
        # print(f"DEBUG (FactAdherence): Against Required Facts Input: '{required_facts}'")

        if self.nltk_ready:
            processed_llm_output_words_set = set(self._process_text_for_matching(llm_output_str))
            # print(f"DEBUG (FactAdherence): Processed LLM Output Tokens (Set): {processed_llm_output_words_set}")

            for i, fact_phrase in enumerate(facts_list_phrases):
                if not fact_phrase: continue
                
                processed_fact_phrase_words = self._process_text_for_matching(fact_phrase)
                # print(f"DEBUG (FactAdherence): Fact {i+1} ('{fact_phrase}') -> Processed Fact Tokens: {processed_fact_phrase_words}")
                if not processed_fact_phrase_words: continue

                all_fact_words_found = True
                for fact_word in processed_fact_phrase_words:
                    if fact_word not in processed_llm_output_words_set:
                        all_fact_words_found = False
                        # print(f"  Word '{fact_word}' from Fact {i+1} NOT FOUND.")
                        break 
                if all_fact_words_found:
                    found_count += 1
                    # print(f"  Fact {i+1} - MATCHED.")
                # else:
                    # print(f"  Fact {i+1} - NO MATCH.")
        else: 
            # Fallback: simple case-insensitive substring for WHOLE phrase
            # This fallback is less granular than the NLTK word-by-word check.
            # print("DEBUG (FactAdherence): Using FALLBACK SUBSTRING CHECK.")
            llm_output_lower = llm_output_str.lower()
            for fact_phrase in facts_list_phrases:
                if fact_phrase.lower() in llm_output_lower:
                    found_count += 1
        
        # print(f"DEBUG (FactAdherence): Found {found_count}/{len(facts_list_phrases)} facts.")
        return found_count / len(facts_list_phrases)

# class FactAdherenceMetric(BaseMetric):
#     def __init__(self):
#         super().__init__("Fact Adherence")
#         self.nltk_ready = False
#         if _NLTK_AVAILABLE:
#             try:
#                 self.lemmatizer = WordNetLemmatizer()
#                 word_tokenize("test") # Test punkt
#                 nltk.pos_tag(word_tokenize("test")) # Test averaged_perceptron_tagger
#                 self.lemmatizer.lemmatize("tests", pos=wordnet.VERB) # Test wordnet with a POS tag
#                 self.nltk_ready = True
#                 print("DEBUG (FactAdherence): NLTK with POS-aware lemmatization is READY.")
#             except Exception as e:
#                 warnings.warn(f"FactAdherenceMetric: NLTK components failed to initialize fully ({e}). Falling back to simple substring matching.")
#                 self.nltk_ready = False
#         else:
#             print("DEBUG (FactAdherence): NLTK not available or not fully configured, falling back to simple substring matching.")

#     def _get_wordnet_pos(self, nltk_tag):
#         """Map NLTK POS tags to WordNet POS tags."""
#         if nltk_tag.startswith('J'):
#             return wordnet.ADJ
#         elif nltk_tag.startswith('V'):
#             return wordnet.VERB
#         elif nltk_tag.startswith('N'):
#             return wordnet.NOUN
#         elif nltk_tag.startswith('R'):
#             return wordnet.ADV
#         else:
#             return wordnet.NOUN # Default to noun

#     def _lemmatize_and_clean_text(self, text: str):
#         if not self.nltk_ready or not text or not isinstance(text, str):
#             # Fallback: lowercase, tokenize by space, remove punctuation rudimentarily
#             if not text or not isinstance(text, str): return []
#             clean_text = ''.join(char for char in text if char not in string.punctuation).lower()
#             return clean_text.split()

#         tokens = word_tokenize(text.lower())
#         # Filter out punctuation
#         tokens_no_punct = [token for token in tokens if token not in string.punctuation and token.isalnum()] # Keep only alphanumeric
        
#         if not tokens_no_punct: # If only punctuation was present
#             return []

#         pos_tags = nltk.pos_tag(tokens_no_punct)
#         lemmatized_tokens = [self.lemmatizer.lemmatize(token, self._get_wordnet_pos(tag)) for token, tag in pos_tags]
#         return lemmatized_tokens

#     def compute(self, llm_output: str, reference_answer: str = None, query: str = None, required_facts: str = None, **kwargs) -> float:
#         if pd.isna(required_facts) or not str(required_facts).strip():
#             return np.nan 

#         facts_list_phrases = [fact.strip() for fact in str(required_facts).split(';') if fact.strip()]
#         if not facts_list_phrases:
#             return np.nan

#         if pd.isna(llm_output) or not str(llm_output).strip():
#             return 0.0
        
#         llm_output_str = str(llm_output)
#         found_count = 0

#         # print(f"DEBUG (FactAdherence): LLM Output: '{llm_output_str}'") # For user debugging
#         # print(f"DEBUG (FactAdherence): Required Facts Input: '{required_facts}'") # For user debugging

#         if self.nltk_ready:
#             lemmatized_llm_output_words_set = set(self._lemmatize_and_clean_text(llm_output_str))
#             # print(f"DEBUG (FactAdherence): Lemmatized LLM Output Tokens (Set): {lemmatized_llm_output_words_set}")

#             for i, fact_phrase in enumerate(facts_list_phrases):
#                 if not fact_phrase: continue
                
#                 lemmatized_fact_phrase_words = self._lemmatize_and_clean_text(fact_phrase)
#                 # print(f"DEBUG (FactAdherence): Fact {i+1} ('{fact_phrase}') -> Lemmatized Fact Tokens: {lemmatized_fact_phrase_words}")
#                 if not lemmatized_fact_phrase_words: continue

#                 all_fact_words_found_for_this_phrase = True
#                 for fact_word in lemmatized_fact_phrase_words:
#                     if fact_word not in lemmatized_llm_output_words_set:
#                         all_fact_words_found_for_this_phrase = False
#                         # print(f"DEBUG (FactAdherence): Word '{fact_word}' from Fact {i+1} NOT FOUND in LLM output.")
#                         break 
                
#                 if all_fact_words_found_for_this_phrase:
#                     found_count += 1
#                     # print(f"DEBUG (FactAdherence): Fact {i+1} ('{fact_phrase}') - MATCHED.")
#                 # else:
#                     # print(f"DEBUG (FactAdherence): Fact {i+1} ('{fact_phrase}') - NO MATCH.")
#         else: 
#             llm_output_lower = llm_output_str.lower()
#             for fact_phrase in facts_list_phrases:
#                 if fact_phrase.lower() in llm_output_lower: # Simple substring for fallback
#                     found_count += 1
        
#         return found_count / len(facts_list_phrases)

    def get_score_description(self, score: float) -> str:
        # ... (This method remains the same as in the previous response) ...
        if pd.isna(score): 
            return "Not Applicable: No valid required facts were provided for this test case."
        if score == 1.0: return "Excellent: All required facts were found."
        elif score >= 0.75: return "Good: Most required facts were found."
        elif score >= 0.5: return "Moderate: Some required facts found, several missing."
        elif score > 0.0: return "Low: Very few required facts were found."
        return "Poor: None of the required facts were found."


# # llm_eval_package/metrics/fact_adherence.py
# from llm_eval_package.metrics.base import BaseMetric
# import numpy as np # For np.nan
# import warnings
# import pandas as pd # For pd.isna

# try:
#     import nltk
#     from nltk.stem import WordNetLemmatizer
#     from nltk.tokenize import word_tokenize
#     _NLTK_AVAILABLE = True
#     try: # Check for necessary NLTK data
#         nltk.data.find('tokenizers/punkt')
#         nltk.data.find('corpora/wordnet')
#         nltk.data.find('corpora/omw-1.4')
#     except LookupError: # More specific exception for missing data
#         warnings.warn(
#             "NLTK data (punkt, wordnet, omw-1.4) not found or NLTK itself is not fully configured. "
#             "Fact Adherence will fall back to simple substring matching. "
#             "To enable advanced matching, run in Python: \n"
#             "import nltk\nnltk.download('punkt')\nnltk.download('wordnet')\nnltk.download('omw-1.4')"
#         )
#         _NLTK_AVAILABLE = False # Treat as unavailable if data is missing
# except ImportError:
#     _NLTK_AVAILABLE = False
#     warnings.warn("NLTK library not found. FactAdherenceMetric will fall back to simple substring matching.")


# class FactAdherenceMetric(BaseMetric):
#     def __init__(self):
#         super().__init__("Fact Adherence")
#         self.nltk_ready = False
#         if _NLTK_AVAILABLE:
#             try:
#                 self.lemmatizer = WordNetLemmatizer()
#                 word_tokenize("test") # Test if punkt is available and working
#                 self.lemmatizer.lemmatize("test") # Test if wordnet is available
#                 self.nltk_ready = True
#                 print("DEBUG: NLTK Lemmatization is READY for Fact Adherence.")
#             except Exception as e:
#                 warnings.warn(f"NLTK components (punkt/wordnet) for FactAdherenceMetric failed to initialize: {e}. Falling back to simple substring matching.")
#         else:
#              print("DEBUG: NLTK Lemmatization is NOT READY for Fact Adherence, falling back.")


#     def _lemmatize_text(self, text):
#         if not self.nltk_ready or not text or not isinstance(text, str):
#              # Fallback for non-string, empty text, or if NLTK not ready
#             return str(text).lower().split() if text else []
        
#         tokens = word_tokenize(text.lower())
#         lemmatized_tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
#         return lemmatized_tokens

#     def _is_sublist(self, sublist, mainlist):
#         if not sublist: return True 
#         if not mainlist: return False
#         len_sub = len(sublist)
#         for i in range(len(mainlist) - len_sub + 1):
#             if mainlist[i:i+len_sub] == sublist:
#                 return True
#         return False

#     def compute(self, llm_output: str, reference_answer: str = None, query: str = None, required_facts: str = None, **kwargs) -> float:
#         if not required_facts or not str(required_facts).strip():
#             return np.nan 

#         facts_list_phrases = [fact.strip() for fact in str(required_facts).split(';') if fact.strip()]
#         if not facts_list_phrases:
#             return np.nan

#         if not llm_output or not llm_output.strip():
#             return 0.0 

#         found_count = 0

#         if self.nltk_ready:
#             # Lemmatize the entire LLM output once and create a set of its words for efficient lookup
#             lemmatized_llm_output_words = set(self._lemmatize_text(llm_output))
            
#             for fact_phrase in facts_list_phrases:
#                 if not fact_phrase: continue # Skip empty fact phrases after split
                
#                 lemmatized_fact_phrase_words = self._lemmatize_text(fact_phrase)
#                 if not lemmatized_fact_phrase_words: continue # Skip if fact phrase becomes empty after lemmatization

#                 # Check if all lemmatized words from the current fact phrase are present in the LLM output
#                 # This is order-independent for words within the fact phrase.
#                 all_fact_words_found = True
#                 for fact_word in lemmatized_fact_phrase_words:
#                     if fact_word not in lemmatized_llm_output_words:
#                         all_fact_words_found = False
#                         break # No need to check other words for this fact phrase
                
#                 if all_fact_words_found:
#                     found_count += 1
#         else: 
#             # Fallback: Simple case-insensitive substring check for the entire fact phrase
#             llm_output_lower = llm_output.lower()
#             for fact_phrase in facts_list_phrases:
#                 if fact_phrase.lower() in llm_output_lower:
#                     found_count += 1
        
#         return found_count / len(facts_list_phrases)
 
#     def get_score_description(self, score: float) -> str:
#         if pd.isna(score): # Use pandas isna for checking np.nan
#             return "Not Applicable: No valid required facts were provided for this test case."
#         # ... (rest of descriptions for 1.0, 0.75, etc. as before) ...
#         if score == 1.0: return "Excellent: All required facts were found."
#         elif score >= 0.75: return "Good: Most required facts were found."
#         elif score >= 0.5: return "Moderate: Some required facts found, several missing."
#         elif score > 0.0: return "Low: Very few required facts were found."
#         return "Poor: None of the required facts were found."
    
