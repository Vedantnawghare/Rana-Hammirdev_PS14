"""
Configuration file for Intelligent Issue Insight Engine
Contains all constants, paths, and system-wide settings
"""

import os
from pathlib import Path


# ============================================================================
# FILE PATHS
# ============================================================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

DATASET_PATH = DATA_DIR / "issues_dataset.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed_issues.csv"

# ============================================================================
# ISSUE CATEGORIES
# ============================================================================
CATEGORIES = [
    "Network",
    "IT Support", 
    "Academic",
    "Facilities",
    "Admin"
]

# ============================================================================
# PRIORITY LEVELS
# ============================================================================
PRIORITY_LEVELS = ["P3", "P2", "P1"]  # Low, Medium, High
PRIORITY_LABELS = {
    "P3": "Low",
    "P2": "Medium", 
    "P1": "High"
}

# ============================================================================
# ISSUE STATUS
# ============================================================================
STATUS_OPTIONS = ["New", "Assigned", "In Progress", "Resolved"]

# ============================================================================
# DATASET CONFIGURATION
# ============================================================================
DATASET_SIZE = 400  # Number of synthetic issues to generate
TRAIN_TEST_SPLIT = 0.8
RANDOM_SEED = 42

# ============================================================================
# NLP CONFIGURATION
# ============================================================================
NLP_CONFIG = {
    "max_features": 500,
    "ngram_range": (1, 2),
    "min_df": 2,
    "max_df": 0.9,
    "stop_words": "english"
}

# ============================================================================
# ML MODEL CONFIGURATION
# ============================================================================
ML_CONFIG = {
    "category_model": {
        "type": "logistic_regression",
        "C": 1.0,
        "max_iter": 1000,
        "random_state": RANDOM_SEED
    },
    "urgency_model": {
        "type": "linear_svm",
        "C": 1.0,
        "max_iter": 1000,
        "random_state": RANDOM_SEED
    }
}

# ============================================================================
# RULE ENGINE THRESHOLDS
# ============================================================================
URGENCY_KEYWORDS = {
    "critical": ["urgent", "emergency", "critical", "asap", "immediately", 
                 "right now", "can't access", "completely down", "not working"],
    "time_sensitive": ["exam", "deadline", "today", "assignment due", 
                       "test", "quiz", "presentation", "meeting"],
    "impact": ["all students", "entire", "everyone", "multiple", 
               "department", "campus-wide", "building"]
}

RECURRING_ISSUE_THRESHOLD = 3  # Number of similar issues to flag as recurring
CLUSTERING_SIMILARITY_THRESHOLD = 0.7
AUTO_ESCALATION_THRESHOLD = 5  # Number of similar unresolved issues

# ============================================================================
# TIME-BASED RULES
# ============================================================================
PEAK_HOURS = {
    "morning": (8, 12),
    "afternoon": (12, 17),
    "evening": (17, 21),
    "night": (21, 24)
}

EXAM_SEASON_MONTHS = [4, 5, 11, 12]  # April, May, November, December

# ============================================================================
# CONFIDENCE THRESHOLDS
# ============================================================================
CONFIDENCE_THRESHOLDS = {
    "high": 0.85,
    "medium": 0.65,
    "low": 0.0
}

HUMAN_REVIEW_THRESHOLD = 0.65  # Route to human if confidence below this

# ============================================================================
# UI CONFIGURATION
# ============================================================================
UI_CONFIG = {
    "page_title": "Issue Insight Engine",
    "page_icon": "🎯",
    "layout": "wide",
    "theme": {
        "primaryColor": "#FF4B4B",
        "backgroundColor": "#FFFFFF",
        "secondaryBackgroundColor": "#F0F2F6"
    }
}

# ============================================================================
# PRIORITY SCORING WEIGHTS
# ============================================================================
PRIORITY_WEIGHTS = {
    "urgency_score": 0.35,
    "impact_score": 0.30,
    "recurrence_score": 0.20,
    "time_sensitivity": 0.15
}

# ============================================================================
# DEPARTMENT CAPACITY (for load index calculation)
# ============================================================================
DEPARTMENT_CAPACITY = {
    "Network": 20,
    "IT Support": 25,
    "Academic": 15,
    "Facilities": 18,
    "Admin": 12
}

# ============================================================================
# ADVANCED NLP CONFIGURATION (STAGE 2)
# ============================================================================

# Hinglish/Hindi common words mapping (lightweight transliteration)
HINGLISH_TO_ENGLISH = {
    # Common Hinglish words
    "mera": "my",
    "mere": "my",
    "mereko": "me",
    "mujhe": "me",
    "hai": "is",
    "tha": "was",
    "nahi": "not",
    "nahin": "not",
    "kya": "what",
    "kab": "when",
    "kahan": "where",
    "kyun": "why",
    "kaise": "how",
    "abhi": "now",
    "aaya": "came",
    "gaya": "went",
    "karo": "do",
    "karna": "to do",
    "kar": "do",
    "hoga": "will be",
    "hua": "happened",
    "hain": "are",
    "ho": "be",
    "thi": "was",
    "the": "were",
    "ka": "of",
    "ki": "of",
    "ke": "of",
    "se": "from",
    "ko": "to",
    "ne": "by",
    "pe": "on",
    "par": "on",
    "matlab": "meaning",
    "yaar": "friend",
    "bhai": "brother",
    "plz": "please",
    "pls": "please",
    "thx": "thanks",
    "ty": "thank you",
    "asap": "as soon as possible",
    "urgent": "urgent",
    "jaldi": "quickly",
    "turant": "immediately",
    "zaroor": "definitely",
    "bahut": "very",
    "bohot": "very",
    "thoda": "little",
    "zyada": "more",
    "kam": "less",
    "problem": "problem",
    "issue": "issue",
    "dikkat": "problem",
    "pareshani": "trouble",
    "theek": "okay",
    "sahi": "correct",
    "galat": "wrong",
    "chal": "work",
    "chalta": "works",
    "band": "stopped",
    "kharab": "broken",
    "kaam": "work",
    "milega": "will get",
    "dega": "will give",
    "ayega": "will come",
    "hona": "to be",
    "chahiye": "should",
    "karna": "to do",
    "lena": "to take",
    "dena": "to give",
    "samajh": "understand",
    "pata": "know",
    "dekh": "see",
    "sun": "listen",
    "bol": "speak",
    "bata": "tell",
    "batao": "tell",
    "help": "help",
    "madad": "help",
    "batana": "to tell",
    "dekhna": "to see",
    "pending": "pending",
    "complete": "complete",
    "hogaya": "done",
    "nahi": "not",
    "bilkul": "absolutely",
    "shayad": "maybe",
    "lagta": "seems",
    "accha": "good",
    "bura": "bad",
    "exam": "exam",
    "test": "test",
    "assignment": "assignment",
    "deadline": "deadline",
    "submit": "submit",
    "upload": "upload",
    "download": "download",
    "login": "login",
    "logout": "logout",
    "password": "password",
    "account": "account",
    "profile": "profile",
    "order": "order",
    "delivery": "delivery",
    "refund": "refund",
    "payment": "payment",
    "ticket": "ticket",
    "complaint": "complaint",
    "resolve": "resolve",
    "fix": "fix",
    "repair": "repair",
    "check": "check"
}

# Common spelling mistakes and corrections
COMMON_SPELLING_CORRECTIONS = {
    "wify": "wifi",
    "wi-fy": "wifi",
    "interneet": "internet",
    "passward": "password",
    "passwrd": "password",
    "accont": "account",
    "acount": "account",
    "probem": "problem",
    "probelm": "problem",
    "isue": "issue",
    "urgnt": "urgent",
    "immediatly": "immediately",
    "tommorow": "tomorrow",
    "recieve": "receive",
    "untill": "until",
    "occured": "occurred",
    "seperate": "separate",
    "definately": "definitely",
    "maintainance": "maintenance",
    "maintainence": "maintenance",
    "realy": "really",
    "wierd": "weird",
    "freind": "friend",
    "reccomend": "recommend",
    "accomodate": "accommodate"
}

# Chat-style abbreviations and informal language
INFORMAL_TO_FORMAL = {
    "plz": "please",
    "pls": "please",
    "pleez": "please",
    "thx": "thanks",
    "ty": "thank you",
    "thnx": "thanks",
    "thanx": "thanks",
    "u": "you",
    "ur": "your",
    "r": "are",
    "y": "why",
    "cuz": "because",
    "bcuz": "because",
    "bcz": "because",
    "gonna": "going to",
    "wanna": "want to",
    "gotta": "got to",
    "dunno": "do not know",
    "kinda": "kind of",
    "sorta": "sort of",
    "gimme": "give me",
    "lemme": "let me",
    "asap": "as soon as possible",
    "fyi": "for your information",
    "btw": "by the way",
    "idk": "i do not know",
    "tbh": "to be honest",
    "imo": "in my opinion",
    "rn": "right now",
    "lol": "",  # Remove internet slang
    "lmao": "",
    "omg": "",
    "wtf": "",
    "smh": "",
    "n": "and",
    "b4": "before",
    "2day": "today",
    "2morrow": "tomorrow",
    "2nite": "tonight",
    "msg": "message",
    "txt": "text",
    "pic": "picture",
    "ppl": "people",
    "sum1": "someone",
    "ne1": "anyone",
    "thru": "through",
    "w/": "with",
    "w/o": "without",
    "b/c": "because"
}

# Language detection patterns (simple rule-based)
HINDI_SCRIPT_PATTERN = r'[\u0900-\u097F]'  # Devanagari script
COMMON_HINDI_WORDS = ["hai", "tha", "nahi", "kya", "kab", "mera", "mere", "abhi", "karo"]
COMMON_ENGLISH_WORDS = ["the", "is", "not", "what", "when", "my", "now", "do"]
