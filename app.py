"""
STAGE 7: MAIN STREAMLIT APPLICATION
Intelligent Issue Insight Engine - Complete Application with Authentication & Enhanced UI

Author: Senior ML Engineering Team
Version: 2.0 - Enhanced with Authentication & Beautiful UI
"""

import sys
sys.path.append('modules')
sys.path.append('ui')

import streamlit as st
import pandas as pd
from pathlib import Path
import hashlib
import json
from datetime import datetime

# Import modules
from modules.nlp_preprocessing import NLPPreprocessor
from modules.ml_models import ModelManager
from modules.rule_engine import CompleteRuleEngine
from modules.clustering import IssueClustering, PatternMiner
from modules.trend_analysis import TrendAnalyzer
from modules.priority_engine import PriorityIntelligenceEngine

# Import UI
from ui.dashboard import (
    render_executive_summary,
    render_live_analysis,
    render_pattern_detection,
    render_trend_insights
)

from config import UI_CONFIG, PROCESSED_DATA_PATH


# ============================================================================
# AUTHENTICATION FUNCTIONS
# ============================================================================

# Auth data file
AUTH_DATA_FILE = Path(__file__).parent / "data" / "users.json"
AUTH_DATA_FILE.parent.mkdir(exist_ok=True)


def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def load_users():
    """Load users from JSON file"""
    if not AUTH_DATA_FILE.exists():
        return {}
    
    try:
        with open(AUTH_DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}


def save_users(users):
    """Save users to JSON file"""
    with open(AUTH_DATA_FILE, 'w') as f:
        json.dump(users, f, indent=2)


def create_user(username: str, password: str, email: str, role: str = "user") -> bool:
    """Create a new user"""
    users = load_users()
    
    if username in users:
        return False
    
    users[username] = {
        "password": hash_password(password),
        "email": email,
        "role": role,
        "created_at": datetime.now().isoformat(),
        "last_login": None
    }
    
    save_users(users)
    return True


def verify_user(username: str, password: str) -> bool:
    """Verify user credentials"""
    users = load_users()
    
    if username not in users:
        return False
    
    if users[username]["password"] == hash_password(password):
        # Update last login
        users[username]["last_login"] = datetime.now().isoformat()
        save_users(users)
        return True
    
    return False


def get_user_info(username: str):
    """Get user information"""
    users = load_users()
    return users.get(username, {})


def initialize_session():
    """Initialize session state for authentication"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_info' not in st.session_state:
        st.session_state.user_info = {}


def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.user_info = {}


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title=UI_CONFIG['page_title'],
    page_icon=UI_CONFIG['page_icon'],
    layout=UI_CONFIG['layout'],
    initial_sidebar_state="expanded"
)


# ============================================================================
# CUSTOM CSS - VIBRANT UI
# ============================================================================

def load_custom_css():
    """Load custom CSS for vibrant, beautiful UI"""
    st.markdown("""
    <style>
        /* Import beautiful fonts */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&family=Space+Mono:wght@400;700&display=swap');
        
        /* Global styling */
        * {
            font-family: 'Poppins', sans-serif;
        }
        
        /* Main app background with gradient */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        
        /* Header styling */
        h1, h2, h3 {
            font-weight: 800 !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
            padding: 2rem 1.5rem;
        }
        
        [data-testid="stSidebar"] * {
            color: white !important;
        }
        
        /* User info section */
        [data-testid="stSidebar"] h2 {
            font-size: 1.2rem !important;
            font-weight: 700 !important;
            margin-bottom: 0.5rem !important;
            color: white !important;
            background: none !important;
            -webkit-text-fill-color: white !important;
        }
        
        [data-testid="stSidebar"] .stRadio > label {
            font-weight: 700;
            font-size: 1.1rem;
            margin-bottom: 1rem;
            display: block;
        }
        
        /* Radio button styling - Navigation items */
        [data-testid="stSidebar"] .stRadio [role="radiogroup"] {
            gap: 0.5rem;
        }
        
        [data-testid="stSidebar"] .stRadio [role="radiogroup"] label {
            background: rgba(255, 255, 255, 0.08);
            padding: 14px 18px;
            border-radius: 14px;
            margin: 6px 0;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            border: 2px solid transparent;
            font-weight: 500;
            font-size: 0.95rem;
            display: flex;
            align-items: center;
            backdrop-filter: blur(10px);
        }
        
        [data-testid="stSidebar"] .stRadio [role="radiogroup"] label:hover {
            background: rgba(255, 255, 255, 0.15);
            transform: translateX(6px);
            border-color: rgba(255, 255, 255, 0.2);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        
        [data-testid="stSidebar"] .stRadio [role="radiogroup"] label[data-checked="true"] {
            background: rgba(255, 255, 255, 0.25);
            font-weight: 700;
            border-color: rgba(255, 255, 255, 0.4);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
            transform: translateX(6px);
        }
        
        /* Sidebar divider */
        [data-testid="stSidebar"] hr {
            border: none;
            height: 1px;
            background: rgba(255, 255, 255, 0.2);
            margin: 1.5rem 0;
        }
        
        /* Sidebar markdown text */
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] strong {
            color: rgba(255, 255, 255, 0.95) !important;
        }
        
        /* Quick stats styling */
        [data-testid="stSidebar"] h3 {
            font-size: 1rem !important;
            font-weight: 600 !important;
            margin: 1rem 0 0.5rem 0 !important;
            color: rgba(255, 255, 255, 0.9) !important;
            background: none !important;
            -webkit-text-fill-color: rgba(255, 255, 255, 0.9) !important;
        }
        
        /* Logout button styling */
        [data-testid="stSidebar"] .stButton > button {
            background: rgba(255, 255, 255, 0.15) !important;
            border: 2px solid rgba(255, 255, 255, 0.3) !important;
            color: white !important;
            padding: 12px 24px !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            transition: all 0.3s ease !important;
            backdrop-filter: blur(10px) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        }
        
        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(255, 255, 255, 0.25) !important;
            border-color: rgba(255, 255, 255, 0.5) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15) !important;
        }
        
        /* Metric cards */
        [data-testid="stMetric"] {
            background: white;
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        
        [data-testid="stMetric"]:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.2);
        }
        
        [data-testid="stMetric"] label {
            font-weight: 600;
            color: #6b7280 !important;
            font-size: 0.95rem;
        }
        
        [data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-size: 2.5rem !important;
            font-weight: 800 !important;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Button styling */
        .stButton > button {
            border-radius: 12px;
            padding: 12px 32px;
            font-weight: 600;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            color: white;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
        
        /* Input fields */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            border-radius: 12px;
            border: 2px solid #e5e7eb;
            padding: 12px 16px;
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        /* Success/Info/Warning/Error boxes */
        .stSuccess, .stInfo, .stWarning, .stError {
            border-radius: 12px;
            padding: 16px;
            border-left: 4px solid;
        }
        
        /* Dataframe styling */
        [data-testid="stDataFrame"] {
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background: white;
            border-radius: 12px;
            padding: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .streamlit-expanderHeader:hover {
            background: #f9fafb;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: white;
            border-radius: 12px;
            padding: 4px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            color: #6b7280;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
        }
        
        /* Custom divider */
        hr {
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, #667eea, transparent);
            margin: 2rem 0;
        }
        
        /* Main header container */
        .main-header {
            background: white;
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            margin-bottom: 2rem;
        }
        
        .main-header h1 {
            font-size: 3rem;
            margin: 0;
        }
        
        .main-header p {
            color: #6b7280;
            font-size: 1.2rem;
            margin: 0.5rem 0 0 0;
        }
        
        /* Plotly charts */
        .js-plotly-plot {
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        /* Animation for cards */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .stMetric, .streamlit-expanderHeader {
            animation: fadeInUp 0.6s ease-out;
        }
        
        /* Login page specific styles */
        .login-page-wrapper {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }
        
        .login-container {
            max-width: 480px;
            margin: 0 auto;
            padding: 0;
            background: transparent;
        }
        
        .login-card {
            background: rgba(255, 255, 255, 0.98);
            border-radius: 28px;
            box-shadow: 0 30px 80px rgba(0, 0, 0, 0.25);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.4);
            overflow: hidden;
            animation: slideUp 0.6s ease-out;
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(40px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .login-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem 2.5rem 2.5rem 2.5rem;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .login-header::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: pulse 4s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.1); opacity: 0.8; }
        }
        
        .login-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
            filter: drop-shadow(0 8px 16px rgba(0, 0, 0, 0.2));
            position: relative;
            z-index: 1;
        }
        
        .login-title {
            font-size: 2.8rem;
            font-weight: 900;
            color: white;
            margin: 0 0 0.5rem 0;
            text-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            position: relative;
            z-index: 1;
            letter-spacing: -0.5px;
        }
        
        .login-subtitle {
            color: rgba(255, 255, 255, 0.95);
            font-size: 1.05rem;
            margin: 0;
            font-weight: 500;
            position: relative;
            z-index: 1;
        }
        
        .login-body {
            padding: 2.5rem;
        }
        
        /* Tab styling for login page */
        .login-body .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            background-color: #f3f4f6;
            border-radius: 14px;
            padding: 6px;
            margin-bottom: 2rem;
        }
        
        .login-body .stTabs [data-baseweb="tab"] {
            border-radius: 10px;
            padding: 12px 28px;
            font-weight: 700;
            font-size: 0.95rem;
            color: #6b7280;
            transition: all 0.3s ease;
        }
        
        .login-body .stTabs [data-baseweb="tab"]:hover {
            background: rgba(102, 126, 234, 0.08);
        }
        
        .login-body .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        
        /* Input styling for login */
        .login-body .stTextInput > div > div > input {
            border-radius: 14px;
            border: 2px solid #e5e7eb;
            padding: 14px 18px;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: #fafafa;
        }
        
        .login-body .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.12);
            background: white;
        }
        
        .login-body .stTextInput label {
            font-weight: 600;
            color: #374151;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }
        
        /* Button styling for login */
        .login-body .stButton > button {
            width: 100%;
            border-radius: 14px;
            padding: 14px 28px;
            font-size: 1.05rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            color: white;
            transition: all 0.3s ease;
            margin-top: 1.5rem;
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.35);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .login-body .stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 28px rgba(102, 126, 234, 0.45);
        }
        
        .login-body .stButton > button:active {
            transform: translateY(-1px);
        }
        
        /* Footer for login page */
        .login-footer {
            text-align: center;
            margin-top: 2rem;
            color: rgba(255, 255, 255, 0.9);
            font-size: 0.9rem;
            font-weight: 500;
        }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# LOGIN PAGE
# ============================================================================

def render_login_page():
    """Render beautiful login page with modern glassmorphism design"""
    
    load_custom_css()
    
    # Main container
    st.markdown('<div class="login-page-wrapper">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        # Header section with gradient background
        st.markdown("""
        <div class="login-header">
            <div class="login-icon">🎯</div>
            <h1 class="login-title">Issue Insight</h1>
            <p class="login-subtitle">Smart Issue Management System</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Body section
        st.markdown('<div class="login-body">', unsafe_allow_html=True)
        
        # Tabs for login/signup
        tab1, tab2 = st.tabs(["🔐 Sign In", "✨ Create Account"])
        
        with tab1:
            st.markdown("<br>", unsafe_allow_html=True)
            username = st.text_input("Username", key="login_username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
            
            if st.button("Sign In", key="login_btn", use_container_width=True):
                if username and password:
                    if verify_user(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.user_info = get_user_info(username)
                        st.success("✅ Welcome back!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.warning("⚠️ Please enter both username and password")
        
        with tab2:
            st.markdown("<br>", unsafe_allow_html=True)
            new_username = st.text_input("Username", key="signup_username", placeholder="Choose a username")
            new_email = st.text_input("Email", key="signup_email", placeholder="your.email@example.com")
            new_password = st.text_input("Password", type="password", key="signup_password", placeholder="Create a strong password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password", placeholder="Confirm your password")
            
            if st.button("Create Account", key="signup_btn", use_container_width=True):
                if new_username and new_email and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("❌ Passwords don't match")
                    elif len(new_password) < 6:
                        st.error("❌ Password must be at least 6 characters")
                    else:
                        if create_user(new_username, new_password, new_email):
                            st.success("✅ Account created! Please sign in.")
                        else:
                            st.error("❌ Username already exists")
                else:
                    st.warning("⚠️ Please fill in all fields")
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close login-body
        st.markdown('</div>', unsafe_allow_html=True)  # Close login-card
        st.markdown('</div>', unsafe_allow_html=True)  # Close login-container
        
        # Footer
        st.markdown("""
        <div class="login-footer">
            <p>© 2024 Issue Insight Engine | Built with ❤️</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close login-page-wrapper


# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

@st.cache_resource
def load_models():
    """Load all models and engines (cached)"""
    with st.spinner("Loading ML models..."):
        # NLP Preprocessor
        preprocessor = NLPPreprocessor()
        
        # ML Models
        model_manager = ModelManager()
        try:
            model_manager.load_models()
        except FileNotFoundError:
            st.error("Models not found! Please run: python train_models.py")
            st.stop()
        
        # Rule Engine
        rule_engine = CompleteRuleEngine()
        
        # Clustering
        clustering = IssueClustering()
        pattern_miner = PatternMiner()
        
        # Trend Analyzer
        trend_analyzer = TrendAnalyzer()
        
        # Priority Engine
        priority_engine = PriorityIntelligenceEngine()
        
        return {
            'preprocessor': preprocessor,
            'model_manager': model_manager,
            'rule_engine': rule_engine,
            'clustering': clustering,
            'pattern_miner': pattern_miner,
            'trend_analyzer': trend_analyzer,
            'priority_engine': priority_engine
        }

@st.cache_data
def load_dataset():
    """Load processed dataset (cached)"""
    try:
        df = pd.read_csv(PROCESSED_DATA_PATH)
        return df
    except FileNotFoundError:
        st.error("Dataset not found! Please run: python modules/data_processor.py")
        st.stop()


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    
    # Initialize authentication
    initialize_session()
    
    # Check if user is authenticated
    if not st.session_state.authenticated:
        render_login_page()
        return
    
    # Load custom CSS for main app
    load_custom_css()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Intelligent Issue Insight Engine</h1>
        <p>Explainable Text Categorization, Pattern Mining & Priority Prediction</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load components
    components = load_models()
    issues_df = load_dataset()
    
    # Sidebar
    with st.sidebar:
        # User welcome section
        st.markdown(f"""
        <div style="
            background: rgba(255, 255, 255, 0.15);
            padding: 1.5rem;
            border-radius: 16px;
            margin-bottom: 1.5rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        ">
            <div style="text-align: center;">
                <div style="
                    width: 64px;
                    height: 64px;
                    background: rgba(255, 255, 255, 0.25);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 1rem auto;
                    font-size: 2rem;
                    border: 3px solid rgba(255, 255, 255, 0.4);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                ">
                    👤
                </div>
                <div style="font-weight: 700; font-size: 1.2rem; margin-bottom: 0.3rem;">
                    {st.session_state.username}
                </div>
                <div style="font-size: 0.85rem; opacity: 0.9;">
                    Administrator
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("## 🧭 Navigation")
        page = st.radio(
            "Select View",
            [
                "📊 Today's Action Panel",
                "🔍 Live Issue Analysis",
                "🔄 Pattern Detection",
                "📈 Trend Insights",
                "ℹ️ About"
            ],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Quick stats with better styling
        st.markdown("### 📌 Quick Stats")
        st.markdown(f"""
        <div style="
            background: rgba(255, 255, 255, 0.1);
            padding: 1rem;
            border-radius: 12px;
            margin: 0.5rem 0;
            backdrop-filter: blur(5px);
        ">
            <div style="margin-bottom: 0.8rem;">
                <div style="font-size: 0.8rem; opacity: 0.8; margin-bottom: 0.2rem;">Total Issues</div>
                <div style="font-size: 1.5rem; font-weight: 800;">{len(issues_df)}</div>
            </div>
            <div style="margin-bottom: 0.8rem;">
                <div style="font-size: 0.8rem; opacity: 0.8; margin-bottom: 0.2rem;">Categories</div>
                <div style="font-size: 1.5rem; font-weight: 800;">{issues_df['category_label'].nunique()}</div>
            </div>
            <div>
                <div style="font-size: 0.8rem; opacity: 0.8; margin-bottom: 0.2rem;">Date Range</div>
                <div style="font-size: 0.75rem; font-weight: 600;">{issues_df['timestamp'].min()[:10]} to {issues_df['timestamp'].max()[:10]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Logout button with enhanced styling
        if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
            logout()
            st.rerun()
    
    # Route to pages
    if page == "📊 Today's Action Panel":
        render_executive_summary(
            issues_df, 
            components['priority_engine'],
            components['rule_engine']
        )
    
    elif page == "🔍 Live Issue Analysis":
        render_live_analysis(
            components['model_manager'],
            components['rule_engine'],
            components['preprocessor']
        )
    
    elif page == "🔄 Pattern Detection":
        render_pattern_detection(
            issues_df,
            components['clustering'],
            components['pattern_miner'],
            components['model_manager'].vectorizer
        )
    
    elif page == "📈 Trend Insights":
        render_trend_insights(
            issues_df,
            components['trend_analyzer']
        )
    
    elif page == "ℹ️ About":
        render_about()
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #6b7280; font-size: 0.9rem;">© 2024 Intelligent Issue Insight Engine v2.0 | Built with ❤️ using Streamlit + Scikit-learn</p>',
        unsafe_allow_html=True
    )


def render_about():
    """About page with beautiful styling"""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## 🎯 About This System")
        
        st.markdown("""
        ### What This System Does
        
        This is an **explainable AI system** that helps administrators:
        """)
        
        features = [
            ("🏷️", "Automatically categorize", "user-reported issues into departments"),
            ("⚡", "Predict priority levels", "(P1/P2/P3) using ML + Rules"),
            ("🔄", "Detect recurring patterns", "to identify systemic problems"),
            ("📈", "Analyze trends", "to anticipate peak loads"),
            ("💡", "Provide explainable decisions", "every prediction comes with reasoning")
        ]
        
        for icon, title, desc in features:
            st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 12px; margin: 0.5rem 0; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
                <strong>{icon} {title}:</strong> {desc}
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🚀 Tech Stack")
        tech_stack = {
            "Frontend": "Streamlit",
            "NLP": "Custom Pipeline",
            "ML": "Scikit-learn",
            "Rules": "Custom Engine",
            "Data": "Pandas, NumPy",
            "Viz": "Plotly"
        }
        
        for tech, desc in tech_stack.items():
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0; font-weight: 600;">
                {tech}: {desc}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 🌟 Key Features (USPs)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🧠 Intelligence**
        - Explainable Priority Prediction
        - Impact × Urgency Logic
        - Recurring Issue Detection
        - Similar Issue Clustering
        """)
    
    with col2:
        st.markdown("""
        **⏰ Time-Aware**
        - Trend Analysis
        - Peak Detection
        - Department Load Index
        - Resource Allocation
        """)
    
    with col3:
        st.markdown("""
        **🎯 Accuracy**
        - Confidence-Based Routing
        - Rule vs ML Comparison
        - Hinglish Support
        - Real-time Processing
        """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 🔄 How It Works
    
    **Pipeline Flow:**
    """)
    
    pipeline_steps = [
        ("1", "Text Preprocessing", "Handle Hinglish, spelling errors, informal language"),
        ("2", "ML Prediction", "TF-IDF + Logistic Regression/SVM"),
        ("3", "Rule Engine", "Business logic for urgency, impact, time context"),
        ("4", "Priority Intelligence", "Combine ML + Rules for final decision"),
        ("5", "Explainability", "Show WHY each decision was made")
    ]
    
    for num, title, desc in pipeline_steps:
        st.markdown(f"""
        <div style="background: white; padding: 1.5rem; border-radius: 12px; margin: 1rem 0; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-left: 4px solid #667eea;">
            <div style="font-size: 2rem; font-weight: 800; color: #667eea; margin-bottom: 0.5rem;">{num}</div>
            <div style="font-weight: 700; font-size: 1.2rem; margin-bottom: 0.3rem;">{title}</div>
            <div style="color: #6b7280;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.info("💡 **Pro Tip:** Use the sidebar to navigate between different views and explore the full capabilities of the system!")


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    main()
