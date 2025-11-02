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

# --- 新增車輛（含車主） ---
def add_vehicle(plate_number, vehicle_type, license_status="valid", owner="Unknown"):
    ontology = load_ontology()

    if plate_number in ontology["vehicles"]:
        print(f"⚠️ 車牌 {plate_number} 已存在。")
        return

    ontology["vehicles"][plate_number] = {
        "type": vehicle_type,
        "license_status": license_status,
        "owner": owner
    }

    save_ontology(ontology)
    print(f"✅ 已新增車輛 {plate_number}（{vehicle_type}，狀態：{license_status}，車主：{owner}）。")

# --- 更新牌照狀態 ---
def update_license(plate_number, new_status):
    ontology = load_ontology()

    if plate_number not in ontology["vehicles"]:
        print(f"❌ 找不到車牌 {plate_number}。")
        return

    ontology["vehicles"][plate_number]["license_status"] = new_status
    save_ontology(ontology)
    print(f"🔄 已將 {plate_number} 狀態更新為：{new_status}")

# --- 新增或更新車主（非必要） ---
def add_owner(owner_name):
    ontology = load_ontology()

    # 這裡只是示範，可擴充 owner-specific metadata
    if "owners" not in ontology:
        ontology["owners"] = {}

    if owner_name in ontology["owners"]:
        print(f"⚠️ 車主 {owner_name} 已存在。")
        return

    ontology["owners"][owner_name] = {"note": "new owner added"}
    save_ontology(ontology)
    print(f"✅ 已新增車主：{owner_name}")

# --- 主程式互動 ---
if __name__ == "__main__":
    print("🚗 Ontology Event Input 模擬器（Level-2 版）")
    print("選擇操作：")
    print("1️⃣ 新增車輛")
    print("2️⃣ 更新車牌狀態")
    print("3️⃣ 新增車主")
    choice = input("請輸入 1 / 2 / 3：").strip()

    if choice == "1":
        plate = input("輸入車牌號碼：").strip()
        vehicle_type = input("輸入車輛類型（如 car/motorcycle/truck）：").strip()
        owner = input("輸入車主姓名：").strip()
        status = input("輸入牌照狀態 (valid/expired)：").strip()
        add_vehicle(plate, vehicle_type, status, owner)
    elif choice == "2":
        plate = input("輸入車牌號碼：").strip()
        status = input("輸入新狀態 (valid/expired)：").strip()
        update_license(plate, status)
    elif choice == "3":
        owner = input("輸入車主姓名：").strip()
        add_owner(owner)
    else:
        print("❌ 無效選項。")

