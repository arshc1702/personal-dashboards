"""
Pulls current weather for Melbourne from Open-Meteo (free, no API key)
and writes data/weather.json in the shape index.html expects.

Change LAT/LON below if the dashboard should track a different city.
"""
import json
import urllib.request
from datetime import datetime, timezone

LAT, LON = -37.8136, 144.9631

WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Dense drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow",
    80: "Light showers", 81: "Showers", 82: "Violent showers",
    95: "Thunderstorm", 96: "Thunderstorm, hail", 99: "Thunderstorm, heavy hail",
}

URL = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LAT}&longitude={LON}"
    "&current=temperature_2m,apparent_temperature,relative_humidity_2m,"
    "precipitation_probability,weather_code,wind_speed_10m"
    "&hourly=temperature_2m,weather_code"
    "&forecast_days=2"
    "&timezone=Australia%2FMelbourne"
)

with urllib.request.urlopen(URL, timeout=15) as resp:
    raw = json.load(resp)

c = raw["current"]

# next 6 hours from the current hour, for the panel's hourly trend strip
h = raw["hourly"]
now_iso = c["time"]
start = h["time"].index(now_iso) if now_iso in h["time"] else 0
hourly = [
    {
        "hour": t[11:16],
        "temp": h["temperature_2m"][i],
        "condition": WMO_CODES.get(h["weather_code"][i], "Unknown"),
    }
    for i, t in enumerate(h["time"][start:start + 6], start=start)
]

out = {
    "temp": c["temperature_2m"],
    "feels_like": c["apparent_temperature"],
    "condition": WMO_CODES.get(c["weather_code"], "Unknown"),
    "wind_kmh": c["wind_speed_10m"],
    "humidity": c["relative_humidity_2m"],
    "rain_chance": c.get("precipitation_probability", 0),
    "hourly": hourly,
    "updated": datetime.now(timezone.utc).isoformat(),
}

with open("data/weather.json", "w") as f:
    json.dump(out, f, indent=2)

print("Wrote data/weather.json:", out)
