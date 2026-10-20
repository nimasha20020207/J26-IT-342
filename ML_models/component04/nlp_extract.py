"""
Natural Language Processing (NLP) Information Extraction Module for Hiking Incidents (Component 4)
Extracts structured indicators from unstructured incident descriptions:
- Emergency category candidates
- Severity indicators
- Contextual environmental hazards
- Physical conditions / symptoms
- Explicit assistance requests
"""
import re
from typing import Dict, List, Any

KEYWORDS = {
    "emergency_type": {
        "injury": [
            "injured", "fell", "fall", "bleeding", "ankle", "bone", "fracture",
            "sprain", "wound", "trauma", "head injury", "twisted", "cut"
        ],
        "lost_hiker": [
            "lost", "missing", "cannot find", "wrong path", "separated",
            "disoriented", "night fall", "dark", "no trail", "off path"
        ],
        "landslide": [
            "landslide", "slope moving", "falling rocks", "mudslide", "debris",
            "earth slip", "boulders", "rockfall"
        ],
        "flooding": [
            "flood", "rising water", "fast stream", "water crossing", "river overflowing",
            "flash flood", "water surge", "submerged"
        ],
        "dehydration_fatigue": [
            "dizzy", "dehydrated", "exhausted", "fatigue", "faint", "cramps",
            "heat stroke", "thirst", "weakness", "vomiting", "passed out"
        ],
        "wildlife_encounter": [
            "wild animal", "elephant", "leopard", "wild boar", "snake",
            "bear", "wasp", "hornet", "monkey attack"
        ],
        "severe_weather": [
            "thunderstorm", "strong winds", "heavy rain", "poor visibility",
            "mist", "fog", "gale", "hypothermia", "freezing", "lightning"
        ],
        "trail_blockage": [
            "fallen tree", "blocked trail", "damaged bridge", "obstacle",
            "impassable", "collapsed bridge"
        ]
    },
    "severity_indicators": {
        "high": [
            "unconscious", "cannot walk", "severe bleeding", "critical",
            "broken leg", "trapped", "dying", "immediate assistance", "emergency", "urgent"
        ],
        "moderate": [
            "pain", "sprained", "dizzy", "heavy rain", "lost", "night",
            "cold", "shivering", "moderate pain", "cannot find route"
        ],
        "low": [
            "minor", "scratch", "slight pain", "safe", "stable", "tired"
        ]
    },
    "environmental_hazards": {
        "heavy_rain": ["heavy rain", "torrential", "downpour", "rainfall", "pouring"],
        "poor_visibility": ["poor visibility", "dense mist", "thick fog", "cannot see", "darkness", "pitch black"],
        "steep_terrain": ["cliff", "steep", "precipice", "loose scree", "slippery rocks", "vertical drop"],
        "high_water": ["swollen river", "fast water", "strong current", "water level rising"],
        "low_battery": ["battery low", "phone dying", "5%", "10%", "battery dead", "shutting down"]
    },
    "required_assistance": {
        "ambulance": ["ambulance", "hospital", "paramedic", "medical doctor"],
        "search_and_rescue": ["search team", "rescue team", "search and rescue", "ranger", "police", "stretcher"],
        "evacuation": ["evacuate", "airlift", "helicopter", "carry down"],
        "first_aid": ["first aid", "bandage", "splint", "antiseptic", "painkiller"]
    }
}

class IncidentNLPExtractor:
    def __init__(self):
        pass

    def extract(self, text: str) -> Dict[str, Any]:
        if not text:
            return {
                "detected_emergency_types": [],
                "severity_urgency": "LOW",
                "environmental_hazards": [],
                "required_assistance": [],
                "primary_candidate": "unknown",
                "confidence_score": 0.0
            }

        t = text.lower()
        extracted: Dict[str, List[str]] = {}

        for category, label_dict in KEYWORDS.items():
            found_items = []
            for label, words in label_dict.items():
                pattern = r"\b(" + "|".join([re.escape(w) for w in words]) + r")\b"
                if re.search(pattern, t):
                    found_items.append(label)
            extracted[category] = found_items

        # Determine severity level from text
        sev_urgency = "LOW"
        if any(w in extracted.get("severity_indicators", []) for w in ["high"]):
            sev_urgency = "HIGH"
        elif any(w in extracted.get("severity_indicators", []) for w in ["moderate"]):
            sev_urgency = "MODERATE"

        # Determine top candidate emergency
        em_types = extracted.get("emergency_type", [])
        primary = em_types[0] if em_types else "unspecified_emergency"
        confidence = 0.90 if len(em_types) == 1 else (0.80 if len(em_types) > 1 else 0.50)

        return {
            "detected_emergency_types": em_types,
            "primary_candidate": primary,
            "severity_urgency": sev_urgency,
            "environmental_hazards": extracted.get("environmental_hazards", []),
            "required_assistance": extracted.get("required_assistance", []),
            "confidence_score": confidence
        }

if __name__ == "__main__":
    extractor = IncidentNLPExtractor()
    sample = "A hiker slipped on steep rocks during heavy downpour, suffering severe bleeding and broken leg. Immediate ambulance needed."
    print("NLP Extraction Result:")
    import json
    print(json.dumps(extractor.extract(sample), indent=2))
