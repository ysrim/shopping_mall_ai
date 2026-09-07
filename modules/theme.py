# modules/theme.py
"""
Genspark 스타일 화이트 테마 CSS
"""

GENSPARK_THEME_CSS = """
<style>
/* ========== 글로벌 스타일 ========== */
:root {
    --primary: #3b82f6;
    --primary-light: #60a5fa;
    --primary-dark: #1d4ed8;
    --secondary: #6366f1;
    --accent: #0891b2;
    --bg-light: #ffffff;
    --bg-lighter: #f9fafb;
    --bg-card: #f3f4f6;
    --border: #e5e7eb;
    --border-light: #f3f4f6;
    --text-primary: #1f2937;
    --text-secondary: #6b7280;
    --text-light: #9ca3af;
    --sidebar-bg: #f3f4f6;
}

* {
    margin: 0;
    padding: 0;
}

html, body {
    background-color: var(--bg-light);
    color: var(--text-primary);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
}

/* ========== Streamlit 기본 오버라이드 ========== */
.stApp {
    background-color: var(--bg-light);
}

.main {
    background-color: var(--bg-light);
}

/* ========== 사이드바 스타일 (바 형식) ========== */
[data-testid="stSidebar"] {
    background-color: var(--sidebar-bg);
    border-right: 1px solid var(--border);
    width: auto !important;
    min-width: 100px;
}

[data-testid="stSidebar"] > div {
    padding: 0 !important;
}

[data-testid="stSidebarNav"] {
    display: none;
}

/* ========== 버튼 스타일 ========== */
.stButton > button {
    background: transparent;
    color: var(--text-secondary);
    border: none;
    padding: 20px 10px;
    border-radius: 0;
    font-weight: 600;
    font-size: 11px;
    transition: all 0.3s ease;
    box-shadow: none;
    border-left: 4px solid transparent;
    width: 100%;
    text-align: center;
}

.stButton > button:hover {
    background-color: #e5e7eb;
    color: var(--primary);
    border-left-color: var(--primary);
    transform: none;
    box-shadow: none;
}

.stButton > button:active {
    transform: none;
}

/* ========== 입력 필드 ========== */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > select,
.stNumberInput > div > div > input,
.stChatInputContainer > div > div > input {
    background-color: var(--bg-light);
    color: var(--text-primary);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 10px 12px;
    transition: all 0.2s ease;
    font-size: 14px;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div > select:focus,
.stNumberInput > div > div > input:focus,
.stChatInputContainer > div > div > input:focus {
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    outline: none;
}

/* ========== 메트릭 카드 ========== */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(99, 102, 241, 0.05) 100%);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    transition: all 0.3s ease;
}

[data-testid="metric-container"]:hover {
    border-color: var(--primary);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
    transform: translateY(-2px);
}

/* ========== 카드 컨테이너 ========== */
.card {
    background-color: var(--bg-lighter);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    margin: 10px 0;
    transition: all 0.3s ease;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card:hover {
    border-color: var(--primary);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
    transform: translateY(-2px);
}

/* ========== 체크박스 & 라디오 ========== */
.stCheckbox > label > span,
.stRadio > label > span {
    color: var(--text-primary);
}

.stCheckbox > label > input[type="checkbox"],
.stRadio > label > input[type="radio"] {
    accent-color: var(--primary);
}

/* ========== 슬라이더 ========== */
.stSlider > div > div > div > div {
    background-color: var(--border);
}

.stSlider > div > div > div > div > div {
    background: linear-gradient(90deg, var(--primary) 0%, var(--primary-light) 100%);
    border-radius: 10px;
}

/* ========== 탭 ========== */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background-color: transparent;
    border-bottom: 2px solid var(--border);
}

.stTabs [data-baseweb="tab"] {
    background-color: transparent;
    border: none;
    color: var(--text-secondary);
    padding: 12px 24px;
    border-bottom: 3px solid transparent;
    transition: all 0.3s ease;
    font-weight: 500;
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-primary);
    border-bottom-color: var(--border);
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: var(--primary);
    border-bottom-color: var(--primary);
}

/* ========== 익스팬더 ========== */
.stExpander {
    background-color: var(--bg-lighter);
    border: 1px solid var(--border);
    border-radius: 8px;
}

.stExpander > div > button {
    background-color: transparent;
    color: var(--text-primary);
    border: none;
    padding: 16px;
}

.stExpander > div > button:hover {
    background-color: var(--border-light);
}

/* ========== 데이터프레임 ========== */
.stDataFrame {
    background-color: var(--bg-lighter);
    border: 1px solid var(--border);
    border-radius: 8px;
}

.stDataFrame thead {
    background-color: var(--bg-card);
    color: var(--text-primary);
}

.stDataFrame tbody tr:hover {
    background-color: var(--border-light);
}

/* ========== 텍스트 ========== */
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary);
    font-weight: 700;
}

p, span, div {
    color: var(--text-primary);
}

/* ========== 링크 ========== */
a {
    color: var(--primary);
    text-decoration: none;
    transition: color 0.2s ease;
}

a:hover {
    color: var(--primary-dark);
    text-decoration: underline;
}

/* ========== 상태 메시지 ========== */
.stSuccess {
    background-color: rgba(34, 197, 94, 0.05);
    border-left: 4px solid #22c55e;
    color: #15803d;
    border-radius: 8px;
    padding: 12px 16px;
}

.stError {
    background-color: rgba(239, 68, 68, 0.05);
    border-left: 4px solid #ef4444;
    color: #7f1d1d;
    border-radius: 8px;
    padding: 12px 16px;
}

.stWarning {
    background-color: rgba(234, 179, 8, 0.05);
    border-left: 4px solid #eab308;
    color: #78350f;
    border-radius: 8px;
    padding: 12px 16px;
}

.stInfo {
    background-color: rgba(59, 130, 246, 0.05);
    border-left: 4px solid var(--primary);
    color: #1e40af;
    border-radius: 8px;
    padding: 12px 16px;
}

/* ========== 채팅 메시지 ========== */
.chat-message {
    margin: 12px 0;
    padding: 14px 16px;
    border-radius: 10px;
    max-width: 80%;
    word-wrap: break-word;
    line-height: 1.5;
}

.chat-message.user {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(99, 102, 241, 0.1) 100%);
    margin-left: auto;
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 10px 0px 10px 10px;
    color: var(--text-primary);
}

.chat-message.assistant {
    background-color: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 0px 10px 10px 10px;
    color: var(--text-primary);
}

/* ========== 로딩 애니메이션 ========== */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.pulse {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* ========== 상태 배지 ========== */
.status-badge-success {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background-color: #22c55e;
    margin-right: 8px;
}

.status-badge-error {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background-color: #ef4444;
    margin-right: 8px;
}

/* ========== 반응형 디자인 ========== */
@media (max-width: 768px) {
    .card {
        padding: 12px;
    }

    .stButton > button {
        width: 100%;
    }

    .chat-message {
        max-width: 95%;
    }
}

/* ========== 마크다운 스타일 ========== */
.stMarkdown {
    color: var(--text-primary);
}

.stMarkdown h1 {
    font-size: 28px;
    margin-bottom: 16px;
}

.stMarkdown h2 {
    font-size: 24px;
    margin-bottom: 12px;
    margin-top: 20px;
}

.stMarkdown h3 {
    font-size: 20px;
    margin-bottom: 10px;
    margin-top: 16px;
}
</style>
"""
