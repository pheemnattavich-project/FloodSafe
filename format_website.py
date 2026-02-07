from playwright.sync_api import sync_playwright
import time
import re

URL = "https://www.thaiwater.net/water/wl"

def click_next(page):
    next_btn = page.locator("button[aria-label='Next Page']")

    if next_btn.count() == 0:
        return False

    if next_btn.get_attribute("disabled") is not None:
        return False

    page.evaluate("""
        () => {
            document.querySelector("button[aria-label='Next Page']").click();
        }
    """)

    return True

def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)

        # รอ table แรก
        page.wait_for_selector("tr.MuiTableRow-root", timeout=60000)

        all_stations = []
        page_no = 1

        while True:
            print(f"\n=== PAGE {page_no} ===")

            rows = page.locator("tr.MuiTableRow-root")
            row_count = rows.count()
            print("ROWS FOUND:", row_count)
            print("=" * 60)

            for i in range(row_count):
                try:
                    row = rows.nth(i)
                    tds = row.locator("td")
                    th = row.locator("th")

                    station_name = clean_text(
                        th.locator("button").first.inner_text()
                    )

                    river = clean_text(tds.nth(0).inner_text())
                    location = clean_text(tds.nth(1).inner_text())
                    water_level = clean_text(tds.nth(2).inner_text())
                    bank_level = clean_text(tds.nth(3).inner_text())

                    status_box = tds.nth(4).locator("div.MuiBox-root").first
                    status = clean_text(status_box.inner_text())

                    trend = "UNKNOWN"
                    trend_btns = tds.nth(6).locator("button")
                    if trend_btns.count() > 0:
                        title = trend_btns.first.get_attribute("title") or ""
                        if "เพิ่มขึ้น" in title:
                            trend = "UP"
                        elif "ลดลง" in title:
                            trend = "DOWN"
                        elif "ทรงตัว" in title:
                            trend = "STABLE"

                    update_time = clean_text(tds.nth(7).inner_text())

                    data = {
                        "station_name": station_name,
                        "river": river,
                        "location": location,
                        "water_level": water_level,
                        "bank_level": bank_level,
                        "status": status,
                        "trend": trend,
                        "update_time": update_time,
                    }

                    print(data)
                    all_stations.append(data)

                except Exception as e:
                    print(f"⚠️ skip row {i}: {e}")

            # ---------- NEXT PAGE ----------
            next_btn = page.locator("button[aria-label='Next Page']")

            if next_btn.count() == 0:
                print("\n❌ Next button not found")
                break

            if next_btn.is_disabled():
                print("\n✅ LAST PAGE REACHED")
                break

            print("➡ CLICK NEXT PAGE")

            # capture first row HTML
            first_row_html = page.locator("tr.MuiTableRow-root").first.inner_html()

            # JS click (bypass MUI overlay)
            page.evaluate("""
            () => {
                const btn = document.querySelector("button[aria-label='Next Page']");
                if (btn && !btn.disabled) btn.click();
            }
            """)

            # wait until table content changes
            page.wait_for_function(
                """
                (oldHTML) => {
                    const row = document.querySelector("tr.MuiTableRow-root");
                    return row && row.innerHTML !== oldHTML;
                }
                """,
                arg=first_row_html,
                timeout=60000
            )

            page_no += 1



        all_stations.append(data)
        print(f"\nTOTAL STATIONS COLLECTED: {len(all_stations)}")
        browser.close()


if __name__ == "__main__":
    main()
