# uv를 사용한 프로젝트 설정 가이드 🚀

`uv`는 매우 빠른 Python 패키지 관리자이자 프로젝트 관리 도구입니다.

## uv 설치

### Windows (PowerShell)
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

### 또는 pip로 설치
```bash
pip install uv
```

### 설치 확인
```bash
uv --version
```

## 프로젝트 설정 방법

### 방법 1: 기존 requirements.txt 사용 (간단)

```bash
# 가상환경 생성 및 패키지 설치 (한 번에!)
uv venv

# 가상환경 활성화
# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate

# requirements.txt에서 패키지 설치
uv pip install -r requirements.txt
```

### 방법 2: uv 프로젝트로 초기화 (권장)

```bash
# 프로젝트 초기화 (Python 버전 자동 감지)
uv init

# 또는 특정 Python 버전 지정
uv init --python 3.11

# 패키지 추가 (자동으로 pyproject.toml에 추가됨)
uv add langchain langchain-openai langchain-community
uv add chromadb
uv add python-dotenv
uv add pydantic pydantic-settings
uv add openai
uv add tiktoken
```

### 방법 3: requirements.txt를 pyproject.toml로 변환

```bash
# uv로 requirements.txt를 읽어서 설치
uv pip install -r requirements.txt

# 또는 pyproject.toml 생성 후
uv add -r requirements.txt
```

## uv 주요 명령어

### 가상환경 관리
```bash
# 가상환경 생성 (기본 이름: .venv)
uv venv

# 원하는 이름으로 가상환경 생성
uv venv venv          # venv 폴더 생성
uv venv myenv         # myenv 폴더 생성
uv venv env           # env 폴더 생성

# 특정 Python 버전으로 가상환경 생성
uv venv --python 3.11

# 이름과 Python 버전 동시 지정
uv venv venv --python 3.11

# 가상환경 활성화 (수동)
# 기본 이름(.venv) 사용 시
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate

# 커스텀 이름(venv) 사용 시
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
```

### 패키지 관리
```bash
# 패키지 추가
uv add requests

# 개발 의존성 추가
uv add --dev pytest

# 패키지 제거
uv remove requests

# 패키지 업데이트
uv sync --upgrade

# 모든 패키지 설치 (pyproject.toml 기반)
uv sync
```

### 실행
```bash
# 가상환경 내에서 스크립트 실행
uv run python main.py

# 또는 직접 실행 (가상환경 자동 활성화)
uv run main.py
```

## 현재 프로젝트에 적용하기

### 빠른 시작 (requirements.txt 사용)

```bash
# 1. uv 설치 확인
uv --version

# 2. 가상환경 생성
uv venv

# 3. 가상환경 활성화
.venv\Scripts\activate  # Windows

# 4. 패키지 설치
uv pip install -r requirements.txt

# 5. 실행
python main.py
```

### 프로젝트 초기화 방식 (권장)

```bash
# 1. 프로젝트 초기화
uv init

# 2. 패키지 추가
uv add langchain==0.1.0 langchain-openai==0.0.2 langchain-community==0.0.10
uv add chromadb==0.4.22
uv add python-dotenv==1.0.0
uv add pydantic==2.5.3 pydantic-settings==2.1.0
uv add openai==1.6.1
uv add tiktoken==0.5.2

# 3. 실행
uv run python main.py
```

## uv의 장점

1. **매우 빠름**: pip보다 10-100배 빠른 패키지 설치
2. **자동 가상환경 관리**: `uv run`으로 자동 활성화
3. **의존성 해결**: 더 나은 의존성 해결 알고리즘
4. **Python 버전 관리**: pyproject.toml에서 Python 버전 지정 가능

## 가상환경 이름 정리

### 기본 동작
- `uv venv` 명령어만 실행하면 → **`.venv`** 폴더 생성 (숨김 폴더)
- 이는 Python 커뮤니티의 표준 관행입니다

### 커스텀 이름 사용
```bash
# venv 폴더로 생성하고 싶다면
uv venv venv

# 다른 이름으로 생성
uv venv myenv
uv venv env
```

### 비교
| 명령어 | 생성되는 폴더 | 특징 |
|--------|--------------|------|
| `uv venv` | `.venv` | 기본값, 숨김 폴더 |
| `uv venv venv` | `venv` | 일반 폴더, venv와 동일한 이름 |
| `python -m venv venv` | `venv` | 표준 venv 방식 |

**추천**: 기본값인 `.venv`를 사용하는 것을 권장합니다. 프로젝트 루트가 깔끔해집니다!

## .gitignore 업데이트

uv를 사용하면 `.venv` 또는 지정한 이름의 폴더가 생성되므로 `.gitignore`에 추가되어 있는지 확인하세요.
(이미 `.venv/`와 `venv/` 모두 추가되어 있습니다!)

## 참고 자료

- [uv 공식 문서](https://docs.astral.sh/uv/)
- [uv GitHub](https://github.com/astral-sh/uv)
