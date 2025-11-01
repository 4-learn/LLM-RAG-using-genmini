# conversion.py
import yaml

ONTOLOGY_PATH = "ontology.yaml"

# --- 載入 ontology ---
def load_ontology():
    with open(ONTOLOGY_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# --- 根據規則檢查車輛是否違規 ---
def check_violation(plate_number):
    ontology = load_ontology()

    if plate_number not in ontology["vehicles"]:
        return f"❌ 找不到車牌 {plate_number}。"

    vehicle = ontology["vehicles"][plate_number]
    rule = ontology["rules"]["expired_license"]

    # 簡單規則判斷
    if vehicle["license_status"] == "expired":
        return f"🚨 車牌 {plate_number} 的牌照已過期，屬於違規車輛。"
    else:
        return f"✅ 車牌 {plate_number} 牌照有效，沒有違規。"

# --- 顯示所有車輛狀態 ---
def list_all():
    ontology = load_ontology()
    print("🚗 車輛列表：")
    for plate, info in ontology["vehicles"].items():
        print(f" - {plate}: {info['license_status']}")

# --- 主互動 ---
if __name__ == "__main__":
    print("🧠 Ontology 問答系統")
    list_all()

    while True:
        q = input("\n請輸入問題（例如『ABC123 違規了嗎？』或輸入 exit 離開）：").strip()
        if q.lower() in ["exit", "quit"]:
            print("👋 再見！")
            break

        # 取出車牌（簡單做法：取英文 + 數字）
        import re
        match = re.search(r"[A-Z0-9]{3,}", q)
        if not match:
            print("⚠️ 請輸入有效的車牌號碼（如 ABC123）")
            continue

        plate = match.group(0)
        answer = check_violation(plate)
        print(answer)

