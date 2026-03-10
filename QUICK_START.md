# 빠른 시작 가이드 🚀

개발자가 처음 시작할 때 해야 할 일들을 순서대로 정리했습니다.

## 1단계: uv 최신화 및 설치 확인

### uv 최신화
```bash
# PowerShell에서 실행
irm https://astral.sh/uv/install.ps1 | iex

# 또는 기존 uv 업데이트
pip install --upgrade uv
```

### uv 버전 확인
```bash
uv --version
```

## 2단계: uv 프로젝트 동기화(가상환경 + 패키지 설치)

`uv` 프로젝트 방식에서는 `pyproject.toml`을 기준으로 설치합니다.

```bash
# (프로젝트 루트에서)
uv sync
```

이 명령이 내부적으로:
- `.venv` 가상환경 생성
- `pyproject.toml` 의존성 설치
- (생성 가능하면) `uv.lock`으로 버전 고정

## 3단계: 설치 확인

**중요**: 이 단계에서 모든 패키지가 설치됩니다:
- LangChain 및 LangGraph
- OpenAI
- 벡터 DB (Chroma)
- 웹 검색 도구
- Streamlit 등

```bash
# Python에서 import 테스트
uv run python -c "import langchain; import langgraph; print('✅ 패키지 설치 완료')"
```

## 4단계: 환경 변수 설정

### .env 파일 생성
```bash
# .env.example을 복사
copy .env.example .env  # Windows
# 또는
cp .env.example .env    # Mac/Linux
```

### .env 파일 편집
`.env` 파일을 열어서 API 키를 입력하세요:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview
VECTOR_DB_PATH=./vector_db

# 웹 검색 API 키 (선택사항)
TAVILY_API_KEY=your_tavily_api_key_here
```

**⚠️ 주의**:
- `.env` 파일은 절대 Git에 커밋하지 마세요!
- `.gitignore`에 이미 포함되어 있습니다.

## 5단계: 벡터 DB 초기화

### 벡터 DB 초기화 스크립트 실행
```bash
python scripts/init_vector_db.py
```

이 스크립트는:
- 벡터 DB 폴더 생성
- 샘플 데이터 추가
- 검색 가능한 상태로 준비

**참고**: 현재는 샘플 데이터가 포함되어 있습니다. 실제 데이터가 준비되면 `scripts/init_vector_db.py`의 `load_sample_documents()` 함수를 수정하세요.

## 6단계: 프로그램 실행 테스트

### 커맨드라인 버전 실행
```bash
uv run python main.py
```

### Streamlit 웹 앱 실행
```bash
uv run streamlit run streamlit_app.py
```

브라우저에서 `http://localhost:8501`로 접속하면 됩니다.

## 문제 해결

### 오류: ModuleNotFoundError: No module named 'langgraph'
**원인**: 패키지가 설치되지 않았습니다.

**해결**:
```bash
# 가상환경이 활성화되어 있는지 확인
# 프롬프트 앞에 (venv) 또는 (beauilt-agent)가 있어야 함

# 패키지 재설치
uv pip install -r requirements.txt
```

### 오류: OpenAI API key not found
**원인**: `.env` 파일이 없거나 API 키가 설정되지 않았습니다.

**해결**:
1. `.env` 파일이 있는지 확인
2. `.env` 파일에 `OPENAI_API_KEY=your_key` 추가
3. 프로그램 재실행

### 오류: 벡터 DB 초기화 실패
**원인**: 벡터 DB가 초기화되지 않았습니다.

**해결**:
```bash
python scripts/init_vector_db.py
```

### uv 명령어가 작동하지 않을 때
**Windows에서 문제가 있을 경우**:
1. PowerShell을 관리자 권한으로 실행
2. 다음 명령어 실행:
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm https://astral.sh/uv/install.ps1 | iex
```

**또는 pip로 직접 설치**:
```bash
pip install uv
```

## 개발 워크플로우

### 일반적인 개발 흐름
1. 가상환경 활성화
2. 코드 수정
3. 테스트 실행
4. 변경사항 커밋

### 패키지 추가 시
```bash
# 패키지 설치
uv pip install 새패키지명

# requirements.txt 업데이트
uv pip freeze > requirements.txt
# 또는 수동으로 requirements.txt에 추가
```

### 코드 실행 전 체크리스트
- [ ] 가상환경 활성화됨
- [ ] 패키지 설치 완료
- [ ] `.env` 파일 설정됨
- [ ] 벡터 DB 초기화됨

## 다음 단계

프로그램이 정상적으로 실행되면:
1. `README.md` 읽기 - 프로젝트 전체 구조 이해
2. `DEVELOPMENT_GUIDE.md` 읽기 - 개발 가이드
3. `USAGE_EXAMPLES.md` 읽기 - 사용 예시
4. 코드 수정 및 테스트

## 유용한 명령어 모음

```bash
# 가상환경 활성화
.venv\Scripts\activate  # Windows

# 패키지 설치
uv pip install -r requirements.txt

# 벡터 DB 초기화
python scripts/init_vector_db.py

# 프로그램 실행
python main.py

# Streamlit 실행
streamlit run streamlit_app.py

# 가상환경 비활성화
deactivate
```

---

**문제가 발생하면 `README.md`의 "문제 해결" 섹션을 참고하세요!** 😊
