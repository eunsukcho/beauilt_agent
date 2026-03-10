# 뷰티 데일리팁 챗봇 💄✨

20~30대 남녀를 위한 친근한 피부 관리 챗봇입니다. 전문 피부관리사가 직접 케어해주는 것처럼 따뜻하고 친근한 톤으로 피부 관리 조언을 제공합니다.

## 📋 프로젝트 개요

이 프로젝트는 LLM Agent를 활용하여 피부 관리 조언을 제공하는 챗봇입니다. OpenAI의 GPT 모델과 벡터 데이터베이스를 활용하여 전문적인 피부 관리 정보를 제공합니다.

## 🎯 주요 기능

### 1. 피부 상태 진단 에이전트
- 사용자가 설명한 피부 상태를 분석
- 피부 타입 (지성, 건성, 복합성, 민감성 등) 판별
- 주요 피부 문제점 파악
- 피부 상태 점수 제공

### 2. 전체 상황 진단 에이전트
- 피부 진단 결과를 바탕으로 종합 분석
- 생활 패턴, 환경 요인 등을 고려한 원인 분석
- 전체적인 피부 건강 수준 평가

### 3. 케어 가이드라인 제공 에이전트
- 피부 상태에 맞는 맞춤형 케어 루틴 제공
- 아침/저녁 스킨케어 순서 안내
- 제품 추천 및 사용법 가이드
- 주간/월간 케어 팁

### 4. 시뮬레이션 에이전트
- 케어 가이드라인 적용 시 예상 변화 시뮬레이션
- 단기(1주일~1개월), 중기(3개월), 장기(6개월~1년) 변화 예측
- 동기부여를 위한 긍정적 전망 제시

### 5. 성분별 적합도 분석 에이전트
- 피부 타입별 추천 성분 분석
- 성분별 적합도 점수 제공
- 성분 조합 가이드
- 제품 선택 체크리스트

## 🛠️ 기술 스택

- **Python**: 주 개발 언어
- **LangChain**: LLM Agent 프레임워크
- **LangGraph**: 워크플로우 관리 (에이전트 간 자동 연결)
- **OpenAI GPT**: 언어 모델 (gpt-4-turbo-preview)
- **Chroma**: 벡터 데이터베이스
- **DuckDuckGo**: 웹 검색 도구 (벡터 DB에 없는 정보 검색)
- **Pydantic**: 데이터 검증 및 설정 관리

## 📦 설치 방법

> 💡 **빠른 시작**: 자세한 단계별 가이드는 [`QUICK_START.md`](QUICK_START.md)를 참고하세요!

### 1. 저장소 클론
```bash
git clone <repository-url>
cd beauilt-agent
```

### 2. 가상 환경 생성 및 활성화

#### 방법 A: venv 사용 (기본)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 방법 B: uv 프로젝트 사용 (권장)
```bash
# uv 설치 (처음 한 번만)
# Windows PowerShell
irm https://astral.sh/uv/install.ps1 | iex

# 또는 pip로 설치
pip install uv

# 프로젝트 의존성 설치 + 가상환경 생성
uv sync
```

### 3. 패키지 설치
```bash
# venv 사용 시
pip install -r requirements.txt

# uv(프로젝트) 사용 시
uv sync
```

### 4. 환경 변수 설정
`.env.example` 파일을 참고하여 `.env` 파일을 생성하고 API 키를 입력하세요.

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집하여 API 키 입력
OPENAI_API_KEY=your_openai_api_key_here

# 웹 검색은 기본적으로 DuckDuckGo를 사용합니다 (추가 API 키 불필요)
# Tavily는 현재 의존성 충돌 이슈로 requirements/pyproject에서 제외했습니다.
```

## 🚀 사용 방법

### 방법 1: 웹 앱으로 사용 (Streamlit)

#### 로컬 실행
```bash
# 앱 실행
uv run streamlit run streamlit_app.py
```

브라우저에서 `http://localhost:8501`로 접속하면 됩니다.

#### Streamlit Cloud에 배포 (무료!)
1. GitHub에 코드 업로드
2. https://streamlit.io/cloud 접속
3. GitHub로 로그인
4. 저장소 연결 및 배포

자세한 내용은 `STREAMLIT_DEPLOY.md`를 참고하세요.

### 방법 2: 커맨드라인으로 사용

### 1. 벡터 DB 초기화

먼저 피부 관리 교본과 교재 데이터를 벡터 DB에 추가해야 합니다.

```bash
uv run python scripts/init_vector_db.py
```

**중요**: 현재는 샘플 데이터가 포함되어 있습니다. 실제 데이터 파일(피부 관리 교본, 교재)이 준비되면 `scripts/init_vector_db.py` 파일의 `load_sample_documents()` 함수를 수정하여 실제 데이터를 로드하도록 변경하세요.

### 2. 챗봇 실행

```bash
uv run python main.py
```

### 3. 대화 예시

```
👤 사용자: 제 피부가 자꾸 번들거리고 트러블이 생겨요

🤖 피부관리사: [피부 진단 결과 제공]

👤 사용자: 전체적으로 분석해주세요

🤖 피부관리사: [종합 분석 결과 제공]

👤 사용자: 케어 방법 알려주세요

🤖 피부관리사: [케어 가이드라인 제공]
```

## 📁 프로젝트 구조

```
beauilt-agent/
├── agents/                  # 에이전트 모듈
│   ├── __init__.py
│   ├── base_agent.py        # 기본 에이전트 클래스
│   ├── skin_diagnosis_agent.py      # 피부 진단 에이전트
│   ├── skin_analysis_agent.py      # 전체 분석 에이전트
│   ├── care_guide_agent.py          # 케어 가이드 에이전트
│   ├── simulation_agent.py          # 시뮬레이션 에이전트
│   ├── ingredient_analysis_agent.py # 성분 분석 에이전트
│   └── web_search_agent.py          # 웹 검색 에이전트
├── workflow/                # LangGraph 워크플로우
│   ├── __init__.py
│   ├── state.py             # 상태 정의
│   ├── nodes.py             # 노드 정의 (각 에이전트)
│   └── graph.py             # 워크플로우 그래프 구성
├── config/                  # 설정 파일
│   ├── __init__.py
│   └── settings.py          # 환경 변수 및 설정 관리
├── vector_db/               # 벡터 데이터베이스 모듈
│   ├── __init__.py
│   └── vector_store.py      # 벡터 DB 관리 클래스
├── scripts/                 # 유틸리티 스크립트
│   ├── __init__.py
│   └── init_vector_db.py    # 벡터 DB 초기화 스크립트
├── main.py                  # 메인 실행 파일 (LangGraph 기반)
├── requirements.txt         # 패키지 의존성
├── .env.example            # 환경 변수 예시 파일
└── README.md               # 프로젝트 설명서
```

## 🔧 주요 모듈 설명

### LangGraph 워크플로우 (`workflow/`)
- **state.py**: 워크플로우 상태 정의 (각 노드 간 데이터 공유)
- **nodes.py**: 각 에이전트를 노드로 변환
- **graph.py**: 워크플로우 그래프 구성 및 엣지 정의

**워크플로우 흐름**:
```
사용자 입력
  ↓
진단 노드 (피부 상태 진단)
  ↓
분석 노드 (종합 분석)
  ↓
가이드 노드 (케어 가이드라인)
  ↓
시뮬레이션 노드 (변화 예측) - 선택적
  ↓
응답 반환
```

### BaseAgent (`agents/base_agent.py`)
모든 에이전트의 기본 클래스입니다. 공통 기능을 제공합니다:
- LLM 초기화 및 관리
- 벡터 DB 검색 기능
- **웹 검색 기능** (벡터 DB 결과가 부족할 때 자동 검색)
- 대화 히스토리 관리
- 프롬프트 구성

### WebSearchAgent (`agents/web_search_agent.py`)
웹 검색 에이전트입니다:
- 벡터 DB에서 찾을 수 없는 정보를 웹에서 검색
- Tavily API 또는 DuckDuckGo 사용
- 검색 결과를 프롬프트에 자동 포함

### VectorStore (`vector_db/vector_store.py`)
벡터 데이터베이스를 관리하는 클래스입니다:
- 문서를 벡터로 변환하여 저장
- 유사도 검색 기능
- 벡터 DB 초기화 및 관리

### Settings (`config/settings.py`)
애플리케이션 설정을 관리합니다:
- 환경 변수 로드
- API 키 관리 (OpenAI, Tavily)
- 설정값 제공

## 📝 데이터베이스 구조

### 벡터 DB (Chroma)
피부 관리 교본과 교재를 벡터화하여 저장합니다. 유사도 검색을 통해 관련 정보를 찾아냅니다.

**데이터 추가 방법**:
1. `scripts/init_vector_db.py` 파일의 `load_sample_documents()` 함수 수정
2. 실제 데이터 파일(PDF, TXT, MD 등)을 읽어서 `Document` 객체로 변환
3. `vector_store.add_documents()` 메서드로 추가

**웹 검색 기능**:
- 벡터 DB에서 검색 결과가 부족하거나 최신 정보가 필요할 때 자동으로 웹 검색 수행
- Tavily API 키가 있으면 더 정확한 검색 결과 제공
- API 키가 없으면 DuckDuckGo 사용 (무료)

### RDB (관계형 데이터베이스)
성분과 효능에 대한 데이터를 저장합니다. (별도 모듈에서 관리)

**성분 데이터 구조 예시**:
- 성분명
- 효능
- 피부 타입별 적합도
- 주의사항
- 다른 성분과의 조합 정보

**중요**: 성분 데이터는 중계 모듈에서 RDB를 조회하여 가져옵니다. `agents/ingredient_analysis_agent.py`의 `get_ingredient_data()` 메서드에 주석으로 표시되어 있습니다.

## 💡 개발 가이드

### LangGraph 워크플로우 이해하기

이 프로젝트는 **LangGraph**를 사용하여 워크플로우를 관리합니다:

1. **상태 (State)**: `workflow/state.py`에서 정의
2. **노드 (Nodes)**: `workflow/nodes.py`에서 각 에이전트를 노드로 변환
3. **그래프 (Graph)**: `workflow/graph.py`에서 노드 간 연결 정의

**워크플로우 특징**:
- 진단 → 분석 → 가이드 → 시뮬레이션 자동 진행
- 각 노드의 결과가 자동으로 다음 노드에 전달
- 상태 관리 자동화

### 새로운 에이전트 추가하기

1. `agents/` 폴더에 새 파일 생성 (예: `new_agent.py`)
2. `BaseAgent`를 상속받는 클래스 작성:

```python
from .base_agent import BaseAgent

class NewAgent(BaseAgent):
    def __init__(self):
        system_prompt = "에이전트의 역할과 성격을 정의하는 프롬프트"
        super().__init__("에이전트이름", system_prompt)

    def process(self, user_input: str, **kwargs) -> str:
        # 벡터 DB + 웹 검색 (자동)
        vector_results, web_results = self.search_with_fallback(user_input)

        # 프롬프트 구성
        prompt = self.build_prompt(user_input, vector_results, web_results)
        response = self.generate_response(prompt)
        self.add_to_history(user_input, response)
        return response
```

3. `workflow/nodes.py`에 새 노드 함수 추가:

```python
def new_agent_node(state: AgentState) -> AgentState:
    """새 에이전트 노드"""
    user_input = state.get("user_input", "")
    # 에이전트 로직 실행
    response = _new_agent.process(user_input)
    state["new_agent_result"] = response
    state["current_step"] = "new_agent"
    return state
```

4. `workflow/graph.py`에 노드 추가 및 엣지 연결
5. `agents/__init__.py`에 새 에이전트 추가

### 벡터 DB에 데이터 추가하기

1. 데이터 파일 준비 (PDF, TXT, MD 등)
2. `scripts/init_vector_db.py` 수정:

```python
def load_sample_documents() -> list:
    documents = []

    # 파일 읽기 예시
    with open("data/skin_care_book.txt", "r", encoding="utf-8") as f:
        content = f.read()
        documents.append(Document(
            page_content=content,
            metadata={"source": "피부관리교본", "type": "일반"}
        ))

    return documents
```

3. 스크립트 실행: `python scripts/init_vector_db.py`

### 성분 데이터 연동하기

성분 데이터는 중계 모듈에서 RDB를 조회하여 가져옵니다. `agents/ingredient_analysis_agent.py`의 `get_ingredient_data()` 메서드를 수정하세요:

```python
def get_ingredient_data(self, ingredient_name: str) -> Optional[Dict[str, Any]]:
    # 중계 모듈에서 RDB 조회
    from middleware import get_ingredient_info
    return get_ingredient_info(ingredient_name)
```

## ⚠️ 주의사항

1. **API 키 보안**: `.env` 파일은 절대 Git에 커밋하지 마세요. `.gitignore`에 포함되어 있습니다.

2. **벡터 DB 경로**: 벡터 DB는 로컬에 저장됩니다. `vector_db/` 폴더는 `.gitignore`에 포함되어 있습니다.

3. **데이터 준비**: 실제 사용 전에 피부 관리 교본과 교재 데이터를 벡터 DB에 추가해야 합니다.

4. **성분 데이터**: 성분 데이터는 별도 모듈에서 관리되므로, 실제 연동 시 중계 모듈을 구현해야 합니다.

## 🐛 문제 해결

### OpenAI API 오류
- `.env` 파일에 올바른 API 키가 입력되어 있는지 확인하세요.
- API 키에 충분한 크레딧이 있는지 확인하세요.

### 벡터 DB 오류
- 벡터 DB가 초기화되지 않았다면 `python scripts/init_vector_db.py`를 실행하세요.
- 벡터 DB 경로에 쓰기 권한이 있는지 확인하세요.

### 모듈 import 오류
- 가상 환경이 활성화되어 있는지 확인하세요.
- `pip install -r requirements.txt`로 모든 패키지가 설치되었는지 확인하세요.

## 📚 참고 자료

- [LangChain 문서](https://python.langchain.com/)
- [OpenAI API 문서](https://platform.openai.com/docs)
- [Chroma 문서](https://docs.trychroma.com/)

## 🤝 기여하기

이 프로젝트는 학습 목적으로 제작되었습니다. 개선 사항이나 버그가 있다면 이슈를 등록해주세요.

## 📄 라이선스

이 프로젝트는 학습 목적으로 제작되었습니다.

---

**개발자 여러분을 응원합니다!** 💪
LLM Agent 강의를 듣고 도전하시는 분들을 위해 최대한 친절하고 자세하게 작성했습니다.
궁금한 점이 있으면 언제든지 질문해주세요! 😊
