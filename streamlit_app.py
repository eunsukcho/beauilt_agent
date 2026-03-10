"""
Streamlit 웹 앱

뷰티 데일리팁 챗봇을 웹 인터페이스로 제공합니다.
"""

# 표준 라이브러리
import logging
import os
import uuid

# Third-party 라이브러리
import streamlit as st

# Streamlit Cloud secrets → 환경변수 동기화 (로컬 .env 없는 환경 대응)
try:
    for _k, _v in st.secrets.items():
        if isinstance(_v, str):
            os.environ.setdefault(_k.upper(), _v)
except Exception:
    pass

# 로컬 모듈
from db.chat_history import (
    delete_session,
    init_db,
    list_recent_sessions,
    load_session,
    save_message,
)
from db.tracker import (
    init_tracker_db,
    add_product,
    stop_product,
    list_active_products,
    list_all_products,
    save_skin_log,
    list_recent_skin_logs,
    get_skin_log,
    CATEGORIES,
    END_REASONS,
)
from workflow.graph import workflow_graph
from workflow.chat_handler import (
    DEFAULT_RESPONSE,
    build_initial_state,
    extract_response,
    handle_followup_question,
    is_followup_question,
    run_workflow,
    update_context,
    validate_user_input,
)
from vector_db import vector_store

# 로깅 설정
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("beauilt-agent.streamlit")

# 세션당 최대 메시지 수 (user + assistant 합산)
MAX_MESSAGES = 50

# 페이지 설정
st.set_page_config(
    page_title="뷰티 데일리팁 챗봇 💄",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #ff6b9d, #c44569);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #f3e5f5;
        margin-right: 20%;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background: linear-gradient(90deg, #ff6b9d, #c44569);
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_vector_db():
    """벡터 DB 초기화 (캐시 사용)"""
    try:
        # 벡터 DB가 이미 초기화되어 있는지 확인
        if os.path.exists(vector_store.persist_directory) and os.listdir(vector_store.persist_directory):
            vector_store.initialize_vector_store()
            return True
        else:
            # 벡터 DB가 없으면 초기화 스크립트 실행
            from scripts.init_vector_db import init_vector_db
            init_vector_db()
            return True
    except Exception as e:
        st.error(f"벡터 DB 초기화 중 오류 발생: {e}")
        return False


def initialize_session_state():
    """세션 상태 초기화"""
    # DB 초기화 (테이블 없으면 생성)
    init_db()
    init_tracker_db()

    # 세션 ID — URL 파라미터로 새로고침 후에도 유지
    if "session_id" not in st.session_state:
        params = st.experimental_get_query_params()
        if "sid" in params:
            sid = params["sid"][0]
            st.session_state.session_id = sid
            # DB에서 이전 대화 복원
            st.session_state.messages = load_session(sid)
        else:
            sid = str(uuid.uuid4())
            st.session_state.session_id = sid
            st.experimental_set_query_params(sid=sid)
            st.session_state.messages = []

    if "workflow" not in st.session_state:
        st.session_state.workflow = workflow_graph

    if "vector_db_initialized" not in st.session_state:
        with st.spinner("벡터 DB를 초기화하는 중..."):
            initialize_vector_db()
        st.session_state.vector_db_initialized = True

    if "previous_context" not in st.session_state:
        st.session_state.previous_context = {
            "diagnosis_result": None,
            "analysis_result": None,
            "care_guide": None,
        }

    # 제품 목록 세션 캐시 — 매 메시지마다 DB 조회하지 않도록
    if "cached_products" not in st.session_state:
        st.session_state.cached_products = list_active_products()

    # 인증 상태 및 요청 카운터
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "request_count" not in st.session_state:
        st.session_state.request_count = 0


def trim_messages() -> None:
    """메시지가 최대치를 초과하면 오래된 것부터 제거"""
    if len(st.session_state.messages) > MAX_MESSAGES:
        st.session_state.messages = st.session_state.messages[-MAX_MESSAGES:]


def process_user_input(user_input: str) -> str:
    """
    사용자 입력을 처리하고 응답 반환

    Args:
        user_input: 사용자 입력

    Returns:
        AI 응답
    """
    # 요청 한도 확인
    from config import get_settings
    limit = get_settings().max_requests_per_session
    if st.session_state.request_count >= limit:
        return f"이번 세션의 요청 한도({limit}회)에 도달했습니다. 페이지를 새로고침하면 다시 이용할 수 있습니다."

    # 입력 검증
    try:
        user_input = validate_user_input(user_input)
    except ValueError as e:
        return str(e)

    # 종료 명령
    if user_input.lower() in {"종료", "exit", "quit", "bye"}:
        return "이용해 주셔서 감사합니다! 건강한 피부 되세요!"

    has_history = len(st.session_state.messages) > 0
    is_followup = is_followup_question(user_input, has_history)

    # 대화 히스토리 변환 (Streamlit messages → chat_handler 형식)
    recent_messages = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in st.session_state.messages[-6:]  # 최근 3쌍
    ]

    initial_state = build_initial_state(
        user_input,
        st.session_state.previous_context,
        [
            {"user": m["content"], "assistant": recent_messages[i + 1]["content"]}
            for i, m in enumerate(recent_messages[:-1])
            if m["role"] == "user" and i + 1 < len(recent_messages)
        ],
        active_products=st.session_state.get("cached_products"),
    )

    try:
        last_node_output = run_workflow(st.session_state.workflow, initial_state)

        if not last_node_output:
            return DEFAULT_RESPONSE

        # 오류 처리
        if last_node_output.get("error"):
            logger.warning("워크플로우 오류: %s", last_node_output["error"])
            return "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."

        # 추가 질문 처리
        if is_followup:
            return handle_followup_question(
                user_input,
                st.session_state.previous_context,
                recent_messages,
            )

        # 응답 추출 및 컨텍스트 업데이트
        response = extract_response(last_node_output)
        if response:
            update_context(st.session_state.previous_context, last_node_output)
            return response

        return DEFAULT_RESPONSE

    except Exception as e:
        logger.error("워크플로우 실행 오류: %s", e, exc_info=True)
        return "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."


def render_login_page(required_password: str) -> None:
    """비밀번호 입력 화면"""
    st.markdown("""
    <div style="max-width:400px; margin:100px auto; text-align:center;">
        <h2>🔒 접근 제한</h2>
        <p>서비스를 이용하려면 비밀번호를 입력하세요.</p>
    </div>
    """, unsafe_allow_html=True)

    col = st.columns([1, 2, 1])[1]
    with col:
        pw = st.text_input("비밀번호", type="password", label_visibility="collapsed",
                           placeholder="비밀번호 입력")
        if st.button("입장", use_container_width=True):
            if pw == required_password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("비밀번호가 틀렸습니다.")


def render_chat_tab():
    """챗봇 탭 UI"""
    # 사이드바
    with st.sidebar:
        st.header("📋 기능 안내")
        st.markdown("""
        **주요 기능:**
        1. 🩺 피부 상태 진단
        2. 📊 전체 상황 분석
        3. 📝 케어 가이드라인 제공
        4. 🔮 시뮬레이션 (변화 예측)
        5. 🧪 성분 분석

        **사용 팁:**
        - 피부 상태를 설명해주시면 자동으로 진단 → 분석 → 가이드까지 제공됩니다!
        - "시뮬레이션"이라고 말씀하시면 변화 예측을 보여드립니다.
        - "성분"에 대해 물어보시면 성분 분석을 해드립니다.
        """)

        st.markdown("---")
        st.markdown("**💡 예시 질문:**")
        st.markdown("""
        - "제 피부가 자꾸 번들거려요"
        - "트러블이 생겨요"
        - "건조한 피부 케어 방법 알려주세요"
        - "나이아신아마이드가 좋을까요?"
        """)

        st.markdown("---")

        if st.button("✏️ 새 대화 시작"):
            new_sid = str(uuid.uuid4())
            st.session_state.session_id = new_sid
            st.session_state.messages = []
            st.session_state.previous_context = {
                "diagnosis_result": None,
                "analysis_result": None,
                "care_guide": None,
            }
            st.experimental_set_query_params(sid=new_sid)
            st.rerun()

        if st.button("🗑️ 현재 대화 삭제"):
            delete_session(st.session_state.session_id)
            st.session_state.messages = []
            st.session_state.previous_context = {
                "diagnosis_result": None,
                "analysis_result": None,
                "care_guide": None,
            }
            st.rerun()

        st.markdown("---")
        st.markdown("**🕘 이전 대화**")
        recent = list_recent_sessions(limit=8)
        current_sid = st.session_state.session_id
        for s in recent:
            label = f"{s['started_at']}  {s['preview']}"
            is_current = s["session_id"] == current_sid
            if is_current:
                st.markdown(f"▶ **{label}**")
            elif st.button(label, key=f"hist_{s['session_id']}"):
                st.session_state.session_id = s["session_id"]
                st.session_state.messages = load_session(s["session_id"])
                st.session_state.previous_context = {
                    "diagnosis_result": None,
                    "analysis_result": None,
                    "care_guide": None,
                }
                st.experimental_set_query_params(sid=s["session_id"])
                st.rerun()

    # 요청 횟수 표시
    from config import get_settings
    limit = get_settings().max_requests_per_session
    remaining = limit - st.session_state.request_count
    st.caption(f"남은 요청 횟수: {remaining}/{limit}")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("피부 관리에 대해 물어보세요..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_message(st.session_state.session_id, "user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("분석 중입니다... 💭"):
                response = process_user_input(prompt)
                st.markdown(response)
                st.session_state.request_count += 1

        st.session_state.messages.append({"role": "assistant", "content": response})
        save_message(st.session_state.session_id, "assistant", response)
        trim_messages()

    if len(st.session_state.messages) == 0:
        st.info("👋 안녕하세요! 피부 관리 전문가입니다. 피부 상태를 설명해주시면 맞춤형 조언을 드리겠습니다!")


def render_product_tab():
    """제품 관리 탭 UI"""
    import datetime

    st.subheader("제품 등록")
    with st.form("add_product_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("제품명 *")
            brand = st.text_input("브랜드")
            category = st.selectbox("카테고리 *", CATEGORIES)
        with col2:
            started_at = st.date_input("사용 시작일 *", value=datetime.date.today())
            ingredients = st.text_area("주요 성분 (선택)", height=80)

        submitted = st.form_submit_button("등록")
        if submitted:
            if not name:
                st.error("제품명을 입력해주세요.")
            else:
                add_product(name, brand, category, str(started_at), ingredients)
                st.session_state.cached_products = list_active_products()
                st.success(f"'{name}' 등록 완료!")
                st.rerun()

    st.markdown("---")
    st.subheader("사용 중인 제품")
    active = list_active_products()
    if not active:
        st.info("등록된 제품이 없습니다.")
    else:
        for p in active:
            with st.expander(f"🧴 {p['name']}  |  {p['category']}  |  {p['started_at']} ~"):
                st.write(f"**브랜드:** {p['brand'] or '-'}")
                if p['ingredients']:
                    st.write(f"**성분:** {p['ingredients']}")

                with st.form(f"stop_form_{p['id']}", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        ended_at = st.date_input("중단일", value=datetime.date.today(),
                                                  key=f"end_date_{p['id']}")
                    with col2:
                        reason = st.selectbox("중단 이유", END_REASONS,
                                              key=f"reason_{p['id']}")
                    if st.form_submit_button("사용 중단"):
                        stop_product(p['id'], str(ended_at), reason)
                        st.session_state.cached_products = list_active_products()
                        st.rerun()

    st.markdown("---")
    st.subheader("전체 제품 이력")
    all_products = list_all_products()
    stopped = [p for p in all_products if p['ended_at']]
    if stopped:
        for p in stopped:
            st.markdown(
                f"~~{p['name']}~~ &nbsp; `{p['category']}` &nbsp; "
                f"{p['started_at']} ~ {p['ended_at']} &nbsp; ({p['end_reason'] or '-'})"
            )
    else:
        st.caption("중단된 제품이 없습니다.")


def render_skin_log_tab():
    """피부 일지 탭 UI"""
    import datetime

    st.subheader("오늘의 피부 상태 기록")
    today = datetime.date.today()
    existing = get_skin_log(str(today))

    with st.form("skin_log_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            moisture = st.slider("수분감", 1, 5,
                                 value=existing["moisture"] if existing else 3,
                                 help="1=매우건조 / 5=촉촉함")
        with col2:
            oiliness = st.slider("유분감", 1, 5,
                                 value=existing["oiliness"] if existing else 3,
                                 help="1=전혀없음 / 5=매우번들")
        with col3:
            trouble = st.slider("트러블", 1, 5,
                                value=existing["trouble"] if existing else 1,
                                help="1=없음 / 5=심함")
        memo = st.text_area("메모 (선택)", value=existing["memo"] if existing else "",
                            placeholder="오늘 피부 특이사항을 적어주세요")

        label = "수정" if existing else "저장"
        if st.form_submit_button(label):
            save_skin_log(str(today), moisture, oiliness, trouble, memo)
            st.success("오늘의 피부 일지가 저장되었습니다!")
            st.rerun()

    st.markdown("---")
    st.subheader("최근 피부 일지")
    logs = list_recent_skin_logs(limit=10)
    if not logs:
        st.info("기록된 피부 일지가 없습니다.")
    else:
        for log in logs:
            with st.expander(f"📅 {log['log_date']}"):
                col1, col2, col3 = st.columns(3)
                col1.metric("수분감", f"{log['moisture']}/5")
                col2.metric("유분감", f"{log['oiliness']}/5")
                col3.metric("트러블", f"{log['trouble']}/5")
                if log['memo']:
                    st.caption(log['memo'])


def main():
    """메인 함수"""
    initialize_session_state()

    # 비밀번호 게이트
    from config import get_settings
    required_pw = get_settings().app_password
    if required_pw and not st.session_state.authenticated:
        render_login_page(required_pw)
        return

    st.markdown("""
    <div class="main-header">
        <h1>✨ 뷰티 데일리팁 챗봇 💄</h1>
        <p>전문 피부관리사가 직접 케어해주는 것처럼 따뜻하고 친근한 피부 관리 조언을 제공합니다</p>
    </div>
    """, unsafe_allow_html=True)

    # 사이드바 상단에 페이지 선택 (chat_input은 탭 안에 넣을 수 없어 페이지 방식 사용)
    with st.sidebar:
        page = st.radio("페이지", ["💬 챗봇", "🧴 제품 관리", "📓 피부 일지"],
                        label_visibility="collapsed")

    if page == "💬 챗봇":
        render_chat_tab()
    elif page == "🧴 제품 관리":
        render_product_tab()
    else:
        render_skin_log_tab()


if __name__ == "__main__":
    main()
