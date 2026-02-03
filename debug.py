print("DEBUG STARTED")

import requests
from bs4 import BeautifulSoup

print("IMPORTS OK")

URL = "https://www.thaiwater.net/water/wl"

try:
    print("SENDING REQUEST...")
    resp = requests.get(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=10
    )
    print("STATUS CODE:", resp.status_code)

    html = resp.text
    print("HTML LENGTH:", len(html))

    soup = BeautifulSoup(html, "html.parser")
    print("TITLE:", soup.title.string if soup.title else "NO TITLE")

    print("TR COUNT:", len(soup.find_all("tr")))

except Exception as e:
    print("ERROR OCCURRED:")
    print(type(e).__name__, e)

print("DEBUG FINISHED")
