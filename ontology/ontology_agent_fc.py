import os
import yaml
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import Tool, FunctionDeclaration

# --- 初始化 ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

ONTOLOGY_PATH = "ontology.yaml"

# --- 查 ontology ---
def load_ontology():
    with open(ONTOLOGY_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def query_ontology(plate: str):
    """查詢 ontology.yaml 中的車輛資料"""
    ontology = load_ontology()
    vehicles = ontology.get("vehicles", {})
    if plate not in vehicles:
        return {"found": False, "facts": [f"Vehicle {plate} not found in ontology."]}
    v = vehicles[plate]
    facts = [f"({plate}, license_status, {v.get('license_status', 'unknown')})"]
    if "type" in v:
        facts.append(f"({plate}, type, {v['type']})")
    return {"found": True, "facts": facts}


# ✅ 正確的 Tool 宣告方式（完全相容現行 SDK）
query_ontology_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="query_ontology",
            description="詢問車輛是否違規",#"查詢 ontology.yaml 中的車輛資料。",
            parameters={
                "type": "object",
                "properties": {
                    "plate": {
                        "type": "string",
                        "description": "車牌號碼，例如 ABC123"
                    }
                },
                "required": ["plate"]
            },
        )
    ]
)

# --- 建立模型 ---
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    tools=[query_ontology_tool]  # ✅ 工具要是 Tool 物件，不是字串
)

SYSTEM_PROMPT = """
你是一個交通助理 Agent。
當使用者詢問車輛是否違規時，請呼叫 query_ontology() 查詢資料，
再根據 ontology facts 回答中文結果。
"""

def chat_with_llm(question: str):
    """Gemini Function Calling"""
    chat = model.start_chat(history=[])

    response = chat.send_message(f"{SYSTEM_PROMPT}\n使用者問題：{question}")

    # 檢查是否有 function_call
    for part in response.candidates[0].content.parts:
        fn_call = part.function_call
        fn_name = fn_call.name or "unknown_function"
        fn_args = fn_call.args or {}
        print(f"🔧 呼叫函式：{fn_name}({fn_args})")

        # 呼叫本地函式
        if fn_name == "query_ontology" and "plate" in fn_args:
            result = query_ontology(fn_args["plate"])
            response = chat.send_message({
                "function_response": {
                    "name": fn_name,
                    "response": result
                }
            })

    # 回傳最終回答
    try:
        return response.text.strip()
    except Exception:
        text_parts = [p.text for p in response.candidates[0].content.parts if hasattr(p, "text")]
        return "\n".join(text_parts) if text_parts else "⚠️ 沒有文字回覆。"

