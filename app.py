import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import pickle
import random
from auth import init_db, signup_user, signin_user



# ─────────────────────────────────────────────
#  1. PAGE CONFIG — MUST BE ABSOLUTE FIRST
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="MediScan.AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  2. GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
  --bg:      #0b0f1a;
  --surface: #111827;
  --card:    #161e2e;
  --border:  #1e2d45;
  --accent:  #38bdf8;
  --accent2: #818cf8;
  --accent3: #34d399;
  --accent4: #fb923c;
  --danger:  #f87171;
  --text:    #e2e8f0;
  --muted:   #64748b;
  --glow:    rgba(56,189,248,.15);
}

html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif;
  background-color: var(--bg) !important;
  color: var(--text) !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2.5rem !important; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

.stTabs [role="tablist"] {
  background: var(--surface);
  border-radius: 14px;
  padding: 6px;
  gap: 4px !important;
  border: 1px solid var(--border);
}
.stTabs [role="tab"] {
  border-radius: 10px !important;
  padding: 8px 18px !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  color: var(--muted) !important;
  transition: all .2s ease;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
  color: #fff !important;
  box-shadow: 0 4px 15px var(--glow) !important;
}

.stNumberInput input, .stTextInput input, .stSelectbox > div > div {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-size: 14px !important;
}
.stNumberInput input:focus, .stTextInput input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--glow) !important;
}

.stNumberInput label, .stSelectbox label, .stTextInput label,
.stFileUploader label, .stRadio label {
  color: var(--text) !important;
  font-size: 13px !important;
  font-weight: 500 !important;
}

.stButton > button {
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 12px !important;
  padding: 12px 32px !important;
  font-size: 15px !important;
  font-weight: 600 !important;
  letter-spacing: .5px;
  transition: all .25s ease !important;
  box-shadow: 0 4px 20px var(--glow) !important;
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 30px rgba(56,189,248,.3) !important;
}

.stSuccess { background: rgba(52,211,153,.12) !important; border-left: 3px solid var(--accent3) !important; border-radius: 10px !important; }
.stError   { background: rgba(248,113,113,.12) !important; border-left: 3px solid var(--danger) !important; border-radius: 10px !important; }
.stInfo    { background: rgba(56,189,248,.10) !important; border-left: 3px solid var(--accent) !important; border-radius: 10px !important; }
.stWarning { background: rgba(251,146,60,.12) !important; border-left: 3px solid var(--accent4) !important; border-radius: 10px !important; }

.stFileUploader > div { background: var(--card) !important; border: 2px dashed var(--border) !important; border-radius: 14px !important; }

hr { border-color: var(--border) !important; }

[data-testid="stMetricValue"] { color: var(--accent) !important; font-size: 2rem !important; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  3. HELPER FUNCTIONS
# ─────────────────────────────────────────────
def card(content_html, color="#38bdf8", padding="24px"):
    st.markdown(f"""
    <div style="background:#161e2e; border:1px solid #1e2d45; border-top:3px solid {color};
                border-radius:16px; padding:{padding}; margin-bottom:16px;">
      {content_html}
    </div>""", unsafe_allow_html=True)

def section_header(title, subtitle="", icon=""):
    st.markdown(f"""
    <div style="margin-bottom:1.5rem;">
      <h2 style="font-family:'DM Serif Display',serif; font-size:2rem; color:#e2e8f0; margin:0;">
        {icon} {title}
      </h2>
      {f'<p style="color:#64748b; font-size:15px; margin-top:4px;">{subtitle}</p>' if subtitle else ''}
    </div>""", unsafe_allow_html=True)

def result_positive(label="Positive", detail=""):
    st.markdown(f"""
    <div style="background:rgba(248,113,113,.12); border:1px solid rgba(248,113,113,.4);
                border-radius:14px; padding:20px 24px; text-align:center; margin-top:16px;">
      <div style="font-size:2.2rem;">⚠️</div>
      <div style="font-size:1.3rem; font-weight:700; color:#f87171; margin:6px 0;">{label}</div>
      {f'<div style="color:#94a3b8; font-size:13px;">{detail}</div>' if detail else ''}
    </div>""", unsafe_allow_html=True)

def result_negative(label="Negative", detail=""):
    st.markdown(f"""
    <div style="background:rgba(52,211,153,.12); border:1px solid rgba(52,211,153,.4);
                border-radius:14px; padding:20px 24px; text-align:center; margin-top:16px;">
      <div style="font-size:2.2rem;">✅</div>
      <div style="font-size:1.3rem; font-weight:700; color:#34d399; margin:6px 0;">{label}</div>
      {f'<div style="color:#94a3b8; font-size:13px;">{detail}</div>' if detail else ''}
    </div>""", unsafe_allow_html=True)

def fake_predict_bar(label="Running AI model"):
    with st.spinner(label):
        time.sleep(1.2)

# ─────────────────────────────────────────────
#  4. INIT DATABASE & SESSION STATE
# ─────────────────────────────────────────────
init_db()

if "user" not in st.session_state:
    st.session_state.user = None

# ─────────────────────────────────────────────
#  5. AUTH PAGE (shown when not logged in)
# ─────────────────────────────────────────────
def show_auth():
    st.markdown("""
    <div style="text-align:center; padding:50px 0 20px;">
      <div style="font-size:3.5rem;">🧬</div>
      <h1 style="font-family:'DM Serif Display',serif; font-size:2.6rem; color:#e2e8f0; margin:10px 0 6px;">
        MediScan.AI
      </h1>
      <p style="color:#64748b; font-size:15px; margin:0;">
        Sign in or create an account to continue
      </p>
    </div>
    """, unsafe_allow_html=True)

    # Center the auth form
    col1, col2, col3 = st.columns([1, 1.1, 1])
    with col2:
        auth_tab1, auth_tab2 = st.tabs(["Sign In", "Sign Up"])

        # ── Sign In ──
        with auth_tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            login    = st.text_input("Username or Email", key="si_login")
            password = st.text_input("Password", type="password", key="si_pass")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Sign In", use_container_width=True, key="si_btn"):
                if not login or not password:
                    st.error("Please fill in all fields.")
                else:
                    ok, msg, user_info = signin_user(login, password)
                    if ok:
                        st.session_state.user = user_info
                        st.rerun()
                    else:
                        st.error(msg)

        # ── Sign Up ──
        with auth_tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            username = st.text_input("Username", key="su_user")
            email    = st.text_input("Email",    key="su_email")
            password = st.text_input("Password", type="password", key="su_pass")
            confirm  = st.text_input("Confirm Password", type="password", key="su_conf")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Create Account", use_container_width=True, key="su_btn"):
                if not username or not email or not password or not confirm:
                    st.error("Please fill in all fields.")
                elif password != confirm:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = signup_user(username, email, password)
                    if ok:
                        st.success("✅ Account created! Please sign in.")
                    else:
                        st.error(msg)

# ─────────────────────────────────────────────
#  6. MAIN APP (shown after login)
# ─────────────────────────────────────────────
def show_app():


    # ── Sidebar ──
    with st.sidebar:
        st.markdown(f"""
        <div style="background:#161e2e; border:1px solid #1e2d45; border-radius:12px;
                    padding:20px 16px; text-align:center; margin-bottom:16px;">
          <div style="font-size:2.5rem;">👤</div>
          <div style="font-weight:600; color:#e2e8f0; font-size:15px; margin-top:8px;">
            {st.session_state.user['username']}
          </div>
          <div style="color:#64748b; font-size:12px; margin-top:4px;">
            {st.session_state.user['email']}
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # ── Top Header Banner ──
    st.markdown(f"""
    <div style="display:flex; align-items:center; justify-content:space-between;
                background:#111827; border:1px solid #1e2d45; border-radius:18px;
                padding:18px 28px; margin-bottom:24px; flex-wrap:wrap; gap:12px;">
      <div>
        <div style="font-family:'DM Serif Display',serif; font-size:1.8rem; color:#e2e8f0; line-height:1.1;">
          🧬 MediScan.AI
        </div>
        <div style="color:#64748b; font-size:13px; margin-top:4px;">
          Welcome, <strong style="color:#38bdf8;">{st.session_state.user['username']}</strong> ·
          Machine Learning + Deep Learning · Clinical Records + Medical Imaging
        </div>
      </div>
      <div style="display:flex; gap:10px; flex-wrap:wrap;">
        <span style="background:rgba(56,189,248,.12); color:#38bdf8; border:1px solid rgba(56,189,248,.3);
                     border-radius:20px; padding:5px 14px; font-size:12px; font-weight:600;">SATI</span>
        <span style="background:rgba(129,140,248,.12); color:#818cf8; border:1px solid rgba(129,140,248,.3);
                     border-radius:20px; padding:5px 14px; font-size:12px; font-weight:600;">AIADS</span>
        <span style="background:rgba(52,211,153,.12); color:#34d399; border:1px solid rgba(52,211,153,.3);
                     border-radius:20px; padding:5px 14px; font-size:12px; font-weight:600;">2022-2026</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Main Tabs ──
    tabs = st.tabs([
        "🏠 Home",
        "🩸 Diabetes",
        "🧠 Brain Tumor",
        "❤️ Heart Disease",
        "ℹ️ About",
    ])

    # ══════════════════════════════════════════════

    with tabs[0]:
        # ── Hero Section ─────────────────────────────────────────────────────────
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;600&display=swap');

        .hero-container {
            background: linear-gradient(135deg, #0a0f1e 0%, #0d1b2a 40%, #0a1628 100%);
            border: 1px solid #1e3a5f;
            border-radius: 20px;
            padding: 60px 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
            margin-bottom: 30px;
        }
        .hero-container::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(ellipse at center,
                rgba(96, 165, 250, 0.05) 0%,
                rgba(168, 85, 247, 0.03) 40%,
                transparent 70%);
            animation: pulse 4s ease-in-out infinite;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            50%       { transform: scale(1.1); opacity: 1; }
        }
        .hero-badge {
            display: inline-block;
            background: linear-gradient(90deg, #1e3a5f, #1e2d45);
            border: 1px solid #3b82f6;
            border-radius: 99px;
            padding: 6px 20px;
            font-family: 'Exo 2', sans-serif;
            font-size: 12px;
            color: #60a5fa;
            letter-spacing: 3px;
            text-transform: uppercase;
            margin-bottom: 24px;
        }
        .hero-title {
            font-family: 'Orbitron', monospace;
            font-size: 52px;
            font-weight: 900;
            background: linear-gradient(135deg, #ffffff 0%, #60a5fa 50%, #a855f7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0 0 16px 0;
            line-height: 1.2;
        }
        .hero-subtitle {
            font-family: 'Exo 2', sans-serif;
            font-size: 18px;
            color: #64748b;
            font-weight: 300;
            margin-bottom: 40px;
            letter-spacing: 1px;
        }
        .hero-stats {
            display: flex;
            justify-content: center;
            gap: 40px;
            flex-wrap: wrap;
            margin-top: 40px;
        }
        .stat-item {
            text-align: center;
        }
        .stat-number {
            font-family: 'Orbitron', monospace;
            font-size: 32px;
            font-weight: 700;
            color: #60a5fa;
        }
        .stat-label {
            font-family: 'Exo 2', sans-serif;
            font-size: 11px;
            color: #475569;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-top: 4px;
        }
        .disease-card {
            background: linear-gradient(135deg, #0d1b2a, #0a1628);
            border: 1px solid #1e3a5f;
            border-radius: 16px;
            padding: 28px 24px;
            text-align: center;
            transition: all 0.3s ease;
            height: 100%;
            position: relative;
            overflow: hidden;
        }
        .disease-card::after {
            content: '';
            position: absolute;
            bottom: 0; left: 0; right: 0;
            height: 3px;
            border-radius: 0 0 16px 16px;
        }
        .card-heart::after  { background: linear-gradient(90deg, #f87171, #ef4444); }
        .card-brain::after  { background: linear-gradient(90deg, #c084fc, #a855f7); }
        .card-diabetes::after { background: linear-gradient(90deg, #34d399, #10b981); }
        .card-icon {
            font-size: 48px;
            margin-bottom: 16px;
            display: block;
        }
        .card-title {
            font-family: 'Orbitron', monospace;
            font-size: 15px;
            font-weight: 700;
            color: #f1f5f9;
            margin-bottom: 10px;
        }
        .card-desc {
            font-family: 'Exo 2', sans-serif;
            font-size: 12px;
            color: #64748b;
            line-height: 1.7;
            margin-bottom: 16px;
        }
        .card-accuracy {
            font-family: 'Orbitron', monospace;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 4px;
        }
        .card-acc-label {
            font-size: 10px;
            color: #475569;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .how-it-works {
            background: linear-gradient(135deg, #0d1b2a, #0a1628);
            border: 1px solid #1e3a5f;
            border-radius: 16px;
            padding: 32px;
            margin: 20px 0;
        }
        .step-item {
            display: flex;
            align-items: flex-start;
            gap: 20px;
            margin-bottom: 24px;
        }
        .step-number {
            font-family: 'Orbitron', monospace;
            font-size: 24px;
            font-weight: 900;
            color: #1e3a5f;
            min-width: 40px;
            line-height: 1;
        }
        .step-content-title {
            font-family: 'Exo 2', sans-serif;
            font-size: 14px;
            font-weight: 600;
            color: #f1f5f9;
            margin-bottom: 4px;
        }
        .step-content-desc {
            font-family: 'Exo 2', sans-serif;
            font-size: 12px;
            color: #64748b;
            line-height: 1.6;
        }
        .tech-badge {
            display: inline-block;
            background: #1e2d45;
            border: 1px solid #2d3f55;
            border-radius: 6px;
            padding: 4px 12px;
            font-size: 11px;
            color: #60a5fa;
            margin: 4px;
            font-family: 'Exo 2', sans-serif;
        }
        .warning-banner {
            background: linear-gradient(135deg, #2d1f0a, #3d2a0f);
            border: 1px solid #f59e0b;
            border-left: 4px solid #f59e0b;
            border-radius: 12px;
            padding: 16px 20px;
            margin-top: 20px;
        }
        </style>

        <!-- Hero Section -->
        <div class="hero-container">
            <div class="hero-badge">⚕️ AI-Powered Medical Screening</div>
            <h1 class="hero-title">MediScan AI</h1>
            <p class="hero-subtitle">
                Advanced Disease Prediction using Machine Learning & Deep Learning
            </p>
            <div style="display:flex; justify-content:center; gap:12px; flex-wrap:wrap;">
                <span style="background:#1e2d45; border:1px solid #3b82f6;
                             border-radius:99px; padding:8px 20px;
                             font-family:'Exo 2',sans-serif; font-size:13px; color:#60a5fa;">
                    ❤️ Heart Disease
                </span>
                <span style="background:#1e2d45; border:1px solid #a855f7;
                             border-radius:99px; padding:8px 20px;
                             font-family:'Exo 2',sans-serif; font-size:13px; color:#c084fc;">
                    🧠 Brain Tumor
                </span>
                <span style="background:#1e2d45; border:1px solid #10b981;
                             border-radius:99px; padding:8px 20px;
                             font-family:'Exo 2',sans-serif; font-size:13px; color:#34d399;">
                    🩸 Diabetes
                </span>
            </div>
            <div class="hero-stats">
                <div class="stat-item">
                    <div class="stat-number">3</div>
                    <div class="stat-label">Diseases Covered</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">90%</div>
                    <div class="stat-label">Heart Accuracy</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">87%</div>
                    <div class="stat-label">Brain Accuracy</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">85%</div>
                    <div class="stat-label">Diabetes Accuracy</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Disease Cards ─────────────────────────────────────────────────────────
        st.markdown("""
        <div style="font-family:'Orbitron',monospace; font-size:13px; color:#475569;
                    text-transform:uppercase; letter-spacing:3px;
                    text-align:center; margin-bottom:20px;">
            Prediction Modules
        </div>
        """, unsafe_allow_html=True)

        card1, card2, card3 = st.columns(3, gap="large")

        with card1:
            st.markdown("""
            <div class="disease-card card-heart">
                <span class="card-icon">❤️</span>
                <div class="card-title">Heart Disease</div>
                <div class="card-desc">
                    Predicts cardiovascular disease risk using clinical indicators
                    like glucose, blood pressure, cholesterol and ECG data.
                </div>
                <div class="card-accuracy" style="color:#f87171;">90%</div>
                <div class="card-acc-label">Model Accuracy</div>
                <div style="margin-top:14px;">
                    <span style="background:#2d1b1b; border:1px solid #f87171;
                                 border-radius:6px; padding:3px 10px;
                                 font-size:10px; color:#f87171;">
                        Random Forest
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with card2:
            st.markdown("""
            <div class="disease-card card-brain">
                <span class="card-icon">🧠</span>
                <div class="card-title">Brain Tumor</div>
                <div class="card-desc">
                    Classifies brain MRI scans into 4 categories — Glioma,
                    Meningioma, Pituitary Tumor and No Tumor using deep learning.
                </div>
                <div class="card-accuracy" style="color:#c084fc;">87%</div>
                <div class="card-acc-label">Model Accuracy</div>
                <div style="margin-top:14px;">
                    <span style="background:#2a1b3d; border:1px solid #c084fc;
                                 border-radius:6px; padding:3px 10px;
                                 font-size:10px; color:#c084fc;">
                        MobileNetV2
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with card3:
            st.markdown("""
            <div class="disease-card card-diabetes">
                <span class="card-icon">🩸</span>
                <div class="card-title">Diabetes</div>
                <div class="card-desc">
                    Predicts diabetes risk using metabolic indicators like
                    glucose level, BMI, insulin, blood pressure and age.
                </div>
                <div class="card-accuracy" style="color:#34d399;">85%</div>
                <div class="card-acc-label">Model Accuracy</div>
                <div style="margin-top:14px;">
                    <span style="background:#1b2d1b; border:1px solid #34d399;
                                 border-radius:6px; padding:3px 10px;
                                 font-size:10px; color:#34d399;">
                        Machine Learning
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── How It Works + Tech Stack ─────────────────────────────────────────────
        hw1, hw2 = st.columns([1, 1], gap="large")

        with hw1:
            st.markdown("""
            <div class="how-it-works">
                <div style="font-family:'Orbitron',monospace; font-size:14px;
                            font-weight:700; color:#f1f5f9; margin-bottom:24px;
                            letter-spacing:1px;">
                    ⚡ How It Works
                </div>
                <div class="step-item">
                    <div class="step-number">01</div>
                    <div>
                        <div class="step-content-title">Select Disease Tab</div>
                        <div class="step-content-desc">
                            Choose from Heart Disease, Brain Tumor or Diabetes
                            prediction from the tabs above.
                        </div>
                    </div>
                </div>
                <div class="step-item">
                    <div class="step-number">02</div>
                    <div>
                        <div class="step-content-title">Enter Your Parameters</div>
                        <div class="step-content-desc">
                            Fill in your health indicators from recent blood tests,
                            reports or upload your MRI scan for brain tumor.
                        </div>
                    </div>
                </div>
                <div class="step-item">
                    <div class="step-number">03</div>
                    <div>
                        <div class="step-content-title">AI Model Analyzes</div>
                        <div class="step-content-desc">
                            Our trained ML/DL models process your inputs and
                            generate a prediction with confidence score.
                        </div>
                    </div>
                </div>
                <div class="step-item" style="margin-bottom:0;">
                    <div class="step-number">04</div>
                    <div>
                        <div class="step-content-title">Get Results & Guidance</div>
                        <div class="step-content-desc">
                            Receive instant prediction with recommended checkups
                            and next steps based on the result.
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with hw2:
            st.markdown("""
            <div class="how-it-works">
                <div style="font-family:'Orbitron',monospace; font-size:14px;
                            font-weight:700; color:#f1f5f9; margin-bottom:24px;
                            letter-spacing:1px;">
                    🛠️ Tech Stack
                </div>
                <div style="margin-bottom:20px;">
                    <div style="font-family:'Exo 2',sans-serif; font-size:12px;
                                color:#475569; text-transform:uppercase;
                                letter-spacing:2px; margin-bottom:10px;">
                        Frontend
                    </div>
                    <span class="tech-badge">🐍 Python</span>
                    <span class="tech-badge">⚡ Streamlit</span>
                    <span class="tech-badge">📊 Plotly</span>
                </div>
                <div style="margin-bottom:20px;">
                    <div style="font-family:'Exo 2',sans-serif; font-size:12px;
                                color:#475569; text-transform:uppercase;
                                letter-spacing:2px; margin-bottom:10px;">
                        Machine Learning
                    </div>
                    <span class="tech-badge">🤖 Scikit-learn</span>
                    <span class="tech-badge">🌲 Random Forest</span>
                    <span class="tech-badge">🌳 Decision Tree</span>
                </div>
                <div style="margin-bottom:20px;">
                    <div style="font-family:'Exo 2',sans-serif; font-size:12px;
                                color:#475569; text-transform:uppercase;
                                letter-spacing:2px; margin-bottom:10px;">
                        Deep Learning
                    </div>
                    <span class="tech-badge">🧠 TensorFlow</span>
                    <span class="tech-badge">⚙️ Keras</span>
                    <span class="tech-badge">📱 MobileNetV2</span>
                </div>
                <div>
                    <div style="font-family:'Exo 2',sans-serif; font-size:12px;
                                color:#475569; text-transform:uppercase;
                                letter-spacing:2px; margin-bottom:10px;">
                        Data Processing
                    </div>
                    <span class="tech-badge">🐼 Pandas</span>
                    <span class="tech-badge">🔢 NumPy</span>
                    <span class="tech-badge">🖼️ Pillow</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Key Features ──────────────────────────────────────────────────────────
        st.markdown("""
        <div style="font-family:'Orbitron',monospace; font-size:13px; color:#475569;
                    text-transform:uppercase; letter-spacing:3px;
                    text-align:center; margin-bottom:20px;">
            Key Features
        </div>
        """, unsafe_allow_html=True)

        f1, f2, f3, f4 = st.columns(4, gap="medium")
        features_list = [
            ("⚡", "#60a5fa", "Instant Results",
             "Get AI predictions in seconds with confidence scores"),
            ("🎯", "#34d399", "High Accuracy",
             "Models trained on real medical datasets with 85-96% accuracy"),
            ("🔒", "#c084fc", "Privacy First",
             "No data stored. All predictions happen locally on your machine"),
            ("📋", "#fbbf24", "Smart Guidance",
             "Personalized checkup recommendations based on your results"),
        ]

        for col, (icon, color, title, desc) in zip([f1, f2, f3, f4], features_list):
            with col:
                st.markdown(f"""
                <div style="background:#0d1b2a; border:1px solid #1e3a5f;
                            border-radius:12px; padding:20px 16px; text-align:center;
                            border-top: 3px solid {color};">
                    <div style="font-size:32px; margin-bottom:12px;">{icon}</div>
                    <div style="font-family:'Orbitron',monospace; font-size:12px;
                                font-weight:700; color:#f1f5f9; margin-bottom:8px;">
                        {title}
                    </div>
                    <div style="font-family:'Exo 2',sans-serif; font-size:11px;
                                color:#64748b; line-height:1.6;">
                        {desc}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # ── Disclaimer Banner ─────────────────────────────────────────────────────
        st.markdown("""
        <div class="warning-banner">
            <div style="font-family:'Exo 2',sans-serif; font-size:13px;
                        color:#f59e0b; font-weight:600; margin-bottom:6px;">
                ⚠️ Important Medical Disclaimer
            </div>
            <div style="font-family:'Exo 2',sans-serif; font-size:12px;
                        color:#92400e; line-height:1.8;">
                This application is developed as an <b style="color:#fbbf24;">
                academic major project</b> and is intended for
                <b style="color:#fbbf24;">educational and research purposes only</b>.
                The predictions made by this system are based on machine learning models
                and should <u>NOT</u> be used as a substitute for professional medical advice,
                diagnosis, or treatment. Always consult a qualified healthcare professional
                for medical decisions. The developers are not responsible for any medical
                decisions made based on this tool.
            </div>
        </div>
        <br>
        """, unsafe_allow_html=True)
    # ══════════════════════════════════════════════
    #  TAB 2 — DIABETES
    # ══════════════════════════════════════════════
    with tabs[1]:
        section_header("Diabetes Prediction", "Based on glucose and metabolic indicators", "🩸")

        # ── Info Expander ────────────────────────────────────────────────────────
        with st.expander("ℹ️ How to fill this form? Click to understand each parameter"):
            di1, di2 = st.columns(2)
            with di1:
                st.markdown("""
                <div style="background:#1e2d45; border-radius:10px; padding:14px; margin-bottom:10px;">
                    <b style="color:#60a5fa;">🩸 Glucose Level</b>
                    <p style="color:#94a3b8; font-size:12px; margin-top:6px; line-height:1.8;">
                        Blood sugar level measured after 2 hours in an oral glucose tolerance test.<br>
                        <b style="color:#34d399;">Normal:</b> below 140 mg/dL<br>
                        <b style="color:#fbbf24;">Prediabetes:</b> 140–199 mg/dL<br>
                        <b style="color:#f87171;">Diabetic:</b> 200 mg/dL or above
                    </p>
                </div>
                <div style="background:#1e2d45; border-radius:10px; padding:14px; margin-bottom:10px;">
                    <b style="color:#60a5fa;">⚖️ BMI (Body Mass Index)</b>
                    <p style="color:#94a3b8; font-size:12px; margin-top:6px; line-height:1.8;">
                        Calculated from your weight and height.<br>
                        <b style="color:#f1f5f9;">Formula:</b> Weight(kg) / Height(m)²<br>
                        <b style="color:#34d399;">Normal:</b> 18.5–24.9<br>
                        <b style="color:#fbbf24;">Overweight:</b> 25–29.9<br>
                        <b style="color:#f87171;">Obese:</b> 30 or above
                    </p>
                </div>
                <div style="background:#1e2d45; border-radius:10px; padding:14px; margin-bottom:10px;">
                    <b style="color:#60a5fa;">💉 Insulin Level</b>
                    <p style="color:#94a3b8; font-size:12px; margin-top:6px; line-height:1.8;">
                        2-Hour serum insulin level (mu U/ml).<br>
                        Available from basic blood test report.<br>
                        <b style="color:#34d399;">Normal:</b> 16–166 mu U/ml<br>
                        <b style="color:#f87171;">High:</b> above 166 mu U/ml
                    </p>
                </div>
                """, unsafe_allow_html=True)
            with di2:
                st.markdown("""
                <div style="background:#1e2d45; border-radius:10px; padding:14px; margin-bottom:10px;">
                    <b style="color:#60a5fa;">🩺 Blood Pressure</b>
                    <p style="color:#94a3b8; font-size:12px; margin-top:6px; line-height:1.8;">
                        Diastolic blood pressure (mm Hg) — the lower number on BP monitor.<br>
                        <b style="color:#34d399;">Normal:</b> below 80 mm Hg<br>
                        <b style="color:#fbbf24;">Elevated:</b> 80–89 mm Hg<br>
                        <b style="color:#f87171;">High:</b> 90 mm Hg or above
                    </p>
                </div>
                <div style="background:#1e2d45; border-radius:10px; padding:14px; margin-bottom:10px;">
                    <b style="color:#60a5fa;">🤰 Pregnancies</b>
                    <p style="color:#94a3b8; font-size:12px; margin-top:6px; line-height:1.8;">
                        Number of times pregnant.<br>
                        Higher number of pregnancies increases gestational diabetes risk.<br>
                        <b style="color:#f1f5f9;">Enter 0</b> if never pregnant or male.
                    </p>
                </div>
                <div style="background:#1e2d45; border-radius:10px; padding:14px; margin-bottom:10px;">
                    <b style="color:#60a5fa;">🔬 Suggested Tests After Prediction</b>
                    <p style="color:#94a3b8; font-size:12px; margin-top:6px; line-height:1.8;">
                        <b style="color:#f1f5f9;">DiabetesPedigreeFunction</b> — genetic diabetes risk score from family history test<br>
                        <b style="color:#f1f5f9;">Skin Thickness</b> — triceps skinfold thickness measured by doctor
                    </p>
                </div>
                """, unsafe_allow_html=True)

        # ── Visual Insights ──────────────────────────────────────────────────────
        with st.expander("📊 Diabetes Insights — Understand the Risk Patterns", expanded=False):
            dv1, dv2, dv3 = st.columns(3)

            with dv1:
                st.markdown("""
                <div style="background:#1e2d45; border-radius:12px; padding:16px;">
                    <div style="font-size:13px; color:#94a3b8; margin-bottom:12px; font-weight:600;">
                        📊 Feature Importance
                    </div>
                """, unsafe_allow_html=True)
                fig_imp = go.Figure(go.Bar(
                    x=[33, 18, 12, 10, 9, 8, 5, 5],
                    y=['Glucose', 'BMI', 'Age', 'DiabetesPedigree', 'Insulin',
                       'BloodPressure', 'SkinThickness', 'Pregnancies'],
                    orientation='h',
                    marker_color=['#f87171', '#fb923c', '#fbbf24', '#a3e635',
                                  '#34d399', '#22d3ee', '#60a5fa', '#c084fc'],
                    text=['33%', '18%', '12%', '10%', '9%', '8%', '5%', '5%'],
                    textposition='outside',
                    textfont=dict(color='white', size=10)
                ))
                fig_imp.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#94a3b8', size=10),
                    height=250,
                    margin=dict(t=10, b=10, l=10, r=40),
                    xaxis=dict(showgrid=True, gridcolor='#1e3a5f', ticksuffix='%'),
                    yaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig_imp, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with dv2:
                st.markdown("""
                <div style="background:#1e2d45; border-radius:12px; padding:16px;">
                    <div style="font-size:13px; color:#94a3b8; margin-bottom:12px; font-weight:600;">
                        🩸 Glucose Risk Zones
                    </div>
                """, unsafe_allow_html=True)
                fig_gluc = go.Figure(go.Bar(
                    x=['Normal\n(<140)', 'Prediabetes\n(140-199)', 'Diabetic\n(≥200)'],
                    y=[15, 45, 85],
                    marker_color=['#34d399', '#fbbf24', '#f87171'],
                    text=['15%', '45%', '85%'],
                    textposition='outside',
                    textfont=dict(color='white', size=11)
                ))
                fig_gluc.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#94a3b8', size=10),
                    height=250,
                    margin=dict(t=10, b=10, l=10, r=10),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='#1e3a5f',
                        range=[0, 110],
                        ticksuffix='%',
                        title='Diabetes Risk'
                    ),
                    xaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig_gluc, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with dv3:
                st.markdown("""
                <div style="background:#1e2d45; border-radius:12px; padding:16px;">
                    <div style="font-size:13px; color:#94a3b8; margin-bottom:12px; font-weight:600;">
                        ⚠️ Normal Reference Ranges
                    </div>
                    <table style="width:100%; font-size:11px; color:#94a3b8; border-collapse:collapse;">
                        <tr style="border-bottom:1px solid #2d3f55;">
                            <th style="text-align:left; padding:5px; color:#60a5fa;">Parameter</th>
                            <th style="text-align:center; padding:5px; color:#34d399;">Normal</th>
                            <th style="text-align:center; padding:5px; color:#f87171;">High Risk</th>
                        </tr>
                        <tr style="border-bottom:1px solid #2d3f55;">
                            <td style="padding:5px;">Glucose</td>
                            <td style="text-align:center; padding:5px; color:#34d399;">&lt;140</td>
                            <td style="text-align:center; padding:5px; color:#f87171;">&gt;200</td>
                        </tr>
                        <tr style="border-bottom:1px solid #2d3f55;">
                            <td style="padding:5px;">BMI</td>
                            <td style="text-align:center; padding:5px; color:#34d399;">18.5–24.9</td>
                            <td style="text-align:center; padding:5px; color:#f87171;">&gt;30</td>
                        </tr>
                        <tr style="border-bottom:1px solid #2d3f55;">
                            <td style="padding:5px;">Blood Pressure</td>
                            <td style="text-align:center; padding:5px; color:#34d399;">&lt;80</td>
                            <td style="text-align:center; padding:5px; color:#f87171;">&gt;90</td>
                        </tr>
                        <tr style="border-bottom:1px solid #2d3f55;">
                            <td style="padding:5px;">Insulin</td>
                            <td style="text-align:center; padding:5px; color:#34d399;">16–166</td>
                            <td style="text-align:center; padding:5px; color:#f87171;">&gt;166</td>
                        </tr>
                        <tr>
                            <td style="padding:5px;">Age</td>
                            <td style="text-align:center; padding:5px; color:#34d399;">&lt;45</td>
                            <td style="text-align:center; padding:5px; color:#f87171;">&gt;45</td>
                        </tr>
                    </table>
                    <div style="margin-top:12px; font-size:11px; color:#64748b; line-height:1.8;">
                        💡 <b style="color:#94a3b8;">Did you know?</b><br>
                        • 1 in 10 adults worldwide has diabetes<br>
                        • 50% of diabetics are undiagnosed<br>
                        • Type 2 diabetes is 90% preventable<br>
                        • Early detection saves lives
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Main Layout ──────────────────────────────────────────────────────────
        col_form, col_result = st.columns([3, 2], gap="large")

        with col_form:
            c1, c2 = st.columns(2)
            with c1:
                d_glucose = st.number_input(
                    "Glucose Level (mg/dL)",
                    0, 300, 120, key="d_glucose",
                    help="Normal: <140 | Prediabetes: 140-199 | Diabetic: ≥200"
                )
                d_bmi = st.number_input(
                    "BMI (Body Mass Index)",
                    0.0, 70.0, 25.0, step=0.1, key="d_bmi",
                    help="Normal: 18.5-24.9 | Overweight: 25-29.9 | Obese: ≥30"
                )
                d_age = st.number_input(
                    "Age", 1, 120, 30, key="d_age",
                    help="Age is a significant risk factor for diabetes"
                )
            with c2:
                d_bp = st.number_input(
                    "Blood Pressure (mm Hg)",
                    0, 200, 70, key="d_bp",
                    help="Diastolic BP — lower number on BP monitor. Normal: <80"
                )
                d_insulin = st.number_input(
                    "Insulin Level (mu U/ml)",
                    0, 900, 80, key="d_insulin",
                    help="2-Hour serum insulin. Normal range: 16–166 mu U/ml"
                )
                d_preg = st.number_input(
                    "Number of Pregnancies",
                    0, 20, 0, key="d_preg",
                    help="Enter 0 if never pregnant or male"
                )

            d_btn = st.button("🔍 Predict Diabetes", key="d_predict_btn", use_container_width=True)

            if d_btn:
                fake_predict_bar("Analyzing metabolic indicators…")

                # Build DataFrame with exact training column order
                feature_dict = {
                    'Pregnancies': [d_preg],
                    'Glucose': [d_glucose],
                    'BloodPressure': [d_bp],
                    'SkinThickness': [20],  # dataset mean default
                    'Insulin': [d_insulin],
                    'BMI': [d_bmi],
                    'DiabetesPedigreeFunction': [0.47],  # dataset mean default
                    'Age': [d_age]
                }

                features_df = pd.DataFrame(feature_dict)

                try:
                    with open("diabetes_disease_LR_model.pkl", "rb") as f:
                        diabetes_model = pickle.load(f)

                    # Check if scaler exists
                    try:
                        with open("diabetes_scaler.pkl", "rb") as f:
                            diabetes_scaler = pickle.load(f)
                        features_scaled = diabetes_scaler.transform(features_df)
                        prediction = diabetes_model.predict(features_scaled)[0]
                        proba = diabetes_model.predict_proba(features_scaled)[0]
                    except FileNotFoundError:
                        # No scaler — predict directly
                        prediction = diabetes_model.predict(features_df)[0]
                        proba = diabetes_model.predict_proba(features_df)[0]

                    conf = int(proba[1] * 100)

                except FileNotFoundError:
                    st.error("⚠️ Model file 'diabetes_model.pkl' not found.")
                    prediction = None
                    conf = 0

                if prediction is not None:
                    with col_result:
                        if prediction == 1:
                            result_positive("Diabetes Detected", f"Risk confidence: {conf}%")
                            st.markdown(f"""
                            <div style="
                                background: linear-gradient(135deg, #2d1b1b, #3d1f1f);
                                border: 1px solid #f87171;
                                border-left: 4px solid #ef4444;
                                border-radius: 12px;
                                padding: 18px 20px;
                                margin-top: 16px;
                            ">
                                <div style="font-size:18px; font-weight:700; color:#f87171; margin-bottom:10px;">
                                    🏥 Please Consult a Doctor
                                </div>
                                <div style="font-size:13px; color:#fca5a5; line-height:1.8;">
                                    Our model indicates a <b>risk of diabetes</b>.
                                    We recommend the following tests and checkups:
                                </div>
                                <ul style="font-size:13px; color:#fcd9d9; margin-top:10px; line-height:2; padding-left:18px;">
                                    <li>🩸 <b>HbA1c Test</b> — Average blood sugar over 3 months</li>
                                    <li>💉 <b>Fasting Blood Sugar Test</b> — Check glucose after fasting</li>
                                    <li>📊 <b>Oral Glucose Tolerance Test</b> — 2 hour glucose test</li>
                                    <li>🧬 <b>DiabetesPedigreeFunction Test</b> — Genetic diabetes risk score from family history</li>
                                    <li>📏 <b>Skin Thickness (Triceps Skinfold)</b> — Body fat measurement by doctor</li>
                                    <li>🩺 <b>Kidney Function Test</b> — Diabetes affects kidneys</li>
                                    <li>👁️ <b>Eye Examination</b> — Check for diabetic retinopathy</li>
                                    <li>🦶 <b>Foot Examination</b> — Check for diabetic neuropathy</li>
                                </ul>
                                <div style="
                                    margin-top:14px;
                                    background:#3d1f1f;
                                    border-radius:8px;
                                    padding:10px 14px;
                                    font-size:12px;
                                    color:#fca5a5;
                                ">
                                    ⚠️ <b>Disclaimer:</b> This is an AI-based screening tool only.
                                    It does <u>not</u> replace professional medical diagnosis.
                                    Please consult a certified endocrinologist or diabetologist.
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                        else:
                            result_negative("No Diabetes Detected", f"Confidence: {100 - conf}% negative")
                            st.markdown(f"""
                            <div style="
                                background: linear-gradient(135deg, #1b2d1b, #1f3d1f);
                                border: 1px solid #34d399;
                                border-left: 4px solid #10b981;
                                border-radius: 12px;
                                padding: 18px 20px;
                                margin-top: 16px;
                            ">
                                <div style="font-size:18px; font-weight:700; color:#34d399; margin-bottom:10px;">
                                    ✅ No Diabetes Risk Detected!
                                </div>
                                <div style="font-size:13px; color:#a7f3d0; line-height:1.8;">
                                    Great news! No significant diabetes risk detected.
                                    Still consider these preventive tests:
                                </div>
                                <ul style="font-size:13px; color:#d1fae5; margin-top:10px; line-height:2; padding-left:18px;">
                                    <li>🧬 <b>DiabetesPedigreeFunction Test</b> — Know your genetic diabetes risk</li>
                                    <li>📏 <b>Skin Thickness Test</b> — Monitor body fat levels</li>
                                    <li>🥗 Maintain a low sugar balanced diet</li>
                                    <li>🏃 Exercise regularly (30 min/day)</li>
                                    <li>⚖️ Keep BMI in healthy range (18.5–24.9)</li>
                                    <li>📅 Annual blood sugar checkup recommended</li>
                                </ul>
                                <div style="
                                    margin-top:14px;
                                    background:#1f3d1f;
                                    border-radius:8px;
                                    padding:10px 14px;
                                    font-size:12px;
                                    color:#a7f3d0;
                                ">
                                    ⚠️ <b>Disclaimer:</b> This is an AI-based screening tool only.
                                    Regular checkups with a doctor are always recommended.
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                        # Risk progress bar
                        st.markdown(f"""
                        <div style="margin-top:14px;">
                          <div style="display:flex; justify-content:space-between; font-size:12px;
                                      color:#64748b; margin-bottom:6px;">
                            <span>Diabetes Risk Score</span><span>{conf}%</span>
                          </div>
                          <div style="background:#1e2d45; border-radius:99px; height:8px;">
                            <div style="background:{'#f87171' if prediction == 1 else '#34d399'};
                                        width:{conf}%; height:100%; border-radius:99px;
                                        transition: width 0.5s ease;">
                            </div>
                          </div>
                        </div>""", unsafe_allow_html=True)

                        # Individual risk indicators
                        st.markdown("""
                        <div style="margin-top:16px; font-size:12px;
                                    color:#64748b; font-weight:600;">
                            Key Risk Indicators:
                        </div>""", unsafe_allow_html=True)

                        indicators = [
                            ("Glucose", d_glucose, 140, 200, "mg/dL"),
                            ("BMI", d_bmi, 25, 30, ""),
                            ("Blood Pressure", d_bp, 80, 90, "mmHg"),
                            ("Insulin", d_insulin, 100, 166, "mu U/ml"),
                        ]

                        for name, value, warn, high, unit in indicators:
                            if value >= high:
                                ind_color = '#f87171'
                                ind_label = 'High Risk'
                            elif value >= warn:
                                ind_color = '#fbbf24'
                                ind_label = 'Borderline'
                            else:
                                ind_color = '#34d399'
                                ind_label = 'Normal'

                            st.markdown(f"""
                            <div style="margin-top:8px; background:#1e2d45;
                                        border-radius:8px; padding:8px 12px;">
                                <div style="display:flex; justify-content:space-between;
                                            font-size:11px; color:#94a3b8;">
                                    <span>{name}</span>
                                    <span style="color:{ind_color};">
                                        {value} {unit} — {ind_label}
                                    </span>
                                </div>
                            </div>""", unsafe_allow_html=True)
    # ══════════════════════════════════════════════
    #
    # ══════════════════════════════════════════════
    #  TAB 3 — BRAIN TUMOR
    # ══════════════════════════════════════════════
    with tabs[2]:
        section_header("Brain Tumor Detection", "MRI scan analysis using deep learning", "🧠")

        # ── Info Expander ────────────────────────────────────────────────────────
        with st.expander("ℹ️ What are the 4 types of Brain Tumors? Click to learn"):
            ti1, ti2 = st.columns(2)
            with ti1:
                st.markdown("""
                <div style="background:#1e2d45; border-radius:10px; padding:14px; margin-bottom:10px;">
                    <b style="color:#c084fc;">🔬 Glioma</b>
                    <p style="color:#94a3b8; font-size:12px; margin-top:6px; line-height:1.8;">
                        Tumor that starts in the <b style="color:#f1f5f9;">glial cells</b> of the brain or spine.
                        One of the most common and aggressive brain tumors.
                        Can affect brain function depending on location.
                    </p>
                </div>
                <div style="background:#1e2d45; border-radius:10px; padding:14px; margin-bottom:10px;">
                    <b style="color:#c084fc;">🔬 Meningioma</b>
                    <p style="color:#94a3b8; font-size:12px; margin-top:6px; line-height:1.8;">
                        Tumor that forms in the <b style="color:#f1f5f9;">meninges</b> (membranes surrounding brain/spine).
                        Usually slow growing and often benign.
                        Most common primary brain tumor type.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            with ti2:
                st.markdown("""
                <div style="background:#1e2d45; border-radius:10px; padding:14px; margin-bottom:10px;">
                    <b style="color:#c084fc;">🔬 Pituitary Tumor</b>
                    <p style="color:#94a3b8; font-size:12px; margin-top:6px; line-height:1.8;">
                        Tumor in the <b style="color:#f1f5f9;">pituitary gland</b> at brain base.
                        Affects hormone production and regulation.
                        Usually benign but can cause hormonal imbalance.
                    </p>
                </div>
                <div style="background:#1e2d45; border-radius:10px; padding:14px; margin-bottom:10px;">
                    <b style="color:#34d399;">✅ No Tumor</b>
                    <p style="color:#94a3b8; font-size:12px; margin-top:6px; line-height:1.8;">
                        No tumor detected in the MRI scan.
                        Brain tissue appears normal.
                        Regular checkups still recommended.
                    </p>
                </div>
                """, unsafe_allow_html=True)

        # ── Visual Insights ──────────────────────────────────────────────────────
        with st.expander("📊 Brain Tumor Insights — Risk Patterns & Facts", expanded=False):
            bi1, bi2, bi3 = st.columns(3)

            with bi1:
                st.markdown("""
                <div style="background:#1e2d45; border-radius:12px; padding:16px;">
                    <div style="font-size:13px; color:#94a3b8; margin-bottom:12px; font-weight:600;">
                        🧠 Tumor Type Distribution
                    </div>
                """, unsafe_allow_html=True)
                fig_pie = go.Figure(go.Pie(
                    labels=['Glioma', 'Meningioma', 'Pituitary', 'No Tumor'],
                    values=[35, 25, 25, 15],
                    hole=0.5,
                    marker=dict(colors=['#f87171', '#fb923c', '#c084fc', '#34d399']),
                    textfont=dict(color='white', size=11)
                ))
                fig_pie.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#94a3b8'),
                    height=220,
                    margin=dict(t=10, b=10, l=10, r=10),
                    showlegend=True,
                    legend=dict(font=dict(color='#94a3b8', size=10))
                )
                st.plotly_chart(fig_pie, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with bi2:
                st.markdown("""
                <div style="background:#1e2d45; border-radius:12px; padding:16px;">
                    <div style="font-size:13px; color:#94a3b8; margin-bottom:12px; font-weight:600;">
                        ⚠️ Severity Level by Type
                    </div>
                """, unsafe_allow_html=True)
                fig_sev = go.Figure(go.Bar(
                    x=['Glioma', 'Meningioma', 'Pituitary', 'No Tumor'],
                    y=[90, 45, 40, 0],
                    marker_color=['#f87171', '#fb923c', '#c084fc', '#34d399'],
                    text=['High', 'Moderate', 'Moderate', 'None'],
                    textposition='outside',
                    textfont=dict(color='white', size=11)
                ))
                fig_sev.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#94a3b8', size=10),
                    height=220,
                    margin=dict(t=10, b=10, l=10, r=10),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='#1e3a5f',
                        range=[0, 110],
                        ticksuffix='%'
                    ),
                    xaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig_sev, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with bi3:
                st.markdown("""
                <div style="background:#1e2d45; border-radius:12px; padding:16px;">
                    <div style="font-size:13px; color:#94a3b8; margin-bottom:12px; font-weight:600;">
                        📋 Quick Reference Guide
                    </div>
                    <table style="width:100%; font-size:11px; color:#94a3b8; border-collapse:collapse;">
                        <tr style="border-bottom:1px solid #2d3f55;">
                            <th style="text-align:left; padding:5px; color:#60a5fa;">Type</th>
                            <th style="text-align:center; padding:5px; color:#60a5fa;">Nature</th>
                            <th style="text-align:center; padding:5px; color:#60a5fa;">Urgency</th>
                        </tr>
                        <tr style="border-bottom:1px solid #2d3f55;">
                            <td style="padding:5px;">Glioma</td>
                            <td style="text-align:center; padding:5px; color:#f87171;">Malignant</td>
                            <td style="text-align:center; padding:5px; color:#f87171;">🔴 Urgent</td>
                        </tr>
                        <tr style="border-bottom:1px solid #2d3f55;">
                            <td style="padding:5px;">Meningioma</td>
                            <td style="text-align:center; padding:5px; color:#fb923c;">Benign</td>
                            <td style="text-align:center; padding:5px; color:#fb923c;">🟠 Monitor</td>
                        </tr>
                        <tr style="border-bottom:1px solid #2d3f55;">
                            <td style="padding:5px;">Pituitary</td>
                            <td style="text-align:center; padding:5px; color:#c084fc;">Benign</td>
                            <td style="text-align:center; padding:5px; color:#c084fc;">🟡 Monitor</td>
                        </tr>
                        <tr>
                            <td style="padding:5px;">No Tumor</td>
                            <td style="text-align:center; padding:5px; color:#34d399;">Normal</td>
                            <td style="text-align:center; padding:5px; color:#34d399;">🟢 Healthy</td>
                        </tr>
                    </table>
                    <div style="margin-top:14px; font-size:11px; color:#64748b; line-height:1.8;">
                        💡 <b style="color:#94a3b8;">MRI Tips:</b><br>
                        • Upload a clear brain MRI scan<br>
                        • Image should be front or side view<br>
                        • Accepted formats: JPG, PNG, JPEG<br>
                        • Higher resolution = better accuracy
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Main Layout ──────────────────────────────────────────────────────────
        col_form, col_result = st.columns([3, 2], gap="large")

        with col_form:
            st.markdown("""
            <div style="background:#1e2d45; border-radius:12px; padding:16px; margin-bottom:16px;">
                <div style="font-size:13px; color:#94a3b8; line-height:1.8;">
                    📌 <b style="color:#f1f5f9;">Instructions:</b><br>
                    • Upload a <b style="color:#c084fc;">brain MRI scan</b> image<br>
                    • Supported formats: <b style="color:#f1f5f9;">JPG, JPEG, PNG</b><br>
                    • Our model will analyze and classify the tumor type<br>
                    • Image will be resized to <b style="color:#f1f5f9;">128×128</b> automatically
                </div>
            </div>
            """, unsafe_allow_html=True)

            uploaded_file = st.file_uploader(
                "Upload Brain MRI Scan",
                type=["jpg", "jpeg", "png"],
                key="brain_mri_upload",
                help="Upload a clear brain MRI image for tumor detection"
            )

            if uploaded_file is not None:
                # Show uploaded image
                from PIL import Image
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded MRI Scan", width="stretch")

            bt_btn = st.button("🔍 Analyze MRI Scan", key="bt_predict_btn", width="stretch")

            if bt_btn:
                if uploaded_file is None:
                    st.warning("⚠️ Please upload a brain MRI image first.")
                else:
                    fake_predict_bar("Analyzing MRI scan with deep learning model…")

                    try:
                        # Load model
                        with open("brain_tumor_model.pkl", "rb") as f:
                            brain_model = pickle.load(f)

                        # Preprocess image — same as training
                        image = Image.open(uploaded_file).convert("RGB")
                        image = image.resize((128, 128))
                        img_array = np.array(image) / 255.0  # normalize
                        img_array = img_array.reshape(1, 128, 128, 3)  # add batch dimension

                        # Predict
                        prediction = brain_model.predict(img_array)
                        class_index = np.argmax(prediction[0])
                        confidence = int(np.max(prediction[0]) * 100)

                        # Map index to class name
                        # ✅ Must match exact order used in training
                        class_names = ['Pituitary', 'Meningioma', 'Glioma', 'No Tumor']
                        predicted_class = class_names[class_index]

                        with col_result:
                            # Result card based on prediction
                            if predicted_class == "No Tumor":
                                result_negative("No Tumor Detected", f"Confidence: {confidence}%")
                                st.markdown(f"""
                                <div style="
                                    background: linear-gradient(135deg, #1b2d1b, #1f3d1f);
                                    border: 1px solid #34d399;
                                    border-left: 4px solid #10b981;
                                    border-radius: 12px;
                                    padding: 18px 20px;
                                    margin-top: 16px;
                                ">
                                    <div style="font-size:18px; font-weight:700; color:#34d399; margin-bottom:10px;">
                                        ✅ Brain Looks Normal!
                                    </div>
                                    <div style="font-size:13px; color:#a7f3d0; line-height:1.8;">
                                        No tumor detected in the MRI scan.
                                        Brain tissue appears normal.
                                    </div>
                                    <ul style="font-size:13px; color:#d1fae5; margin-top:10px; line-height:2; padding-left:18px;">
                                        <li>💊 Maintain regular health checkups</li>
                                        <li>🧘 Manage stress and get proper sleep</li>
                                        <li>🥗 Follow a brain-healthy diet</li>
                                        <li>📅 Annual MRI if family history exists</li>
                                    </ul>
                                    <div style="
                                        margin-top:14px; background:#1f3d1f;
                                        border-radius:8px; padding:10px 14px;
                                        font-size:12px; color:#a7f3d0;
                                    ">
                                        ⚠️ <b>Disclaimer:</b> This is an AI screening tool only.
                                        Always confirm with a certified radiologist.
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)

                            else:
                                # Tumor detected — color based on type
                                color_map = {
                                    'Glioma': ('#f87171', '#ef4444', '#2d1b1b', '#3d1f1f', '#fcd9d9'),
                                    'Meningioma': ('#fb923c', '#f97316', '#2d1f1b', '#3d261a', '#fed7aa'),
                                    'Pituitary': ('#c084fc', '#a855f7', '#2a1b3d', '#331f4d', '#e9d5ff'),
                                }
                                c1, c2, c3, c4, c5 = color_map[predicted_class]

                                result_positive(f"{predicted_class} Tumor Detected", f"Confidence: {confidence}%")

                                # Tumor specific info
                                tumor_info = {
                                    'Glioma': {
                                        'desc': 'Glioma is a serious tumor in glial cells. Immediate medical attention is required.',
                                        'checks': [
                                            '🏥 Immediate neurosurgeon consultation',
                                            '🔬 Biopsy for tumor grading',
                                            '📡 Advanced MRI / CT Scan',
                                            '💊 Oncologist evaluation',
                                            '⚡ Radiation therapy assessment',
                                            '🧪 Genetic tumor markers test'
                                        ]
                                    },
                                    'Meningioma': {
                                        'desc': 'Meningioma is usually benign but requires monitoring and specialist review.',
                                        'checks': [
                                            '🏥 Neurologist consultation',
                                            '📡 Follow-up MRI in 3–6 months',
                                            '💊 Medication evaluation',
                                            '🔬 Surgical assessment if needed',
                                            '🧘 Stress and lifestyle management',
                                            '📅 Regular monitoring schedule'
                                        ]
                                    },
                                    'Pituitary': {
                                        'desc': 'Pituitary tumors affect hormone levels. Endocrinologist consultation is advised.',
                                        'checks': [
                                            '🏥 Endocrinologist consultation',
                                            '🩸 Hormone level blood tests',
                                            '📡 MRI of pituitary gland',
                                            '👁️ Vision field test',
                                            '💊 Hormone therapy evaluation',
                                            '🔬 Surgical assessment if needed'
                                        ]
                                    }
                                }

                                info = tumor_info[predicted_class]
                                checks_html = "".join([f"<li>{c}</li>" for c in info['checks']])

                                st.markdown(f"""
                                <div style="
                                    background: linear-gradient(135deg, {c3}, {c4});
                                    border: 1px solid {c1};
                                    border-left: 4px solid {c2};
                                    border-radius: 12px;
                                    padding: 18px 20px;
                                    margin-top: 16px;
                                ">
                                    <div style="font-size:18px; font-weight:700; color:{c1}; margin-bottom:10px;">
                                        🏥 Immediate Medical Attention Required
                                    </div>
                                    <div style="font-size:13px; color:{c5}; line-height:1.8;">
                                        {info['desc']}
                                    </div>
                                    <ul style="font-size:13px; color:{c5}; margin-top:10px; line-height:2; padding-left:18px;">
                                        {checks_html}
                                    </ul>
                                    <div style="
                                        margin-top:14px; background:{c4};
                                        border-radius:8px; padding:10px 14px;
                                        font-size:12px; color:{c5};
                                    ">
                                        ⚠️ <b>Disclaimer:</b> This is an AI-based screening tool only.
                                        It does <u>not</u> replace professional medical diagnosis.
                                        Please consult a certified neurologist immediately.
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)

                            # Confidence bar
                            bar_color = '#34d399' if predicted_class == 'No Tumor' else (
                                '#f87171' if predicted_class == 'Glioma' else (
                                    '#fb923c' if predicted_class == 'Meningioma' else '#c084fc'))

                            st.markdown(f"""
                            <div style="margin-top:14px;">
                              <div style="display:flex; justify-content:space-between; font-size:12px;
                                          color:#64748b; margin-bottom:6px;">
                                <span>Detection Confidence</span><span>{confidence}%</span>
                              </div>
                              <div style="background:#1e2d45; border-radius:99px; height:8px;">
                                <div style="background:{bar_color};
                                            width:{confidence}%; height:100%; border-radius:99px;
                                            transition: width 0.5s ease;">
                                </div>
                              </div>
                            </div>""", unsafe_allow_html=True)

                            # All class probabilities
                            st.markdown("""
                            <div style="margin-top:16px; font-size:12px; color:#64748b; font-weight:600;">
                                All Class Probabilities:
                            </div>""", unsafe_allow_html=True)

                            all_classes = ['Pituitary', 'Meningioma', 'Glioma', 'No Tumor']
                            all_colors = ['#c084fc', '#fb923c', '#f87171', '#34d399']
                            all_probs = prediction[0]

                            for cls, prob, col in zip(all_classes, all_probs, all_colors):
                                prob_pct = int(prob * 100)
                                st.markdown(f"""
                                <div style="margin-top:8px;">
                                  <div style="display:flex; justify-content:space-between;
                                              font-size:11px; color:#94a3b8; margin-bottom:3px;">
                                    <span>{cls}</span><span>{prob_pct}%</span>
                                  </div>
                                  <div style="background:#1e2d45; border-radius:99px; height:5px;">
                                    <div style="background:{col}; width:{prob_pct}%;
                                                height:100%; border-radius:99px;"></div>
                                  </div>
                                </div>""", unsafe_allow_html=True)

                    except FileNotFoundError:
                        st.error("⚠️ Model file 'brain_tumor_model.pkl' not found.")
                    except Exception as e:
                        st.error(f"⚠️ Error during prediction: {str(e)}")
    # ══════════════════════════════════════════════
    # ══════════════════════════════════════════════
    #TAB 4 — HEART DISEASE
    # ══════════════════════════════════════════════
    with tabs[3]:
        section_header("Heart Disease Prediction", "Based on ECG and cardiovascular indicators", "❤️")

        # ── Info expander for parameter explanation ──────────────────────────────
        with st.expander("ℹ️ How to fill this form? Click to understand each parameter"):
            ei1, ei2 = st.columns(2)
            with ei1:
                st.markdown("""
                    <div style="background:#1e2d45; border-radius:10px; padding:14px; margin-bottom:10px;">
                        <b style="color:#60a5fa;">🩸 Chest Pain Type</b>
                        <ul style="color:#94a3b8; font-size:12px; margin-top:6px; line-height:1.9;">
                            <li><b style="color:#f1f5f9;">Typical Angina</b> — Classic heart chest pressure during activity</li>
                            <li><b style="color:#f1f5f9;">Atypical Angina</b> — Burning/stabbing chest pain, not always with activity</li>
                            <li><b style="color:#f1f5f9;">Non-Anginal</b> — Chest pain from acidity, muscle or anxiety</li>
                            <li><b style="color:#f1f5f9;">Asymptomatic</b> — No chest pain at all</li>
                        </ul>
                    </div>
                    <div style="background:#1e2d45; border-radius:10px; padding:14px; margin-bottom:10px;">
                        <b style="color:#60a5fa;">💉 Fasting Blood Sugar</b>
                        <p style="color:#94a3b8; font-size:12px; margin-top:6px;">
                            Your blood sugar level after fasting for 8+ hours.<br>
                            <b style="color:#f1f5f9;">Yes</b> = above 120 mg/dL (possible diabetic risk)<br>
                            <b style="color:#f1f5f9;">No</b> = 120 mg/dL or below (normal)
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            with ei2:
                st.markdown("""
                    <div style="background:#1e2d45; border-radius:10px; padding:14px; margin-bottom:10px;">
                        <b style="color:#60a5fa;">❤️ Max Heart Rate</b>
                        <p style="color:#94a3b8; font-size:12px; margin-top:6px;">
                            Highest heart rate achieved during physical activity or stress test.<br>
                            <b style="color:#f1f5f9;">Normal range:</b> 60–100 bpm at rest<br>
                            <b style="color:#f1f5f9;">Max during exercise:</b> roughly 220 minus your age
                        </p>
                    </div>
                    <div style="background:#1e2d45; border-radius:10px; padding:14px; margin-bottom:10px;">
                        <b style="color:#60a5fa;">🩺 Resting Blood Pressure</b>
                        <p style="color:#94a3b8; font-size:12px; margin-top:6px;">
                            Blood pressure measured while at rest (systolic value).<br>
                            <b style="color:#f1f5f9;">Normal:</b> below 120 mmHg<br>
                            <b style="color:#f1f5f9;">High:</b> above 140 mmHg (hypertension risk)
                        </p>
                    </div>
                    <div style="background:#1e2d45; border-radius:10px; padding:14px; margin-bottom:10px;">
                        <b style="color:#60a5fa;">🔬 Serum Cholesterol</b>
                        <p style="color:#94a3b8; font-size:12px; margin-top:6px;">
                            Total cholesterol level in your blood.<br>
                            <b style="color:#f1f5f9;">Healthy:</b> below 200 mg/dL<br>
                            <b style="color:#f1f5f9;">Borderline:</b> 200–239 mg/dL<br>
                            <b style="color:#f1f5f9;">High risk:</b> above 240 mg/dL
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Visual Insights Section ───────────────────────────────────────────────
        with st.expander("📊 Heart Disease Insights — Understand the Risk Patterns", expanded=False):
            v1, v2, v3 = st.columns(3)

            with v1:
                st.markdown("""
                    <div style="background:#1e2d45; border-radius:12px; padding:16px; text-align:center;">
                        <div style="font-size:13px; color:#94a3b8; margin-bottom:12px; font-weight:600;">
                            🫀 Chest Pain Type vs Disease Risk
                        </div>
                    """, unsafe_allow_html=True)
                cp_data = {
                    "Typical\nAngina": 24,
                    "Atypical\nAngina": 80,
                    "Non\nAnginal": 77,
                    "Asymp-\ntomatic": 66
                }

                fig1 = go.Figure(go.Bar(
                    x=list(cp_data.keys()),
                    y=list(cp_data.values()),
                    marker_color=['#34d399', '#f87171', '#fb923c', '#fbbf24'],
                    text=[f"{v}%" for v in cp_data.values()],
                    textposition='outside',
                    textfont=dict(color='white', size=11)
                ))
                fig1.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#94a3b8', size=10),
                    height=220,
                    margin=dict(t=10, b=10, l=10, r=10),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='#1e3a5f',
                        range=[0, 100],
                        ticksuffix='%'
                    ),
                    xaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig1, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with v2:
                st.markdown("""
                    <div style="background:#1e2d45; border-radius:12px; padding:16px; text-align:center;">
                        <div style="font-size:13px; color:#94a3b8; margin-bottom:12px; font-weight:600;">
                            📊 Key Risk Factors Impact
                        </div>
                    """, unsafe_allow_html=True)
                factors = ['Chest Pain', 'Vessels (ca)', 'Thalassemia', 'Blood Pressure', 'Cholesterol',
                           'ST Depression']
                importances = [33.1, 10.2, 10.1, 9.7, 9.6, 8.0]
                fig2 = go.Figure(go.Bar(
                    x=importances,
                    y=factors,
                    orientation='h',
                    marker_color='#60a5fa',
                    text=[f"{v}%" for v in importances],
                    textposition='outside',
                    textfont=dict(color='white', size=10)
                ))
                fig2.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#94a3b8', size=10),
                    height=220,
                    margin=dict(t=10, b=10, l=10, r=10),
                    xaxis=dict(
                        showgrid=True,
                        gridcolor='#1e3a5f',
                        ticksuffix='%'
                    ),
                    yaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig2, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with v3:
                st.markdown("""
                    <div style="background:#1e2d45; border-radius:12px; padding:16px; text-align:center;">
                        <div style="font-size:13px; color:#94a3b8; margin-bottom:12px; font-weight:600;">
                            ⚠️ Know Your Risk Levels
                        </div>
                        <table style="width:100%; font-size:11px; color:#94a3b8; border-collapse:collapse;">
                            <tr style="border-bottom:1px solid #2d3f55;">
                                <th style="text-align:left; padding:6px; color:#60a5fa;">Parameter</th>
                                <th style="text-align:center; padding:6px; color:#34d399;">Normal</th>
                                <th style="text-align:center; padding:6px; color:#f87171;">High Risk</th>
                            </tr>
                            <tr style="border-bottom:1px solid #2d3f55;">
                                <td style="padding:6px;">Blood Pressure</td>
                                <td style="text-align:center; padding:6px; color:#34d399;">&lt;120</td>
                                <td style="text-align:center; padding:6px; color:#f87171;">&gt;140</td>
                            </tr>
                            <tr style="border-bottom:1px solid #2d3f55;">
                                <td style="padding:6px;">Cholesterol</td>
                                <td style="text-align:center; padding:6px; color:#34d399;">&lt;200</td>
                                <td style="text-align:center; padding:6px; color:#f87171;">&gt;240</td>
                            </tr>
                            <tr style="border-bottom:1px solid #2d3f55;">
                                <td style="padding:6px;">Heart Rate</td>
                                <td style="text-align:center; padding:6px; color:#34d399;">60–100</td>
                                <td style="text-align:center; padding:6px; color:#f87171;">&gt;100</td>
                            </tr>
                            <tr style="border-bottom:1px solid #2d3f55;">
                                <td style="padding:6px;">Blood Sugar</td>
                                <td style="text-align:center; padding:6px; color:#34d399;">&lt;100</td>
                                <td style="text-align:center; padding:6px; color:#f87171;">&gt;126</td>
                            </tr>
                            <tr>
                                <td style="padding:6px;">BMI</td>
                                <td style="text-align:center; padding:6px; color:#34d399;">18–25</td>
                                <td style="text-align:center; padding:6px; color:#f87171;">&gt;30</td>
                            </tr>
                        </table>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Input Form ────────────────────────────────────────────────────────────
        col_form, col_result = st.columns([3, 2], gap="large")

        with col_form:
            c1, c2 = st.columns(2)
            with c1:
                h_age = st.number_input("Age", 1, 120, 52, key="h_age")
                h_sex = st.selectbox("Sex", ["Male", "Female"], key="h_sex")
                h_cp = st.selectbox(
                    "Chest Pain Type",
                    [0, 1, 2, 3],
                    format_func=lambda x: [
                        "0 — Typical Angina (classic heart pressure)",
                        "1 — Atypical Angina (burning/stabbing pain)",
                        "2 — Non-Anginal (acidity/muscle pain)",
                        "3 — Asymptomatic (no chest pain)"
                    ][x],
                    key="h_cp"
                )
                h_trestbps = st.number_input(
                    "Resting Blood Pressure (mmHg)",
                    60, 250, 130,
                    key="h_bp",
                    help="Normal: <120 | Borderline: 120-139 | High: ≥140"
                )
            with c2:
                h_chol = st.number_input(
                    "Serum Cholesterol (mg/dL)",
                    100, 600, 250,
                    key="h_chol",
                    help="Healthy: <200 | Borderline: 200-239 | High: ≥240"
                )
                h_thalach = st.number_input(
                    "Max Heart Rate Achieved",
                    60, 250, 160,
                    key="h_thal",
                    help="Estimated max = 220 minus your age"
                )
                h_fbs = st.selectbox(
                    "Fasting Blood Sugar > 120 mg/dL",
                    [0, 1],
                    format_func=lambda
                        x: "Yes — Above 120 mg/dL (diabetic risk)" if x else "No — 120 mg/dL or below (normal)",
                    key="h_fbs"
                )

            h_btn = st.button("🔍 Predict Heart Disease", key="h_predict_btn", use_container_width=True)

            if h_btn:
                fake_predict_bar("Running cardiovascular risk model…")

                sex_val = 1 if h_sex == "Male" else 0

                feature_dict = {
                    'age': [h_age],
                    'sex': [sex_val],
                    'cp': [h_cp],
                    'trestbps': [h_trestbps],
                    'chol': [h_chol],
                    'fbs': [h_fbs],
                    'restecg': [0],
                    'thalach': [h_thalach],
                    'exang': [0],
                    'oldpeak': [1.07],
                    'slope': [1],
                    'ca': [0],
                    'thal': [3]
                }

                features_df = pd.DataFrame(feature_dict)

                try:
                    with open("heart_disease_RF_model.pkl", "rb") as f:
                        heart_model = pickle.load(f)
                    with open("heart_disease_scaler_RF.pkl", "rb") as f:
                        heart_scaler = pickle.load(f)

                    features_scaled = heart_scaler.transform(features_df)
                    prediction = heart_model.predict(features_scaled)[0]

                    try:
                        proba = heart_model.predict_proba(features_scaled)[0]
                        conf = int(proba[1] * 100)
                    except:
                        conf = 50

                except FileNotFoundError:
                    st.error(
                        "⚠️ Model file not found. Please check 'heart_disease_model.pkl' and 'heart_disease_scaler.pkl'.")
                    prediction = None
                    conf = 0

                if prediction is not None:
                    with col_result:
                        if prediction == 1:
                            result_positive("Heart Disease Detected", f"Risk confidence: {conf}%")
                            st.markdown(f"""
                                <div style="
                                    background: linear-gradient(135deg, #2d1b1b, #3d1f1f);
                                    border: 1px solid #f87171;
                                    border-left: 4px solid #ef4444;
                                    border-radius: 12px;
                                    padding: 18px 20px;
                                    margin-top: 16px;
                                ">
                                    <div style="font-size:18px; font-weight:700; color:#f87171; margin-bottom:10px;">
                                        🏥 Please Consult a Doctor
                                    </div>
                                    <div style="font-size:13px; color:#fca5a5; line-height:1.8;">
                                        Based on your inputs, our model indicates a <b>risk of heart disease</b>.
                                        We strongly recommend the following checkups:
                                    </div>
                                    <ul style="font-size:13px; color:#fcd9d9; margin-top:10px; line-height:2; padding-left:18px;">
                                        <li>📋 <b>ECG / EKG</b> — Electrocardiogram test</li>
                                        <li>🩸 <b>Lipid Profile</b> — Full cholesterol panel</li>
                                        <li>🫀 <b>Echocardiogram</b> — Heart ultrasound</li>
                                        <li>🏃 <b>Stress Test</b> — Exercise tolerance test</li>
                                        <li>🔬 <b>Troponin Blood Test</b> — Heart muscle damage marker</li>
                                        <li>📡 <b>Coronary Angiography</b> — If advised by doctor</li>
                                    </ul>
                                    <div style="
                                        margin-top:14px;
                                        background:#3d1f1f;
                                        border-radius:8px;
                                        padding:10px 14px;
                                        font-size:12px;
                                        color:#fca5a5;
                                    ">
                                        ⚠️ <b>Disclaimer:</b> This is an AI-based screening tool only.
                                        It does <u>not</u> replace professional medical diagnosis.
                                        Please visit a certified cardiologist.
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)

                        else:
                            result_negative("Low Heart Disease Risk", f"Confidence: {100 - conf}% negative")
                            st.markdown(f"""
                                <div style="
                                    background: linear-gradient(135deg, #1b2d1b, #1f3d1f);
                                    border: 1px solid #34d399;
                                    border-left: 4px solid #10b981;
                                    border-radius: 12px;
                                    padding: 18px 20px;
                                    margin-top: 16px;
                                ">
                                    <div style="font-size:18px; font-weight:700; color:#34d399; margin-bottom:10px;">
                                        ✅ Your Heart Looks Healthy!
                                    </div>
                                    <div style="font-size:13px; color:#a7f3d0; line-height:1.8;">
                                        Great news! No significant heart disease risk detected.
                                        Keep maintaining a healthy lifestyle:
                                    </div>
                                    <ul style="font-size:13px; color:#d1fae5; margin-top:10px; line-height:2; padding-left:18px;">
                                        <li>🥗 Eat a heart-healthy, balanced diet</li>
                                        <li>🏃 Exercise regularly (30 min/day)</li>
                                        <li>🚭 Avoid smoking and limit alcohol</li>
                                        <li>😴 Get 7–8 hours of quality sleep</li>
                                        <li>📅 Get annual health checkups done</li>
                                    </ul>
                                    <div style="
                                        margin-top:14px;
                                        background:#1f3d1f;
                                        border-radius:8px;
                                        padding:10px 14px;
                                        font-size:12px;
                                        color:#a7f3d0;
                                    ">
                                        ⚠️ <b>Disclaimer:</b> This is an AI-based screening tool only.
                                        Regular checkups with a doctor are always recommended.
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)

                        # Risk progress bar
                        st.markdown(f"""
                            <div style="margin-top:14px;">
                              <div style="display:flex; justify-content:space-between; font-size:12px;
                                          color:#64748b; margin-bottom:6px;">
                                <span>Cardiovascular Risk Score</span><span>{conf}%</span>
                              </div>
                              <div style="background:#1e2d45; border-radius:99px; height:8px;">
                                <div style="background:{'#f87171' if prediction == 1 else '#34d399'};
                                            width:{conf}%; height:100%; border-radius:99px;
                                            transition: width 0.5s ease;">
                                </div>
                              </div>
                            </div>""", unsafe_allow_html=True)
    # ══════════════════════════════════════════════

    #  TAB 5 — ABOUT
    # ══════════════════════════════════════════════
    with tabs[4]:
        # ── Hero ──────────────────────────────────────────────────────────────────
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;600&display=swap');
        .about-card {
            background: linear-gradient(135deg, #0d1b2a, #0a1628);
            border: 1px solid #1e3a5f;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 16px;
            height: 100%;
        }
        .member-card {
            background: linear-gradient(135deg, #0d1b2a, #111827);
            border: 1px solid #1e3a5f;
            border-radius: 16px;
            padding: 22px 18px;
            text-align: center;
            height: 100%;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        .member-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, #38bdf8, #818cf8);
        }
        .lead-card::before {
            background: linear-gradient(90deg, #f59e0b, #fb923c);
        }
        .section-title {
            font-family: 'Orbitron', monospace;
            font-size: 11px;
            color: #475569;
            text-transform: uppercase;
            letter-spacing: 3px;
            text-align: center;
            margin-bottom: 20px;
        }
        </style>

        <!-- Project Banner -->
        <div style="
            background: linear-gradient(135deg, #0a0f1e 0%, #0d1b2a 50%, #0a1628 100%);
            border: 1px solid #1e3a5f;
            border-radius: 20px;
            padding: 50px 40px;
            text-align: center;
            margin-bottom: 30px;
            position: relative;
            overflow: hidden;
        ">
            <div style="position:absolute; top:0; left:0; right:0; bottom:0;
                        background: radial-gradient(ellipse at 30% 50%,
                        rgba(56,189,248,0.05) 0%, transparent 60%),
                        radial-gradient(ellipse at 70% 50%,
                        rgba(129,140,248,0.05) 0%, transparent 60%);">
            </div>
            <div style="position:relative; z-index:1;">
                <div style="display:inline-block; background:#1e2d45; border:1px solid #38bdf8;
                            border-radius:99px; padding:6px 20px; font-family:'Exo 2',sans-serif;
                            font-size:11px; color:#38bdf8; letter-spacing:3px;
                            text-transform:uppercase; margin-bottom:20px;">
                    🎓 Major Project — 2025–26
                </div>
                <h1 style="font-family:'Orbitron',monospace; font-size:42px; font-weight:900;
                           background: linear-gradient(135deg, #ffffff 0%, #38bdf8 50%, #818cf8 100%);
                           -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                           background-clip:text; margin:0 0 12px 0; line-height:1.2;">
                    Hybrid AI System For Disease Prediction
                </h1>
                <p style="font-family:'Exo 2',sans-serif; font-size:16px; color:#64748b;
                          margin-bottom:24px; font-weight:300;">
                    An AI-powered clinical screening system using Machine Learning & Deep Learning
                </p>
                <div style="display:flex; justify-content:center; gap:10px; flex-wrap:wrap;">
                    <span style="background:#1e2d45; border:1px solid #38bdf8; border-radius:99px;
                                 padding:6px 16px; font-family:'Exo 2',sans-serif;
                                 font-size:12px; color:#38bdf8;">
                        🏛️ SATI Vidisha
                    </span>
                    <span style="background:#1e2d45; border:1px solid #818cf8; border-radius:99px;
                                 padding:6px 16px; font-family:'Exo 2',sans-serif;
                                 font-size:12px; color:#818cf8;">
                        🤖 Dept. of Artificial Intelligence
                    </span>
                    <span style="background:#1e2d45; border:1px solid #34d399; border-radius:99px;
                                 padding:6px 16px; font-family:'Exo 2',sans-serif;
                                 font-size:12px; color:#34d399;">
                        📅 Academic Session 2022–26
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Model Accuracy Stats ──────────────────────────────────────────────────
        st.markdown('<div class="section-title">⚡ Model Performance</div>',
                    unsafe_allow_html=True)

        m1, m2, m3 = st.columns(3, gap="large")
        models = [
            ("❤️", "#f87171", "Heart Disease", "Random Forest", "90%",
             "UCI Heart Disease Dataset", "1025 records", "13 features"),
            ("🧠", "#c084fc", "Brain Tumor", "MobileNetV2", "87%",
             "Brain Tumor MRI Dataset", "7200 MRI images", "4 tumor classes"),
            ("🩸", "#34d399", "Diabetes", "Machine Learning", "80%",
             "Pima Indians Diabetes", "768 records", "8 features"),
        ]
        for col, (icon, color, name, model, acc, dataset, size, feat) in zip(
                [m1, m2, m3], models
        ):
            with col:
                st.markdown(f"""
                <div style="background:#0d1b2a; border:1px solid #1e3a5f;
                            border-radius:16px; padding:24px; text-align:center;
                            border-top:3px solid {color};">
                    <div style="font-size:40px; margin-bottom:12px;">{icon}</div>
                    <div style="font-family:'Orbitron',monospace; font-size:13px;
                                font-weight:700; color:#f1f5f9; margin-bottom:6px;">
                        {name}
                    </div>
                    <div style="font-family:'Orbitron',monospace; font-size:38px;
                                font-weight:900; color:{color}; margin:10px 0 4px;">
                        {acc}
                    </div>
                    <div style="font-size:10px; color:#475569; text-transform:uppercase;
                                letter-spacing:2px; margin-bottom:16px;">
                        Test Accuracy
                    </div>
                    <div style="background:#111827; border-radius:8px; padding:10px 12px;
                                text-align:left;">
                        <div style="font-size:11px; color:#64748b; line-height:2;">
                            🤖 <b style="color:#94a3b8;">Model:</b> {model}<br>
                            📦 <b style="color:#94a3b8;">Dataset:</b> {dataset}<br>
                            📊 <b style="color:#94a3b8;">Size:</b> {size}<br>
                            🔢 <b style="color:#94a3b8;">Features:</b> {feat}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Project Overview ──────────────────────────────────────────────────────
        st.markdown('<div class="section-title">📋 Project Overview</div>',
                    unsafe_allow_html=True)



        # ── Google Font import (put this ONCE at the top of your app) ──
        st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Exo+2:wght@400;700&display=swap" rel="stylesheet">
        """, unsafe_allow_html=True)



        # ── Project Description Card ──
        def badge(label, color="#60a5fa"):
            return (
                f'<span style="background:#1e2d45; border:1px solid #2d3f55; '
                f'border-radius:6px; padding:4px 12px; font-size:11px; '
                f'color:{color}; margin-bottom:6px; display:inline-block;">{label}</span>'
            )

        # Categorized badges with matching colors
        ml_tools = ["Scikit-learn", "Random Forest", "Pandas", "NumPy"]
        dl_tools = ["TensorFlow", "Keras", "MobileNetV2"]
        app_tools = ["Python", "Streamlit", "Plotly"]

        badge_html = (
                " ".join(badge(b, "#818cf8") for b in ml_tools) + " " +
                " ".join(badge(b, "#c084fc") for b in dl_tools) + " " +
                " ".join(badge(b, "#60a5fa") for b in app_tools)
        )

        st.markdown(f"""
        <div style="background:#0d1b2a; border:1px solid #1e3a5f; border-radius:16px;
                    padding:28px 32px; margin-bottom:24px;">
            <div style="font-family:'Exo 2',sans-serif; font-size:14px;
                        color:#94a3b8; line-height:2;">
                This project presents a
                <span style="font-weight:700; color:#38bdf8;">Hybrid AI Disease Prediction System</span>
                that combines classical Machine Learning and modern Deep Learning techniques to
                predict three critical medical conditions — Heart Disease, Brain Tumor, and Diabetes.
                <br><br>
                The system is designed to assist in early screening by analyzing patient health
                records and medical images. It uses
                <span style="font-weight:700; color:#818cf8;">Random Forest</span>
                and other ML models for tabular clinical data, and
                <span style="font-weight:700; color:#c084fc;">MobileNetV2 Transfer Learning</span>
                for brain MRI image classification into 4 categories —
                Glioma, Meningioma, Pituitary, and No Tumor.
                <br><br>
                The goal is to provide an accessible, easy-to-use web interface where users can
                enter basic health parameters and receive instant AI-powered screening results
                along with personalized medical recommendations.
            </div>
            <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:20px;">
                {badge_html}
            </div>
        </div>
        """, unsafe_allow_html=True)
        # ── Team Section ──────────────────────────────────────────────────────────
        st.markdown('<div class="section-title">👨‍💻 Project Team</div>',
                    unsafe_allow_html=True)

        # Team Lead
        st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Exo+2:wght@400;700&display=swap" rel="stylesheet">

        <div style="background: linear-gradient(135deg, #1a1200, #221a00);
                    border: 1px solid #f59e0b;
                    border-top: 3px solid #f59e0b;
                    border-radius: 16px; padding: 24px 28px;
                    margin-bottom: 20px; text-align:center;">
            <div style="font-size:48px; margin-bottom:10px;">👨‍💻</div>
            <div style="font-family:'Exo 2',sans-serif; font-size:22px;
                        font-weight:700; color:#f1f5f9; margin-bottom:6px;">
                Kuldeep Patidar
            </div>
            <div style="font-family:'Exo 2',sans-serif; font-size:13px;
                        color:#64748b; margin-bottom:12px;">
                Roll No. 0108AI221030 · Dept. of Artificial Intelligence
            </div>
        </div>
        """, unsafe_allow_html=True)
        #Team Members
        tm1, tm2, tm3 = st.columns(3, gap="large")
        members = [
            ("👨‍💻", "Gagan Meena", "0108AI221024", "#38bdf8",
             "#1a2535"),
            ("👨‍💻", "Deepesh Shrivastava", "0108AI221019", "#818cf8",
             "#1a1a35"),
            ("👨‍💻", "Sandeep Mishra", "0108AI221053", "#34d399",
             "#1a2d1a"),
        ]
        for col, (icon, name, roll, color, bg) in zip(
                [tm1, tm2, tm3], members
        ):
            with col:
                st.markdown(f"""
                <div style="background:{bg}; border:1px solid #1e3a5f;
                            border-top:3px solid {color}; border-radius:16px;
                            padding:22px 18px; text-align:center;">
                    <div style="font-size:40px; margin-bottom:10px;">{icon}</div>
                    <div style="font-family:'Exo 2',sans-serif; font-size:16px;
                                font-weight:700; color:#f1f5f9; margin-bottom:4px;">
                        {name}
                    </div>
                    <div style="font-family:'Exo 2',sans-serif; font-size:11px;
                                color:#64748b; margin-bottom:14px;">
                        Roll No. {roll}
                    
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Mentor + College ──────────────────────────────────────────────────────
        st.markdown('<div class="section-title">🏛️ Institute & Mentor</div>',
                    unsafe_allow_html=True)

        ic1, ic2 = st.columns(2, gap="large")

        with ic1:
            st.markdown("""
            <div style="background:#0d1b2a; border:1px solid #1e3a5f;
                        border-top:3px solid #38bdf8; border-radius:16px; padding:28px;">
                <div style="font-size:40px; text-align:center; margin-bottom:16px;">🏛️</div>
                <div style="font-family:'Orbitron',monospace; font-size:12px; color:#38bdf8;
                            text-transform:uppercase; letter-spacing:2px;
                            text-align:center; margin-bottom:14px;">
                    Institute
                </div>
                <div style="font-family:'Exo 2',sans-serif; font-size:18px; font-weight:700;
                            color:#f1f5f9; text-align:center; margin-bottom:6px;">
                    Samrat Ashok Technological Institute
                </div>
                <div style="font-family:'Exo 2',sans-serif; font-size:13px; color:#64748b;
                            text-align:center; margin-bottom:20px;">
                    Vidisha, Madhya Pradesh
                </div>
                <div style="background:#111827; border-radius:10px; padding:14px 16px;">
                    <div style="font-size:12px; color:#64748b; line-height:2.2;">
                        🎓 <b style="color:#94a3b8;">Degree:</b>
                            B.Tech — Artificial Intelligence<br>
                        📅 <b style="color:#94a3b8;">Year:</b>
                            4rd Year · Academic Year 2025–26<br>
                        📚 <b style="color:#94a3b8;">Project Type:</b>
                            Major Project (8th Semester)<br>
                        🏆 <b style="color:#94a3b8;">Domain:</b>
                            AI in Healthcare
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with ic2:
            st.markdown("""
            <div style="background:#0d1b2a; border:1px solid #1e3a5f;
                        border-top:3px solid #fb923c; border-radius:16px; padding:28px;">
                <div style="font-size:40px; text-align:center; margin-bottom:16px;">👩‍🏫</div>
                <div style="font-family:'Orbitron',monospace; font-size:12px; color:#fb923c;
                            text-transform:uppercase; letter-spacing:2px;
                            text-align:center; margin-bottom:14px;">
                    Project Mentor
                </div>
                <div style="font-family:'Exo 2',sans-serif; font-size:20px; font-weight:700;
                            color:#f1f5f9; text-align:center; margin-bottom:6px;">
                    Prof. Shaila Chugh
                </div>
                <div style="font-family:'Exo 2',sans-serif; font-size:13px; color:#64748b;
                            text-align:center; margin-bottom:20px;">
                    Department of Artificial Intelligence · SATI Vidisha
                </div>
                <div style="background:#111827; border-radius:10px; padding:14px 16px;">
                    <div style="font-size:12px; color:#64748b; line-height:2.2;">
                        🎯 <b style="color:#94a3b8;">Guided:</b>
                            Project Design & Architecture<br>
                        📊 <b style="color:#94a3b8;">Reviewed:</b>
                            Model Selection & Evaluation<br>
                        💡 <b style="color:#94a3b8;">Advised:</b>
                            Research Methodology<br>
                        ✅ <b style="color:#94a3b8;">Approved:</b>
                            Final Project Submission
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Dataset Sources ───────────────────────────────────────────────────────
        st.markdown('<div class="section-title">📦 Dataset Sources</div>',
                    unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#0d1b2a; border:1px solid #1e3a5f;
                    border-radius:16px; padding:24px 28px; margin-bottom:24px;">
            <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px;">
                <div style="background:#111827; border-radius:10px; padding:16px;">
                    <div style="font-size:24px; margin-bottom:8px;">❤️</div>
                    <div style="font-family:'Exo 2',sans-serif; font-size:13px;
                                font-weight:600; color:#f87171; margin-bottom:6px;">
                        Heart Disease Dataset
                    </div>
                    <div style="font-size:11px; color:#64748b; line-height:1.8;">
                        📌 UCI Heart Disease Dataset<br>
                        🌐 Source: Kaggle<br>
                        📊 1025 patient records<br>
                        🔢 13 clinical features<br>
                        🎯 Binary classification
                    </div>
                </div>
                <div style="background:#111827; border-radius:10px; padding:16px;">
                    <div style="font-size:24px; margin-bottom:8px;">🧠</div>
                    <div style="font-family:'Exo 2',sans-serif; font-size:13px;
                                font-weight:600; color:#c084fc; margin-bottom:6px;">
                        Brain Tumor MRI Dataset
                    </div>
                    <div style="font-size:11px; color:#64748b; line-height:1.8;">
                        📌 Nickparvar Brain Tumor Dataset<br>
                        🌐 Source: Kaggle<br>
                        📊 7200 MRI images<br>
                        🔢 4 tumor categories<br>
                        🎯 Multi-class classification
                    </div>
                </div>
                <div style="background:#111827; border-radius:10px; padding:16px;">
                    <div style="font-size:24px; margin-bottom:8px;">🩸</div>
                    <div style="font-family:'Exo 2',sans-serif; font-size:13px;
                                font-weight:600; color:#34d399; margin-bottom:6px;">
                        Diabetes Dataset
                    </div>
                    <div style="font-size:11px; color:#64748b; line-height:1.8;">
                        📌 Pima Indians Diabetes Dataset<br>
                        🌐 Source: Kaggle<br>
                        📊 768 patient records<br>
                        🔢 8 metabolic features<br>
                        🎯 Binary classification
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Acknowledgement + Disclaimer ─────────────────────────────────────────
        st.markdown("""
        <div style="background:linear-gradient(135deg, #0d1b2a, #111827);
                    border:1px solid #1e3a5f; border-radius:16px;
                    padding:24px 28px; margin-bottom:16px; text-align:center;">
            <div style="font-family:'Orbitron',monospace; font-size:13px;
                        color:#38bdf8; margin-bottom:14px; letter-spacing:2px;">
                🙏 ACKNOWLEDGEMENT
            </div>
            <div style="font-family:'Exo 2',sans-serif; font-size:13px;
                        color:#64748b; line-height:2; max-width:700px; margin:0 auto;">
                We express our sincere gratitude to
                <b style="color:#fb923c;">Prof. Shaila Chugh</b>
                for her valuable guidance and continuous support throughout this project.
                We also thank <b style="color:#38bdf8;">SATI Vidisha</b> and the
                <b style="color:#818cf8;">Department of Artificial Intelligence</b>
                for providing the resources and infrastructure needed to complete this work.
                Special thanks to <b style="color:#34d399;">Kaggle</b> and the open-source
                community for the datasets and tools used in this project.
            </div>
        </div>

        <div style="background:rgba(251,146,60,0.08); border:1px solid rgba(251,146,60,0.3);
                    border-left:4px solid #fb923c; border-radius:12px;
                    padding:16px 20px; margin-bottom:16px;">
            <div style="font-family:'Exo 2',sans-serif; font-size:13px;
                        color:#fb923c; font-weight:600; margin-bottom:6px;">
                ⚠️ Medical Disclaimer
            </div>
            <div style="font-family:'Exo 2',sans-serif; font-size:12px;
                        color:#92400e; line-height:1.8;">
                This application is developed purely as an
                <b style="color:#fbbf24;">academic major project</b>
                for educational and research purposes only. The AI predictions made by
                this system should <u>NOT</u> be used as a substitute for professional
                medical advice, diagnosis, or treatment. Always consult a qualified and
                licensed healthcare professional for any medical decisions.
                The developers and SATI Vidisha are not responsible for any medical
                decisions made based on this tool.
            </div>
        </div>

        <div style="text-align:center; padding:16px 0;">
            <div style="font-family:'Exo 2',sans-serif; font-size:12px; color:#334155;">
                © 2026 Kuldeep Patidar · Gagan Meena · Deepesh Shrivastava · Sandeep Mishra
                <br>Samrat Ashok Technological Institute Vidisha · Dept. of Artificial Intelligence
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  7. ROUTER — show auth wall OR main app
# ─────────────────────────────────────────────
if st.session_state.user:
    show_app()
else:
    show_auth()
