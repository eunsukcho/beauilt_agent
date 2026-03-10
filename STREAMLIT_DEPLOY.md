# Streamlit 배포 가이드 🚀

이 가이드에서는 뷰티 데일리팁 챗봇을 Streamlit Cloud에 배포하는 방법을 설명합니다.

## 배포 옵션

### 1. Streamlit Cloud (무료, 추천!)
- **장점**: 완전 무료, 자동 배포, HTTPS 지원
- **단점**: 공개 저장소 필요 (GitHub)
- **URL**: https://streamlit.io/cloud

### 2. 다른 옵션들
- **Heroku**: 유료 (무료 티어 종료)
- **Railway**: 무료 티어 있음
- **Render**: 무료 티어 있음
- **AWS/GCP/Azure**: 유료 (프리 티어 있음)

## Streamlit Cloud 배포 방법

### 1. GitHub에 코드 업로드

```bash
# Git 초기화 (아직 안 했다면)
git init
git add .
git commit -m "Initial commit"

# GitHub에 저장소 생성 후
git remote add origin https://github.com/your-username/beauilt-agent.git
git push -u origin main
```

### 2. Streamlit Cloud에 연결

1. **Streamlit Cloud 접속**: https://share.streamlit.io/
2. **GitHub로 로그인**
3. **"New app" 클릭**
4. **저장소 선택**: `your-username/beauilt-agent`
5. **메인 파일 경로**: `streamlit_app.py`
6. **브랜치**: `main` (또는 `master`)
7. **고급 설정**:
   - Python 버전: 3.11
   - Secrets: 환경 변수 추가 (아래 참고)

### 3. 환경 변수 설정 (Secrets)

Streamlit Cloud의 "Secrets" 섹션에 다음을 추가:

```toml
[secrets]
OPENAI_API_KEY = "your_openai_api_key_here"
```

또는 Streamlit Cloud 대시보드에서:
1. 앱 설정 → Secrets
2. 다음 형식으로 입력:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. 배포 완료!

배포가 완료되면 자동으로 URL이 생성됩니다:
```
https://your-app-name.streamlit.app
```

## 로컬에서 테스트하기

배포 전에 로컬에서 테스트:

```bash
# uv 프로젝트 의존성 설치 + 가상환경 생성
uv sync

# 앱 실행
uv run streamlit run streamlit_app.py
```

브라우저에서 `http://localhost:8501`로 접속하면 됩니다.

## 필수 파일 확인

배포 전에 다음 파일들이 있는지 확인:

1. ✅ `streamlit_app.py` - Streamlit 앱 파일
2. ✅ `requirements.txt` - 패키지 의존성
3. ✅ `.streamlit/config.toml` - Streamlit 설정 (선택사항)
4. ✅ `.env.example` - 환경 변수 예시 (참고용)

## 주의사항

### 1. API 키 보안
- ❌ **절대** `.env` 파일을 Git에 커밋하지 마세요!
- ✅ Streamlit Cloud의 Secrets 사용
- ✅ `.gitignore`에 `.env` 추가 확인

### 2. 벡터 DB
- 벡터 DB는 로컬 파일 시스템에 저장됩니다
- Streamlit Cloud는 임시 파일 시스템을 사용하므로 재시작 시 초기화될 수 있습니다
- **해결책**:
  - 벡터 DB를 클라우드 스토리지에 저장 (S3, GCS 등)
  - 또는 매번 초기화하도록 설정

### 3. 리소스 제한
- Streamlit Cloud 무료 티어는 리소스 제한이 있습니다
- 많은 사용자가 동시에 접속하면 느려질 수 있습니다

## 벡터 DB 문제 해결

Streamlit Cloud는 임시 파일 시스템을 사용하므로, 벡터 DB를 초기화하도록 수정:

### 방법 1: 매번 초기화 (간단하지만 느림)

`streamlit_app.py`에 추가:
```python
@st.cache_resource
def initialize_vector_db():
    """벡터 DB 초기화 (캐시 사용)"""
    from scripts.init_vector_db import init_vector_db
    init_vector_db()
    return True

# 앱 시작 시 초기화
if "vector_db_initialized" not in st.session_state:
    initialize_vector_db()
    st.session_state.vector_db_initialized = True
```

### 방법 2: 클라우드 스토리지 사용 (권장)

벡터 DB를 S3나 다른 클라우드 스토리지에 저장하고 로드하도록 수정합니다.

## 배포 후 확인사항

1. ✅ 앱이 정상적으로 로드되는가?
2. ✅ API 키가 제대로 설정되었는가?
3. ✅ 벡터 DB가 초기화되는가?
4. ✅ 웹 검색이 작동하는가?
5. ✅ 채팅이 정상적으로 동작하는가?

## 문제 해결

### 앱이 로드되지 않을 때
- `requirements.txt` 확인
- 로그 확인 (Streamlit Cloud 대시보드)
- Python 버전 확인

### API 키 오류
- Secrets에 올바르게 설정되었는지 확인
- 변수명이 정확한지 확인 (대소문자 구분)

### 벡터 DB 오류
- 벡터 DB 초기화 코드 확인
- 파일 경로 확인

## 추가 기능

### 커스텀 도메인
Streamlit Cloud Pro를 사용하면 커스텀 도메인을 연결할 수 있습니다.

### 비공개 앱
Streamlit Cloud는 기본적으로 공개 앱입니다. 비공개로 만들려면:
- Streamlit Cloud Pro 사용
- 또는 다른 플랫폼 사용 (Railway, Render 등)

## 참고 자료

- [Streamlit Cloud 문서](https://docs.streamlit.io/streamlit-cloud)
- [Streamlit 배포 가이드](https://docs.streamlit.io/deploy)
- [Streamlit Secrets 관리](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management)

---

**배포 성공을 기원합니다!** 🎉
