# ✅ Keyword-based intent classification (no LLM required)

# Intent keyword map
INTENT_MAP = {
    "ask_fact": [
        "who", "what", "when", "where", "how", "fact", "information",
        "tell me", "question", "history", "details", "background"
    ],
    "plan_trip": [
        "plan", "trip", "itinerary", "travel", "schedule", "days",
        "visit", "route", "journey", "vacation", "holiday"
    ],
    "compare_hotels": [
        "compare", "hotel", "hotels", "accommodation", "stay",
        "price", "rating", "location", "amenities"
    ],
    "explore_place": [
        "explore", "location", "place", "overview", "learn about",
        "discover", "attractions", "things to do", "sights"
    ]
}

def classify_intent(query: str, model: str = "qwen:0.5b") -> str:
    query_lower = query.lower()

    for intent, keywords in INTENT_MAP.items():
        if any(keyword in query_lower for keyword in keywords):
            return intent

    return "unsupported"