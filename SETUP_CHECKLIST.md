# 개발 환경 설정 체크리스트 ✅

개발을 시작하기 전에 확인해야 할 사항들을 체크리스트로 정리했습니다.

## 필수 사항

### 1. uv 설치 및 최신화
- [ ] uv 설치 확인: `uv --version`
- [ ] uv 최신화: `pip install --upgrade uv` 또는 `irm https://astral.sh/uv/install.ps1 | iex`

### 2. 가상환경 설정
- [ ] 가상환경 생성: `uv venv`
- [ ] 가상환경 활성화: `.venv\Scripts\activate` (Windows)
- [ ] 프롬프트에 `(venv)` 또는 `(beauilt-agent)` 표시 확인

### 3. 패키지 설치
- [ ] requirements.txt 설치: `uv pip install -r requirements.txt`
- [ ] 설치 확인: `python -c "import langchain; import langgraph; print('OK')"`

### 4. 환경 변수 설정
- [ ] `.env` 파일 생성: `copy .env.example .env`
- [ ] OpenAI API 키 입력: `OPENAI_API_KEY=your_key`
- [ ] (선택) Tavily API 키 입력: `TAVILY_API_KEY=your_key`

### 5. 벡터 DB 초기화
- [ ] 벡터 DB 초기화: `python scripts/init_vector_db.py`
- [ ] `vector_db/` 폴더 생성 확인

### 6. 실행 테스트
- [ ] 커맨드라인 실행: `python main.py`
- [ ] Streamlit 실행: `streamlit run streamlit_app.py`

## 선택 사항

### 개발 도구
- [ ] IDE 설정 (VSCode, PyCharm 등)
- [ ] Python 확장 설치
- [ ] Git 설정

### 추가 설정
- [ ] 실제 피부 관리 데이터 준비
- [ ] 성분 데이터베이스 연동 준비
- [ ] Streamlit Cloud 배포 준비

## 문제 발생 시

### ModuleNotFoundError
```bash
# 해결: 패키지 재설치
uv pip install -r requirements.txt
```

### API Key 오류
```bash
# 해결: .env 파일 확인
# OPENAI_API_KEY가 올바르게 설정되었는지 확인
```

### 벡터 DB 오류
```bash
# 해결: 벡터 DB 재초기화
python scripts/init_vector_db.py
```

## 다음 단계

모든 체크리스트를 완료했다면:
1. `QUICK_START.md` 읽기
2. `README.md` 읽기
3. `DEVELOPMENT_GUIDE.md` 읽기
4. 코드 수정 및 개발 시작!

---

**체크리스트를 모두 완료하면 개발을 시작할 수 있습니다!** 🎉
