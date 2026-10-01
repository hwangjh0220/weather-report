# ==============================================================================
# GitHub Repository: https://github.com/hwangjh0220/weather-report
# 과제명: 4주차 날씨 리포트 프로그램
# 기능:
#   - 사용자에게 지역(기본값: 서울)을 입력받음
#   - 오늘부터 모레까지(3일간) 오전 6시, 오후 3시 날씨 정보 표기
#   - 일일 최저/최고 기온 안내
#   - 날씨 정보를 JSON 파일로 저장 여부 선택 (y/n)
#   - Open-Meteo API 활용 (인증키 불필요, 무료)
# ==============================================================================

import json
from datetime import datetime
from typing import Any, Dict, Optional, Tuple
import requests

# 주요 도시 좌표 데이터 (원하는 도시 추가/변경 가능)
CITY_COORDINATES: Dict[str, Tuple[float, float]] = {
    "서울": (37.5665, 126.9780),
    "천안": (36.8151, 127.1139),
    "부산": (35.1796, 129.0756),
    "대구": (35.8714, 128.6014),
    "인천": (37.4563, 126.7052),
    "대전": (36.3504, 127.3845),
    "광주": (35.1595, 126.8526),
}

# WMO 날씨 해석 코드 매핑
WMO_WEATHER_CODES: Dict[int, str] = {
    0: "맑음",
    1: "대체로 맑음",
    2: "주로 맑음",
    3: "흐림",
    45: "안개",
    48: "서리 안개",
    51: "가벼운 이슬비",
    53: "보통 이슬비",
    55: "강한 이슬비",
    61: "약한 비",
    63: "보통 비",
    65: "강한 비",
    71: "약한 눈",
    73: "보통 눈",
    75: "강한 눈",
    80: "약한 소나기",
    81: "보통 소나기",
    82: "강한 소나기",
    95: "뇌우",
}


def get_weather_desc(code: int) -> str:
    """WMO 코드를 읽기 쉬운 한글 날씨 명칭으로 변환합니다."""
    return WMO_WEATHER_CODES.get(code, "정보 없음")


def fetch_weather_data(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """Open-Meteo API에서 시간별/일별 예보 데이터를 호출합니다."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "Asia/Tokyo",
        "forecast_days": 3,
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        print(f"날씨 데이터를 불러오는데 실패했습니다: {exc}")
        return None


def format_forecast_display(data: Dict[str, Any], city: str) -> Dict[str, Any]:
    """터미널 출력 형식에 맞춰 포맷팅하고 저장용 데이터를 가공합니다."""
    hourly = data.get("hourly", {})
    daily = data.get("daily", {})

    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    humidities = hourly.get("relative_humidity_2m", [])
    precip_probs = hourly.get("precipitation_probability", [])
    weather_codes = hourly.get("weather_code", [])
    wind_speeds = hourly.get("wind_speed_10m", [])

    day_labels = ["오늘", "내일", "모레"]
    result_report = {
        "city": city,
        "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "forecast": [],
    }

    print("\n" + "=" * 50)
    print(f"[{city} 지역 날씨 리포트 (3일 예보)]")
    print("=" * 50)

    for day_idx in range(min(3, len(daily.get("time", [])))):
        date_str = daily["time"][day_idx]
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = dt.strftime("%m.%d.")
        label = day_labels[day_idx]

        min_temp = round(daily["temperature_2m_min"][day_idx])
        max_temp = round(daily["temperature_2m_max"][day_idx])

        print(f"\n🗓️  {label} ({formatted_date})")
        print("-" * 45)

        day_data = {
            "date": date_str,
            "label": label,
            "min_temp": min_temp,
            "max_temp": max_temp,
            "slots": {},
        }

        # 오전 06:00 (index: day_idx * 24 + 6), 오후 15:00 (index: day_idx * 24 + 15)
        target_slots = [("오전 06:00", day_idx * 24 + 6), ("오후 15:00", day_idx * 24 + 15)]

        for slot_name, idx in target_slots:
            if idx < len(times):
                w_desc = get_weather_desc(weather_codes[idx])
                temp = round(temps[idx])
                pop = precip_probs[idx]
                hum = humidities[idx]
                wind = round(wind_speeds[idx])

                day_data["slots"][slot_name] = {
                    "weather": w_desc,
                    "temp": temp,
                    "pop": pop,
                    "humidity": hum,
                    "wind": wind,
                }

                print(f"  🌅 {slot_name}" if "06:00" in slot_name else f"  ☀️  {slot_name}")
                print(f"     날씨: {w_desc}")
                print(f"     기온: {temp} ℃")
                print(f"     강수확률: {pop}%")
                print(f"     습도: {hum}%")
                print(f"     풍속: {wind} m/s")

        print(f"\n  🏷️  일일 기온: 최저 {min_temp} ℃ / 최고 {max_temp} ℃")
        print("=" * 50)

        result_report["forecast"].append(day_data)

    return result_report


def save_to_json(data: Dict[str, Any], city: str) -> None:
    """가공된 날씨 정보를 JSON 파일로 저장합니다."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"weather_{city}_{timestamp}.json"
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    print(f"성공적으로 저장되었습니다: {file_name}")


def main() -> None:
    # 1. 지역 입력 (기본값: 서울)
    user_input = input("조회할 지역을 입력하세요 (기본값: 서울): ").strip()
    city = user_input if user_input else "서울"

    if city not in CITY_COORDINATES:
        print(f"'{city}' 좌표 정보가 없습니다. 기본값 '서울'로 진행합니다.")
        city = "서울"

    lat, lon = CITY_COORDINATES[city]

    # 2. 날씨 데이터 조회 및 출력
    raw_weather = fetch_weather_data(lat, lon)
    if not raw_weather:
        return

    processed_report = format_forecast_display(raw_weather, city)

    # 3. JSON 저장 선택
    choice = input("\n날씨 정보를 JSON 파일로 저장하시겠습니까? (y/n): ").strip().lower()
    if choice == "y":
        save_to_json(processed_report, city)
    else:
        print("저장하지 않고 프로그램을 종료합니다.")


if __name__ == "__main__":
    main()