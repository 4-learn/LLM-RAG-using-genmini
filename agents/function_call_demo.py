# function_call_demo.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ---- 業務邏輯（最小記憶：程式生命週期內有效）----
pet_name_store = {"name": None}

def save_pet_info(name: str):
    pet_name_store["name"] = name
    print(f"🐾 [save_pet_info] 已記錄：{name}")
    return {"status": "ok", "message": f"已記錄下小狗的名字：{name}"}

def get_pet_name():
    name = pet_name_store["name"]
    print(f"📦 [get_pet_name] 目前記錄：{name}")
    if name:
        return {"status": "ok", "name": name}
    else:
        return {"status": "empty", "message": "尚未登記狗狗名字"}

# ---- 工具宣告----
tools = [
    {
        "function_declarations": [
            {
                "name": "save_pet_info",
                "description": "儲存使用者的狗狗名字",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "狗狗的名字"}
                    },
                    "required": ["name"]
                },
            },
            {
                "name": "get_pet_name",
                "description": "取得已記錄的狗狗名字",
                "parameters": {"type": "object", "properties": {}},  # 無參數
            },
        ]
    }
]

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    tools=tools,
)

# 用 chat session，較好處理多輪 & 工具回填
chat = model.start_chat(history=[])

def maybe_call_tools_and_respond(resp):
    """
    如果模型提出 function_call，就呼叫對應函式，
    之後用 role='tool' + function_response 回回去，再拿最終回覆。
    """
    # 可能有多個 part；逐一檢查
    for part in resp.candidates[0].content.parts:
        if getattr(part, "function_call", None):
            fc = part.function_call
            fname = fc.name
            fargs = dict(fc.args) if fc.args else {}
            print(f"🤖 模型決定呼叫函式：{fname}({fargs})")

            # 執行本地函式
            if fname == "save_pet_info":
                result = save_pet_info(fargs.get("name", ""))
            elif fname == "get_pet_name":
                result = get_pet_name()
            else:
                result = {"status": "error", "message": f"未知函式：{fname}"}

            # 正確的「工具回填」格式（重點）：
            tool_msg = {
                "role": "tool",
                "parts": [
                    {
                        "function_response": {
                            "name": fname,
                            "response": result,
                        }
                    }
                ]
            }

            # 把工具結果回送給模型，取得最終文字回覆
            follow_up = chat.send_message(tool_msg)
            print("🤖 最終回覆：", follow_up.text)
            return

    # 沒有 function_call 就當一般對話
    print("💬 一般對話：", resp.text)

if __name__ == "__main__":
    tests = [
        "哈囉",                 # 一般對話
        "我家的狗，叫做小美",   # 會觸發 save_pet_info(name="小美")
        "你家的狗叫什麼名字？", # 會觸發 get_pet_name()
    ]
    for t in tests:
        print(f"\n🧑 使用者說：{t}")
        resp = chat.send_message(t)
        maybe_call_tools_and_respond(resp)
