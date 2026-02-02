import requests

API_URL = "https://www.thaiwater.net/json/telestation/list.json"

def scrape_thaiwater():
    resp = requests.get(API_URL, timeout=20)
    resp.raise_for_status()

    json_data = resp.json()

    # ✅ โครงสร้างจริงของ ThaiWater
    if "data" not in json_data:
        raise ValueError("ไม่พบ key 'data' ใน JSON")

    stations = json_data["data"]

    if not isinstance(stations, list):
        raise ValueError("'data' ไม่ใช่ list")

    results = []

    for d in stations:
        if not isinstance(d, dict):
            continue

        results.append({
            "station_name": d.get("station_name"),
            "province": d.get("province"),
            "amphoe": d.get("amphoe"),
            "tambon": d.get("tambon"),
            "water_level": d.get("wl"),
            "status": d.get("wl_status"),
            "datetime": d.get("datetime")
        })

    return results


if __name__ == "__main__":
    data = scrape_thaiwater()
    print(f"✅ ดึงข้อมูลได้ {len(data)} สถานี")
    for d in data[:5]:
        print(d)
