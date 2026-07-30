import httpx

def get_weather(city: str) -> dict:
    """
    언제 쓰는 함수인가?
    → 사용자가 특정 도시의 날씨를 알고 싶을 때 사용한다.
    → LLM이 날씨 요약을 하기 전에 실제 데이터를 가져올 때 사용한다.
    """

    # 1. 도시 → 위도/경도 변환
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo = httpx.get(geo_url, params={"name": city, "count": 1}).json()

    if not geo.get("results"):
        return {"error": f"도시를 찾을 수 없습니다: {city}"}

    lat = geo["results"][0]["latitude"]
    lon = geo["results"][0]["longitude"]

    # 2. 날씨 조회
    weather_url = "https://api.open-meteo.com/v1/forecast"
    data = httpx.get(
        weather_url,
        params={
            "latitude": lat,
            "longitude": lon,
            "current_weather": True
        }
    ).json()

    current = data["current_weather"]

    return {
        "city": city,
        "temperature": current["temperature"],
        "windspeed": current["windspeed"],
        "weathercode": current["weathercode"],
    }


# 테스트 코드
if __name__ == "__main__":
    print(get_weather("Seoul"))