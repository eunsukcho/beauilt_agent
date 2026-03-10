# 라우터가 호출되는 과정 설명 🚀

Python 초보자를 위한 단계별 설명입니다.

## 📍 `initial_router()` 함수가 호출되는 위치

### 1단계: 함수 등록 (workflow/graph.py)

```python
# workflow/graph.py의 96번째 줄
workflow.add_node("router", initial_router)  # ← 여기서 함수를 등록!
```

**의미**: 
- `initial_router` 함수를 "router"라는 이름의 노드로 등록
- 아직 호출하지 않음! 단지 "이 함수를 사용할 거야"라고 등록만 함

### 2단계: 시작점 설정 (workflow/graph.py)

```python
# workflow/graph.py의 104번째 줄
workflow.set_entry_point("router")  # ← "router" 노드부터 시작하겠다!
```

**의미**:
- 워크플로우가 시작될 때 "router" 노드를 먼저 실행하겠다고 설정
- 아직 호출하지 않음! 단지 "시작점을 정해둔" 상태

### 3단계: 실제 호출 (main.py 또는 streamlit_app.py)

#### 방법 1: main.py에서 호출

```python
# main.py의 127번째 줄
for output in self.workflow.stream(initial_state):  # ← 여기서 실제로 호출됨!
    final_state = output
```

#### 방법 2: streamlit_app.py에서 호출

```python
# streamlit_app.py의 182번째 줄
for output in st.session_state.workflow.stream(initial_state):  # ← 여기서 실제로 호출됨!
    final_state = output
```

**의미**:
- `workflow.stream(initial_state)`를 호출하면
- LangGraph가 자동으로 `set_entry_point("router")`로 설정한 노드를 찾아서
- `initial_router(initial_state)` 함수를 **자동으로 호출**합니다!

## 🔄 전체 흐름도

```
1. 프로그램 시작
   ↓
2. main.py의 process_user_input() 실행
   ↓
3. initial_state = {...}  (사용자 입력 포함)
   ↓
4. self.workflow.stream(initial_state) 호출
   ↓
5. LangGraph가 "router" 노드를 찾음
   ↓
6. LangGraph가 initial_router(initial_state) 자동 호출! ⭐
   ↓
7. initial_router()가 의도를 분류하고 state 업데이트
   ↓
8. route_by_intent()로 다음 노드 결정
   ↓
9. 다음 노드로 이동 (diagnosis, ingredient_analysis 등)
```

## 💡 핵심 개념

### Python에서 함수를 호출하는 방법

**일반적인 방법**:
```python
def my_function():
    print("안녕!")

my_function()  # ← 직접 호출
```

**LangGraph의 방법**:
```python
def initial_router(state):
    return state

# 1. 함수를 등록만 함 (호출 안 함)
workflow.add_node("router", initial_router)

# 2. 시작점 설정 (호출 안 함)
workflow.set_entry_point("router")

# 3. stream()을 호출하면 LangGraph가 자동으로 initial_router() 호출!
workflow.stream(state)  # ← 이때 LangGraph가 내부적으로 initial_router() 호출
```

## 📂 파일별 역할

| 파일 | 역할 | 호출 여부 |
|------|------|----------|
| `workflow/router.py` | `initial_router()` 함수 정의 | ❌ 호출 안 함 (정의만) |
| `workflow/graph.py` | 함수를 노드로 등록 | ❌ 호출 안 함 (등록만) |
| `main.py` | `workflow.stream()` 호출 | ✅ **여기서 실제 호출!** |
| `streamlit_app.py` | `workflow.stream()` 호출 | ✅ **여기서 실제 호출!** |

## 🎯 실제 코드 위치

### `initial_router()` 함수 정의
- **파일**: `workflow/router.py`
- **줄**: 16번째 줄
- **역할**: 함수를 정의만 함 (아직 호출 안 됨)

### `initial_router()` 함수 등록
- **파일**: `workflow/graph.py`
- **줄**: 96번째 줄 (`workflow.add_node("router", initial_router)`)
- **역할**: 함수를 워크플로우에 등록

### `initial_router()` 실제 호출
- **파일**: `main.py`
- **줄**: 127번째 줄 (`self.workflow.stream(initial_state)`)
- **역할**: LangGraph가 자동으로 `initial_router()` 호출

또는

- **파일**: `streamlit_app.py`
- **줄**: 182번째 줄 (`st.session_state.workflow.stream(initial_state)`)
- **역할**: LangGraph가 자동으로 `initial_router()` 호출

## 🔍 더 자세히 보기

`main.py`의 127번째 줄을 보면:

```python
for output in self.workflow.stream(initial_state):
    final_state = output
```

이 코드가 실행되면:
1. LangGraph가 `set_entry_point("router")`를 확인
2. "router" 노드가 `initial_router` 함수임을 확인
3. **자동으로 `initial_router(initial_state)` 호출**
4. 결과를 받아서 다음 노드로 전달

**중요**: Python에서는 함수 이름만 전달하면 나중에 호출할 수 있습니다!

```python
# 함수 정의
def my_function():
    print("호출됨!")

# 함수 이름을 변수에 저장 (호출 안 함)
func = my_function  # ← 괄호 없음!

# 나중에 호출
func()  # ← 이제 호출됨!
```

LangGraph도 같은 원리로 작동합니다!
