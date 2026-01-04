"""
Construction terminology dictionary for context-aware rephrasing.
Maps abbreviations and short terms to their full professional forms.
"""

import os
import difflib
from typing import Dict, List, Tuple

# Construction-specific abbreviations and terms
TERM_EXPANSIONS = {
    # Structural terms
    "rebar": "reinforcement bar",
    "conc": "concrete",
    "fdn": "foundation",
    "ftg": "footing",
    "col": "column",
    "bm": "beam",
    "slab": "floor slab",
    "rcc": "reinforced cement concrete",
    "pcc": "plain cement concrete",
    
    # BIM/Design terms
    "bim": "Building Information Model",
    "cad": "Computer-Aided Design",
    "lod": "Level of Detail",
    "ifc": "Industry Foundation Classes",
    "dwg": "drawing file",
    "rvt": "Revit model",
    "nwc": "Navisworks cache file",
    "mep": "Mechanical, Electrical, and Plumbing",
    "hvac": "Heating, Ventilation, and Air Conditioning",
    
    # QA/QC terms
    "ncr": "Non-Conformance Report",
    "rfi": "Request for Information",
    "qc": "Quality Control",
    "qa": "Quality Assurance",
    "qaqc": "Quality Assurance and Quality Control",
    "snag": "defect or punch list item",
    "punchlist": "punch list",
    
    # Document terms
    "spec": "specification",
    "specs": "specifications",
    "dwgs": "drawings",
    "submittal": "submittal document",
    "boq": "Bill of Quantities",
    "bom": "Bill of Materials",
    "sor": "Schedule of Rates",
    
    # Process terms
    "appr": "approved",
    "apprvd": "approved",
    "rej": "rejected",
    "rev": "revision",
    "amd": "amendment",
    "co": "Change Order",
    "gfc": "Good for Construction",
    "ifc": "Issued for Construction",
}

# Common typos mapping (typo -> correct term)
TYPO_MAPPINGS = {
    # Common keyboard/phonetic typos
    "iim": "BIM",
    "im": "BIM",
    "bim": "BIM",
    "colum": "column",
    "clm": "column",
    "col": "column",
    "imges": "images",
    "img": "images",
    "pic": "pictures",
    "dwg": "drawing",
    "drg": "drawing",
    "conc": "concrete",
    "concreat": "concrete",
    "rnf": "reinforcement",
    "rebar": "reinforcement bar",
    "spec": "specification",
    "specs": "specifications",
    "dim": "dimension",
    "dims": "dimensions",
    "lvls": "levels",
    "el": "elevation",
    "sec": "section",
    "det": "detail",
}

# Status-based tone templates
TONE_TEMPLATES = {
    "submit": {
        "prefix_phrases": [
            "The document has been reviewed and",
            "Upon review,",
            "Having reviewed the submission,",
            "The submitted document",
        ],
        "tone": "neutral and professional",
        "action_words": ["approved", "accepted", "verified", "confirmed", "compliant"],
    },
    "reject": {
        "prefix_phrases": [
            "The submission has been rejected due to",
            "Upon review, the following issues were identified:",
            "The document cannot be approved because",
            "This submission does not meet requirements:",
        ],
        "tone": "firm but polite",
        "action_words": ["rejected", "non-compliant", "incorrect", "not acceptable", "requires correction"],
    },
    "revise": {
        "prefix_phrases": [
            "Please revise the following:",
            "The submission requires revisions:",
            "Kindly address the following concerns:",
            "Minor revisions are required:",
        ],
        "tone": "constructive and guiding",
        "action_words": ["revise", "update", "modify", "correct", "amend", "resubmit"],
    },
}

# Common construction review issues (for pattern matching)
COMMON_ISSUES = {
    "dimension": ["dimensions", "measurements", "sizing", "scale"],
    "spacing": ["rebar spacing", "bar spacing", "clearance", "cover"],
    "clash": ["clash detection", "interference", "conflict", "coordination issue"],
    "missing": ["missing information", "incomplete", "not provided", "lacking"],
    "wrong": ["incorrect", "error", "discrepancy", "mismatch"],
    "quality": ["quality issue", "workmanship", "finish", "standard"],
    "safety": ["safety concern", "hazard", "risk", "non-compliance"],
    "delay": ["schedule delay", "behind schedule", "time overrun"],
    "cost": ["cost overrun", "budget issue", "variation", "additional cost"],
}

# Professional sentence structures by status
SENTENCE_STRUCTURES = {
    "submit": [
        "{document} has been reviewed and approved. {details}",
        "The submitted {document} meets all requirements. {details}",
        "Approved. {details}",
    ],
    "reject": [
        "The {document} has been rejected. {reason}. Please revise and resubmit.",
        "Rejection: {reason}. Correction is required before approval.",
        "The submission does not meet the required standards. {reason}.",
    ],
    "revise": [
        "Please revise the {document}. {reason}.",
        "Minor revisions required: {reason}. Please update and resubmit.",
        "The {document} requires the following updates: {reason}.",
    ],
}


def expand_abbreviations(text: str) -> tuple[str, list[str]]:
    """
    Expand known abbreviations and fix common typos in the text.
    
    Returns:
        tuple: (expanded_text, list of expansions made)
    """
    words = text.split()
    expanded_words = []
    expansions_made = []
    
    for word in words:
        lower_word = word.lower().strip(".,!?")
        
        # Check typos first
        if lower_word in TYPO_MAPPINGS:
            corrected = TYPO_MAPPINGS[lower_word]
            expanded_words.append(corrected)
            expansions_made.append(f"{word} -> {corrected}")
            continue
            
        # Check standard abbreviations
        if lower_word in TERM_EXPANSIONS:
            expanded = TERM_EXPANSIONS[lower_word]
            expanded_words.append(expanded)
            expansions_made.append(f"{word} -> {expanded}")
        else:
            expanded_words.append(word)
    
    return " ".join(expanded_words), expansions_made


def get_tone_context(status: str) -> dict:
    """Get the tone context for a given status."""
    return TONE_TEMPLATES.get(status.lower(), TONE_TEMPLATES["submit"])


def detect_issue_category(text: str) -> str:
    """Detect the category of issue mentioned in the text."""
    text_lower = text.lower()
    
    for category, keywords in COMMON_ISSUES.items():
        if category in text_lower or any(kw in text_lower for kw in keywords):
            return category
    
    return "general"


# Global glossary cache
GLOSSARY_CACHE = {}

def load_glossary():
    """Load the construction glossary from the text file."""
    global GLOSSARY_CACHE
    if GLOSSARY_CACHE:
        return

    try:
        # Path to construction-terms.txt (2 levels up from services/)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        file_path = os.path.join(base_dir, "construction-terms.txt")
        
        if not os.path.exists(file_path):
            print(f"⚠️ Glossary file not found at: {file_path}")
            return

        print(f"📚 Loading glossary from: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        current_term = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # If line is short and looks like a term (not a sentence), treat as key
            # Simple heuristic: If line is short (< 40 chars) and doesn't end with period
            if len(line) < 40 and not line.endswith("."):
                current_term = line.lower()
                if current_term not in GLOSSARY_CACHE:
                    GLOSSARY_CACHE[current_term] = ""
            elif current_term:
                # Append definition to current term
                GLOSSARY_CACHE[current_term] += line + " "
                
        print(f"✅ Loaded {len(GLOSSARY_CACHE)} terms from glossary.")
        
    except Exception as e:
        print(f"❌ Failed to load glossary: {e}")


def find_relevant_glossary_terms(user_input: str, limit: int = 3) -> str:
    """
    Find relevant terms in the glossary based on user input.
    Uses fuzzy matching to handle typos.
    """
    if not GLOSSARY_CACHE:
        load_glossary()
        
    results = []
    seen_terms = set()
    input_words = user_input.split()
    
    # 1. Direct/Fuzzy Match check for each word in input
    for word in input_words:
        word = word.lower().strip(".,!?")
        if len(word) < 2: 
            continue
            
        # Get close matches from glossary keys
        matches = difflib.get_close_matches(word, GLOSSARY_CACHE.keys(), n=2, cutoff=0.7)
        
        for match in matches:
            if match not in seen_terms:
                definition = GLOSSARY_CACHE[match].strip()
                # formatting: "Term: Definition"
                results.append(f"- {match.title()}: {definition[:150]}...") # Truncate long defs
                seen_terms.add(match)
                
    # 2. Add TYPO_MAPPINGS resolutions if not already found
    for word in input_words:
        word = word.lower().strip()
        if word in TYPO_MAPPINGS:
            corrected = TYPO_MAPPINGS[word]
            if corrected.lower() not in seen_terms:
                results.append(f"- {corrected}: (Corrected from '{word}')")
                seen_terms.add(corrected.lower())

    return "\n".join(results[:limit])
