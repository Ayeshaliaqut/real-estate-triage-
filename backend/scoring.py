import re
from typing import Tuple, List, Dict, Any

from .constants import (
    LOCATION_SCORES,
    BUDGET_SCORE_RULES,
    TIMEFRAME_SCORES,
    CONTACT_SCORES,
    MESSAGE_KEYWORD_SCORES,
    SPAM_KEYWORDS,
    SPAM_PENALTY,
    MAX_SCORE,
    MIN_SCORE,
    TIERS,
)


def score_location(location: str) -> Tuple[int, List[str]]:
    """dubai and abudabi score highest"""
    if not location or str(location).strip() == "":
        return 0, ["location:missing (-5 penalty)"]
    loc = str(location).strip()
    score = LOCATION_SCORES.get(loc, 5)
    return score, [f"location:{loc} (+{score})"]


def score_budget(budget: Any, property_type: str) -> Tuple[int, List[str]]:
    """score based on budget"""
    if budget is None or str(budget).strip() == "":
        return 0, ["budget:missing"]
    
    try:
        b = float(str(budget).replace(",", "").replace("$", "").strip())
    except Exception:
        return 0, ["budget:invalid"]
    
    # Find matching budget range
    for lo, hi, sc in BUDGET_SCORE_RULES:
        if lo <= b <= hi:
            #boost score of buyers with hight budget
            bonus = 0
            if property_type == "buy" and b >= 1000000:
                bonus = 5
                return sc + bonus, [f"budget:{int(b)} (+{sc}+{bonus} high-value buyer)"]
            # Boost for sellers with valuable properties
            elif property_type == "sell" and b >= 1000000:
                bonus = 5
                return sc + bonus, [f"budget:{int(b)} (+{sc}+{bonus} valuable property)"]
            
            return sc, [f"budget:{int(b)} (+{sc})"]
    
    # Default to highest if somehow not matched
    last_score = BUDGET_SCORE_RULES[-1][2]
    return last_score, [f"budget:{int(b)} (+{last_score})"]


def score_timeframe(timeframe: str, property_type: str) -> Tuple[int, List[str]]:
    """score based on urgncy - now is the most valuable"""
    if not timeframe or str(timeframe).strip() == "":
        return 0, ["timeframe:missing"]
    
    tf = str(timeframe).strip().lower()
    
    for k, v in TIMEFRAME_SCORES.items():
        if k in tf:
            bonus = 0
            if k == "now" and property_type in ["buy", "rent"]:
                bonus = 5
                return v + bonus, [f"timeframe:{timeframe} (+{v}+{bonus} immediate need)"]
            
            return v, [f"timeframe:{timeframe} (+{v})"]
    
    return 0, [f"timeframe:{timeframe} (+0)"]


def score_contact(email: str, phone: str) -> Tuple[int, List[str]]:
    """based on contact information"""
    score = 0
    reasons: List[str] = []
    
    has_email = email and "@" in str(email)
    has_phone = phone and re.sub(r"\D", "", str(phone)).strip()
    
    if has_email:
        score += CONTACT_SCORES.get("has_email", 0)
        reasons.append(f"has_email (+{CONTACT_SCORES.get('has_email', 0)})")
    
    if has_phone:
        score += CONTACT_SCORES.get("has_phone", 0)
        reasons.append(f"has_phone (+{CONTACT_SCORES.get('has_phone', 0)})")
    
    # Bonus for having BOTH email and phone
    if has_email and has_phone:
        bonus = 5
        score += bonus
        reasons.append(f"complete_contact (+{bonus})")
    
    if not has_email and not has_phone:
        reasons.append("no_contact (-10 penalty)")
        score -= 10
    
    return score, reasons


def score_message(message: str, property_type: str) -> Tuple[int, List[str]]:
    """Score message quality and detect spam"""
    if not message or str(message).strip() == "":
        return -5, ["message:empty (-5)"]
    
    m = str(message).lower()
    score = 0
    reasons: List[str] = []
    
    # Check for spam first
    spam_detected = False
    for spam in SPAM_KEYWORDS:
        if spam in m:
            score -= SPAM_PENALTY
            reasons.append(f"spam:{spam} (-{SPAM_PENALTY})")
            spam_detected = True
    
    # If spam detected-don't give positive points for keywords
    if not spam_detected:
        for k, v in MESSAGE_KEYWORD_SCORES.items():
            if k in m:
                score += v
                reasons.append(f"msg_has_{k} (+{v})")
        
        # Message len and detail score
        length_words = len(m.split())
        if length_words >= 15:
            add = 12
            score += add
            reasons.append(f"detailed_message (+{add})")
        elif length_words >= 8:
            add = 8
            score += add
            reasons.append(f"message_length (+{add})")
        elif length_words >= 4:
            add = 4
            score += add
            reasons.append(f"message_length (+{add})")
        else:
            reasons.append("short_message (+0)")
        
        # Check for property type mismatch 
        type_mismatch = False
        if property_type == "rent" and ("want to sell" in m or "selling" in m):
            type_mismatch = True
            reasons.append("type_mismatch (potential confusion)")
        elif property_type == "buy" and ("want to rent" in m or "looking to rent" in m):
            type_mismatch = True
            reasons.append("type_mismatch (potential confusion)")
        
        # Uncertainty signals 
        if any(phrase in m for phrase in ["not sure", "maybe", "thinking about", "might"]):
            penalty = 8
            score -= penalty
            reasons.append(f"uncertainty (-{penalty})")
    
    return score, reasons


def compute_qualification_score(lead: Dict[str, Any]) -> Tuple[int, List[str]]:
    """Compute overall qualification score with improved logic"""
    total = 0
    reasons: List[str] = []
    
    property_type = str(lead.get("property_type", "")).lower()
    
    # Location scoring
    s_loc, r_loc = score_location(lead.get("location_preference", ""))
    total += s_loc
    reasons += r_loc
    
    # Budget scoring 
    s_bud, r_bud = score_budget(lead.get("budget", None), property_type)
    total += s_bud
    reasons += r_bud
    
    # Timeframe scoring
    s_tf, r_tf = score_timeframe(lead.get("timeframe_to_move", ""), property_type)
    total += s_tf
    reasons += r_tf
    
    # Contact scoring 
    s_contact, r_contact = score_contact(lead.get("email", ""), lead.get("phone", ""))
    total += s_contact
    reasons += r_contact
    
    # Message scoring 
    s_msg, r_msg = score_message(lead.get("message", ""), property_type)
    total += s_msg
    reasons += r_msg
    
    # Seller boost 
    if property_type == "sell":
        seller_boost = 10
        total += seller_boost
        reasons.append(f"seller_lead (+{seller_boost})")
    
    # Clamp to bounds
    if total < MIN_SCORE:
        total = MIN_SCORE
    if total > MAX_SCORE:
        total = MAX_SCORE
    
    return int(total), reasons


def score_to_tier(score: int) -> Tuple[str, str]:
    """Map numeric score to a tier and recommended action"""
    selected = TIERS[0]
    for name, min_score, action in TIERS:
        if score >= min_score:
            selected = (name, min_score, action)
    tier_name, _, recommended_action = selected
    return tier_name, recommended_action