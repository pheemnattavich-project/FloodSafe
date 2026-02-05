from playwright.sync_api import sync_playwright
import time
import re

URL = "https://www.thaiwater.net/water/wl"

def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)

        page.wait_for_timeout(5000)

        stations = []
        page_index = 1

        while True:
            if page.is_closed():
                print("PAGE CLOSED → STOP")
                break

            print(f"\n=== PAGE {page_index} ===")

            # force render rows
            try:
                for _ in range(10):
                    page.mouse.wheel(0, 2000)
                    page.wait_for_timeout(300)
            except:
                print("SCROLL FAILED → STOP")
                break

            page.wait_for_selector("tr.MuiTableRow-root")

            rows = page.locator("tr.MuiTableRow-root")
            row_count = rows.count()

            print(f"ROWS FOUND: {row_count}")
            print("=" * 60)

            for i in range(row_count):
                row = rows.nth(i)
                tds = row.locator("td")

                if tds.count() < 9:
                    continue

                try:
                    station_name = normalize_text(
                        row.locator("span.MuiButton-label").inner_text()
                    )
                except:
                    continue

                river = normalize_text(tds.nth(1).inner_text())
                location = normalize_text(tds.nth(2).inner_text())
                water_level = normalize_text(tds.nth(3).inner_text())

                status = normalize_text(
                    tds.nth(5).locator("div.MuiBox-root").last.inner_text()
                )

                trend = "UNKNOWN"
                trend_btn = tds.nth(7).locator("button")

                if trend_btn.count() > 0:
                    title = trend_btn.first.get_attribute("title") or ""
                    if "เพิ่มขึ้น" in title:
                        trend = "UP"
                    elif "ลดลง" in title:
                        trend = "DOWN"
                    elif "ทรงตัว" in title:
                        trend = "STABLE"

                update_time = normalize_text(tds.nth(8).inner_text())

                station = {
                    "station_name": station_name,
                    "river": river,
                    "location": location,
                    "water_level": water_level,
                    "status": status,
                    "trend": trend,
                    "update_time": update_time
                }

                stations.append(station)
                print(station)

            # =========================
            # NEXT BUTTON (SAFE CHECK)
            # =========================
            next_btn = page.locator(
                "button:has(svg path[d*='16.59L13.17'])"
            )

            if next_btn.count() == 0:
                print("NO NEXT BUTTON → FINISHED")
                break

            if next_btn.is_disabled():
                print("NEXT BUTTON DISABLED → FINISHED")
                break

            print("CLICK NEXT → loading next page")
            next_btn.click()
            page.wait_for_timeout(2500)

            page_index += 1

        print("\n" + "=" * 60)
        print(f"TOTAL PARSED STATIONS: {len(stations)}")

        browser.close()

if __name__ == "__main__":
    main()
