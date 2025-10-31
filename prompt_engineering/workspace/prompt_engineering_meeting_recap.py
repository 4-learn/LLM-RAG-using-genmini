import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# 1️⃣ 讀取 .env 取得 GEMINI_API_KEY
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("❌ 找不到 GEMINI_API_KEY，請確認 .env 檔是否存在且內容正確。")

# 2️⃣ 設定 Gemini API key
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

# 3️⃣ 讓使用者輸入會議逐字稿
transcript = input("請輸入會議逐字稿內容：\n")

# 4️⃣ 設計提示工程 (Prompt)
prompt = f"""
你是一位會議助理，請根據以下逐字稿內容，
自動整理出會議摘要，並以 JSON 格式回覆，包含下列欄位：
- meet_topic：會議主題
- meeting_participants：與會者
- recap：會議摘要

請直接輸出純 JSON，不要加上任何文字、註解或程式碼標記。

逐字稿如下：
{transcript}
"""

# 5️⃣ 呼叫 Gemini 模型
response = model.generate_content(prompt)

# 6️⃣ 嘗試解析 LLM 的輸出
try:
    # 部分模型會意外加上 ```json ... ``` 包裝，可清理
    raw_text = response.text.strip()
    cleaned = raw_text.replace("```json", "").replace("```", "").strip()
    output_data = json.loads(cleaned)

    # 寫入 output.json
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print("✅ 已成功產生 output.json：")
    print(json.dumps(output_data, ensure_ascii=False, indent=2))

except json.JSONDecodeError:
    print("⚠️ 模型輸出不是有效 JSON，請檢查輸出內容：")
    print(response.text)
