"""
STAGE 6: MAIN DASHBOARD LAYOUT
Product-grade admin dashboard

Sections:
- Executive Summary (Today's Action Panel)
- Live Issue Analysis
- Pattern Detection
- Trend Insights
- Department Load Index

Author: Senior Product & UI Team
"""

import streamlit as st
import pandas as pd
from typing import Dict, List
import plotly.express as px
import plotly.graph_objects as go

from components import (
    priority_badge, confidence_meter, metric_card,
    explanation_panel, issue_card, comparison_table,
    action_recommendations
)


def render_executive_summary(issues_df: pd.DataFrame, 
                            priority_engine,
                            rule_engine):
    """
    Today's Action Panel - Executive View
    
    Shows:
    - Critical issues needing immediate attention
    - Department load status
    - Key metrics
    """
    st.markdown("## Today's Action Panel")
    
    # Filter today's issues
    today_issues = issues_df[
        pd.to_datetime(issues_df['timestamp']).dt.date == pd.Timestamp.now().date()
    ]
    
    if len(today_issues) == 0:
        st.info("No issues reported today")
        today_issues = issues_df.head(20)  # Use recent issues instead
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        metric_card("Total Issues", str(len(today_issues)))
    
    with col2:
        p1_count = len(today_issues[today_issues['priority_label'] == 'P1'])
        metric_card("High Priority", str(p1_count))
    
    with col3:
        new_count = len(today_issues[today_issues['issue_status'] == 'New'])
        metric_card("Unassigned", str(new_count))
    
    with col4:
        resolved_count = len(today_issues[today_issues['issue_status'] == 'Resolved'])
        metric_card("Resolved Today", str(resolved_count))
    
    # Critical issues requiring immediate attention
    st.markdown("### Immediate Action Required")
    
    critical_issues = today_issues[
        (today_issues['priority_label'] == 'P1') & 
        (today_issues['issue_status'].isin(['New', 'Assigned']))
    ].head(5)
    
    if len(critical_issues) > 0:
        for idx, issue in critical_issues.iterrows():
            issue_card(issue.to_dict(), show_details=True)
    else:
        st.success("No critical issues pending!")
    
    # Department load
    st.markdown("### Department Load Index")
    
    issues_list = issues_df[issues_df['issue_status'].isin(['New', 'Assigned', 'In Progress'])].to_dict('records')
    load_info = priority_engine.calculate_department_load(issues_list)
    
    load_df = pd.DataFrame([
        {
            'Department': dept,
            'Current Load': info['current_load'],
            'Capacity': info['capacity'],
            'Load %': info['load_percentage'],
            'Status': info['status']
        }
        for dept, info in load_info.items()
    ])
    
    st.dataframe(load_df, use_container_width=True, hide_index=True)


def render_live_analysis(model_manager, rule_engine, preprocessor):
    """
    Live Issue Analysis - Test predictions in real-time
    """
    st.markdown("## Live Issue Analysis")
    
    st.markdown("Enter an issue description to see real-time ML + Rules analysis:")
    
    # Input
    user_input = st.text_area(
        "Issue Description",
        placeholder="Example: urgent wifi not working entire building exam in 1 hour",
        height=100
    )
    
    if st.button("Analyze Issue", type="primary"):
        if user_input:
            with st.spinner("Analyzing..."):
                # Preprocess
                preprocessed = preprocessor.preprocess(user_input, return_steps=True)
                cleaned_text = preprocessed['cleaned_text']
                
                # ML Prediction
                ml_result = model_manager.predict_issue(cleaned_text)
                
                # Rule Analysis
                rule_result = rule_engine.analyze_issue(
                    text=cleaned_text,
                    category=ml_result['category']
                )
                
                # Priority Intelligence
                from modules.priority_engine import PriorityIntelligenceEngine
                priority_engine = PriorityIntelligenceEngine()
                final_result = priority_engine.calculate_final_priority(ml_result, rule_result)
                
                # Display results
                st.markdown("---")
                st.markdown("### Analysis Results")
                
                # Tabs for different views
                tab1, tab2, tab3, tab4 = st.tabs([
                    "Final Decision", 
                    "ML Prediction", 
                    "Rule Analysis",
                    "Preprocessing"
                ])
                
                with tab1:
                    st.markdown("### Final Priority & Routing")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Priority:**")
                        priority_badge(final_result['final_priority'], size='large')
                        st.markdown(f"**Category:** {ml_result['category']}")
                        confidence_meter(final_result['confidence_score'], "Overall Confidence")
                    
                    with col2:
                        st.markdown("**Decision Source:**")
                        st.info(final_result['decision_source'])
                        
                        if final_result['escalation_triggers']:
                            st.warning("**Auto-Escalation Triggers:**")
                            for trigger in final_result['escalation_triggers']:
                                st.markdown(f"- {trigger}")
                    
                    explanation_panel(final_result['explanation'], "Priority Decision Explanation")
                
                with tab2:
                    st.markdown("### ML Model Prediction")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Category Prediction:**")
                        st.markdown(f"**{ml_result['category']}**")
                        confidence_meter(ml_result['category_confidence'], "Category Confidence")
                        
                        st.markdown("**Top 3 Categories:**")
                        for cat_info in ml_result['category_top_3']:
                            st.markdown(f"- {cat_info['category']}: {cat_info['confidence']:.1%}")
                    
                    with col2:
                        st.markdown("**Priority Prediction:**")
                        priority_badge(ml_result['priority'])
                        confidence_meter(ml_result['priority_confidence'], "Priority Confidence")
                        
                        if ml_result['needs_human_review']:
                            st.warning("⚠️ Low confidence - Human review recommended")
                    
                    st.markdown("**Key Decision Factors (TF-IDF):**")
                    keywords_df = pd.DataFrame(ml_result['top_keywords'], columns=['Keyword', 'Score'])
                    st.dataframe(keywords_df, use_container_width=True, hide_index=True)
                
                with tab3:
                    st.markdown("### Rule-Based Analysis")
                    
                    explanation_panel(rule_result['explanation'], "Complete Rule Analysis")
                    
                    st.markdown("**Score Breakdown:**")
                    scores = rule_result['score_breakdown']
                    scores_df = pd.DataFrame([
                        {'Component': k.replace('_', ' ').title(), 'Score': f"{v:.3f}"}
                        for k, v in scores.items()
                    ])
                    st.dataframe(scores_df, use_container_width=True, hide_index=True)
                
                with tab4:
                    st.markdown("### Text Preprocessing Pipeline")
                    
                    steps = preprocessed['processing_steps']
                    
                    st.markdown(f"**Original:** {steps['original']}")
                    st.markdown(f"**Normalized:** {steps['normalized']}")
                    st.markdown(f"**Language:** {preprocessed['detected_language']}")
                    st.markdown(f"**Spell-Checked:** {steps['spell_checked']}")
                    st.markdown(f"**Transliterated:** {steps['transliterated']}")
                    st.markdown(f"**Formalized:** {steps['formalized']}")
                    st.markdown(f"**Cleaned:** {steps['cleaned']}")
                    st.markdown(f"**Tokens:** {steps['tokens']}")
                    st.markdown(f"**Lemmatized:** {steps['lemmatized']}")
                    st.markdown(f"**Final:** {preprocessed['cleaned_text']}")
                
                # Comparison
                st.markdown("### ML vs Rules Comparison")
                comparison_table(ml_result, rule_result)
                
                # Action recommendations
                action_recommendations(final_result['final_priority'], ml_result['category'])
        
        else:
            st.warning("Please enter an issue description")


def render_pattern_detection(issues_df, clustering, pattern_miner, vectorizer):
    """
    Pattern Detection View - Find recurring issues
    """
    st.markdown("## Pattern Detection & Clustering")
    
    # Set vectorizer for clustering
    clustering.set_vectorizer(vectorizer)
    
    # Cluster issues
    issues_list = issues_df.to_dict('records')
    clusters = clustering.cluster_issues(issues_list[:100])  # Cluster recent 100
    
    if clusters:
        st.markdown(f"### Found {len(clusters)} Issue Clusters")
        
        for cluster in clusters[:5]:  # Top 5 clusters
            with st.expander(
                f" Cluster #{cluster['cluster_id']} - {cluster['cluster_size']} issues - {cluster['urgency_signal']}"
            ):
                st.markdown(f"**Root Cause Hypothesis:** {cluster['root_cause_hypothesis']}")
                st.markdown(f"**Common Category:** {cluster['common_category']}")
                st.markdown(f"**Common Priority:** {cluster['common_priority']}")
                st.markdown(f"**High Priority Issues:** {cluster['high_priority_count']}")
                
                st.markdown("**Issue IDs:**")
                st.write(", ".join(cluster['issue_ids'][:10]))
    
    # Frequent patterns
    st.markdown("### Frequent Patterns")
    patterns = pattern_miner.mine_frequent_patterns(issues_list, min_support=3)
    
    if patterns:
        patterns_df = pd.DataFrame(patterns[:20])
        st.dataframe(patterns_df[['pattern', 'frequency', 'common_category', 'common_priority']], 
                    use_container_width=True, hide_index=True)


def render_trend_insights(issues_df, trend_analyzer):
    """
    Trend Insights - Temporal patterns
    """
    st.markdown("## Trend Insights")
    
    issues_list = issues_df.to_dict('records')
    
    # Time distribution
    time_dist = trend_analyzer.analyze_time_distribution(issues_list)
    
    if time_dist:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Peak Hours")
            st.markdown(f"**Busiest Hours:** {', '.join(time_dist['peak_hours'])}")
            
            # Hourly chart
            hourly_data = pd.DataFrame([
                {'Hour': f"{h}:00", 'Count': c}
                for h, c in sorted(time_dist['hourly_distribution'].items())
            ])
            fig = px.bar(hourly_data, x='Hour', y='Count', title='Issues by Hour of Day')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Day Distribution")
            st.markdown(f"**Busiest Day:** {time_dist['busiest_day']}")
            
            # Daily chart
            daily_data = pd.DataFrame([
                {'Day': k, 'Count': v}
                for k, v in time_dist['daily_distribution'].items()
            ])
            fig = px.bar(daily_data, x='Day', y='Count', title='Issues by Day of Week')
            st.plotly_chart(fig, use_container_width=True)
    
    # Category trends
    st.markdown("### Category Trends")
    category_trends = trend_analyzer.analyze_category_trends(issues_list)
    
    if category_trends:
        trends_df = pd.DataFrame([
            {
                'Category': cat,
                'Trend': info['trend'],
                'Current Rate': f"{info['current_rate']:.1f}/day",
                'Previous Rate': f"{info['previous_rate']:.1f}/day"
            }
            for cat, info in category_trends.items()
        ])
        st.dataframe(trends_df, use_container_width=True, hide_index=True)
