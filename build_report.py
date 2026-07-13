import urllib.request
import json
import re
from datetime import datetime
from zoneinfo import ZoneInfo

LAT = 40.84
LON = -81.76
TZ = ZoneInfo("America/New_York")

HEADERS = {
    "User-Agent": "WayneCountyOffGridWeather/2.3"
}


def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def hazard_summary(periods, alerts):
    # Active alerts always take priority
    if alerts["features"]:
        return alerts["features"][0]["properties"]["headline"]

    text = " ".join(p["detailedForecast"] for p in periods[:4])
    lower = text.lower()

    # Heat Index
    m = re.search(r"Heat index values? as high as (\d+)", text, re.IGNORECASE)
    if m:
        return f"Heat index up to {m.group(1)}°F."

    # Wind gusts
    m = re.search(r"gusts? as high as (\d+)\s*mph", text, re.IGNORECASE)
    if m:
        return f"Wind gusts up to {m.group(1)} mph."

    # Rainfall totals
    m = re.search(
        r"between ([0-9.]+) and ([0-9.]+) inches",
        text,
        re.IGNORECASE,
    )
    if m:
        return f"Heavy rain: {m.group(1)}–{m.group(2)} inches possible."

    # Thunderstorms
    if "severe thunderstorm" in lower:
        return "Severe thunderstorms possible."

    if "thunderstorm" in lower:
        return "Thunderstorms possible."

    # Flooding
    if "flash flood" in lower:
        return "Flash flooding possible."

    if "flood" in lower:
        return "Flooding possible."

    # Winter weather
    if "freezing rain" in lower:
        return "Freezing rain possible."

    if "snow" in lower:
        return "Snow expected."

    if "fog" in lower:
        return "Reduced visibility in fog."

    return "No significant hazards expected."


# --------------------------------------------------------
# Download weather data
# --------------------------------------------------------

points = fetch(f"https://api.weather.gov/points/{LAT},{LON}")

forecast = fetch(points["properties"]["forecast"])
hourly = fetch(points["properties"]["forecastHourly"])
alerts = fetch(f"https://api.weather.gov/alerts/active?point={LAT},{LON}")

generated = datetime.now(TZ)

forecast_updated = datetime.fromisoformat(
    forecast["properties"]["updateTime"]
).astimezone(TZ)

current = hourly["properties"]["periods"][0]
periods = forecast["properties"]["periods"]
today = periods[0]

# --------------------------------------------------------
# Build report
# --------------------------------------------------------

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

# --------------------------------------------------------
# Summary
# --------------------------------------------------------

report.append("SUMMARY")
report.append("-------")

summary = today["detailedForecast"].split(".")[0].strip() + "."
report.append(summary)

if alerts["features"]:
    report.append("Active alerts in effect.")
else:
    report.append("No active alerts.")

report.append(hazard_summary(periods, alerts))
report.append("")

# --------------------------------------------------------
# Current Conditions
# --------------------------------------------------------

report.append("CURRENT CONDITIONS")
report.append("------------------")

report.append(
    f"{current['temperature']}°{current['temperatureUnit']}  "
    f"{current['shortForecast']}"
)

wind_speed = current["windSpeed"].strip()
wind_dir = current["windDirection"].strip()

if wind_speed.startswith("0"):
    report.append("Wind: Calm")
elif wind_dir:
    report.append(f"Wind: {wind_dir} {wind_speed}")
else:
    report.append(f"Wind: {wind_speed}")

report.append("")

# --------------------------------------------------------
# Active Alerts
# --------------------------------------------------------

report.append("ACTIVE ALERTS")
report.append("-------------")

if alerts["features"]:
    for alert in alerts["features"]:
        report.append(alert["properties"]["headline"])
else:
    report.append("None")

report.append("")

# --------------------------------------------------------
# Forecast
# --------------------------------------------------------

report.append("FORECAST")
report.append("--------")

for period in periods[:4]:
    report.append("")
    report.append(period["name"])
    report.append("")
    report.append(period["detailedForecast"])

report.append("")
report.append("=" * 58)

# --------------------------------------------------------
# Save report
# --------------------------------------------------------

with open("report.txt", "w") as f:
    f.write("\n".join(report))

print("report.txt updated successfully.")
