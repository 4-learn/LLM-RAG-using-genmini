# agent_conversion.py
import os
import re
from dotenv import load_dotenv
import google.generativeai as genai
from conversion import check_violation, list_all

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

SYSTEM_PROMPT = """
你是一個交通助理 Agent。
任務：幫助判斷使用者是否在詢問「車輛違規狀況」。
請以 JSON 回答：
{
  "intent": "violation" 或 "other",
  "plate": "車牌號碼（若有）"
}
例子：
- 問題：「ABC123 違規了嗎？」 → {"intent": "violation", "plate": "ABC123"}
- 問題：「XYZ789 壞壞？」 → {"intent": "violation", "plate": "XYZ789"}
- 問題：「你好嗎？」 → {"intent": "other", "plate": ""}
"""

def parse_intent(user_input: str):
    """呼叫 Gemini，解析語意意圖"""
    try:
        resp = model.generate_content(f"{SYSTEM_PROMPT}\n使用者問題：{user_input}")
        text = resp.text.strip()
        # 嘗試從回答中抓 JSON 區塊
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            import json
            data = json.loads(match.group(0))
            return data
        else:
            return {"intent": "other", "plate": ""}
    except Exception as e:
        print("⚠️ LLM 解析錯誤：", e)
        return {"intent": "other", "plate": ""}

if __name__ == "__main__":
    print("🤖 交通語意助理啟動！")
    list_all()

    while True:
        q = input("\n請輸入問題（例如『XYZ789 壞壞？』或輸入 exit 離開）：").strip()
        if q.lower() in ["exit", "quit"]:
            print("👋 再見！")
            break

        intent_data = parse_intent(q)
        intent = intent_data.get("intent")
        plate = intent_data.get("plate")

        if intent == "violation" and plate:
            print(f"🎯 解析到車牌：{plate}")
            answer = check_violation(plate)
            print(f"🤖 {answer}")
        else:
            print("💬 我想你不是在問交通問題喔 😄")

