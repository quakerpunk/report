import urllib.request
import json
from datetime import datetime
from zoneinfo import ZoneInfo

LAT = 40.84
LON = -81.76
TZ = ZoneInfo("America/New_York")

HEADERS = {
    "User-Agent": "WayneCountyOffGridWeather/2.0"
}


def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


points = fetch(f"https://api.weather.gov/points/{LAT},{LON}")

forecast = fetch(points["properties"]["forecast"])
hourly = fetch(points["properties"]["forecastHourly"])

# Active alerts for this point
alerts = fetch(
    f"https://api.weather.gov/alerts/active?point={LAT},{LON}"
)

generated = datetime.now(TZ)

forecast_updated = datetime.fromisoformat(
    forecast["properties"]["updateTime"]
).astimezone(TZ)

current = hourly["properties"]["periods"][0]

report = []

report.append("=" * 58)
report.append("WAYNE COUNTY OFF-GRID WEATHER REPORT")
report.append("=" * 58)
report.append("")
report.append(
    f"Forecast Issued : {forecast_updated.strftime('%Y-%m-%d %I:%M %p %Z')}"
)
report.append(
    f"Report Generated: {generated.strftime('%Y-%m-%d %I:%M %p %Z')}"
)
report.append("")

# Current Conditions
report.append("CURRENT CONDITIONS")
report.append("------------------")
report.append(
    f"{current['temperature']}°{current['temperatureUnit']}  "
    f"{current['shortForecast']}"
)
report.append(
    f"Wind: {current['windDirection']} {current['windSpeed']}"
)
report.append("")

# Alerts
report.append("ACTIVE ALERTS")
report.append("-------------")

features = alerts["features"]

if not features:
    report.append("None")
else:
    for alert in features:
        p = alert["properties"]
        report.append(f"* {p['headline']}")

report.append("")

# Forecast
report.append("FORECAST")
report.append("--------")

for p in forecast["properties"]["periods"][:4]:
    report.append("")
    report.append(p["name"])
    report.append(p["detailedForecast"])

report.append("")
report.append("SEVERE WEATHER")
report.append("----------------")

report.append(
    "SPC Outlook: (Coming in Version 2.1)"
)

report.append("")
report.append("=" * 58)

with open("report.txt", "w") as f:
    f.write("\n".join(report))

print("Updated report.txt")
