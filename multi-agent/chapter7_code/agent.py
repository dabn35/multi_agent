from typing import TypedDict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from weather_tool import get_weather

# 상태 정의
class WeatherState(TypedDict):
    city: str           # 입력: 도시 이름
    weather: dict       # 날씨 API 응답
    summary: str        # LLM이 만든 한 문장 요약
    is_ok: bool         # 검증 통과 여부
    attempt: int        # 요약 시도 횟수

# LLM 설정
load_dotenv()
llm = ChatGroq(model="llama-3.3-70b-versatile")


# 노드 1: 날씨 조회
def fetch_weather(state: WeatherState) -> dict:
    result = get_weather(state["city"])
    print(f"[날씨 조회] {result}")
    return {"weather": result}


# 노드 2: 요약 생성 (LLM 사용)
def summarize(state: WeatherState) -> dict:
    w = state["weather"]

    # 에러 처리
    if "error" in w:
        return {
            "summary": w["error"],
            "attempt": state["attempt"] + 1
        }

    prompt = (
        f"{w['city']}의 현재 날씨: 기온 {w['temperature']}°C, "
        f"풍속 {w['windspeed']}km/h. 비전공자에게 한 문장으로 요약해라. 반드시 한국어로만 작성해라."
    )

    result = llm.invoke(prompt)

    print(f"[요약 시도 {state['attempt'] + 1}] {result.content}")

    return {
        "summary": result.content,
        "attempt": state["attempt"] + 1
    }


# 노드 3: 검증 (LLM 사용)
def check(state: WeatherState) -> dict:
    prompt = (
        f"다음 요약이 도시명과 날씨 정보를 모두 포함하는가? '{state['summary']}'\n"
        "포함하면 'yes', 아니면 'no'만 답해라."
    )

    result = llm.invoke(prompt)

    verdict = result.content.strip().lower() == "yes"

    print(f"[검증] {'통과' if verdict else '재요약 필요'}")

    return {"is_ok": verdict}


from langgraph.graph import StateGraph, END


# 분기 함수
def route(state: WeatherState) -> str:
    if state["is_ok"]:
        return "end"
    if state["attempt"] >= 3:
        print("[종료] 최대 시도 횟수 초과")
        return "end"
    return "summarize"


# 그래프 생성
builder = StateGraph(WeatherState)

# 노드 등록
builder.add_node("fetch_weather", fetch_weather)
builder.add_node("summarize", summarize)
builder.add_node("check", check)

# 흐름 연결
builder.set_entry_point("fetch_weather")
builder.add_edge("fetch_weather", "summarize")
builder.add_edge("summarize", "check")

# 조건 분기
builder.add_conditional_edges(
    "check",
    route,
    {
        "end": END,
        "summarize": "summarize"
    }
)

# 그래프 컴파일
graph = builder.compile()


if __name__ == "__main__":
    result = graph.invoke({
        "city": "dahyun",
        "weather": {},
        "summary": "",
        "is_ok": False,
        "attempt": 0,
    })

    print("\n--- 최종 요약 ---")
    print(result["summary"])
    print(f"총 시도 횟수: {result['attempt']}")


print("\n--- 실패 케이스 테스트 ---")

result = graph.invoke({
    "city": "Nonexistentcity123",
    "weather": {},
    "summary": "",
    "is_ok": False,
    "attempt": 0,
})

print(result["summary"])