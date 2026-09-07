import streamlit as st
from modules.theme import GENSPARK_THEME_CSS
from modules.state_manager import StateManager

st.set_page_config(
    page_title="AI 쇼핑 어시스턴트",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(GENSPARK_THEME_CSS, unsafe_allow_html=True)

# ============ 세션 상태 초기화 ============
if "current_page" not in st.session_state:
    st.session_state.current_page = "chatbot"

if "documents_loaded" not in st.session_state:
    saved_state = StateManager.load_state()
    st.session_state.documents_loaded = saved_state["documents_loaded"]
    st.session_state.index_loaded = saved_state["index_loaded"]
    st.session_state.chat_history = StateManager.load_chat_history()

# ============ 사이드바 네비게이션 (바 형식) ============
with st.sidebar:
    # 커스텀 CSS로 사이드바 좁게
    st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    .sidebar-header {
        text-align: center;
        padding: 20px 0;
        border-bottom: 1px solid #e5e7eb;
    }
    .sidebar-header img {
        width: 40px;
        height: 40px;
    }
    .nav-container {
        padding: 0;
    }
    .nav-item {
        padding: 20px 0;
        text-align: center;
        border-left: 4px solid transparent;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .nav-item:hover {
        background-color: #f3f4f6;
        border-left-color: #3b82f6;
        color: #3b82f6;
    }
    .nav-item.active {
        background-color: #e0e7ff;
        border-left-color: #3b82f6;
        color: #3b82f6;
        font-weight: 600;
    }
    .nav-icon {
        font-size: 28px;
        display: block;
        margin-bottom: 8px;
    }
    .nav-label {
        font-size: 11px;
        font-weight: 500;
        display: block;
    }
    </style>
    """, unsafe_allow_html=True)

    # 사이드바 헤더
    st.markdown("""
    <div class="sidebar-header">
        🛍️
    </div>
    """, unsafe_allow_html=True)

    # 네비게이션 바
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)

    # 챗봇 버튼
    if st.button(
        "💬\n챗봇",
        key="nav_chatbot",
        use_container_width=True,
        help="챗봇"
    ):
        st.session_state.current_page = "chatbot"
        st.rerun()

    # 대시보드 버튼
    if st.button(
        "📊\n대시보드",
        key="nav_dashboard",
        use_container_width=True,
        help="대시보드"
    ):
        st.session_state.current_page = "dashboard"
        st.rerun()

    # 설정 버튼
    if st.button(
        "⚙️\n설정",
        key="nav_settings",
        use_container_width=True,
        help="설정"
    ):
        st.session_state.current_page = "settings"
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # 하단 정보
    st.markdown("---")
    st.caption("v1.0")

# ============ 페이지 로드 ============
if st.session_state.current_page == "chatbot":
    with open("page_modules/chatbot.py", "r", encoding="utf-8") as f:
        exec(f.read())

elif st.session_state.current_page == "dashboard":
    with open("page_modules/dashboard.py", "r", encoding="utf-8") as f:
        exec(f.read())

elif st.session_state.current_page == "settings":
    with open("page_modules/settings.py", "r", encoding="utf-8") as f:
        exec(f.read())
