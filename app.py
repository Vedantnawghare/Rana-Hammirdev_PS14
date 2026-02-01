"""
STAGE 7: MAIN STREAMLIT APPLICATION
Intelligent Issue Insight Engine - Complete Application

Author: Senior ML Engineering Team
"""

import sys
sys.path.append('modules')
sys.path.append('ui')

import streamlit as st
import pandas as pd
from pathlib import Path

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
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title=UI_CONFIG['page_title'],
    page_icon=UI_CONFIG['page_icon'],
    layout=UI_CONFIG['layout'],
    initial_sidebar_state="expanded"
)


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
            st.error("❌ Models not found! Please run: python train_models.py")
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
        st.error("❌ Dataset not found! Please run: python modules/data_processor.py")
        st.stop()


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    
    # Header
    st.markdown("""
    # 🎯 Intelligent Issue Insight Engine
    ### Explainable Text Categorization, Pattern Mining & Priority Prediction
    """)
    
    st.markdown("---")
    
    # Load components
    components = load_models()
    issues_df = load_dataset()
    
    # Sidebar
    st.sidebar.markdown("## 📋 Navigation")
    page = st.sidebar.radio(
        "Select View",
        [
            "📊 Today's Action Panel",
            "🔍 Live Issue Analysis",
            "🔄 Pattern Detection",
            "📈 Trend Insights",
            "📚 About"
        ]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Total Issues:** {len(issues_df)}")
    st.sidebar.markdown(f"**Categories:** {issues_df['category_label'].nunique()}")
    st.sidebar.markdown(f"**Date Range:** {issues_df['timestamp'].min()} to {issues_df['timestamp'].max()}")
    
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
    
    elif page == "📚 About":
        render_about()
    
    # Footer
    st.markdown("---")
    st.caption("Intelligent Issue Insight Engine v1.0 | Built with Streamlit + Scikit-learn")


def render_about():
    """About page"""
    st.markdown("## 📚 About This System")
    
    st.markdown("""
    ### 🎯 What This System Does
    
    This is an **explainable AI system** that helps administrators:
    
    1. **Automatically categorize** user-reported issues into departments
    2. **Predict priority levels** (P1/P2/P3) using ML + Rules
    3. **Detect recurring patterns** to identify systemic problems
    4. **Analyze trends** to anticipate peak loads
    5. **Provide explainable decisions** - every prediction comes with reasoning
    
    ### 🧠 How It Works
    
    **Pipeline:**
    
    1. **Text Preprocessing** → Handle Hinglish, spelling errors, informal language
    2. **ML Prediction** → TF-IDF + Logistic Regression/SVM
    3. **Rule Engine** → Business logic for urgency, impact, time context
    4. **Priority Intelligence** → Combine ML + Rules for final decision
    5. **Explainability** → Show WHY each decision was made
    
    ### 🎨 Key Features (USPs)
    
    ✅ **Explainable Priority Prediction** - Clear reasoning for every decision  
    ✅ **Impact × Urgency Logic** - Multi-dimensional priority scoring  
    ✅ **Recurring Issue Detection** - Auto-escalation for patterns  
    ✅ **Similar Issue Clustering** - Root cause identification  
    ✅ **Time-Aware Insights** - Trend analysis and peak detection  
    ✅ **Department Load Index** - Resource allocation guidance  
    ✅ **Confidence-Based Routing** - Human review for low-confidence cases  
    ✅ **Rule vs ML Comparison** - Explainability transparency  
    ✅ **Today's Action Panel** - Executive decision dashboard  
    ✅ **Hinglish Support** - Real-world multilingual input handling  
    
    ### 🛠️ Tech Stack
    
    - **Frontend:** Streamlit
    - **NLP:** Custom pipeline (spelling, Hinglish, transliteration)
    - **ML:** Scikit-learn (Logistic Regression, Linear SVM, TF-IDF)
    - **Rules:** Custom explainability engine
    - **Data:** Pandas, NumPy
    - **Viz:** Plotly, Streamlit native charts
    
    ### 👥 Built By
    
    Senior ML Engineering & Product Team
    """)


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    main()
