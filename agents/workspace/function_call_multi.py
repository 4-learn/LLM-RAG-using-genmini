# function_call_light_demo.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

# 載入 API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ---- 業務邏輯（最小記憶：程式生命週期內有效）----
light_state = {"status": "off"}

def turn_on_light():
    light_state["status"] = "on"
    print("💡 [turn_on_light] 燈已開啟")
    return {"status": "ok", "message": "燈已經打開囉，現在亮起來了！"}

def turn_off_light():
    light_state["status"] = "off"
    print("🌙 [turn_off_light] 燈已關閉")
    return {"status": "ok", "message": "燈已經關掉囉，晚安～"}

# ---- 工具宣告 ----
tools = [
    {
        "function_declarations": [
            {
                "name": "turn_on_light",
                "description": "打開燈光，讓房間變亮。",
                "parameters": {"type": "object", "properties": {}},  # 無參數
            },
            {
                "name": "turn_off_light",
                "description": "關閉燈光，讓房間變暗。",
                "parameters": {"type": "object", "properties": {}},  # 無參數
            },
        ]
    }
]

# ---- 建立模型 ----
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    tools=tools,
)

# 使用 chat session（支援多輪 + 工具回填）
chat = model.start_chat(history=[])

# ---- 工具呼叫處理 ----
def maybe_call_tools_and_respond(resp):
    for part in resp.candidates[0].content.parts:
        if getattr(part, "function_call", None):
            fc = part.function_call
            fname = fc.name
            print(f"🤖 模型決定呼叫函式：{fname}()")

            # 執行對應函式
            if fname == "turn_on_light":
                result = turn_on_light()
            elif fname == "turn_off_light":
                result = turn_off_light()
            else:
                result = {"status": "error", "message": f"未知函式：{fname}"}

            # 工具回填
            tool_msg = {
                "role": "tool",
                "parts": [
                    {
                        "function_response": {
                            "name": fname,
                            "response": result,
                        }
                    }
                ],
            }

            # 回傳工具結果給模型，取得最終回答
            follow_up = chat.send_message(tool_msg)
            print("🤖 最終回覆：", follow_up.text)
            return

    # 沒有 function_call，就當一般聊天
    print("💬 一般對話：", resp.text)

# ---- 主程式 ----
if __name__ == "__main__":
    print("🕹️ 模擬智慧燈光控制（輸入 'exit' 結束）\n")
    while True:
        user_input = input("🧑 你說：")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("👋 結束對話，再見～")
            break

        resp = chat.send_message(user_input)
        maybe_call_tools_and_respond(resp)
