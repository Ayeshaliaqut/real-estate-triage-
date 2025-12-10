LOCATION_SCORES = {
    "Dubai": 25,     
    "Abu Dhabi": 22,     
    "Sharjah": 15,         
    "Ajman": 12,           
    "Al Ain": 14,          
    "Ras Al Khaimah": 12,  
}

BUDGET_SCORE_RULES = [
    (0, 50000, 3),              
    (50001, 100000, 10),     
    (100001, 500000, 18),       
    (500001, 1500000, 28),
    (1500001, 3000000, 35),   
    (3000001, float("inf"), 40), 
]
#timegrame scoring
TIMEFRAME_SCORES = {
    "now": 35,              #hot
    "1-3 months": 25,       #warm
    "1–3 months": 25,       #diff formats
    "3-6 months": 15,       #cool
    "3–6 months": 15,
    "6+ months": 5,         #cold
    "6 months+": 5,
}

# Contact completeness
CONTACT_SCORES = {
    "has_email": 10,
    "has_phone": 12,        
}

MESSAGE_KEYWORD_SCORES = {
    "urgent": 12,           # High urgency
    "immediately": 10,
    "asap": 10,
    "buy": 10,              # Clear intent
    "purchase": 10,
    "sell": 10,
    "selling": 10,
    "rent": 8,
    "looking": 6,           # Active search
    "searching": 6,
    "interested": 6,
    "need": 7,
    "require": 7,
    "moving": 8,
    "relocating": 8,
    "villa": 5,             # Property specificity
    "apartment": 5,
    "penthouse": 7,
    "studio": 4,
    "1br": 4,
    "2br": 5,
    "3br": 6,
    "4br": 7,
    "bedroom": 4,
    "budget": 5,            # Financial readiness
    "approved": 8,          # Pre-approved financing
    "cash": 10,             # Cash buyers are premium
    "investor": 8,          # Investment buyers
}
#find out low quality leads
SPAM_KEYWORDS = [
    "work from home",
    "make money",
    "earn money",
    "click here",
    "test",
    "testing",
    "not about property",
    "free offer",
    "limited time",
    "act now",
    "10000$",
    "weekly income",
]
SPAM_PENALTY = 50  

# Score bounds
MAX_SCORE = 100
MIN_SCORE = 0

# Tier thresholds:
TIERS = [
    ("junk", 0, "ignore"),         # 0-39: Spam, incomplete, or irrelevant
    ("low", 40, "nurture"),        # 40-64: Potential, but needs warming
    ("medium", 65, "call later"),  # 65-79: Good leads, follow up soon
    ("hot", 80, "call now"),       # 80+: Excellent leads, immediate action
]

# LLM fallback
LLM_DEFAULT_FALLBACK = {"intent_label": "casual_inquiry", "short_reason": "llm-fallback"}