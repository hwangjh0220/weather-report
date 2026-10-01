# GitHub: https://github.com/hwangjh0220/weather-report
import requests

def fetch_weather_data(lat: float, lon: float):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "Asia/Tokyo",
        "forecast_days": 3,
    }
    response = requests.get(url, params=params)
    return response.json()

if __name__ == "__main__":
    print("API 연결 준비 완료")