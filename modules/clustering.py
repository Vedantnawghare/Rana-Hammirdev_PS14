"""
STAGE 5: CLUSTERING & SIMILARITY DETECTION
Identify similar issues and root causes

Features:
- Similar issue clustering
- Root cause identification
- Pattern mining
- Auto-escalation triggers

Author: Senior ML Engineering Team
"""

import numpy as np
from typing import List, Dict, Tuple
from collections import defaultdict, Counter   # <-- add Counter here
from sklearn.metrics.pairwise import cosine_similarity

from config import CLUSTERING_SIMILARITY_THRESHOLD



class IssueClustering:
    """
    Cluster similar issues to identify root causes
    
    Why clustering:
    - Multiple users reporting same issue → Single root cause
    - "WiFi down Building A" (5 reports) → Fix once, solve all
    - Helps admins prioritize systemic issues
    """
    
    def __init__(self, similarity_threshold: float = CLUSTERING_SIMILARITY_THRESHOLD):
        self.similarity_threshold = similarity_threshold
        self.vectorizer = None  # Will be set from trained TF-IDF
    
    def set_vectorizer(self, vectorizer):
        """Set TF-IDF vectorizer (from trained ML models)"""
        self.vectorizer = vectorizer
    
    def find_similar_issues(self, issue_text: str, all_issues: List[Dict],
                           top_n: int = 10) -> List[Dict]:
        """
        Find issues similar to given issue
        
        Args:
            issue_text: Current issue text (cleaned)
            all_issues: List of dicts with 'cleaned_text' and metadata
            top_n: Return top N most similar
        
        Returns:
            List of similar issues with similarity scores
        """
        if not self.vectorizer:
            raise ValueError("Vectorizer not set! Call set_vectorizer() first")
        
        if not all_issues:
            return []
        
        # Vectorize current issue
        current_vector = self.vectorizer.transform([issue_text])
        
        # Vectorize all issues
        all_texts = [issue['cleaned_text'] for issue in all_issues]
        all_vectors = self.vectorizer.transform(all_texts)
        
        # Calculate cosine similarity
        similarities = cosine_similarity(current_vector, all_vectors)[0]
        
        # Get top similar issues (excluding perfect matches - same issue)
        similar_indices = np.argsort(similarities)[::-1]
        
        similar_issues = []
        for idx in similar_indices[:top_n]:
            similarity_score = similarities[idx]
            
            # Skip if perfect match (same issue) or below threshold
            if similarity_score >= 0.99:  # Same issue
                continue
            if similarity_score < self.similarity_threshold:
                break
            
            similar_issue = all_issues[idx].copy()
            similar_issue['similarity_score'] = similarity_score
            similar_issues.append(similar_issue)
        
        return similar_issues
    
    def cluster_issues(self, issues: List[Dict]) -> List[Dict]:
        """
        Group issues into clusters by similarity
        
        Returns clusters with:
        - Cluster ID
        - Issues in cluster
        - Root cause hypothesis
        - Urgency level
        """
        if not self.vectorizer or not issues:
            return []
        
        # Vectorize all issues
        texts = [issue['cleaned_text'] for issue in issues]
        vectors = self.vectorizer.transform(texts)
        
        # Calculate pairwise similarity matrix
        similarity_matrix = cosine_similarity(vectors)
        
        # Simple clustering: Group issues with similarity > threshold
        n_issues = len(issues)
        visited = set()
        clusters = []
        
        for i in range(n_issues):
            if i in visited:
                continue
            
            # Start new cluster
            cluster = {
                'cluster_id': len(clusters) + 1,
                'issues': [issues[i]],
                'issue_ids': [issues[i].get('issue_id', f'issue_{i}')]
            }
            visited.add(i)
            
            # Find similar issues
            for j in range(i + 1, n_issues):
                if j in visited:
                    continue
                
                if similarity_matrix[i][j] >= self.similarity_threshold:
                    cluster['issues'].append(issues[j])
                    cluster['issue_ids'].append(issues[j].get('issue_id', f'issue_{j}'))
                    visited.add(j)
            
            # Only keep clusters with 2+ issues
            if len(cluster['issues']) >= 2:
                # Analyze cluster
                cluster_analysis = self._analyze_cluster(cluster['issues'])
                cluster.update(cluster_analysis)
                clusters.append(cluster)
        
        # Sort by cluster size (descending)
        clusters.sort(key=lambda x: x['cluster_size'], reverse=True)
        
        return clusters
    
    def _analyze_cluster(self, cluster_issues: List[Dict]) -> Dict:
        """
        Analyze a cluster to identify patterns
        
        Returns:
            - cluster_size: Number of issues
            - common_category: Most common category
            - common_priority: Most common priority
            - root_cause_hypothesis: Best guess at root cause
            - urgency_signal: Escalation recommendation
        """
        # Count occurrences
        categories = [issue.get('category_label', 'Unknown') for issue in cluster_issues]
        priorities = [issue.get('priority_label', 'P3') for issue in cluster_issues]
        
        category_counts = Counter(categories)
        priority_counts = Counter(priorities)
        
        common_category = category_counts.most_common(1)[0][0]
        common_priority = priority_counts.most_common(1)[0][0]
        
        # Extract common keywords (root cause hypothesis)
        all_text = ' '.join([issue['cleaned_text'] for issue in cluster_issues])
        words = all_text.split()
        word_counts = Counter(words)
        
        # Get top 5 common words (excluding stopwords)
        common_words = [word for word, count in word_counts.most_common(10) 
                       if len(word) > 3][:5]
        
        root_cause_hypothesis = ' '.join(common_words)
        
        # Urgency signal
        cluster_size = len(cluster_issues)
        high_priority_count = sum(1 for p in priorities if p == 'P1')
        
        if cluster_size >= 5 or high_priority_count >= 3:
            urgency_signal = "⚠️ HIGH - IMMEDIATE ATTENTION REQUIRED"
        elif cluster_size >= 3:
            urgency_signal = "⚡ MEDIUM - MONITOR CLOSELY"
        else:
            urgency_signal = "📊 LOW - ROUTINE PATTERN"
        
        return {
            'cluster_size': cluster_size,
            'common_category': common_category,
            'common_priority': common_priority,
            'root_cause_hypothesis': root_cause_hypothesis,
            'urgency_signal': urgency_signal,
            'high_priority_count': high_priority_count
        }


# ============================================================================
# PATTERN MINING
# ============================================================================

class PatternMiner:
    """
    Mine recurring patterns across issues
    
    Identifies:
    - Frequent co-occurring keywords
    - Time-based patterns
    - Category-specific patterns
    """
    
    def mine_frequent_patterns(self, issues: List[Dict], min_support: int = 3) -> List[Dict]:
        """
        Find frequently occurring keyword patterns
        
        Args:
            issues: List of issues with cleaned_text
            min_support: Minimum occurrences to be considered frequent
        
        Returns:
            List of patterns with metadata
        """
        # Extract all bigrams (2-word phrases)
        pattern_counts = defaultdict(lambda: {
            'count': 0,
            'categories': [],
            'priorities': [],
            'issue_ids': []
        })
        
        for issue in issues:
            text = issue.get('cleaned_text', '')
            words = text.split()
            
            # Generate bigrams
            for i in range(len(words) - 1):
                bigram = f"{words[i]} {words[i+1]}"
                pattern_counts[bigram]['count'] += 1
                pattern_counts[bigram]['categories'].append(issue.get('category_label', 'Unknown'))
                pattern_counts[bigram]['priorities'].append(issue.get('priority_label', 'P3'))
                pattern_counts[bigram]['issue_ids'].append(issue.get('issue_id', ''))
        
        # Filter by min_support
        frequent_patterns = []
        for pattern, data in pattern_counts.items():
            if data['count'] >= min_support:
                category_counts = Counter(data['categories'])
                priority_counts = Counter(data['priorities'])
                
                frequent_patterns.append({
                    'pattern': pattern,
                    'frequency': data['count'],
                    'common_category': category_counts.most_common(1)[0][0],
                    'common_priority': priority_counts.most_common(1)[0][0],
                    'issue_ids': data['issue_ids'][:10]  # Sample
                })
        
        # Sort by frequency
        frequent_patterns.sort(key=lambda x: x['frequency'], reverse=True)
        
        return frequent_patterns
