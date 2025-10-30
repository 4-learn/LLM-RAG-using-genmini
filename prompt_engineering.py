import os
from dotenv import load_dotenv
import google.generativeai as genai

# 讀取 .env 檔
load_dotenv()

# 從環境變數取得 API key
api_key = os.getenv("GEMINI_API_KEY")

# 檢查 key 是否存在
if not api_key:
    raise ValueError("❌ 找不到 GEMINI_API_KEY，請確認 .env 檔是否存在並有內容。")

# 設定 Gemini API key
genai.configure(api_key=api_key)

# 初始化模型
model = genai.GenerativeModel("gemini-2.5-flash")

# 發送 prompt
content = "本次會議的重點如下： \n \
*   **市場策略研討：** 針對新產品的市場策略進行了深入討論。 \n \
*   **預算分配確認：** 正式確認了下個季度的預算分配方案。 \n \
*   **團隊建設規劃：** 規劃並確定了團隊建設活動的時間與地點。 "
response = model.generate_content("你是一個會議側寫員，請幫我總結這次會議的重點，格式為 JSON。會議內容如下：\n" + content)

# 輸出結果
print("🤖 Gemini 回覆：", response.text)