from playwright.sync_api import sync_playwright

URL = "https://www.thaiwater.net/water/wl"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, timeout=60000)

    # wait until JS renders something meaningful
    page.wait_for_timeout(5000)

    # dump page length to confirm JS ran
    html = page.content()
    print("HTML LENGTH AFTER JS:", len(html))

    # try grabbing any visible text
    rows = page.locator("text=สถานี")
    print("FOUND 'สถานี' TEXT COUNT:", rows.count())

    # print first chunk of visible text
    print("\n=== PAGE TEXT SAMPLE ===")
    print(page.inner_text("body")[:1000])

    browser.close()
