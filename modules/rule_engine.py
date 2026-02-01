"""
STAGE 4: RULE ENGINE & EXPLAINABILITY LAYER
Production-grade rule-based decision system
"""

import re
from typing import Dict, List
from datetime import datetime

from config import URGENCY_KEYWORDS, EXAM_SEASON_MONTHS, PEAK_HOURS, PRIORITY_WEIGHTS

# -------------------------------
# KEYWORD RULE ENGINE
# -------------------------------
class KeywordRuleEngine:
    def __init__(self):
        self.urgency_keywords = URGENCY_KEYWORDS

    def detect_urgency_signals(self, text: str) -> Dict:
        text_lower = text.lower()
        matched_critical = [kw for kw in self.urgency_keywords['critical'] if kw in text_lower]
        matched_time_sensitive = [kw for kw in self.urgency_keywords['time_sensitive'] if kw in text_lower]
        matched_impact = [kw for kw in self.urgency_keywords['impact'] if kw in text_lower]

        critical_score = min(len(matched_critical) * 0.4, 0.6)
        time_score = min(len(matched_time_sensitive) * 0.3, 0.3)
        impact_score = min(len(matched_impact) * 0.2, 0.2)
        urgency_score = critical_score + time_score + impact_score

        if urgency_score >= 0.6:
            urgency_level = "HIGH"
        elif urgency_score >= 0.3:
            urgency_level = "MEDIUM"
        else:
            urgency_level = "LOW"

        explanation_parts = []
        if matched_critical:
            explanation_parts.append(f"Critical keywords: {', '.join(matched_critical[:3])}")
        if matched_time_sensitive:
            explanation_parts.append(f"Time-sensitive: {', '.join(matched_time_sensitive[:3])}")
        if matched_impact:
            explanation_parts.append(f"High impact: {', '.join(matched_impact[:3])}")

        explanation = "; ".join(explanation_parts) or "No urgency signals detected"

        return {
            "urgency_score": urgency_score,
            "urgency_level": urgency_level,
            "matched_keywords": {
                "critical": matched_critical,
                "time_sensitive": matched_time_sensitive,
                "impact": matched_impact,
            },
            "explanation": explanation,
        }

# -------------------------------
# TIME-BASED RULE ENGINE
# -------------------------------
class TimeBasedRuleEngine:
    def __init__(self):
        self.exam_months = EXAM_SEASON_MONTHS
        self.peak_hours = PEAK_HOURS

    def analyze_temporal_context(self, timestamp: str) -> Dict:
        try:
            dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        except:
            dt = datetime.now()

        is_exam_period = dt.month in self.exam_months
        hour = dt.hour

        if self.peak_hours['morning'][0] <= hour < self.peak_hours['morning'][1]:
            time_of_day = "morning"
            peak_multiplier = 0.8
        elif self.peak_hours['afternoon'][0] <= hour < self.peak_hours['afternoon'][1]:
            time_of_day = "afternoon"
            peak_multiplier = 1.0
        elif self.peak_hours['evening'][0] <= hour < self.peak_hours['evening'][1]:
            time_of_day = "evening"
            peak_multiplier = 0.9
        else:
            time_of_day = "night"
            peak_multiplier = 0.7

        is_weekend = dt.weekday() >= 5
        weekend_multiplier = 0.85 if is_weekend else 1.0

        time_score = min((0.5 + (0.3 if is_exam_period else 0)) * peak_multiplier * weekend_multiplier, 1.0)

        explanation_parts = [f"Reported during {time_of_day}"]
        if is_exam_period:
            explanation_parts.insert(0, "Exam period - higher priority")
        if is_weekend:
            explanation_parts.append("Weekend - slightly lower priority")

        return {
            "time_score": time_score,
            "is_exam_period": is_exam_period,
            "time_of_day": time_of_day,
            "is_weekend": is_weekend,
            "is_peak_hour": peak_multiplier >= 0.9,
            "explanation": "; ".join(explanation_parts),
        }

# -------------------------------
# IMPACT ASSESSMENT ENGINE
# -------------------------------
class ImpactAssessmentEngine:
    def assess_impact(self, text: str, category: str = None) -> Dict:
        text_lower = text.lower()
        high = ['all', 'entire', 'everyone', 'whole', 'campus', 'building', 'department', 'multiple', 'many', 'widespread', 'campus-wide', 'system-wide']
        medium = ['several', 'few', 'some', 'group', 'class', 'floor', 'room', 'lab']
        low = ['my', 'i', 'me', 'personal', 'own']

        high_count = sum(1 for kw in high if kw in text_lower)
        medium_count = sum(1 for kw in medium if kw in text_lower)
        low_count = sum(1 for kw in low if kw in text_lower)

        category_impact = {'Network': 0.8, 'Facilities': 0.6, 'IT Support': 0.4, 'Academic': 0.5, 'Admin': 0.3}
        base_impact = category_impact.get(category, 0.5)

        if high_count > 0:
            impact_score = min(base_impact + 0.4, 1.0)
            impact_level = "HIGH"
            estimated_users = "50-500+"
            explanation = "High-impact keywords detected: affects multiple users"
        elif medium_count > 0:
            impact_score = base_impact
            impact_level = "MEDIUM"
            estimated_users = "10-50"
            explanation = "Medium-impact scope: affects a group"
        elif low_count > 0:
            impact_score = max(base_impact - 0.3, 0.1)
            impact_level = "LOW"
            estimated_users = "1-5"
            explanation = "Individual issue: single user affected"
        else:
            impact_score = base_impact
            impact_level = "MEDIUM"
            estimated_users = "Unknown"
            explanation = f"Estimated based on category ({category})"

        return {
            "impact_score": impact_score,
            "impact_level": impact_level,
            "estimated_users_affected": estimated_users,
            "explanation": explanation,
        }

# -------------------------------
# RECURRING ISSUE DETECTOR
# -------------------------------
class RecurringIssueDetector:
    def detect_recurring_pattern(self, current_text: str, historical_issues: List[str], similarity_threshold: float = 0.6) -> Dict:
        if not historical_issues:
            return {"is_recurring": False, "recurrence_count": 0, "similar_issues": [], "explanation": "No historical data available", "escalation_recommended": False}

        current_words = set(current_text.lower().split())
        similar_issues = []
        for hist in historical_issues:
            hist_words = set(hist.lower().split())
            similarity = len(current_words & hist_words) / len(current_words | hist_words)
            if similarity >= similarity_threshold:
                similar_issues.append({"text": hist, "similarity": similarity})

        recurrence_count = len(similar_issues)
        is_recurring = recurrence_count >= 3

        explanation = ("⚠️ RECURRING ISSUE: {} similar reports found".format(recurrence_count)
                       if is_recurring else
                       f"Similar to {recurrence_count} past issue(s)" if recurrence_count > 0 else
                       "First occurrence of this issue")

        return {"is_recurring": is_recurring, "recurrence_count": recurrence_count, "similar_issues": similar_issues[:5], "explanation": explanation, "escalation_recommended": is_recurring}

# -------------------------------
# COMPLETE RULE ENGINE
# -------------------------------
class CompleteRuleEngine:
    def __init__(self):
        self.keyword_engine = KeywordRuleEngine()
        self.time_engine = TimeBasedRuleEngine()
        self.impact_engine = ImpactAssessmentEngine()
        self.recurring_detector = RecurringIssueDetector()

    def analyze_issue(self, text: str, timestamp: str = None, category: str = None, historical_issues: List[str] = None) -> Dict:
        timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        historical_issues = historical_issues or []

        urgency = self.keyword_engine.detect_urgency_signals(text)
        time_ctx = self.time_engine.analyze_temporal_context(timestamp)
        impact = self.impact_engine.assess_impact(text, category)
        recurring = self.recurring_detector.detect_recurring_pattern(text, historical_issues)

        weights = {**{"urgency_score": 0.4, "time_sensitivity": 0.3, "impact_score": 0.3, "recurrence_score": 0.1}, **PRIORITY_WEIGHTS}

        combined_score = min(
            urgency['urgency_score'] * weights['urgency_score'] +
            time_ctx['time_score'] * weights['time_sensitivity'] +
            impact['impact_score'] * weights['impact_score'] +
            (weights['recurrence_score'] if recurring['is_recurring'] else 0),
            1.0
        )

        if combined_score >= 0.75 or recurring['is_recurring']:
            priority = "P1"
            label = "High"
        elif combined_score >= 0.45:
            priority = "P2"
            label = "Medium"
        else:
            priority = "P3"
            label = "Low"

        explanation = f"Rule-based priority: {priority}, combined score: {combined_score:.2f}"

        return {
            "rule_priority": priority,
            "priority_label": label,
            "combined_score": combined_score,
            "urgency_analysis": urgency,
            "time_analysis": time_ctx,
            "impact_analysis": impact,
            "recurring_analysis": recurring,
            "explanation": explanation,
        }
