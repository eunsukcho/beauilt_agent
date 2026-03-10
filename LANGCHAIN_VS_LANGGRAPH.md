# LangChain vs LangGraph 비교 📊

현재 프로젝트의 구조와 LangGraph로 전환 시의 차이점을 설명합니다.

## 현재 구조 (LangChain)

### 특징
- 각 에이전트가 독립적으로 동작
- `main.py`에서 키워드 기반 라우팅
- 수동 상태 관리 (`user_session` 딕셔너리)

### 코드 구조
```python
# main.py
class BeautyChatbot:
    def route_request(self, user_input: str):
        # 키워드로 에이전트 선택
        if "진단" in user_input:
            return self.diagnosis_agent.process(user_input)
        elif "분석" in user_input:
            return self.analysis_agent.process(...)
        # ...
```

### 장점
- ✅ 간단하고 이해하기 쉬움
- ✅ 각 에이전트가 독립적이라 디버깅 용이
- ✅ 유연한 라우팅 가능

### 단점
- ❌ 워크플로우가 명확하지 않음
- ❌ 상태 관리가 수동적
- ❌ 에이전트 간 자동 연결이 어려움

## LangGraph 구조

### 특징
- 워크플로우를 그래프로 정의
- 에이전트 간 자동 흐름 제어
- 상태 관리 자동화

### 코드 구조 예시
```python
from langgraph.graph import StateGraph, END

# 상태 정의
class AgentState(TypedDict):
    user_input: str
    diagnosis_result: Optional[str]
    analysis_result: Optional[str]
    care_guide: Optional[str]
    current_step: str

# 그래프 생성
workflow = StateGraph(AgentState)

# 노드 추가 (각 에이전트)
workflow.add_node("diagnosis", diagnosis_node)
workflow.add_node("analysis", analysis_node)
workflow.add_node("care_guide", care_guide_node)
workflow.add_node("simulation", simulation_node)

# 엣지 추가 (흐름 정의)
workflow.set_entry_point("diagnosis")
workflow.add_edge("diagnosis", "analysis")
workflow.add_edge("analysis", "care_guide")
workflow.add_conditional_edges(
    "care_guide",
    should_simulate,  # 조건 함수
    {
        "yes": "simulation",
        "no": END
    }
)
workflow.add_edge("simulation", END)

# 그래프 컴파일
app = workflow.compile()
```

### 장점
- ✅ 워크플로우가 명확하고 시각화 가능
- ✅ 상태 관리 자동화
- ✅ 조건부 분기 처리 용이
- ✅ 에이전트 간 자동 연결

### 단점
- ❌ 학습 곡선이 있음
- ❌ 초기 설정이 복잡할 수 있음

## 언제 무엇을 사용할까?

### LangChain 사용 시기
- 간단한 챗봇
- 에이전트가 독립적으로 동작
- 유연한 라우팅이 필요
- 빠른 프로토타이핑

### LangGraph 사용 시기
- 복잡한 워크플로우
- 에이전트 간 순차적 실행 필요
- 조건부 분기 처리 필요
- 상태 관리가 중요한 경우
- 워크플로우 시각화 필요

## 현재 프로젝트에 적용

### 현재 프로젝트의 워크플로우
```
사용자 입력
  ↓
키워드 분석
  ↓
에이전트 선택
  ├─→ 진단 에이전트
  ├─→ 분석 에이전트 (진단 결과 필요)
  ├─→ 가이드 에이전트 (진단/분석 결과 필요)
  ├─→ 시뮬레이션 에이전트 (가이드 필요)
  └─→ 성분 분석 에이전트
```

### LangGraph로 전환 시 워크플로우
```
사용자 입력
  ↓
진단 노드 (항상 실행)
  ↓
분석 노드 (진단 결과 사용)
  ↓
가이드 노드 (진단/분석 결과 사용)
  ↓
시뮬레이션 노드? (조건부)
  ↓
성분 분석 노드? (조건부)
  ↓
응답 반환
```

## 전환 시 고려사항

### 1. 의존성 추가
```bash
pip install langgraph
```

### 2. 코드 구조 변경
- 각 에이전트를 노드 함수로 변환
- 상태 클래스 정의
- 그래프 구성

### 3. 장단점
- **장점**: 워크플로우 명확화, 자동 상태 관리
- **단점**: 학습 필요, 코드 복잡도 증가

## 추천

### 현재 프로젝트의 경우
현재 구조로도 충분히 동작하지만, **LangGraph로 전환하면**:
1. 피부 진단 → 분석 → 가이드 → 시뮬레이션 자동 연결
2. 각 단계 결과가 자동으로 다음 단계에 전달
3. 워크플로우가 더 명확해짐

### 선택 가이드
- **LangChain 유지**: 현재 구조가 만족스럽고, 간단함을 선호
- **LangGraph 전환**: 워크플로우를 체계화하고 싶고, 학습 의지가 있음

---

**결론**: 현재는 **LangChain**을 사용하고 있으며, 필요하다면 **LangGraph**로 전환할 수 있습니다!
