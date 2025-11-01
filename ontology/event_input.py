# event_input.py
import yaml

ONTOLOGY_PATH = "ontology.yaml"

# --- 讀取 ontology ---
def load_ontology():
    with open(ONTOLOGY_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# --- 儲存 ontology ---
def save_ontology(data):
    with open(ONTOLOGY_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)

# --- 新增車輛 ---
def add_vehicle(plate_number, vehicle_type, license_status="valid"):
    ontology = load_ontology()
    if plate_number in ontology["vehicles"]:
        print(f"⚠️ 車牌 {plate_number} 已存在。")
        return
    ontology["vehicles"][plate_number] = {
        "type": vehicle_type,             # ✅ 改成 type
        "license_status": license_status
    }
    save_ontology(ontology)
    print(f"✅ 已新增車輛 {plate_number}。")

# --- 更新牌照狀態 ---
def update_license(plate_number, new_status):
    ontology = load_ontology()
    if plate_number not in ontology["vehicles"]:
        print(f"❌ 找不到車牌 {plate_number}。")
        return
    ontology["vehicles"][plate_number]["license_status"] = new_status
    save_ontology(ontology)
    print(f"🔄 已將 {plate_number} 狀態更新為：{new_status}")

# --- 主程式互動 ---
if __name__ == "__main__":
    print("🚗 Ontology Event Input 模擬器")
    print("選擇操作：1. 新增車輛  2. 更新牌照狀態")
    choice = input("請輸入 1 或 2：")

    if choice == "1":
        plate = input("輸入車牌號碼：")
        vehicle_type = input("輸入車輛類型（如 car/motorcycle/truck）：")
        status = input("輸入牌照狀態 (valid/expired)：")
        add_vehicle(plate, vehicle_type, status)
    elif choice == "2":
        plate = input("輸入車牌號碼：")
        status = input("輸入新狀態 (valid/expired)：")
        update_license(plate, status)
    else:
        print("❌ 無效選項。")
