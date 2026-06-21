KEYWORD_MAP = {
    "Food": [
        "swiggy", "zomato", "dominos", "domino", "mcdonalds", "mcdonald",
        "burger king", "subway", "starbucks", "cafe coffee day", "ccd",
        "kfc", "pizza hut", "barbeque nation", "behrouz", "faasos",
        "box8", "freshmenu", "dunkin", "baskin", "restaurant", "cafe",
        "hotel", "dhaba", "biryani", "kitchen", "foods", "bakery",
        "sweet", "juice", "chai", "tea", "coffee",
    ],
    "Transport": [
        "uber", "ola", "rapido", "meru", "metro", "irctc", "railways",
        "railway", "bus", "petrol", "diesel", "fuel", "hp petrol",
        "indian oil", "bharat petroleum", "shell", "namma metro",
        "bmtc", "ksrtc", "redbus", "makemytrip flight", "indigo",
        "air india", "spicejet", "vistara", "goair", "parking",
        "fastag", "toll",
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "ajio", "nykaa", "meesho",
        "snapdeal", "shopsy", "tata cliq", "reliance digital",
        "croma", "vijay sales", "h&m", "zara", "uniqlo", "max fashion",
        "lifestyle", "shoppers stop", "pantaloons", "westside",
        "dmart", "big bazaar", "reliance fresh", "more supermarket",
        "spencer", "star bazaar", "lenskart", "pepperfry", "urban ladder",
        "ikea",
    ],
    "Subscription": [
        "netflix", "spotify", "amazon prime", "hotstar", "disney",
        "youtube premium", "apple music", "gaana", "jio saavn",
        "zee5", "sonyliv", "voot", "mxplayer", "altbalaji",
        "linkedin premium", "microsoft 365", "adobe", "canva",
        "dropbox", "google one", "icloud",
    ],
    "Utilities": [
        "airtel", "jio", "vi ", "vodafone", "idea", "bsnl",
        "electricity", "bescom", "msedcl", "tata power", "adani electric",
        "water bill", "gas", "indane", "hp gas", "bharat gas",
        "broadband", "act fibernet", "hathway", "tikona",
        "postpaid", "recharge", "bill payment",
    ],
    "Health": [
        "apollo", "medplus", "1mg", "pharmeasy", "netmeds",
        "practo", "cult fit", "cure fit", "healthians",
        "thyrocare", "lal path", "dr lal", "max hospital",
        "fortis", "manipal", "narayana", "aiims", "clinic",
        "pharmacy", "medical", "hospital", "diagnostics",
        "gym", "fitness", "yoga",
    ],
    "Entertainment": [
        "pvr", "inox", "cinepolis", "bookmyshow", "paytm movies",
        "wonderla", "imagica", "esselworld", "bowling", "smaaash",
        "timezone", "virtual reality", "escape room", "paintball",
        "amusement", "theme park", "concert", "event",
    ],
}


def keyword_categorize(merchant: str) -> tuple[str, float]:
    """
    Categorize merchant using keyword matching.
    Returns (category, confidence).
    Confidence is 1.0 if matched, 0.0 if fallback to Other.
    """
    merchant_lower = merchant.lower().strip()

    for category, keywords in KEYWORD_MAP.items():
        for keyword in keywords:
            if keyword in merchant_lower:
                return category, 1.0

    return "Other", 0.0


def bulk_keyword_categorize(merchants: list[str]) -> list[dict]:
    """Categorize a list of merchants. Returns list of results."""
    results = []
    for merchant in merchants:
        category, confidence = keyword_categorize(merchant)
        results.append({
            "merchant": merchant,
            "category": category,
            "confidence": confidence,
            "method": "keyword",
        })
    return results