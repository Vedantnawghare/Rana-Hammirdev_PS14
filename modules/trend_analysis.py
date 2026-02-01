import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict


class TrendAnalyzer:
    """
    Analyze temporal patterns in issues
    
    Insights:
    - When are issues most reported?
    - Which categories spike at what times?
    - Are issues increasing or decreasing?
    """
    
    def analyze_time_distribution(self, issues: List[Dict]) -> Dict:
        """
        Analyze when issues are reported
        
        Returns distribution by:
        - Hour of day
        - Day of week
        - Month
        """
        # Parse timestamps
        timestamps = []
        for issue in issues:
            try:
                ts = datetime.strptime(issue['timestamp'], "%Y-%m-%d %H:%M:%S")
                timestamps.append(ts)
            except:
                continue
        
        if not timestamps:
            return {}
        
        # Hour distribution
        hour_counts = defaultdict(int)
        for ts in timestamps:
            hour_counts[ts.hour] += 1
        
        # Day of week distribution
        day_counts = defaultdict(int)
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for ts in timestamps:
            day_counts[day_names[ts.weekday()]] += 1
        
        # Month distribution
        month_counts = defaultdict(int)
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        for ts in timestamps:
            month_counts[month_names[ts.month - 1]] += 1
        
        # Find peak hours
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        peak_hours = sorted_hours[:3]
        
        return {
            'hourly_distribution': dict(hour_counts),
            'daily_distribution': dict(day_counts),
            'monthly_distribution': dict(month_counts),
            'peak_hours': [f"{h}:00" for h, c in peak_hours],
            'busiest_day': max(day_counts.items(), key=lambda x: x[1])[0],
            'busiest_month': max(month_counts.items(), key=lambda x: x[1])[0]
        }
    
    def analyze_category_trends(self, issues: List[Dict]) -> Dict:
        """
        Track how categories trend over time
        """
        # Group by category and time
        category_timeline = defaultdict(lambda: defaultdict(int))
        
        for issue in issues:
            try:
                ts = datetime.strptime(issue['timestamp'], "%Y-%m-%d %H:%M:%S")
                date = ts.strftime("%Y-%m-%d")
                category = issue.get('category_label', 'Unknown')
                category_timeline[category][date] += 1
            except:
                continue
        
        # Calculate trends
        trends = {}
        for category, timeline in category_timeline.items():
            sorted_dates = sorted(timeline.items())
            if len(sorted_dates) >= 2:
                # Simple trend: compare first half vs second half
                mid = len(sorted_dates) // 2
                first_half_avg = sum(c for d, c in sorted_dates[:mid]) / mid
                second_half_avg = sum(c for d, c in sorted_dates[mid:]) / (len(sorted_dates) - mid)
                
                if second_half_avg > first_half_avg * 1.2:
                    trend = "INCREASING"
                elif second_half_avg < first_half_avg * 0.8:
                    trend = "DECREASING"
                else:
                    trend = "STABLE"
                
                trends[category] = {
                    'trend': trend,
                    'current_rate': second_half_avg,
                    'previous_rate': first_half_avg
                }
        
        return trends
    
    def detect_anomalies(self, issues: List[Dict]) -> List[Dict]:
        """
        Detect unusual spikes in issue volume
        
        Anomaly = Day with >2x average daily volume
        """
        # Count issues per day
        daily_counts = defaultdict(int)
        for issue in issues:
            try:
                ts = datetime.strptime(issue['timestamp'], "%Y-%m-%d %H:%M:%S")
                date = ts.strftime("%Y-%m-%d")
                daily_counts[date] += 1
            except:
                continue
        
        if not daily_counts:
            return []
        
        # Calculate average
        avg_daily = sum(daily_counts.values()) / len(daily_counts)
        
        # Find anomalies
        anomalies = []
        for date, count in daily_counts.items():
            if count > avg_daily * 2:
                anomalies.append({
                    'date': date,
                    'count': count,
                    'avg': avg_daily,
                    'severity': 'HIGH' if count > avg_daily * 3 else 'MEDIUM'
                })
        
        return sorted(anomalies, key=lambda x: x['count'], reverse=True)
