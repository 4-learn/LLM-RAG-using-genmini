# agent_home_theater.py
import os
import yaml
from dotenv import load_dotenv
import google.generativeai as genai

# === 載入 API Key ===
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# === 初始化 YAML 狀態檔 ===
STATE_FILE = "home_theater.yaml"
if not os.path.exists(STATE_FILE):
    default_state = {
        "home_theater": {
            "light": {"status": "on", "brightness": 75},
            "air_conditioner": {"mode": "cool", "temperature": 24},
            "speaker": {"volume": 65}
        }
    }
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(default_state, f, allow_unicode=True)

# === FSM 狀態 ===
STATE = "DISCUSSING"  # 可為：DISCUSSING（討論中）/ UPDATING（更新中）/ QUERYING（查詢中）

# === 功能函式 ===
def update_yaml(device, field, value):
    """更新 YAML 狀態"""
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    data["home_theater"][device][field] = value
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True)
    return f"✅ 已更新 {device}.{field} → {value}"

def read_yaml(device):
    """讀取指定設備狀態"""
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["home_theater"].get(device, {})

# === 初始化 LLM 模型 ===
model = genai.GenerativeModel("gemini-2.5-flash")

# 系統提示：定義 LLM 的語意空間
SYSTEM_PROMPT = """
你是一個智慧家庭助理，負責管理「家庭劇院」中的三種設備：
- 燈光（light）：具有開關狀態(status: on/off)與亮度(brightness: 0–100)
- 冷氣（air_conditioner）：具有模式(mode: cool/heat/off)與溫度(temperature: °C)
- 音響（speaker）：具有音量(volume: 0–100)

請只以 JSON 回答：
{
  "intent": "update" | "query" | "other",
  "device": "light" | "air_conditioner" | "speaker",
  "field": "status" | "brightness" | "mode" | "temperature" | "volume",
  "value": "字串或數值 (若為更新)",
  "comment": "自然語言簡短說明"
}
"""

def parse_intent(user_input):
    """呼叫 LLM 解析使用者語意意圖"""
    try:
        resp = model.generate_content(f"{SYSTEM_PROMPT}\n使用者：{user_input}")
        import re, json
        match = re.search(r"\{.*\}", resp.text, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
            return data
    except Exception as e:
        print("⚠️ 語意解析錯誤：", e)
    return {"intent": "other"}

# === 主程式流程 ===
if __name__ == "__main__":
    print("🤖 智慧家庭助理啟動！")
    print("💡 範例指令：『關掉燈光』、『把冷氣調到 26 度』、『音響音量多少？』")
    print("輸入 exit 可離開系統。")

    while True:
        q = input("\n🧑 使用者：").strip()
        if q.lower() in ["exit", "quit"]:
            print("👋 再見！")
            break

        intent_data = parse_intent(q)
        intent = intent_data.get("intent", "other")

        # === 更新模式 ===
        if intent == "update":
            STATE = "UPDATING"
            device = intent_data.get("device")
            field = intent_data.get("field")
            value = intent_data.get("value")
            print(update_yaml(device, field, value))
            print("🤖", intent_data.get("comment", "已完成更新。"))

        # === 查詢模式 ===
        elif intent == "query":
            STATE = "QUERYING"
            device = intent_data.get("device")
            state = read_yaml(device)
            print(f"📊 {device} 目前狀態：", state)
            print("🤖", intent_data.get("comment", "這是目前的設定狀態。"))

        # === 討論模式 ===
        else:
            STATE = "DISCUSSING"
            print("💬", intent_data.get("comment", "我們繼續聊家庭劇院的設定吧～"))

        print(f"🔄 [FSM 狀態] {STATE}")
