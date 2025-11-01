# ontology_agent.py
import os
import yaml
import google.generativeai as genai
from dotenv import load_dotenv

# --- 初始化 ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = genai.GenerativeModel("gemini-2.5-flash")
ONTOLOGY_PATH = "ontology.yaml"

# --- 載入 ontology ---
def load_ontology():
    with open(ONTOLOGY_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# --- 查詢 ontology（第二層）---
def query_ontology(plate):
    ontology = load_ontology()
    vehicles = ontology.get("vehicles", {})
    if plate not in vehicles:
        return {"found": False, "facts": [f"Vehicle {plate} not found in ontology."]}
    
    vehicle = vehicles[plate]
    facts = [
        f"({plate}, license_status, {vehicle['license_status']})",
        f"({plate}, type, {vehicle['type']})"
    ]
    return {"found": True, "facts": facts}

# --- LLM 推理（第三層）---
SYSTEM_PROMPT = """
You are a traffic assistant agent.
You will receive ontology facts in YAML form and a user question.
Reason about the ontology and rules, then answer naturally in Chinese.
"""

def llm_reason(question, facts):
    facts_text = "\n".join(facts)
    prompt = f"{SYSTEM_PROMPT}\nOntology facts:\n{facts_text}\n\nUser question: {question}"
    resp = MODEL.generate_content(prompt)
    return resp.text.strip()

