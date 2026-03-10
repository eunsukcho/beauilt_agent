# 개발 가이드 📖

이 문서는 LLM Agent 강의를 듣고 처음 도전하는 개발자를 위한 상세한 개발 가이드입니다.

## 🎓 LLM Agent 기본 개념

### 에이전트(Agent)란?
에이전트는 사용자의 요청을 받아 적절한 도구(도구, 데이터베이스 등)를 사용하여 작업을 수행하는 AI 시스템입니다.

이 프로젝트에서는:
- **에이전트**: 각 기능별 전문가 (피부 진단, 분석, 케어 가이드 등)
- **도구**: 벡터 DB 검색, LLM 호출 등
- **메모리**: 대화 히스토리, 사용자 세션 정보

### 벡터 DB란?
벡터 DB는 텍스트를 숫자 배열(벡터)로 변환하여 저장하고, 의미적으로 유사한 텍스트를 빠르게 찾을 수 있는 데이터베이스입니다.

**작동 원리**:
1. 문서를 작은 청크로 나눔
2. 각 청크를 벡터(숫자 배열)로 변환 (Embedding)
3. 사용자 질문도 벡터로 변환
4. 유사도가 높은 문서를 찾아 반환

## 📂 프로젝트 구조 이해하기

### 1. `config/settings.py` - 설정 관리
환경 변수에서 API 키와 설정값을 읽어옵니다.

**왜 필요한가?**
- API 키를 코드에 직접 작성하면 보안 위험
- 환경별로 다른 설정 사용 가능 (개발/운영)

**사용 방법**:
```python
from config import get_settings

settings = get_settings()
api_key = settings.openai_api_key
```

### 2. `vector_db/vector_store.py` - 벡터 DB 관리
피부 관리 교본을 벡터화하여 저장하고 검색합니다.

**주요 메서드**:
- `initialize_vector_store()`: 벡터 DB 초기화
- `add_documents()`: 문서 추가
- `similarity_search()`: 유사도 검색

**사용 예시**:
```python
from vector_db import vector_store

# 문서 추가
documents = [Document(page_content="피부 관리 방법...", metadata={...})]
vector_store.add_documents(documents)

# 검색
results = vector_store.similarity_search("트러블 관리", k=5)
```

### 3. `agents/base_agent.py` - 기본 에이전트
모든 에이전트의 공통 기능을 제공합니다.

**주요 기능**:
- LLM 초기화 및 호출
- 벡터 DB 검색
- 대화 히스토리 관리
- 프롬프트 구성

**상속하여 사용**:
```python
class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__("에이전트이름", "시스템 프롬프트")

    def process(self, user_input: str, **kwargs) -> str:
        # 에이전트 로직 구현
        pass
```

### 4. 각 에이전트 파일들
각 에이전트는 특정 기능을 담당합니다.

**에이전트 간 데이터 전달**:
- `diagnosis_result`: 피부 진단 결과
- `analysis_result`: 종합 분석 결과
- `care_guide`: 케어 가이드라인

이 정보들은 `main.py`의 `user_session`에 저장되어 에이전트 간에 공유됩니다.

## 🔄 실행 흐름 이해하기

### 1. 프로그램 시작
```
main.py 실행
  ↓
BeautyChatbot 초기화
  ↓
각 에이전트 인스턴스 생성
  ↓
대화 루프 시작
```

### 2. 사용자 입력 처리
```
사용자 입력
  ↓
route_request() - 요청 분석
  ↓
적절한 에이전트 선택
  ↓
에이전트.process() 호출
  ↓
벡터 DB 검색 (필요시)
  ↓
프롬프트 구성
  ↓
LLM 호출
  ↓
응답 반환
```

### 3. 에이전트 내부 처리
```
process() 메서드 호출
  ↓
search_knowledge_base() - 벡터 DB 검색
  ↓
build_prompt() - 프롬프트 구성
  ↓
generate_response() - LLM 호출
  ↓
add_to_history() - 히스토리 저장
  ↓
응답 반환
```

## 💻 코드 수정 가이드

### 1. 말투 변경하기
각 에이전트의 `system_prompt`를 수정하세요.

**위치**: `agents/*_agent.py` 파일의 `__init__()` 메서드

**예시**:
```python
system_prompt = """당신은 전문 피부 관리사입니다.
말투는 더욱 친근하고...  # 여기를 수정
"""
```

### 2. 벡터 DB 검색 개수 변경하기
`search_knowledge_base()` 호출 시 `k` 파라미터를 조정하세요.

**예시**:
```python
context = self.search_knowledge_base(query, k=10)  # 기본값 5에서 10으로 변경
```

### 3. LLM 모델 변경하기
`.env` 파일에서 모델을 변경하거나 `config/settings.py`에서 기본값을 변경하세요.

**예시**:
```env
OPENAI_MODEL=gpt-3.5-turbo
```

### 4. 대화 히스토리 개수 변경하기
`agents/base_agent.py`의 `generate_response()` 메서드에서 히스토리 개수를 조정하세요.

**예시**:
```python
for conv in self.conversation_history[-10:]:  # 최근 10개로 변경
```

## 📊 데이터 구조 이해하기

### Document 객체
벡터 DB에 저장되는 문서 형식입니다.

```python
Document(
    page_content="실제 텍스트 내용",
    metadata={
        "source": "출처",
        "type": "문서 타입"
    }
)
```

### 대화 히스토리
```python
[
    {
        "user": "사용자 입력",
        "assistant": "AI 응답"
    },
    ...
]
```

### 사용자 세션
```python
{
    "diagnosis_result": "진단 결과 텍스트",
    "analysis_result": "분석 결과 텍스트",
    "care_guide": "가이드라인 텍스트"
}
```

## 🐛 디버깅 팁

### 1. 벡터 DB 검색 결과 확인
```python
results = vector_store.similarity_search("질문", k=5)
for i, doc in enumerate(results):
    print(f"결과 {i+1}: {doc.page_content[:100]}...")
```

### 2. 프롬프트 확인
```python
prompt = self.build_prompt(user_input, context)
print("=== 프롬프트 ===")
print(prompt)
```

### 3. LLM 응답 확인
`agents/base_agent.py`의 `generate_response()` 메서드에 로그 추가:
```python
response = self.llm.invoke(messages)
print(f"LLM 응답: {response.content}")  # 추가
return response.content
```

## 🔧 성능 최적화 팁

### 1. 벡터 DB 검색 최적화
- 필요한 만큼만 검색 (`k` 값 조정)
- 검색 쿼리를 구체적으로 작성

### 2. 프롬프트 최적화
- 시스템 프롬프트를 명확하게 작성
- 불필요한 컨텍스트 제거

### 3. 대화 히스토리 관리
- 너무 많은 히스토리는 토큰 낭비
- 필요한 만큼만 유지 (현재: 최근 5개)

## 📚 학습 자료

### LangChain 기본 개념
1. **LLM**: 언어 모델 (OpenAI GPT 등)
2. **Prompt**: LLM에 전달하는 입력
3. **Chain**: 여러 단계를 연결한 처리 흐름
4. **Agent**: 도구를 사용하는 AI 시스템
5. **Memory**: 대화 히스토리 저장

### 벡터 DB 기본 개념
1. **Embedding**: 텍스트를 벡터로 변환
2. **Similarity Search**: 유사도 검색
3. **Chunking**: 문서를 작은 단위로 분할

## ❓ 자주 묻는 질문

### Q1: 벡터 DB에 데이터를 추가하려면?
A: `scripts/init_vector_db.py`의 `load_sample_documents()` 함수를 수정하세요.

### Q2: 성분 데이터는 어떻게 연동하나요?
A: `agents/ingredient_analysis_agent.py`의 `get_ingredient_data()` 메서드를 수정하여 중계 모듈을 호출하세요.

### Q3: 에이전트를 추가하려면?
A: `agents/` 폴더에 새 파일을 만들고 `BaseAgent`를 상속받아 구현하세요. `main.py`에도 추가해야 합니다.

### Q4: API 키 오류가 발생해요
A: `.env` 파일에 올바른 API 키가 입력되어 있는지 확인하세요.

### Q5: 벡터 DB가 비어있어요
A: `python scripts/init_vector_db.py`를 실행하여 데이터를 추가하세요.

## 🎯 다음 단계

1. **실제 데이터 추가**: 피부 관리 교본과 교재를 벡터 DB에 추가
2. **성분 데이터 연동**: RDB와 연동하는 중계 모듈 구현
3. **에이전트 개선**: 프롬프트 튜닝 및 기능 추가
4. **UI 개발**: 웹 인터페이스 또는 챗봇 UI 추가
5. **테스트**: 다양한 시나리오로 테스트

---

**궁금한 점이 있으면 언제든지 질문해주세요!** 😊
