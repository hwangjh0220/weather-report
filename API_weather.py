# GitHub Repository: [https://github.com/hwangjh0220/weather-report](https://github.com/hwangjh0220/weather-report)
import requests
import json

WMO_WEATHER_CODES = {0: "맑음", 1: "대체로 맑음", 2: "주로 맑음", 3: "흐림"}

def get_weather_desc(code):
    return WMO_WEATHER_CODES.get(code, "정보 없음")

def fetch_weather_data(lat: float, lon: float):
    url = "[https://api.open-meteo.com/v1/forecast](https://api.open-meteo.com/v1/forecast)"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "Asia/Tokyo",
        "forecast_days": 3,
    }
    return requests.get(url, params=params).json()

def save_to_json(data, city="서울"):
    filename = f"weather_{city}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"저장 완료: {filename}")

def format_forecast_display(data, city="서울"):
    daily = data.get("daily", {})
    print(f"\n[{city} 날씨 리포트]")
    for i in range(3):
        print(f"🗓️ Day {i+1} ({daily['time'][i]}): 최저 {daily['temperature_2m_min'][i]}℃ / 최고 {daily['temperature_2m_max'][i]}℃")

if __name__ == "__main__":
    d = fetch_weather_data(37.5665, 126.9780)
    format_forecast_display(d)
    save_to_json(d)