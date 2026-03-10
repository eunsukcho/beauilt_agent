# LangGraph 전환 가이드 🔄

이 문서는 LangChain에서 LangGraph로 전환한 내용을 설명합니다.

## 주요 변경사항

### 1. 워크플로우 관리
- **이전**: `main.py`에서 키워드 기반 라우팅
- **현재**: LangGraph로 워크플로우 자동 관리

### 2. 상태 관리
- **이전**: `user_session` 딕셔너리로 수동 관리
- **현재**: `AgentState`로 자동 상태 관리

### 3. 에이전트 간 데이터 전달
- **이전**: 수동으로 이전 결과를 전달
- **현재**: 상태를 통해 자동 전달

### 4. 웹 검색 기능 추가
- 벡터 DB 검색 결과가 부족할 때 자동으로 웹 검색
- Tavily API 또는 DuckDuckGo 사용

## 워크플로우 구조

```
사용자 입력
  ↓
진단 노드 (피부 상태 진단)
  ↓
라우팅 (성분 분석 또는 분석)
  ├─→ 성분 분석 노드 → 종료
  └─→ 분석 노드
        ↓
      가이드 노드 (케어 가이드라인)
        ↓
      시뮬레이션 노드 (선택적) → 종료
```

## 파일 구조 변경

### 새로 추가된 파일
- `workflow/state.py`: 상태 정의
- `workflow/nodes.py`: 노드 정의
- `workflow/graph.py`: 그래프 구성
- `agents/web_search_agent.py`: 웹 검색 에이전트

### 수정된 파일
- `main.py`: LangGraph 기반으로 재작성
- `agents/base_agent.py`: 웹 검색 기능 추가
- `config/settings.py`: Tavily API 키 설정 추가
- `requirements.txt`: LangGraph 및 웹 검색 도구 추가

## 사용 방법

### 기본 사용법 (변경 없음)
```bash
python main.py
```

### 웹 검색 설정 (선택사항)
`.env` 파일에 Tavily API 키 추가:
```env
TAVILY_API_KEY=your_tavily_api_key_here
```

API 키가 없으면 DuckDuckGo를 자동으로 사용합니다.

## 워크플로우 특징

### 자동 진행
- 진단 → 분석 → 가이드 자동 진행
- 각 단계의 결과가 자동으로 다음 단계에 전달

### 조건부 분기
- 성분 분석 요청 시 성분 분석 노드로 분기
- 시뮬레이션 요청 시 시뮬레이션 노드로 분기

### 웹 검색 자동화
- 벡터 DB 검색 결과가 부족하면 자동으로 웹 검색
- 검색 결과가 프롬프트에 자동 포함

## 장점

1. **명확한 워크플로우**: 그래프로 워크플로우 시각화 가능
2. **자동 상태 관리**: 수동 상태 관리 불필요
3. **확장성**: 새로운 노드 추가가 쉬움
4. **웹 검색 통합**: 벡터 DB와 웹 검색 자동 통합

## 주의사항

1. **LangGraph 학습 필요**: LangGraph 개념 이해 필요
2. **상태 구조**: `AgentState` 구조 변경 시 모든 노드 수정 필요
3. **디버깅**: 워크플로우 디버깅이 다소 복잡할 수 있음

## 참고 자료

- [LangGraph 문서](https://langchain-ai.github.io/langgraph/)
- [LangGraph 튜토리얼](https://langchain-ai.github.io/langgraph/tutorials/)
