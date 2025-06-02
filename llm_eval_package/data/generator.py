# import json
# import random
# import copy
# import pandas as pd
# from pathlib import Path
# import sys
# import os

# """
# Generates mock data in a flat, row-per-evaluation format.
# Ensures generated data strictly follows the required input columns:
# 'query', 'llm_output', 'reference_answer', 'test_description', 'test_config'.
# """

# # Ensure tasks module can be found if run directly
# try:
#     # Adjust path to correctly import from llm_eval_package.tasks.registry
#     current_dir = Path(__file__).parent
#     # This path assumes llm_eval_package is one level up from data/generator.py
#     project_root_if_direct = current_dir.parent.parent
#     if str(project_root_if_direct) not in sys.path:
#         sys.sys.path.insert(0, str(project_root_if_direct))
#     from llm_eval_package.tasks.registry import RAG_FAQ, SUMMARIZATION, CLASSIFICATION, CHATBOT, GENERIC
# except ImportError:
#     print("Warning: Could not import task constants from llm_eval_package.tasks.registry. Using string literals.")
#     RAG_FAQ = "rag_faq"; SUMMARIZATION = "summarization"; CLASSIFICATION = "classification"; CHATBOT = "chatbot"; GENERIC = "generic"


# def generate_mock_data_flat(num_samples_per_task=3, seed=42):
#     random.seed(seed)
#     all_data = []
#     eval_id_counter = 1

#     MODEL_GOOD = "model_A_good_semantics"
#     MODEL_PARTIAL = "model_B_partial_semantics"
#     MODEL_POOR = "model_C_poor_lexical_diff_semantics"

#     # # --- RAG/FAQ Data ---
#     # rag_cases = [
#     #     {
#     #         "input": {"question": "Describe the process of photosynthesis."},
#     #         "ref": {
#     #             "ground_truth": "Photosynthesis is the process used by plants, algae, and some bacteria to convert light energy into chemical energy, through a process that uses sunlight, water, and carbon dioxide, releasing oxygen as a byproduct.",
#     #             "ref_facts": "converts light to chemical energy,uses sunlight,uses water,uses carbon dioxide,releases oxygen", # Kept for internal logic, but not output
#     #             "ref_key_points": "Process definition,Inputs (light water CO2),Outputs (chemical energy oxygen),Organisms (plants algae bacteria)" # Kept for internal logic, but not output
#     #         }
#     #     },
#     #     {
#     #         "input": {"question": "What are the benefits of regular exercise?"},
#     #         "ref": {
#     #             "ground_truth": "Regular physical activity can improve your muscle strength, boost your endurance, help control weight, combat health conditions, improve mood, and promote better sleep.",
#     #             "ref_facts": "improves muscle strength,boosts endurance,controls weight,combats health conditions,improves mood,promotes better sleep",
#     #             "ref_key_points": "Physical benefits,Mental benefits,Specific examples (strength weight mood sleep)"
#     #         }
#     #     },
#     # ]

#     # for i in range(num_samples_per_task):
#     #     case = copy.deepcopy(rag_cases[i % len(rag_cases)])
#     #     input_data = case["input"]
#     #     ref_data = case["ref"]
        
#     #     # Internal use of facts/key_points for generating varied responses
#     #     facts = ref_data.get("ref_facts", "").split(',') if ref_data.get("ref_facts") else []
#     #     facts = [f.strip() for f in facts if f.strip()]
#     #     key_points = ref_data.get("ref_key_points", "").split(',') if ref_data.get("ref_key_points") else []
#     #     key_points = [kp.strip() for kp in key_points if kp.strip()]

#     #     responses = {}
#     #     responses[MODEL_GOOD] = f"Plants transform light into usable energy using CO2 and H2O, and they give off oxygen. This vital process supports most life on Earth. It involves {facts[0] if facts else 'key elements'} and covers {key_points[0] if key_points else 'main topics'}."
#     #     responses[MODEL_PARTIAL] = f"Photosynthesis is about plants making food. They use sunlight. This is related to {facts[0] if facts else 'one fact'}."
#     #     if i % 2 == 0:
#     #          responses[MODEL_POOR] = "Gardening is a fun hobby. You need good soil for plants to grow. Water is also important for flowers."
#     #     else:
#     #          responses[MODEL_POOR] = f"The sun's energy is powerful. Carbon is an element. Oxygen is what we breathe. This process is complex and involves {random.choice(['leaves', 'roots', 'badword'])}."


#     #     for model_name, response in responses.items():
#     #         all_data.append({
#     #             "id": f"rag_{eval_id_counter:03d}", 
#     #             "task_type": RAG_FAQ,
#     #             "model": model_name,
#     #             "query": input_data["question"],
#     #             "reference_answer": ref_data["ground_truth"],
#     #             "llm_output": response,
#     #             "test_description": f"Core RAG: {input_data['question'][:30]}...",
#     #             "test_config": "Science_Basics", # Specific test_config
#     #         })
#     #         eval_id_counter += 1
    
#     # # --- Summarization Data ---
#     # sum_cases = [
#     #      {
#     #         "input": {"question": "Summarize the following text about the impact of renewable energy: Renewable energy sources like solar and wind power are crucial for mitigating climate change by reducing greenhouse gas emissions. Their adoption also fosters energy independence and can create new economic opportunities, though challenges in grid integration and storage remain."},
#     #         "ref": {
#     #             "ground_truth": "Renewable energy, such as solar and wind, helps fight climate change by cutting emissions, enhances energy security, and boosts economic growth, despite grid and storage issues.", 
#     #             "ref_key_points": "Climate change mitigation,Emission reduction,Energy independence,Economic opportunities,Grid integration challenges,Storage challenges"
#     #             }
#     #     },
#     # ]
#     # for i in range(num_samples_per_task):
#     #     case = copy.deepcopy(sum_cases[i % len(sum_cases)])
#     #     input_data = case["input"]
#     #     ref_data = case["ref"]
#     #     key_points = ref_data.get("ref_key_points", "").split(',') if ref_data.get("ref_key_points") else []
#     #     key_points = [kp.strip() for kp in key_points if kp.strip()]

#     #     responses = {}
#     #     responses[MODEL_GOOD] = "Using renewable sources like wind and solar is key to lessening climate change impact via lower emissions. It also supports energy autonomy and economic development, though integrating them into the grid and storing the energy are hurdles."
#     #     responses[MODEL_PARTIAL] = "Renewable energy is good for the planet. Solar panels are one type."
#     #     responses[MODEL_POOR] = "Fossil fuels have been used for a long time. They are non-renewable. Pollution is a major concern for cities worldwide."

#     #     for model_name, response in responses.items():
#     #         all_data.append({
#     #             "id": f"sum_{eval_id_counter:03d}",
#     #             "task_type": SUMMARIZATION,
#     #             "model": model_name,
#     #             "query": input_data["question"],
#     #             "reference_answer": ref_data["ground_truth"],
#     #             "llm_output": response,
#     #             "test_description": f"Core Summary: {input_data['question'][:30]}...",
#     #             "test_config": "Energy_Impact",
#     #         })
#     #         eval_id_counter += 1

#     # # --- Classification Data ---
#     # cls_cases = [
#     #     {"input": {"question": "This movie was an absolute masterpiece, truly unforgettable!"}, "ref": {"ground_truth": "positive"}},
#     #     {"input": {"question": "I found the experience to be rather dull and uninspiring."}, "ref": {"ground_truth": "negative"}},
#     #     {"input": {"question": "The service was acceptable, nothing special."}, "ref": {"ground_truth": "neutral"}},
#     # ]
#     # labels = ["positive", "negative", "neutral"]
#     # for i in range(num_samples_per_task * 2):
#     #     case = copy.deepcopy(cls_cases[i % len(cls_cases)])
#     #     input_data = case["input"]; ref_data = case["ref"]; true_label = ref_data["ground_truth"]
#     #     other_labels = [l for l in labels if l != true_label]
#     #     responses = {
#     #         MODEL_GOOD: true_label,
#     #         MODEL_PARTIAL: random.choice([true_label, random.choice(other_labels)]) if other_labels else true_label,
#     #         MODEL_POOR: random.choice(other_labels) if other_labels else true_label
#     #     }
#     #     if random.random() < 0.1: responses[MODEL_GOOD] = random.choice(other_labels) if other_labels else true_label

#     #     for model_name, response in responses.items():
#     #         all_data.append({
#     #             "id": f"cls_{eval_id_counter:03d}",
#     #             "test_description": f"Core Classification: {input_data['question'][:20]}... ({model_name})",
#     #             "task_type": CLASSIFICATION,
#     #             "model": model_name,
#     #             "query": input_data["question"],
#     #             "reference_answer": ref_data["ground_truth"],
#     #             "llm_output": response,
#     #             "test_config": "Sentiment_Analysis",
#     #         })
#     #         eval_id_counter += 1

#     # # --- Chatbot Data ---
#     # chat_cases = [
#     #     {"input": {"question": "Hello, how are you doing today?"}, "ref": {"ground_truth": "I'm doing well, thank you for asking! How can I assist you?"}},
#     #     {"input": {"question": "Can you explain the concept of artificial intelligence in simple terms?"}, "ref": {"ground_truth": "Certainly! AI is about creating smart computer systems that can perform tasks typically requiring human intelligence, like learning, problem-solving, and understanding language."}},
#     # ]
#     # for i in range(num_samples_per_task):
#     #     case = copy.deepcopy(chat_cases[i % len(chat_cases)])
#     #     input_data = case["input"]; ref_data = case["ref"]
#     #     responses = {
#     #         MODEL_GOOD: f"{ref_data['ground_truth'][:-15]} What can I do for you?",
#     #         MODEL_PARTIAL: "I am a chatbot. I can answer questions.",
#     #         MODEL_POOR: "The sky is blue. Did you know that dogs are mammals?"
#     #     }
#     #     for model_name, response in responses.items():
#     #         all_data.append({
#     #             "id": f"chat_{eval_id_counter:03d}",
#     #             "task_type": CHATBOT,
#     #             "model": model_name,
#     #             "query": input_data["question"],
#     #             "reference_answer": ref_data["ground_truth"],
#     #             "llm_output": response,
#     #             "test_description": f"Core Chatbot: {input_data['question'][:30]}...",
#     #             "test_config": "General_Conversation",
#     #         })
#     #         eval_id_counter += 1
            
#     # --- New HR Test Cases ---
#     hr_cases = [
#         {
#             "input": {"question": "What is the policy for annual leave accrual?"},
#             "ref": {
#                 "ground_truth": "Employees accrue 15 days of annual leave per year, with a maximum carry-over of 5 days to the next year. Leave is prorated for part-time staff.",
#                 "ref_facts": "15 days annual leave,5 days carry-over,prorated for part-time",
#                 "ref_key_points": "Annual leave,Accrual rate,Carry-over,Part-time policy"
#             }
#         },
#         {
#             "input": {"question": "How do I submit a reimbursement claim for business travel?"},
#             "ref": {
#                 "ground_truth": "Business travel reimbursement claims must be submitted via the HR portal within 30 days of travel, attaching all original receipts. Approval typically takes 5 business days.",
#                 "ref_facts": "submit via HR portal,within 30 days,attach original receipts,5 business days approval",
#                 "ref_key_points": "Reimbursement,Submission method,Deadline,Required documents,Approval time"
#             }
#         },
#         {
#             "input": {"question": "Can I work from home if I have a sick child?"},
#             "ref": {
#                 "ground_truth": "Our company policy allows for remote work in cases of dependent care. Please notify your manager and HR, and ensure your work can be completed remotely.",
#                 "ref_facts": "remote work allowed,dependent care,notify manager,notify HR",
#                 "ref_key_points": "Work from home,Dependent care,Notification process"
#             }
#         },
#     ]
#     for i in range(num_samples_per_task):
#         case = copy.deepcopy(hr_cases[i % len(hr_cases)])
#         input_data = case["input"]; ref_data = case["ref"]
#         responses = {
#             MODEL_GOOD: f"You accrue 15 days of annual leave per year, with 5 days carry-over. Part-time staff leave is prorated. This is our standard HR policy.",
#             MODEL_PARTIAL: "Annual leave information is available. Please consult the HR handbook for specifics.",
#             MODEL_POOR: "Taking time off is good for mental health. Remember to relax."
#         }
#         for model_name, response in responses.items():
#             all_data.append({
#                 "id": f"hr_{eval_id_counter:03d}",
#                 "task_type": RAG_FAQ,
#                 "model": model_name,
#                 "query": input_data["question"],
#                 "reference_answer": ref_data["ground_truth"],
#                 "llm_output": response,
#                 "test_description": f"HR Policy: {input_data['question'][:40]}...",
#                 "test_config": "HR_Policy_FAQ", # Specific and clear test_config
#             })
#             eval_id_counter += 1

#     # --- New Finance Test Cases ---
#     finance_cases = [
#         {
#             "input": {"question": "What is the current interest rate for a 30-year fixed mortgage?"},
#             "ref": {
#                 "ground_truth": "As of today, May 25, 2025, the interest rate for a 30-year fixed mortgage is approximately 6.85%. This rate is subject to change based on market conditions.",
#                 "ref_facts": "6.85% interest rate,30-year fixed mortgage,subject to change",
#                 "ref_key_points": "Mortgage,Interest rate,Term,Market conditions"
#             }
#         },
#         {
#             "input": {"question": "Explain the concept of compound interest."},
#             "ref": {
#                 "ground_truth": "Compound interest is the interest on a loan or deposit calculated based on both the initial principal and the accumulated interest from previous periods. It's 'interest on interest'.",
#                 "ref_facts": "interest on principal,interest on accumulated interest,interest on interest",
#                 "ref_key_points": "Compound interest,Definition,Calculation basis,Accumulation"
#             }
#         },
#         {
#             "input": {"question": "What are the requirements to open a new savings account?"},
#             "ref": {
#                 "ground_truth": "To open a new savings account, you need a valid government-issued ID, proof of address, and an initial deposit of at least $100. You must be 18 years or older.",
#                 "ref_facts": "valid ID,proof of address,min $100 deposit,18+ age",
#                 "ref_key_points": "Savings account,Requirements,ID,Deposit,Age"
#             }
#         },
#     ]
#     for i in range(num_samples_per_task):
#         case = copy.deepcopy(finance_cases[i % len(finance_cases)])
#         input_data = case["input"]; ref_data = case["ref"]
#         responses = {
#             MODEL_GOOD: f"The 30-year fixed mortgage rate is currently around 6.85% as of today. Please note, rates can change due to market conditions.",
#             MODEL_PARTIAL: "Mortgage rates are available on our website. They can fluctuate.",
#             MODEL_POOR: "Investing in stocks can be risky. Diversify your portfolio."
#         }
#         for model_name, response in responses.items():
#             all_data.append({
#                 "id": f"fin_{eval_id_counter:03d}",
#                 "task_type": RAG_FAQ,
#                 "model": model_name,
#                 "query": input_data["question"],
#                 "reference_answer": ref_data["ground_truth"],
#                 "llm_output": response,
#                 "test_description": f"Finance Product Info: {input_data['question'][:40]}...",
#                 "test_config": "Financial_Product_Info",
#             })
#             eval_id_counter += 1

#     # --- New Branch/Location Test Cases ---
#     branch_cases = [
#         {
#             "input": {"question": "What are the operating hours of the main branch in downtown Singapore?"},
#             "ref": {
#                 "ground_truth": "The main branch in downtown Singapore operates from 9:00 AM to 5:00 PM on weekdays (Monday-Friday) and is closed on weekends and public holidays.",
#                 "ref_facts": "9 AM to 5 PM,weekdays,closed weekends,closed public holidays",
#                 "ref_key_points": "Operating hours,Main branch,Location (Singapore),Days of week"
#             }
#         },
#         {
#             "input": {"question": "Is the Orchard Road branch open on Saturday?"},
#             "ref": {
#                 "ground_truth": "No, the Orchard Road branch is closed on Saturdays. It operates Monday to Friday from 9:30 AM to 6:00 PM.",
#                 "ref_facts": "Orchard Road branch closed Saturday,Mon-Fri 9:30 AM-6:00 PM",
#                 "ref_key_points": "Branch specific,Weekend hours,Weekday hours"
#             }
#         },
#         {
#             "input": {"question": "Where is the nearest ATM to my current location (10 Bayfront Avenue)?"},
#             "ref": {
#                 "ground_truth": "The nearest ATM to 10 Bayfront Avenue is located at Marina Bay Sands, Level 1, near the taxi stand. It is accessible 24/7.",
#                 "ref_facts": "Marina Bay Sands,Level 1,24/7 access",
#                 "ref_key_points": "ATM location,Accessibility,Specific address"
#             }
#         },
#     ]
#     for i in range(num_samples_per_task):
#         case = copy.deepcopy(branch_cases[i % len(branch_cases)])
#         input_data = case["input"]; ref_data = case["ref"]
#         responses = {
#             MODEL_GOOD: f"The main branch in downtown Singapore is open from 9 AM to 5 PM on weekdays. It's closed on weekends and public holidays.",
#             MODEL_PARTIAL: "Our branches have varying operating hours. Please check the branch locator on our website.",
#             MODEL_POOR: "Singapore has many beautiful places to visit, including Marina Bay."
#         }
#         for model_name, response in responses.items():
#             all_data.append({
#                 "id": f"brn_{eval_id_counter:03d}",
#                 "task_type": RAG_FAQ,
#                 "model": model_name,
#                 "query": input_data["question"],
#                 "reference_answer": ref_data["ground_truth"],
#                 "llm_output": response,
#                 "test_description": f"Branch/ATM Query: {input_data['question'][:40]}...",
#                 "test_config": "Branch_Operations_Info",
#             })
#             eval_id_counter += 1

#     return all_data


# def save_mock_data(data, output_dir="data", base_filename="llm_eval_mock_data_generated"):
#     output_dir_path = Path(output_dir)
#     output_dir_path.mkdir(parents=True, exist_ok=True)

#     json_path = output_dir_path / f"{base_filename}.json"
#     with open(json_path, 'w', encoding='utf-8') as f:
#         json.dump(data, f, indent=4, ensure_ascii=False)
#     print(f"Mock data generated and saved to {json_path}")

#     csv_path = output_dir_path / f"{base_filename}.csv"
#     try:
#         df = pd.DataFrame(data)
#         # Define column order to strictly match the required output columns
#         cols_order = ['id', 'task_type', 'model', 'query', 'llm_output', 'reference_answer', 'test_description', 'test_config']
        
#         # Filter DataFrame to only include these columns
#         df = df[cols_order]
#         df.fillna('', inplace=True)
#         df.to_csv(csv_path, index=False, encoding='utf-8')
#         print(f"Mock data also saved to {csv_path}")
#     except ImportError:
#         print("Pandas not installed, skipping CSV save.")
#     except Exception as e:
#         print(f"Error saving CSV: {e}")

# if __name__ == "__main__":
#     project_root = Path(__file__).resolve().parent.parent.parent
#     data_dir = project_root / "data"
#     mock_data = generate_mock_data_flat(num_samples_per_task=2) # Reduced samples for quicker testing
#     save_mock_data(mock_data, output_dir=data_dir, base_filename="llm_eval_mock_data_generated")
