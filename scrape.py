import requests
from bs4 import BeautifulSoup
from typing import List


# ==============================
# Config
# ==============================
THAIWATER_URL = "https://www.thaiwater.net/water/wl"


# ==============================
# Fetch HTML
# ==============================
def fetch_html(url: str) -> str:
    """
    Download HTML from Thaiwater website
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


# ==============================
# Parse HTML
# ==============================
def parse_station_names(html: str) -> List[str]:
    """
    Parse station names from Thaiwater HTML table
    Only extracts:
        <span class="MuiButton-label">สถานี...</span>
    """
    soup = BeautifulSoup(html, "html.parser")

    station_names: List[str] = []

    # Loop through every table row
    rows = soup.find_all("tr")

    for row in rows:
        # Exact selector based on provided HTML
        name_span = row.select_one("th span.MuiButton-label")

        if not name_span:
            continue

        station_name = name_span.get_text(strip=True)
        station_names.append(station_name)

    return station_names


# ==============================
# Main scrape function
# ==============================
def scrape_thaiwater_station_names() -> List[str]:
    html = fetch_html(THAIWATER_URL)
    return parse_station_names(html)


# ==============================
# Run directly
# ==============================
if __name__ == "__main__":
    stations = scrape_thaiwater_station_names()
    print(f"✅ Found {len(stations)} station names")
    for name in stations[:10]:
        print(name)
