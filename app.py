import streamlit as st

# ─── Page config — SABSE PEHLE ───────────────────────────────────────────────
st.set_page_config(
    page_title="ISRO Quiz App",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import os
import time
from dotenv import load_dotenv

load_dotenv()

try:
    if hasattr(st, 'secrets'):
        for k, v in st.secrets.items():
            if isinstance(v, str):
                os.environ[k] = v
except:
    pass

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@400;600&display=swap');
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #0a0f14 !important;
    color: #e0e0e0 !important;
    font-family: 'Rajdhani', sans-serif;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="collapsedControl"] {display: none;}
[data-testid="stAppViewContainer"] > .main { background-color: #0a0f14; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0f14; }
::-webkit-scrollbar-thumb { background: #00d4ff; border-radius: 3px; }
h1, h2, h3 { font-family: 'Orbitron', monospace; color: #00d4ff; }
.stButton > button {
    background: linear-gradient(135deg, #00d4ff22, #00d4ff44) !important;
    color: #00d4ff !important;
    border: 1px solid #00d4ff !important;
    border-radius: 8px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    padding: 10px 28px !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    background: #00d4ff !important;
    color: #0a0f14 !important;
}
.stTextInput > div > div > input {
    background-color: #0d1a26 !important;
    color: #e0e0e0 !important;
    border: 1px solid #00d4ff44 !important;
    border-radius: 8px !important;
}
.stTabs [data-baseweb="tab-list"] {
    background-color: #0d1a26 !important;
    border-radius: 8px !important;
    padding: 4px !important;
}
.stTabs [data-baseweb="tab"] { color: #8899aa !important; border-radius: 6px !important; }
.stTabs [aria-selected="true"] {
    background-color: #00d4ff22 !important;
    color: #00d4ff !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Constants ────────────────────────────────────────────────────────────────
ADMIN_EMAIL = "aayushi706848@gmail.com"

# ─── Session state ────────────────────────────────────────────────────────────
for key in ["user", "page", "user_email", "user_uid", "user_name",
            "selected_category", "category_title", "show_forgot"]:
    if key not in st.session_state:
        st.session_state[key] = None
if st.session_state.page is None:
    st.session_state.page = "login"
if st.session_state.show_forgot is None:
    st.session_state.show_forgot = False

# ─── Helpers ──────────────────────────────────────────────────────────────────
def is_valid_email(email):
    import re
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', email))

def clear_quiz_state():
    for k in ["quiz_questions", "quiz_index", "quiz_score",
              "quiz_answers", "quiz_cat_loaded",
              "answered", "selected_option"]:
        if k in st.session_state:
            del st.session_state[k]
    for k in [k for k in st.session_state if k.startswith("timer_start_")]:
        del st.session_state[k]

def go_home():
    clear_quiz_state()
    st.session_state.page = "home"
    st.rerun()

# ─── LOGIN PAGE ───────────────────────────────────────────────────────────────
def show_login():
    from firebase_config import (login_user, signup_user,
                                  send_password_reset,
                                  send_verification_email)

    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; padding:40px 0 24px;">
            <h1 style="font-size:2em;">🚀 ISRO Quiz</h1>
            <p style="color:#8899aa; font-size:16px;">
                India's Space Quiz Platform
            </p>
        </div>
        """, unsafe_allow_html=True)

        # ── Forgot Password ───────────────────────────────────────────────────
        if st.session_state.show_forgot:
            st.markdown("""
            <div style="background:#0d1a26; border:1px solid #f59e0b44;
                        border-left:4px solid #f59e0b; border-radius:12px;
                        padding:24px; margin-bottom:16px;">
                <div style="font-family:'Orbitron',monospace;
                            color:#f59e0b; margin-bottom:8px;">
                    🔑 Reset Password
                </div>
                <div style="color:#8899aa; font-size:13px;">
                    Enter your registered email to receive a reset link.
                </div>
            </div>
            """, unsafe_allow_html=True)

            reset_email = st.text_input(
                "Reset Email", placeholder="your@email.com",
                key="reset_email_input", label_visibility="collapsed")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                if st.button("← Back to Login",
                             use_container_width=True, key="back_to_login"):
                    st.session_state.show_forgot = False
                    st.rerun()
            with c2:
                if st.button("Send Reset Link 📧",
                             use_container_width=True, key="send_reset"):
                    if not reset_email:
                        st.error("❌ Please enter your email!")
                    elif not is_valid_email(reset_email.strip()):
                        st.error("❌ Invalid email format!")
                    else:
                        with st.spinner("Sending..."):
                            ok, res = send_password_reset(
                                reset_email.strip().lower())
                        if ok:
                            st.success("✅ Reset email sent! Check inbox.")
                        else:
                            if "EMAIL_NOT_FOUND" in str(res):
                                st.error("❌ Email not registered!")
                            else:
                                st.error("❌ Failed. Try again.")
            return

        # ── Tabs ──────────────────────────────────────────────────────────────
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

        with tab1:
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            l_email = st.text_input(
                "Email", placeholder="your@email.com",
                key="l_email", label_visibility="collapsed")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            l_pass = st.text_input(
                "Password", type="password", placeholder="Enter password",
                key="l_pass", label_visibility="collapsed")
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

            if st.button("Login 🚀", use_container_width=True, key="login_btn"):
                if not l_email or not l_pass:
                    st.error("❌ Please enter email and password!")
                elif not is_valid_email(l_email.strip()):
                    st.error("❌ Invalid email format!")
                else:
                    with st.spinner("Logging in..."):
                        res = login_user(l_email.strip().lower(), l_pass)

                    if len(res) == 3:
                        success, result, id_token = res
                    else:
                        success, result = res
                        id_token = None

                    if success:
                        st.session_state.user       = result["uid"]
                        st.session_state.user_email = result["email"]
                        st.session_state.user_uid   = result["uid"]
                        st.session_state.user_name  = result["display_name"]
                        st.session_state.page       = "home"
                        st.rerun()
                    elif result == "EMAIL_NOT_VERIFIED":
                        st.session_state["_temp_token"] = id_token
                        st.markdown("""
                        <div style="background:#2a1a0a; border:1px solid #f59e0b;
                                    border-radius:10px; padding:16px; margin:8px 0;">
                            <div style="color:#f59e0b; font-weight:700; margin-bottom:8px;">
                                ⚠️ Email Not Verified!
                            </div>
                            <div style="color:#fcd34d; font-size:13px; line-height:1.8;">
                                Please verify your email before logging in.<br>
                                Check your inbox for the verification link.
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("📧 Resend Verification Email",
                                     use_container_width=True, key="resend_btn"):
                            token = st.session_state.get("_temp_token")
                            if token:
                                with st.spinner("Sending..."):
                                    ok, _ = send_verification_email(token)
                                if ok:
                                    st.success("✅ Sent! Check inbox.")
                                else:
                                    st.error("❌ Failed. Try again.")
                    else:
                        err = str(result)
                        if "INVALID_LOGIN_CREDENTIALS" in err:
                            st.error("❌ Wrong email or password!")
                        elif "EMAIL_NOT_FOUND" in err:
                            st.error("❌ Email not registered! Sign up first.")
                        elif "TOO_MANY_ATTEMPTS" in err:
                            st.error("❌ Too many attempts. Try later.")
                        elif "USER_DISABLED" in err:
                            st.error("❌ Account disabled.")
                        else:
                            st.error("❌ Login failed. Try again.")

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            _, cfp = st.columns([2, 1])
            with cfp:
                if st.button("🔑 Forgot Password?",
                             use_container_width=True, key="forgot_btn"):
                    st.session_state.show_forgot = True
                    st.rerun()

        with tab2:
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            s_name = st.text_input(
                "Name", placeholder="Your full name",
                key="s_name", label_visibility="collapsed")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            s_email = st.text_input(
                "Email", placeholder="your@email.com",
                key="s_email", label_visibility="collapsed")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            s_pass = st.text_input(
                "Password", type="password",
                placeholder="Minimum 6 characters",
                key="s_pass", label_visibility="collapsed")
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

            if st.button("Create Account 🛸",
                         use_container_width=True, key="signup_btn"):
                if not s_name or not s_email or not s_pass:
                    st.error("❌ Please fill all fields!")
                elif not is_valid_email(s_email.strip()):
                    st.error("❌ Invalid email format!")
                elif len(s_pass) < 6:
                    st.error("❌ Password must be 6+ characters!")
                else:
                    with st.spinner("Creating account..."):
                        ok, res = signup_user(
                            s_email.strip().lower(), s_pass, s_name.strip())
                    if ok:
                        st.markdown("""
                        <div style="background:#0a2a0a; border:1px solid #22c55e;
                                    border-radius:10px; padding:16px; margin:8px 0;">
                            <div style="color:#22c55e; font-weight:700; margin-bottom:6px;">
                                ✅ Account Created!
                            </div>
                            <div style="color:#86efac; font-size:13px; line-height:1.8;">
                                📧 Verification email sent.<br>
                                👆 Click the link to verify.<br>
                                🔐 Then come back and login.
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        err = str(res)
                        if "EMAIL_EXISTS" in err:
                            st.error("❌ Email already registered!")
                        elif "WEAK_PASSWORD" in err:
                            st.error("❌ Password too weak!")
                        elif "INVALID_EMAIL" in err:
                            st.error("❌ Invalid email!")
                        else:
                            st.error("❌ Signup failed. Try again.")

# ─── HOME PAGE ────────────────────────────────────────────────────────────────
def show_home():
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center;
                background:#0d1a26; border-bottom:1px solid #00d4ff33;
                padding:12px 32px; margin-bottom:24px;">
        <div style="font-family:'Orbitron',monospace; color:#00d4ff; font-size:20px;">
            🚀 ISRO Quiz
        </div>
        <div style="display:flex; align-items:center; gap:16px;">
            <span style="color:#8899aa; font-size:14px;">
                👤 <span style="color:#00d4ff;">{st.session_state.user_name}</span>
            </span>
            {'<span style="background:#00d4ff22; color:#00d4ff; font-size:11px; padding:3px 10px; border-radius:20px; border:1px solid #00d4ff44;">ADMIN</span>' if st.session_state.user_email == ADMIN_EMAIL else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; padding:16px 0 28px;">
        <h1 style="font-size:2em;">🛸 Test Your Space Knowledge</h1>
        <p style="color:#8899aa; font-size:16px;">
            Choose a category and start the quiz!
        </p>
    </div>
    """, unsafe_allow_html=True)

    categories = [
        {"icon":"🚀","title":"Rockets","subtitle":"PSLV • GSLV • LVM3",
         "desc":"India's powerful launch vehicles","color":"#ff6b35","key":"rockets"},
        {"icon":"🛸","title":"Satellites","subtitle":"INSAT • IRS • NavIC",
         "desc":"Indian satellites and missions","color":"#00d4ff","key":"satellites"},
        {"icon":"🌙","title":"Missions","subtitle":"Chandrayaan • Mangalyaan • Aditya",
         "desc":"ISRO's historic space missions","color":"#a855f7","key":"missions"},
        {"icon":"👨‍🔬","title":"Scientists","subtitle":"Kalam • Sarabhai • Dhawan",
         "desc":"India's greatest space scientists","color":"#22c55e","key":"scientists"}
    ]

    c1, c2 = st.columns(2)
    for i, cat in enumerate([c1, c2, c1, c2]):
        with cat:
            d = categories[i]
            st.markdown(f"""
            <div style="background:#0d1a26; border:1px solid {d['color']}33;
                        border-left:4px solid {d['color']}; border-radius:12px;
                        padding:24px; margin:8px 0; min-height:160px;">
                <div style="font-size:2.2em;">{d['icon']}</div>
                <div style="font-family:'Orbitron',monospace; color:{d['color']};
                            font-size:1.1em; font-weight:700; margin:6px 0;">
                    {d['title']}
                </div>
                <div style="color:#8899aa; font-size:12px;">{d['subtitle']}</div>
                <div style="color:#ccd6f6; font-size:13px; margin:6px 0;">{d['desc']}</div>
                <div style="color:#556677; font-size:11px; margin-top:10px;">
                    📝 10 Questions &nbsp;•&nbsp; ⏱️ 60 sec each
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Start {d['title']} Quiz →",
                         key=f"cat_{d['key']}", use_container_width=True):
                clear_quiz_state()
                st.session_state.selected_category = d['key']
                st.session_state.category_title    = d['title']
                st.session_state.page = "quiz"
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    for col, (val, label, color) in zip(
        st.columns(3),
        [("4","Categories","#00d4ff"),
         ("40+","Questions","#a855f7"),
         ("🏆","Leaderboard","#FFD700")]
    ):
        with col:
            st.markdown(f"""
            <div style="background:#0d1a26; border:1px solid {color}22;
                        border-radius:10px; padding:16px; text-align:center;">
                <div style="color:{color}; font-size:1.8em; font-weight:700;">{val}</div>
                <div style="color:#8899aa; font-size:13px;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _, col_b, _ = st.columns([1, 1, 1])
    with col_b:
        if st.button("📊 My Analytics", use_container_width=True, key="home_analytics"):
            st.session_state.page = "analytics"
            st.rerun()
        if st.button("🏆 Leaderboard", use_container_width=True, key="home_leader"):
            st.session_state.page = "leaderboard"
            st.rerun()
        if st.session_state.user_email == ADMIN_EMAIL:
            if st.button("⚙️ Admin Panel", use_container_width=True, key="home_admin"):
                st.session_state.page = "admin"
                st.rerun()
        if st.button("🚪 Logout", use_container_width=True, key="home_logout"):
            for k in ["user","user_email","user_uid","user_name"]:
                st.session_state[k] = None
            st.session_state.page = "login"
            st.rerun()

# ─── QUIZ PAGE ────────────────────────────────────────────────────────────────
def show_quiz():
    from questions import QUESTIONS
    import random

    cat       = st.session_state.selected_category
    cat_title = st.session_state.category_title

    if "quiz_questions" not in st.session_state or \
       st.session_state.get("quiz_cat_loaded") != cat:
        qs = QUESTIONS[cat].copy()
        random.shuffle(qs)
        st.session_state.quiz_questions  = qs[:10]
        st.session_state.quiz_index      = 0
        st.session_state.quiz_score      = 0
        st.session_state.quiz_answers    = []
        st.session_state.quiz_cat_loaded = cat
        st.session_state.answered        = False
        st.session_state.selected_option = None

    qs  = st.session_state.quiz_questions
    idx = st.session_state.quiz_index

    if idx >= len(qs):
        st.session_state.page = "result"
        st.rerun()
        return

    q = qs[idx]

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center;
                background:#0d1a26; border-bottom:1px solid #00d4ff33;
                padding:12px 32px; margin-bottom:20px;">
        <div style="font-family:'Orbitron',monospace; color:#00d4ff; font-size:16px;">
            🚀 {cat_title} Quiz
        </div>
        <div style="color:#8899aa; font-size:14px;">
            ⭐ Score: <span style="color:#00d4ff; font-weight:700;">
            {st.session_state.quiz_score}</span>
            &nbsp;|&nbsp; Q{idx+1}/{len(qs)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Progress bar ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:#0d1a26; border-radius:10px; height:6px; margin-bottom:16px;">
        <div style="background:linear-gradient(90deg,#00d4ff,#0066ff);
                    width:{int((idx/len(qs))*100)}%; height:6px; border-radius:10px;">
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Timer ─────────────────────────────────────────────────────────────────
    timer_key = f"timer_start_{idx}"
    if timer_key not in st.session_state:
        st.session_state[timer_key] = time.time()

    if not st.session_state.answered:
        elapsed   = int(time.time() - st.session_state[timer_key])
        remaining = max(0, 60 - elapsed)
        pct_left  = remaining / 60

        if pct_left > 0.5:    t_color = "#22c55e"
        elif pct_left > 0.25: t_color = "#f59e0b"
        else:                  t_color = "#ef4444"

        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:16px;
                    background:#0d1a26; border:1px solid {t_color}44;
                    border-radius:10px; padding:12px 20px; margin-bottom:16px;">
            <div style="font-size:1.8em;">⏱️</div>
            <div style="flex:1;">
                <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                    <span style="color:#8899aa; font-size:13px;">Time Remaining</span>
                    <span style="color:{t_color}; font-weight:700; font-size:18px;">
                        {remaining}s
                    </span>
                </div>
                <div style="background:#0a0f14; border-radius:6px; height:8px;">
                    <div style="background:{t_color}; width:{int(pct_left*100)}%;
                                height:8px; border-radius:6px;"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if remaining == 0:
            st.session_state.answered        = True
            st.session_state.selected_option = -1
            st.session_state.quiz_answers.append({
                "question":   q['question'], "selected":   -1,
                "correct":    q['correct'],  "options":    q['options'],
                "fact":       q['fact'],     "is_correct": False
            })
            st.warning("⏰ Time's up! Moving to next question...")
            time.sleep(1)
            st.session_state.quiz_index      += 1
            st.session_state.answered         = False
            st.session_state.selected_option  = None
            if timer_key in st.session_state:
                del st.session_state[timer_key]
            st.rerun()
            return

    # ── Question ──────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:#0d1a26; border:1px solid #00d4ff44;
                border-left:4px solid #00d4ff; border-radius:12px;
                padding:24px; margin-bottom:20px;">
        <div style="color:#556677; font-size:12px; margin-bottom:10px;">
            QUESTION {idx+1} OF {len(qs)}
        </div>
        <div style="color:#ffffff; font-size:1.15em; font-weight:600; line-height:1.6;">
            {q['question']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    answered = st.session_state.answered
    selected = st.session_state.selected_option

    # ── Options ───────────────────────────────────────────────────────────────
    for i, option in enumerate(q['options']):
        if answered:
            if i == q['correct']:
                color, bg, icon = "#22c55e", "#0a2a0a", "✅"
            elif i == selected and i != q['correct']:
                color, bg, icon = "#ef4444", "#2a0a0a", "❌"
            else:
                color, bg, icon = "#334155", "#0d1a26", "○"
            st.markdown(f"""
            <div style="background:{bg}; border:1px solid {color};
                        border-radius:10px; padding:14px 20px; margin:6px 0;
                        color:{color}; font-size:15px;">
                {icon} &nbsp; {'ABCD'[i]}.&nbsp; {option}
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.button(f"{'ABCD'[i]}.  {option}",
                         key=f"opt_{idx}_{i}", use_container_width=True):
                st.session_state.selected_option = i
                st.session_state.answered        = True
                is_correct = (i == q['correct'])
                if is_correct:
                    st.session_state.quiz_score += 1
                st.session_state.quiz_answers.append({
                    "question":   q['question'], "selected":   i,
                    "correct":    q['correct'],  "options":    q['options'],
                    "fact":       q['fact'],     "is_correct": is_correct
                })
                if timer_key in st.session_state:
                    del st.session_state[timer_key]
                st.rerun()

    # ── Feedback ──────────────────────────────────────────────────────────────
    if answered:
        is_right = (selected == q['correct'])
        st.markdown(f"""
        <div style="background:{'#0a2a0a' if is_right else '#2a0a0a'};
                    border:1px solid {'#22c55e' if is_right else '#ef4444'};
                    border-radius:10px; padding:16px 20px; margin:16px 0;">
            <div style="color:{'#22c55e' if is_right else '#ef4444'};
                        font-weight:700; margin-bottom:6px;">
                {'🎉 Correct!' if is_right else '😕 Wrong Answer!'}
            </div>
            <div style="color:#ccd6f6; font-size:13px; line-height:1.6;">
                💡 <b>Fact:</b> {q['fact']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            if st.button("🏠 Home", use_container_width=True, key=f"qhome_{idx}"):
                go_home()
        with c2:
            label = "Next Question →" if idx < len(qs)-1 else "See Results 🏆"
            if st.button(label, use_container_width=True, key=f"next_{idx}"):
                st.session_state.quiz_index      += 1
                st.session_state.answered         = False
                st.session_state.selected_option  = None
                st.rerun()
        with c3:
            if st.button("🚫 Quit", use_container_width=True, key=f"quit_{idx}"):
                go_home()

    # Auto-refresh timer every second
    if not st.session_state.answered:
        time.sleep(1)
        st.rerun()

# ─── RESULT PAGE ──────────────────────────────────────────────────────────────
def show_result():
    from firebase_config import save_quiz_result

    score     = st.session_state.quiz_score
    answers   = st.session_state.quiz_answers
    total     = len(answers)
    cat_title = st.session_state.category_title
    pct       = round((score/total)*100) if total > 0 else 0
    wrong     = [a for a in answers if not a['is_correct']]

    save_quiz_result(st.session_state.user_uid,
                     st.session_state.selected_category,
                     score, total, wrong)

    if pct >= 80:   gc, gt, ge = "#22c55e", "Excellent! 🏆", "🥇"
    elif pct >= 50: gc, gt, ge = "#f59e0b", "Good Job! 👍",  "🥈"
    else:           gc, gt, ge = "#ef4444", "Keep Practicing! 💪", "📚"

    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center;
                background:#0d1a26; border-bottom:1px solid #00d4ff33;
                padding:12px 32px; margin-bottom:24px;">
        <div style="font-family:'Orbitron',monospace; color:#00d4ff; font-size:18px;">
            🏆 Quiz Results
        </div>
        <div style="color:#8899aa; font-size:14px;">{cat_title}</div>
    </div>
    """, unsafe_allow_html=True)

    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="background:#0d1a26; border:2px solid {gc};
                    border-radius:16px; padding:32px; text-align:center; margin-bottom:20px;">
            <div style="font-size:3.5em;">{ge}</div>
            <div style="font-family:'Orbitron',monospace; color:{gc};
                        font-size:2.5em; font-weight:700; margin:8px 0;">
                {score}/{total}
            </div>
            <div style="color:#8899aa;">{pct}% Accuracy</div>
            <div style="color:{gc}; font-size:1.1em; font-weight:600; margin-top:8px;">
                {gt}
            </div>
        </div>
        <div style="display:flex; gap:12px; margin-bottom:20px;">
            <div style="flex:1; background:#0d1a26; border:1px solid #22c55e44;
                        border-radius:10px; padding:14px; text-align:center;">
                <div style="color:#22c55e; font-size:1.6em; font-weight:700;">{score}</div>
                <div style="color:#8899aa; font-size:12px;">Correct</div>
            </div>
            <div style="flex:1; background:#0d1a26; border:1px solid #ef444444;
                        border-radius:10px; padding:14px; text-align:center;">
                <div style="color:#ef4444; font-size:1.6em; font-weight:700;">{total-score}</div>
                <div style="color:#8899aa; font-size:12px;">Wrong</div>
            </div>
            <div style="flex:1; background:#0d1a26; border:1px solid #00d4ff44;
                        border-radius:10px; padding:14px; text-align:center;">
                <div style="color:#00d4ff; font-size:1.6em; font-weight:700;">{pct}%</div>
                <div style="color:#8899aa; font-size:12px;">Score</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🏠 Back to Home", use_container_width=True, key="r_home"):
            go_home()
        if st.button("🔄 Retry Quiz", use_container_width=True, key="r_retry"):
            clear_quiz_state()
            st.session_state.page = "quiz"
            st.rerun()
        if st.button("🏆 Leaderboard", use_container_width=True, key="r_leader"):
            st.session_state.page = "leaderboard"
            st.rerun()
        if st.button("📊 My Analytics", use_container_width=True, key="r_analytics"):
            st.session_state.page = "analytics"
            st.rerun()

    # ── Gemini AI ──────────────────────────────────────────────────────────────
    if wrong:
        st.markdown("""
        <div style="margin:28px 0 16px;">
            <h2 style="font-size:1.2em;">🤖 AI Explanation for Wrong Answers</h2>
            <p style="color:#8899aa; font-size:13px;">
                Click the button to get Gemini AI explanation.
            </p>
        </div>
        """, unsafe_allow_html=True)

        for i, ans in enumerate(wrong):
            with st.expander(f"❌ {ans['question']}", expanded=(i==0)):
                ca, cb = st.columns(2)
                with ca:
                    st.markdown(f"""
                    <div style="background:#2a0a0a; border:1px solid #ef4444;
                                border-radius:8px; padding:12px;">
                        <div style="color:#ef4444; font-size:11px;">YOUR ANSWER</div>
                        <div style="color:#fca5a5; font-size:14px; margin-top:4px;">
                            {ans['options'][ans['selected']]
                             if ans['selected'] >= 0 else '⏰ Time expired'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with cb:
                    st.markdown(f"""
                    <div style="background:#0a2a0a; border:1px solid #22c55e;
                                border-radius:8px; padding:12px;">
                        <div style="color:#22c55e; font-size:11px;">CORRECT ANSWER</div>
                        <div style="color:#86efac; font-size:14px; margin-top:4px;">
                            {ans['options'][ans['correct']]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown(f"""
                <div style="background:#0d1a26; border:1px solid #00d4ff22;
                            border-radius:8px; padding:12px; margin:8px 0;">
                    <div style="color:#00d4ff; font-size:11px;">💡 QUICK FACT</div>
                    <div style="color:#94a3b8; font-size:13px; margin-top:4px; line-height:1.6;">
                        {ans['fact']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button("🤖 Get AI Explanation", key=f"ai_{i}"):
                    with st.spinner("Gemini AI is thinking..."):
                        try:
                            import google.generativeai as genai
                            api_key = os.getenv("GEMINI_API_KEY")
                            if not api_key:
                                st.error("❌ GEMINI_API_KEY not found!")
                            else:
                                genai.configure(api_key=api_key)
                                model    = genai.GenerativeModel('gemini-1.5-flash')
                                response = model.generate_content(
                                    f"""You are an ISRO space quiz tutor.
Question: {ans['question']}
Student answered: {ans['options'][ans['selected']] if ans['selected'] >= 0 else 'Did not answer (time expired)'}
Correct answer: {ans['options'][ans['correct']]}
Fact: {ans['fact']}
In 3-4 sentences explain: why answer is wrong, why correct is right, one interesting ISRO fact. Simple English.""")
                                st.markdown(f"""
                                <div style="background:#1a0a2a; border:1px solid #a855f744;
                                            border-left:3px solid #a855f7; border-radius:8px;
                                            padding:16px; margin-top:8px;">
                                    <div style="color:#a855f7; font-size:11px; margin-bottom:8px;">
                                        🤖 GEMINI AI
                                    </div>
                                    <div style="color:#e2e8f0; font-size:14px; line-height:1.7;">
                                        {response.text}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"AI Error: {e}")
    else:
        _, col2, _ = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="background:#0a2a0a; border:1px solid #22c55e;
                        border-radius:12px; padding:24px; text-align:center; margin-top:16px;">
                <div style="font-size:2em;">🎯</div>
                <div style="color:#22c55e; font-size:1.1em; font-weight:600;">
                    Perfect Score! No wrong answers!
                </div>
                <div style="color:#86efac; font-size:13px; margin-top:8px;">
                    You are an ISRO Expert! 🚀
                </div>
            </div>
            """, unsafe_allow_html=True)

# ─── LEADERBOARD ──────────────────────────────────────────────────────────────
def show_leaderboard():
    from firebase_config import get_leaderboard

    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center;
                background:#0d1a26; border-bottom:1px solid #00d4ff33;
                padding:12px 32px; margin-bottom:24px;">
        <div style="font-family:'Orbitron',monospace; color:#00d4ff; font-size:18px;">
            🏆 Leaderboard
        </div>
        <div style="color:#8899aa; font-size:14px;">Top 10 Players</div>
    </div>
    <div style="text-align:center; padding:8px 0 24px;">
        <h1>🏆 Hall of Fame</h1>
        <p style="color:#8899aa;">Top ISRO Quiz Champions</p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Loading leaderboard..."):
        leaders = get_leaderboard(10)

    if not leaders:
        st.markdown("""
        <div style="text-align:center; padding:40px; color:#8899aa;">
            <div style="font-size:3em;">🚀</div>
            <div style="margin-top:12px; font-size:1.1em;">
                No players yet. Be the first!
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        if len(leaders) >= 3:
            c1, c2, c3 = st.columns(3)
            for col, p, medal, color in [
                (c2, leaders[0], "🥇", "#FFD700"),
                (c1, leaders[1], "🥈", "#C0C0C0"),
                (c3, leaders[2], "🥉", "#CD7F32")
            ]:
                with col:
                    st.markdown(f"""
                    <div style="background:#0d1a26; border:2px solid {color};
                                border-radius:12px; padding:20px; text-align:center; margin:4px;">
                        <div style="font-size:2.5em;">{medal}</div>
                        <div style="color:{color}; font-weight:700;
                                    font-family:'Orbitron',monospace; margin:8px 0;">
                            {p['name'][:12]}
                        </div>
                        <div style="color:#00d4ff; font-size:1.4em; font-weight:700;">
                            {p['score']}
                        </div>
                        <div style="color:#8899aa; font-size:11px;">{p['quizzes']} quizzes</div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("""<br>
        <div style="background:#0d1a26; border:1px solid #00d4ff22;
                    border-radius:12px; overflow:hidden;">
            <div style="display:grid; grid-template-columns:60px 1fr 100px 90px;
                        padding:12px 20px; border-bottom:1px solid #00d4ff22;
                        color:#00d4ff; font-size:12px; font-weight:600;">
                <div>RANK</div><div>PLAYER</div>
                <div style="text-align:center;">SCORE</div>
                <div style="text-align:center;">QUIZZES</div>
            </div>
        """, unsafe_allow_html=True)

        for i, p in enumerate(leaders):
            is_me  = p['name'] == st.session_state.user_name
            bg     = "#0d2a1a" if is_me else ("rgba(0,212,255,0.03)" if i%2==0 else "#0d1a26")
            icon   = ["🥇","🥈","🥉"][i] if i < 3 else f"#{i+1}"
            border = "border-left:3px solid #00d4ff;" if is_me else ""
            st.markdown(f"""
            <div style="display:grid; grid-template-columns:60px 1fr 100px 90px;
                        padding:14px 20px; background:{bg};
                        border-bottom:1px solid #ffffff06; {border}">
                <div>{icon}</div>
                <div style="color:{'#00d4ff' if is_me else '#e2e8f0'};
                            font-weight:{'700' if is_me else '400'};">
                    {p['name']} {'⬅ You' if is_me else ''}
                </div>
                <div style="text-align:center; color:#00d4ff; font-weight:700;">
                    {p['score']}
                </div>
                <div style="text-align:center; color:#8899aa;">{p['quizzes']}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1, 1])
    with col2:
        if st.button("🏠 Back to Home", use_container_width=True, key="lb_home"):
            go_home()

# ─── ANALYTICS PAGE ───────────────────────────────────────────────────────────
def show_analytics():
    from firebase_config import get_db
    from firebase_admin import firestore as fs

    uid  = st.session_state.user_uid
    name = st.session_state.user_name

    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center;
                background:#0d1a26; border-bottom:1px solid #00d4ff33;
                padding:12px 32px; margin-bottom:24px;">
        <div style="font-family:'Orbitron',monospace; color:#00d4ff; font-size:18px;">
            📊 My Analytics
        </div>
        <div style="color:#8899aa; font-size:14px;">Personal Stats</div>
    </div>
    """, unsafe_allow_html=True)

    try:
        db       = get_db()
        user_doc = db.collection("users").document(uid).get()
        user     = user_doc.to_dict() if user_doc.exists else {}

        attempts_ref  = db.collection("quiz_results")\
            .where("uid","==",uid)\
            .order_by("timestamp", direction=fs.Query.DESCENDING)\
            .limit(20).stream()
        attempts_list = [a.to_dict() for a in attempts_ref]

    except Exception as e:
        st.error(f"Error loading analytics: {e}")
        _, col2, _ = st.columns([1, 1, 1])
        with col2:
            if st.button("🏠 Back to Home", use_container_width=True, key="an_err_home"):
                go_home()
        return

    total_quizzes = user.get("quizzes_taken", 0)
    total_score   = user.get("total_score",   0)

    if attempts_list:
        percentages  = [a.get("percentage", 0) for a in attempts_list]
        best_percent = max(percentages)
        avg_percent  = round(sum(percentages)/len(percentages), 1)
    else:
        best_percent = avg_percent = 0

    st.markdown(f"""
    <div style="text-align:center; padding:8px 0 20px;">
        <h1 style="font-size:1.6em;">📊 {name}'s Performance</h1>
    </div>
    """, unsafe_allow_html=True)

    for col, (val, label, color, icon) in zip(
        st.columns(4),
        [(str(total_quizzes), "Total Quizzes", "#00d4ff", "🎯"),
         (str(total_score),   "Total Score",   "#22c55e", "⭐"),
         (f"{best_percent}%", "Best Score",    "#FFD700", "🏆"),
         (f"{avg_percent}%",  "Avg Accuracy",  "#a855f7", "📈")]
    ):
        with col:
            st.markdown(f"""
            <div style="background:#0d1a26; border:1px solid {color}33;
                        border-top:3px solid {color}; border-radius:12px;
                        padding:20px; text-align:center; margin-bottom:8px;">
                <div style="font-size:1.8em;">{icon}</div>
                <div style="color:{color}; font-size:1.8em; font-weight:700;">{val}</div>
                <div style="color:#8899aa; font-size:12px; margin-top:4px;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    cat_colors = {"rockets":"#ff6b35","satellites":"#00d4ff",
                  "missions":"#a855f7","scientists":"#22c55e"}
    cat_icons  = {"rockets":"🚀","satellites":"🛸",
                  "missions":"🌙","scientists":"👨‍🔬"}

    if attempts_list:
        # Category performance
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-family:'Orbitron',monospace; color:#00d4ff;
                    font-size:1em; margin-bottom:16px;">
            📂 Category Performance
        </div>
        """, unsafe_allow_html=True)

        cat_data = {}
        for a in attempts_list:
            cat = a.get("category","unknown")
            if cat not in cat_data:
                cat_data[cat] = {"scores":[],"attempts":0}
            cat_data[cat]["scores"].append(a.get("percentage",0))
            cat_data[cat]["attempts"] += 1

        if cat_data:
            cols = st.columns(len(cat_data))
            for col, (cat, data) in zip(cols, cat_data.items()):
                avg   = round(sum(data["scores"])/len(data["scores"]),1)
                best  = max(data["scores"])
                color = cat_colors.get(cat,"#00d4ff")
                icon  = cat_icons.get(cat,"📝")
                with col:
                    st.markdown(f"""
                    <div style="background:#0d1a26; border:1px solid {color}44;
                                border-left:4px solid {color}; border-radius:12px;
                                padding:16px; text-align:center;">
                        <div style="font-size:2em;">{icon}</div>
                        <div style="color:{color}; font-weight:700;
                                    font-family:'Orbitron',monospace;
                                    font-size:0.9em; margin:8px 0;">
                            {cat.title()}
                        </div>
                        <div style="color:#e2e8f0; font-size:1.4em; font-weight:700;">
                            {avg}%
                        </div>
                        <div style="color:#8899aa; font-size:11px;">avg accuracy</div>
                        <div style="color:#556677; font-size:11px; margin-top:4px;">
                            Best: {best}% • {data['attempts']} attempts
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # Recent attempts
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-family:'Orbitron',monospace; color:#00d4ff;
                    font-size:1em; margin-bottom:16px;">
            🕐 Recent Attempts
        </div>
        <div style="background:#0d1a26; border:1px solid #00d4ff22;
                    border-radius:12px; overflow:hidden;">
            <div style="display:grid; grid-template-columns:1fr 100px 80px 80px;
                        padding:12px 20px; border-bottom:1px solid #00d4ff22;
                        color:#00d4ff; font-size:12px; font-weight:600;">
                <div>CATEGORY</div>
                <div style="text-align:center;">SCORE</div>
                <div style="text-align:center;">ACCURACY</div>
                <div style="text-align:center;">GRADE</div>
            </div>
        """, unsafe_allow_html=True)

        for i, a in enumerate(attempts_list[:10]):
            cat   = a.get("category","")
            score = a.get("score",0)
            total = a.get("total",10)
            pct   = a.get("percentage",0)
            color = cat_colors.get(cat,"#00d4ff")
            icon  = cat_icons.get(cat,"📝")
            bg    = "rgba(0,212,255,0.03)" if i%2==0 else "#0d1a26"
            if pct >= 80:   grade, gc = "Excellent","#22c55e"
            elif pct >= 50: grade, gc = "Good",     "#f59e0b"
            else:           grade, gc = "Practice", "#ef4444"
            st.markdown(f"""
            <div style="display:grid; grid-template-columns:1fr 100px 80px 80px;
                        padding:14px 20px; background:{bg};
                        border-bottom:1px solid #ffffff06; align-items:center;">
                <div>
                    <span style="font-size:1.2em;">{icon}</span>
                    <span style="color:#e2e8f0; margin-left:8px;">{cat.title()}</span>
                </div>
                <div style="text-align:center; color:#00d4ff; font-weight:700;">
                    {score}/{total}
                </div>
                <div style="text-align:center; color:#8899aa;">{pct}%</div>
                <div style="text-align:center; color:{gc}; font-size:12px;">{grade}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Bar chart
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-family:'Orbitron',monospace; color:#00d4ff;
                    font-size:1em; margin-bottom:16px;">
            📈 Last 5 Quiz Scores
        </div>
        """, unsafe_allow_html=True)

        for a in reversed(attempts_list[:5]):
            pct   = a.get("percentage",0)
            cat   = a.get("category","").title()
            color = "#22c55e" if pct>=80 else "#f59e0b" if pct>=50 else "#ef4444"
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:12px; margin:8px 0;">
                <div style="color:#8899aa; font-size:13px; min-width:90px;">
                    {cat[:10]}
                </div>
                <div style="flex:1; background:#0d1a26; border-radius:6px;
                            height:20px; overflow:hidden;">
                    <div style="background:linear-gradient(90deg,{color},{color}88);
                                width:{pct}%; height:20px; border-radius:6px;">
                    </div>
                </div>
                <div style="color:{color}; font-weight:700; font-size:13px;
                            min-width:40px;">{pct}%</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding:40px; color:#8899aa;">
            <div style="font-size:3em;">🎯</div>
            <div style="font-size:1.1em; margin-top:12px;">No quiz attempts yet!</div>
            <div style="font-size:13px; margin-top:8px;">
                Complete a quiz to see your analytics here.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1, 1])
    with col2:
        if st.button("🏠 Back to Home", use_container_width=True, key="an_home"):
            go_home()

# ─── ADMIN PANEL ──────────────────────────────────────────────────────────────
def show_admin():
    from firebase_config import get_db

    if st.session_state.user_email != ADMIN_EMAIL:
        st.markdown("""
        <div style="text-align:center; padding:60px;">
            <div style="font-size:4em;">🔒</div>
            <h2 style="color:#ef4444;">Access Denied</h2>
            <p style="color:#8899aa;">You are not authorized.</p>
        </div>
        """, unsafe_allow_html=True)
        _, col2, _ = st.columns([1, 1, 1])
        with col2:
            if st.button("🏠 Go Home", use_container_width=True, key="ad_deny"):
                go_home()
        return

    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center;
                background:#0d1a26; border-bottom:1px solid #00d4ff33;
                padding:12px 32px; margin-bottom:24px;">
        <div style="font-family:'Orbitron',monospace; color:#00d4ff; font-size:18px;">
            ⚙️ Admin Panel
        </div>
        <div style="color:#22c55e; font-size:13px;">● Authorized</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["➕ Add Question","📋 Manage Questions","👥 Users"])

    with tab1:
        st.markdown("### ➕ Add New Question")
        c1, c2 = st.columns(2)
        with c1:
            category = st.selectbox("Category",
                ["rockets","satellites","missions","scientists"])
        with c2:
            difficulty = st.selectbox("Difficulty",["Easy","Medium","Hard"])
        question = st.text_area("Question", placeholder="Enter question...")
        ca, cb = st.columns(2)
        with ca:
            opt0 = st.text_input("Option A", key="oa")
            opt1 = st.text_input("Option B", key="ob")
        with cb:
            opt2 = st.text_input("Option C", key="oc")
            opt3 = st.text_input("Option D", key="od")
        correct = st.selectbox("Correct Answer",["A","B","C","D"])
        fact    = st.text_area("Fun Fact", placeholder="Interesting fact...")

        if st.button("➕ Add to Firestore", use_container_width=True, key="add_q"):
            if all([question, opt0, opt1, opt2, opt3, fact]):
                try:
                    get_db().collection("questions").add({
                        "category":   category,
                        "question":   question,
                        "options":    [opt0,opt1,opt2,opt3],
                        "correct":    ["A","B","C","D"].index(correct),
                        "fact":       fact,
                        "difficulty": difficulty,
                        "created_by": st.session_state.user_email
                    })
                    st.success("✅ Question added to Firestore!")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            else:
                st.warning("⚠️ Please fill all fields!")

    with tab2:
        st.markdown("### 📋 Manage Questions")
        cat_f = st.selectbox("Filter by Category",
            ["All","rockets","satellites","missions","scientists"], key="qf")
        try:
            db    = get_db()
            docs  = db.collection("questions").stream() if cat_f=="All" \
                    else db.collection("questions")\
                           .where("category","==",cat_f).stream()
            qlist = [{"id":d.id,**d.to_dict()} for d in docs]
            st.markdown(f"**{len(qlist)} questions found**")

            for q in qlist:
                with st.expander(f"📝 {q.get('question','')[:70]}..."):
                    st.markdown(f"""
                    <div style="background:#0a0f14; border:1px solid #00d4ff22;
                                border-radius:8px; padding:12px; margin-bottom:12px;">
                        <div style="color:#8899aa; font-size:12px;">
                            Category: <span style="color:#00d4ff;">
                            {q.get('category','')}</span>
                        </div>
                        <div style="color:#e2e8f0; margin:8px 0;">
                            {q.get('question','')}
                        </div>
                        <div style="color:#8899aa; font-size:13px;">
                            {'<br>'.join([f"{chr(65+i)}. {o}"
                            for i,o in enumerate(q.get('options',[]))])}
                        </div>
                        <div style="color:#22c55e; font-size:13px; margin-top:6px;">
                            ✅ Correct: {['A','B','C','D'][q.get('correct',0)]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    with st.form(key=f"ef_{q['id']}"):
                        new_q  = st.text_area("Edit Question",
                                              value=q.get('question',''),
                                              key=f"eq_{q['id']}")
                        opts   = q.get('options',['','','',''])
                        e1, e2 = st.columns(2)
                        with e1:
                            na = st.text_input("A", value=opts[0], key=f"ea_{q['id']}")
                            nb = st.text_input("B", value=opts[1], key=f"eb_{q['id']}")
                        with e2:
                            nc = st.text_input("C", value=opts[2], key=f"ec_{q['id']}")
                            nd = st.text_input("D", value=opts[3], key=f"ed_{q['id']}")
                        nc2 = st.selectbox("Correct Answer",["A","B","C","D"],
                                           index=q.get('correct',0),
                                           key=f"ecr_{q['id']}")
                        nf  = st.text_area("Fun Fact", value=q.get('fact',''),
                                           key=f"ef2_{q['id']}")
                        s1, s2 = st.columns(2)
                        with s1:
                            if st.form_submit_button("💾 Save Changes",
                                                     use_container_width=True):
                                try:
                                    db.collection("questions")\
                                      .document(q['id']).update({
                                        "question": new_q,
                                        "options":  [na,nb,nc,nd],
                                        "correct":  ["A","B","C","D"].index(nc2),
                                        "fact":     nf
                                    })
                                    st.success("✅ Updated!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ {e}")
                        with s2:
                            if st.form_submit_button("🗑️ Delete",
                                                     use_container_width=True):
                                try:
                                    db.collection("questions")\
                                      .document(q['id']).delete()
                                    st.success("✅ Deleted!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ {e}")
        except Exception as e:
            st.error(f"Error loading questions: {e}")

    with tab3:
        st.markdown("### 👥 All Registered Users")
        try:
            users = [u.to_dict() for u in
                     get_db().collection("users").stream()]
            st.markdown(f"**Total: {len(users)} users**")
            for i, u in enumerate(users):
                bg = "rgba(0,212,255,0.03)" if i%2==0 else "#0d1a26"
                st.markdown(f"""
                <div style="background:{bg}; border:1px solid #00d4ff11;
                            border-radius:8px; padding:12px 16px; margin:4px 0;
                            display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px;">
                    <span style="color:#94a3b8;">{u.get('email','')}</span>
                    <span style="color:#e2e8f0;">{u.get('display_name','')}</span>
                    <span style="color:#00d4ff;">Score: {u.get('total_score',0)}</span>
                    <span style="color:#8899aa;">{u.get('quizzes_taken',0)} quizzes</span>
                </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {e}")

    st.markdown("<br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1, 1])
    with col2:
        if st.button("🏠 Back to Home", use_container_width=True, key="ad_home"):
            go_home()

# ─── ROUTER ───────────────────────────────────────────────────────────────────
if st.session_state.user is None:
    show_login()
else:
    page = st.session_state.page
    if   page == "quiz":        show_quiz()
    elif page == "result":      show_result()
    elif page == "leaderboard": show_leaderboard()
    elif page == "analytics":   show_analytics()
    elif page == "admin":       show_admin()
    else:                       show_home()