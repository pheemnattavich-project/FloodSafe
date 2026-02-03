print("SCRIPT STARTED")

from playwright.sync_api import sync_playwright
print("PLAYWRIGHT IMPORTED")

with sync_playwright() as p:
    print("PLAYWRIGHT CONTEXT OK")
    browser = p.chromium.launch(headless=False)
    print("BROWSER LAUNCHED")

    page = browser.new_page()
    page.goto("https://example.com")
    print("PAGE LOADED")

    print("TITLE:", page.title())

    browser.close()

print("SCRIPT FINISHED")
