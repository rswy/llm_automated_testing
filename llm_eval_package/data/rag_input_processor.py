# llm_eval_package/data/rag_input_processor.py
import requests
import json
import pandas as pd
from datetime import datetime, timezone
import urllib3
import time

# --- Default Configurations (Consider moving to a config file or managing securely) ---
DEFAULT_API_URL = "https://s-studio-egpsg-sit-01.apps.ecpocpth001.sg.uobnet.com/chatassist/api/chat"

# IMPORTANT: The Bearer token is sensitive and will expire.
# This should be updated regularly and managed securely (e.g., via environment variables, a secure config).
DEFAULT_API_HEADERS = {
    "Content-Type": "application/json",
    "Application-Id": "EGP",
    "Channel-Id": "STUDIO",
    "Country": "SG",
    "Authorization": "Bearer YOUR_EXPIRED_OR_PLACEHOLDER_TOKEN_HERE" # <-- UPDATE THIS TOKEN
}

DEFAULT_DOMAINS = {
    'Finance': '/dmofinance-122',
    'HR': '/hr-161',
    'SG Branch': '/branch-ops-181',
    'TH Branch': '/thailand-101',
    'GWB': 'gwb-25',
    'DMO': '/dmo-61'
    # Add other domains as needed
}
# --- End Default Configurations ---

def fetch_bot_responses(input_csv_path: str, output_csv_path: str,
                        query_column: str = "query",
                        domain_key: str = 'SG Branch',
                        api_url: str = None,
                        api_headers: dict = None,
                        domains: dict = None,
                        sender_id: str = "testusr",
                        api_timeout: int = 30,
                        max_retries: int = 2,
                        retry_delay: int = 5):
    """
    Fetches responses from an RAG bot for queries in a CSV file and saves them.

    Args:
        input_csv_path (str): Path to the input CSV with queries.
        output_csv_path (str): Path to save the output CSV with an 'llm_output' column.
        query_column (str): Name of the column in input_csv_path containing queries.
        domain_key (str): Key for the desired domain in the domains dictionary.
        api_url (str, optional): Custom API URL. Defaults to DEFAULT_API_URL.
        api_headers (dict, optional): Custom API headers. Defaults to DEFAULT_API_HEADERS.
                                      'Req-Date-Time' will be updated automatically.
                                      Ensure 'Authorization' token is valid.
        domains (dict, optional): Custom domains dictionary. Defaults to DEFAULT_DOMAINS.
        sender_id (str): Sender ID for the API payload.
        api_timeout (int): Timeout for API requests in seconds.
        max_retries (int): Maximum number of retries for failed API calls.
        retry_delay (int): Delay between retries in seconds.

    Returns:
        str: Path to the output CSV file.

    Raises:
        FileNotFoundError: If input_csv_path does not exist.
        ValueError: If query_column is not in the input CSV or domain_key is invalid.
    """
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    current_api_url = api_url or DEFAULT_API_URL
    # Use a copy of default headers to prevent modification of the global default
    current_api_headers = (api_headers or DEFAULT_API_HEADERS).copy()
    current_domains = domains or DEFAULT_DOMAINS

    # Check if input_csv_path is a string path or a file-like object for pandas
    if isinstance(input_csv_path, str):
        if not pd.io.common.file_exists(input_csv_path): # type: ignore
            raise FileNotFoundError(f"Input CSV file not found: {input_csv_path}")
        df = pd.read_csv(input_csv_path)
    elif hasattr(input_csv_path, 'read'): # Check if it's a file-like object
        df = pd.read_csv(input_csv_path)
    else:
        raise ValueError("input_csv_path must be a file path string or a file-like object")


    if query_column not in df.columns:
        raise ValueError(f"Query column '{query_column}' not found in the input data.")

    domain_path = current_domains.get(domain_key)
    if not domain_path:
        raise ValueError(f"Domain key '{domain_key}' not found in domains configuration. Available keys: {list(current_domains.keys())}")

    if "YOUR_EXPIRED_OR_PLACEHOLDER_TOKEN_HERE" in current_api_headers.get("Authorization", ""):
        print("Warning: API headers appear to use a placeholder token. Ensure a valid token is provided.")

    responses_list = []
    print(f"Fetching responses for {len(df)} queries using domain '{domain_key}' ({domain_path})...")

    for idx, row in df.iterrows():
        query_text = str(row[query_column]) # Ensure query_text is a string
        current_api_headers["Req-Date-Time"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        payload = {
            "message": query_text,
            "senderId": sender_id,
            "domain": domain_path
        }

        attempt = 0
        success = False
        while attempt <= max_retries and not success:
            try:
                print(f"Attempt {attempt + 1} for query {idx + 1}/{len(df)}: '{query_text[:50]}...'")
                response = requests.post(current_api_url, headers=current_api_headers,
                                         data=json.dumps(payload), verify=False, timeout=api_timeout)
                response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

                full_message = ""
                # Handle cases where response.text might be empty or not as expected
                if response.text and response.text.strip():
                    for line in response.text.strip().splitlines():
                        try:
                            obj = json.loads(line)
                            full_message += str(obj.get("data", "")) # Ensure data is string
                        except json.JSONDecodeError:
                            print(f"  Warning: Non-JSON line in response for query {idx+1}: {line}")
                            # If the line itself is the message (for non-streaming simple JSON response)
                            if not full_message and attempt == 0: # Append only if full_message is empty and it's the first try.
                                full_message += line 
                            continue
                else: # Handle empty response
                    print(f"  Warning: Empty response text for query {idx+1}")
                    full_message = "Error: Empty API response"


                responses_list.append(full_message)
                print(f"  Success (Status {response.status_code}) for query {idx + 1}.")
                success = True
            except requests.exceptions.RequestException as e:
                print(f"  API Error (Attempt {attempt + 1}) for query {idx + 1}: {e}")
                if attempt == max_retries:
                    responses_list.append(f"Error: Max retries reached. Last error: {str(e)}")
                else:
                    time.sleep(retry_delay) # Wait before retrying
            except Exception as e:
                print(f"  Unexpected Error (Attempt {attempt + 1}) for query {idx + 1}: {e}")
                if attempt == max_retries:
                     responses_list.append(f"Error: Max retries reached. Last unexpected error: {str(e)}")
                else:
                    time.sleep(retry_delay)
            attempt += 1
        
        if not success and len(responses_list) != (idx + 1): # Ensure placeholder is added if all retries fail
             responses_list.append(f"Error: Failed to get response for query '{query_text[:50]}...' after {max_retries+1} attempts.")


    df['llm_output'] = responses_list  # This column name is what the eval framework expects
    
    if isinstance(output_csv_path, str):
        df.to_csv(output_csv_path, index=False, encoding='utf-8')
        print(f"\nResponses fetched and saved to '{output_csv_path}' in the 'llm_output' column.")
        return output_csv_path
    elif hasattr(output_csv_path, 'write'): # Check if it's a file-like object for pandas to_csv
        df.to_csv(output_csv_path, index=False, encoding='utf-8')
        print(f"\nResponses fetched and written to provided stream in the 'llm_output' column.")
        return output_csv_path # Or handle differently if it's a stream
    else:
        raise ValueError("output_csv_path must be a file path string or a writable file-like object")