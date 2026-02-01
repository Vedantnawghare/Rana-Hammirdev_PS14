"""
STAGE 5: PRIORITY INTELLIGENCE ENGINE
Smart priority calculation combining ML + Rules

Features:
- Impact × Urgency matrix
- ML + Rules hybrid
- Auto-escalation logic
- Department load balancing

Author: Senior ML Engineering Team
"""

from typing import Dict, List
from config import PRIORITY_WEIGHTS, DEPARTMENT_CAPACITY


class PriorityIntelligenceEngine:
    """
    Calculate final priority using all available signals
    
    Combines:
    - ML predictions
    - Rule-based scores
    - Impact assessment
    - Temporal context
    - Recurrence patterns
    - Department load
    """
    
    def calculate_final_priority(self, 
                                 ml_result: Dict,
                                 rule_result: Dict,
                                 department_load: Dict = None) -> Dict:
        """
        Smart priority calculation
        
        Logic:
        1. Start with ML or Rules (whichever has higher confidence)
        2. Adjust for impact
        3. Adjust for temporal context
        4. Check for auto-escalation triggers
        5. Consider department capacity
        """
        # Extract scores
        ml_priority = ml_result.get('priority', 'P3')
        ml_confidence = ml_result.get('priority_confidence', 0.5)
        
        rule_priority = rule_result.get('rule_priority', 'P3')
        rule_score = rule_result.get('combined_score', 0.5)
        
        # Priority to numeric
        priority_to_num = {'P1': 3, 'P2': 2, 'P3': 1}
        num_to_priority = {3: 'P1', 2: 'P2', 1: 'P3'}
        
        ml_num = priority_to_num[ml_priority]
        rule_num = priority_to_num[rule_priority]
        
        # Weighted combination (favor higher confidence source)
        if ml_confidence >= 0.75:
            # Trust ML
            final_num = ml_num
            decision_source = "ML (High Confidence)"
        elif rule_score >= 0.70:
            # Trust Rules
            final_num = rule_num
            decision_source = "Rules (High Score)"
        else:
            # Average and round up (err on side of higher priority)
            final_num = max(ml_num, rule_num)
            decision_source = "Hybrid (Conservative)"
        
        # Auto-escalation triggers
        escalation_triggers = []
        
        # Trigger 1: Recurring issue
        if rule_result.get('recurring_analysis', {}).get('is_recurring', False):
            final_num = max(final_num, 2)  # At least P2
            escalation_triggers.append("Recurring issue pattern detected")
        
        # Trigger 2: High impact
        if rule_result.get('impact_analysis', {}).get('impact_level') == 'HIGH':
            final_num = max(final_num, 2)  # At least P2
            escalation_triggers.append("High impact - multiple users affected")
        
        # Trigger 3: Exam period + urgent keywords
        time_analysis = rule_result.get('time_analysis', {})
        urgency_analysis = rule_result.get('urgency_analysis', {})
        if time_analysis.get('is_exam_period') and urgency_analysis.get('urgency_level') == 'HIGH':
            final_num = 3  # Force P1
            escalation_triggers.append("Exam period + urgent keywords")
        
        # Convert back to priority
        final_priority = num_to_priority[final_num]
        
        # Department load adjustment
        dept_adjustment = ""
        if department_load:
            category = ml_result.get('category', 'Unknown')
            load_pct = department_load.get(category, 0)
            
            if load_pct > 90 and final_priority == 'P3':
                dept_adjustment = f"⚠️ {category} dept at {load_pct}% capacity - consider reassignment"
        
        return {
            'final_priority': final_priority,
            'ml_priority': ml_priority,
            'rule_priority': rule_priority,
            'decision_source': decision_source,
            'escalation_triggers': escalation_triggers,
            'department_adjustment': dept_adjustment,
            'confidence_score': max(ml_confidence, rule_score),
            'explanation': self._build_priority_explanation(
                final_priority, decision_source, escalation_triggers, 
                ml_confidence, rule_score
            )
        }
    
    def _build_priority_explanation(self, priority, source, triggers, ml_conf, rule_score):
        """Build explanation for priority decision"""
        explanation = [
            f"**Final Priority: {priority}**",
            f"Decision Source: {source}",
            f"ML Confidence: {ml_conf:.1%} | Rule Score: {rule_score:.2f}"
        ]
        
        if triggers:
            explanation.append("\n**Auto-Escalation Triggers:**")
            for trigger in triggers:
                explanation.append(f"  • {trigger}")
        
        return "\n".join(explanation)
    
    def calculate_department_load(self, current_issues: List[Dict]) -> Dict:
        """
        Calculate current load per department
        
        Returns percentage of capacity for each category
        """
        # Count unresolved issues per category
        category_counts = {}
        for issue in current_issues:
            if issue.get('issue_status') in ['New', 'Assigned', 'In Progress']:
                category = issue.get('category_label', 'Unknown')
                category_counts[category] = category_counts.get(category, 0) + 1
        
        # Calculate load percentage
        load_percentages = {}
        for category, capacity in DEPARTMENT_CAPACITY.items():
            current_load = category_counts.get(category, 0)
            load_pct = (current_load / capacity) * 100
            load_percentages[category] = {
                'current_load': current_load,
                'capacity': capacity,
                'load_percentage': load_pct,
                'status': '🔴 OVERLOADED' if load_pct > 100 
                         else '🟡 HIGH' if load_pct > 80
                         else '🟢 NORMAL'
            }
        
        return load_percentages
