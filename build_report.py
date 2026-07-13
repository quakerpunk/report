import urllib.request
import json
from datetime import datetime
from zoneinfo import ZoneInfo

# Orrville / Wayne County
LAT = 40.84
LON = -81.76

headers = {
    "User-Agent": "WinlinkWeatherReport/1.0 (github)"
}

def fetch(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

# Find the correct forecast URL
points = fetch(f"https://api.weather.gov/points/{LAT},{LON}")

forecast_url = points["properties"]["forecast"]

forecast = fetch(forecast_url)

periods = forecast["properties"]["periods"]

now = datetime.now(ZoneInfo("America/New_York"))

report = f"""WAYNE COUNTY WEATHER REPORT
Updated: {now.strftime("%Y-%m-%d %I:%M %p %Z")}

FORECAST

"""

for p in periods[:4]:
    report += f"{p['name']}\n"
    report += f"{p['detailedForecast']}\n\n"

with open("report.txt","w") as f:
    f.write(report)

print("Updated report.txt")
