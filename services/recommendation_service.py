from urllib.parse import quote_plus

PLATFORM_SEARCH = {
    "amazon": "https://www.amazon.in/s?k={q}",
    "flipkart": "https://www.flipkart.com/search?q={q}",
    "ikea": "https://www.ikea.com/in/en/search/?q={q}",
    "swiggy": "https://www.swiggy.com/search?query={q}",
    "zomato": "https://www.zomato.com/search?q={q}",
    "oyo": "https://www.oyorooms.com/search?q={q}",
}

def platform_link(platform: str, query: str) -> str:
    template = PLATFORM_SEARCH.get(platform.lower())
    return template.format(q=quote_plus(query)) if template else "#"

def home_fallback(data: dict) -> dict:
    budget = float(data["budget"])
    rooms = data.get("rooms", [])
    per_room = budget / max(len(rooms), 1)
    items = []
    for room in rooms:
        q = f"{data.get('style','Modern')} {room} decor"
        items.append({
            "category": room,
            "item": f"{data.get('style','Modern')} {room} starter decor set",
            "estimated_price": round(per_room, 2),
            "platform": "Amazon",
            "link": platform_link("amazon", q),
            "reason": "Budget-balanced starter option; verify current price before purchase."
        })
    return {
        "planner": "home", "budget": budget,
        "summary": f"A {data.get('style','Modern')} home plan across {len(rooms)} room(s), keeping the total near ₹{budget:,.0f}.",
        "budget_allocation": {room: round(per_room, 2) for room in rooms},
        "recommendations": items
    }

def party_fallback(data: dict) -> dict:
    budget = float(data["budget"])
    allocation = {"food": round(budget*0.50,2), "decoration": round(budget*0.20,2), "entertainment": round(budget*0.15,2), "venue": round(budget*0.15,2)}
    guests = int(data["guests"])
    food_per_guest = allocation["food"] / guests
    return {
        "planner":"party", "budget":budget,
        "summary": f"A {data.get('event_type','Birthday')} plan for {guests} guests at {data.get('venue','Home')}, with food capped near ₹{allocation['food']:,.0f}.",
        "budget_allocation": allocation,
        "recommendations": [
            {"category":"Food", "item":f"Catering / meal options for {guests} guests", "estimated_price":allocation["food"], "platform":"Swiggy", "link":platform_link("swiggy", data.get('event_type','party')+" catering"), "reason":f"Target food spend is about ₹{food_per_guest:,.0f} per guest."},
            {"category":"Food", "item":"Restaurant/event food options", "estimated_price":allocation["food"], "platform":"Zomato", "link":platform_link("zomato", data.get('event_type','party')+" catering"), "reason":"Useful for comparing local restaurant options."},
            {"category":"Decoration", "item":f"{data.get('event_type','Party')} decoration package", "estimated_price":allocation["decoration"], "platform":"Amazon", "link":platform_link("amazon", data.get('event_type','party')+" decorations"), "reason":"Keeps decoration within the planned share."},
            {"category":"Venue", "item":"Accommodation/venue search", "estimated_price":allocation["venue"], "platform":"OYO", "link":platform_link("oyo", data.get('venue','event venue')), "reason":"Compare available venues or nearby stays."}
        ]
    }

def jewelry_fallback(data: dict) -> dict:
    budget = float(data["budget"])
    occasion = data.get("occasion", "Special Occasion")
    style = data.get("style", "Elegant")
    query = f"{style} jewelry {occasion}"
    return {
        "planner":"jewelry", "budget":budget,
        "summary": f"{style} jewelry suggestions for a {occasion} within ₹{budget:,.0f}. Image analysis is optional.",
        "budget_allocation": {"main_piece": round(budget*0.65,2), "earrings": round(budget*0.20,2), "backup": round(budget*0.15,2)},
        "recommendations": [
            {"category":"Main Piece", "item":f"{style} necklace / statement piece", "estimated_price":round(budget*0.65,2), "platform":"Amazon", "link":platform_link("amazon", query), "reason":"Leaves room for complementary pieces while staying inside the budget."},
            {"category":"Earrings", "item":f"Matching {style} earrings", "estimated_price":round(budget*0.20,2), "platform":"Flipkart", "link":platform_link("flipkart", query+" earrings"), "reason":"Complements the main jewelry choice."},
            {"category":"Alternative", "item":f"Alternative {style} jewelry set", "estimated_price":round(budget*0.15,2), "platform":"Amazon", "link":platform_link("amazon", query+" set"), "reason":"Backup option if the main item is unavailable."}
        ]
    }
