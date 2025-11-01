# query_home_theater.py
import yaml

STATE_FILE = "home_theater.yaml"

def query_device(device=None):
    """查詢家庭劇院設備狀態"""
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    devices = data["home_theater"]

    if not device:
        print("🎬 家庭劇院目前狀態：")
        for k, v in devices.items():
            print(f"  - {k}：{v}")
    else:
        info = devices.get(device)
        if info:
            print(f"🔍 {device} 狀態：{info}")
        else:
            print(f"⚠️ 查無 {device} 這個設備。")

if __name__ == "__main__":
    print("📊 查詢家庭劇院設備狀態")
    print("可輸入：light / air_conditioner / speaker / all")
    print("輸入 exit 離開查詢模式。")

    while True:
        q = input("\n請輸入想查詢的設備名稱：").strip().lower()
        if q in ["exit", "quit"]:
            print("👋 離開查詢模式。")
            break
        if q == "all":
            query_device()
        else:
            query_device(q)
