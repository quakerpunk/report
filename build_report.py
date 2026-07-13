from datetime import datetime
from zoneinfo import ZoneInfo

now = datetime.now(ZoneInfo("America/New_York"))

report = f"""==================================================
WAYNE COUNTY, OHIO WEATHER REPORT

Updated: {now.strftime("%Y-%m-%d %I:%M %p %Z")}

CURRENT CONDITIONS
(Placeholder)

FORECAST
(Placeholder)

ALERTS
(Placeholder)

METAR
(Placeholder)

SPC
(Placeholder)

==================================================
"""

with open("report.txt", "w") as f:
    f.write(report)

print("report.txt updated.")
