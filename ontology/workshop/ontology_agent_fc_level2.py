import os
import yaml
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import Tool, FunctionDeclaration

# --- 初始化 ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

ONTOLOGY_PATH = "ontology.yaml"

# --- 輔助函式：讀 ontology ---
def load_ontology():
    with open(ONTOLOGY_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# --- 查單車輛 ---
def query_ontology(plate: str):
    ontology = load_ontology()
    vehicles = ontology.get("vehicles", {})
    if plate not in vehicles:
        return {"found": False, "facts": [f"Vehicle {plate} not found."]}
    v = vehicles[plate]
    facts = [
        f"({plate}, license_status, {v.get('license_status', 'unknown')})",
        f"({plate}, type, {v.get('type', 'unknown')})",
        f"({plate}, owner, {v.get('owner', 'unknown')})",
    ]
    return {"found": True, "facts": facts}

# --- 查詢某車主的所有車 ---
def query_owner(owner: str):
    ontology = load_ontology()
    vehicles = ontology.get("vehicles", {})
    owned = [
        (p, v["license_status"]) for p, v in vehicles.items() if v.get("owner") == owner
    ]
    return {"found": bool(owned), "vehicles": owned}

# --- 定義 Tool ---
tools = [
    Tool(function_declarations=[
        FunctionDeclaration(
            name="query_ontology",
            description="查詢單一車輛的 ontology facts。",
            parameters={
                "type": "object",
                "properties": {
                    "plate": {"type": "string", "description": "車牌號碼，如 ABC123"}
                },
                "required": ["plate"]
            }
        ),
        FunctionDeclaration(
            name="query_owner",
            description="查詢某位車主擁有哪些車輛與狀態。",
            parameters={
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "車主姓名"}
                },
                "required": ["owner"]
            }
        )
    ])
]

# --- 建立模型 ---
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    tools=tools
)

SYSTEM_PROMPT = """
你是一個交通助理 Agent。
你可以呼叫 query_ontology() 或 query_owner() 來查詢 ontology.yaml。
規則：
1. 若 license_status == "expired" → 該車輛違規。
2. 若同一車主有兩台以上 expired 車 → 該車主為高風險。
請以中文回答。
"""

def chat_with_llm(question: str):
    chat = model.start_chat(history=[])
    response = chat.send_message(f"{SYSTEM_PROMPT}\n使用者問題：{question}")

    for part in response.candidates[0].content.parts:
        fn_call = getattr(part, "function_call", None)
        if not fn_call:
            continue

        fn_name = fn_call.name or "unknown"
        fn_args = fn_call.args or {}
        print(f"🔧 呼叫函式：{fn_name}({fn_args})")

        # 執行本地函式
        if fn_name == "query_ontology" and "plate" in fn_args:
            result = query_ontology(fn_args["plate"])
        elif fn_name == "query_owner" and "owner" in fn_args:
            result = query_owner(fn_args["owner"])
        else:
            result = {"error": "Unknown function or missing args."}

        # 回傳給 LLM
        response = chat.send_message({
            "function_response": {"name": fn_name, "response": result}
        })

    try:
        return response.text.strip()
    except Exception:
        parts = [p.text for p in response.candidates[0].content.parts if hasattr(p, "text")]
        return "\n".join(parts) if parts else "⚠️ 無文字回覆。"

