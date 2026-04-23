from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ── Keyword dictionaries ───────────────────────────────────────────────────────
POSITIVE_KEYWORDS = {
    "organic":        {"category": "Material",      "emoji": "♻️",  "weight": 2, "reason": "Contains organic material"},
    "recyclable":     {"category": "Material",      "emoji": "♻️",  "weight": 2, "reason": "Can be recycled after use"},
    "biodegradable":  {"category": "Material",      "emoji": "♻️",  "weight": 3, "reason": "Breaks down naturally"},
    "recycled":       {"category": "Material",      "emoji": "♻️",  "weight": 2, "reason": "Made from recycled content"},
    "upcycled":       {"category": "Material",      "emoji": "♻️",  "weight": 2, "reason": "Creatively reused material"},
    "natural":        {"category": "Material",      "emoji": "♻️",  "weight": 1, "reason": "Uses natural materials"},
    "bamboo":         {"category": "Material",      "emoji": "♻️",  "weight": 2, "reason": "Bamboo is highly renewable"},
    "plant-based":    {"category": "Material",      "emoji": "♻️",  "weight": 2, "reason": "Derived from plants"},
    "compostable":    {"category": "Packaging",     "emoji": "📦",  "weight": 3, "reason": "Can be composted"},
    "zero waste":     {"category": "Packaging",     "emoji": "📦",  "weight": 3, "reason": "Produces no waste"},
    "reusable":       {"category": "Packaging",     "emoji": "📦",  "weight": 2, "reason": "Designed to be reused"},
    "non-toxic":      {"category": "Chemicals",     "emoji": "🧪",  "weight": 2, "reason": "Free from harmful toxins"},
    "chemical-free":  {"category": "Chemicals",     "emoji": "🧪",  "weight": 2, "reason": "No harmful chemicals used"},
    "renewable":      {"category": "Sustainability","emoji": "🌍",  "weight": 2, "reason": "Uses renewable resources"},
    "sustainable":    {"category": "Sustainability","emoji": "🌍",  "weight": 2, "reason": "Designed for sustainability"},
    "eco-friendly":   {"category": "Sustainability","emoji": "🌍",  "weight": 2, "reason": "Explicitly eco-friendly"},
    "carbon neutral": {"category": "Sustainability","emoji": "🌍",  "weight": 3, "reason": "Offsets all carbon emissions"},
    "solar":          {"category": "Energy",        "emoji": "⚡",  "weight": 3, "reason": "Powered by clean solar energy"},
    "energy efficient":{"category":"Energy",        "emoji": "⚡",  "weight": 2, "reason": "Consumes less energy"},
}

NEGATIVE_KEYWORDS = {
    "plastic":           {"category": "Material",      "emoji": "♻️",  "weight": -2, "reason": "Plastic takes centuries to decompose"},
    "non-biodegradable": {"category": "Material",      "emoji": "♻️",  "weight": -3, "reason": "Does not break down naturally"},
    "synthetic":         {"category": "Material",      "emoji": "♻️",  "weight": -1, "reason": "Synthetic materials harm ecosystems"},
    "single-use":        {"category": "Packaging",     "emoji": "📦",  "weight": -2, "reason": "Single-use products create excess waste"},
    "non-recyclable":    {"category": "Packaging",     "emoji": "📦",  "weight": -2, "reason": "Cannot be recycled"},
    "chemical":          {"category": "Chemicals",     "emoji": "🧪",  "weight": -2, "reason": "Contains harmful chemicals"},
    "toxic":             {"category": "Chemicals",     "emoji": "🧪",  "weight": -3, "reason": "Contains toxic substances"},
    "bleached":          {"category": "Chemicals",     "emoji": "🧪",  "weight": -2, "reason": "Bleaching uses harsh chemicals"},
    "microplastic":      {"category": "Chemicals",     "emoji": "🧪",  "weight": -3, "reason": "Microplastics pollute waterways"},
    "pvc":               {"category": "Chemicals",     "emoji": "🧪",  "weight": -3, "reason": "PVC contains hazardous additives"},
    "harmful":           {"category": "Chemicals",     "emoji": "🧪",  "weight": -2, "reason": "Harmful to the environment"},
    "fossil fuel":       {"category": "Energy",        "emoji": "⚡",  "weight": -3, "reason": "Relies on non-renewable fossil fuels"},
    "petroleum":         {"category": "Energy",        "emoji": "⚡",  "weight": -3, "reason": "Derived from petroleum"},
    "aerosol":           {"category": "Sustainability","emoji": "🌍",  "weight": -2, "reason": "Aerosols contribute to air pollution"},
}

CATEGORY_ORDER = ["Material", "Packaging", "Chemicals", "Energy", "Sustainability"]
CATEGORY_EMOJI = {"Material":"♻️","Packaging":"📦","Chemicals":"🧪","Energy":"⚡","Sustainability":"🌍"}


def analyze(text):
    lower = text.lower()
    found_pos, found_neg = [], []

    for kw, data in POSITIVE_KEYWORDS.items():
        if kw in lower:
            found_pos.append({"keyword": kw, **data})

    for kw, data in NEGATIVE_KEYWORDS.items():
        if kw in lower:
            found_neg.append({"keyword": kw, **data})

    if not found_pos and not found_neg:
        return {"verdict": "insufficient"}

    # Overall score
    pos_sum = sum(k["weight"] for k in found_pos)
    neg_sum = sum(abs(k["weight"]) for k in found_neg)
    total   = pos_sum + neg_sum
    score   = round((pos_sum / total) * 10, 1) if total else 0
    score   = max(1.0, min(10.0, score))

    # Per-category breakdown
    cats = {}
    for k in found_pos + found_neg:
        c = k["category"]
        if c not in cats:
            cats[c] = {"pos": 0, "neg": 0, "reasons": []}
        if k["weight"] > 0:
            cats[c]["pos"] += k["weight"]
            cats[c]["reasons"].append({"text": k["reason"], "good": True})
        else:
            cats[c]["neg"] += abs(k["weight"])
            cats[c]["reasons"].append({"text": k["reason"], "good": False})

    breakdown = []
    for cat in CATEGORY_ORDER:
        if cat in cats:
            d = cats[cat]
            t = d["pos"] + d["neg"]
            s = round((d["pos"] / t) * 10) if t else 5
            breakdown.append({
                "category": cat,
                "emoji":    CATEGORY_EMOJI[cat],
                "score":    s,
                "reasons":  d["reasons"],
            })

    verdict = "eco" if score >= 7 else "partial" if score >= 4 else "harmful"
    label   = ("🟢 Eco-Friendly"       if verdict == "eco"
               else "🟡 Partially Eco-Friendly" if verdict == "partial"
               else "🔴 Environmental Concern")
    low_data = (len(found_pos) + len(found_neg)) <= 2

    return {
        "verdict":   verdict,
        "score":     score,
        "label":     label,
        "breakdown": breakdown,
        "found_pos": [k["keyword"] for k in found_pos],
        "found_neg": [k["keyword"] for k in found_neg],
        "reasons":   [{"text": k["reason"], "good": True}  for k in found_pos] +
                     [{"text": k["reason"], "good": False} for k in found_neg],
        "low_data":  low_data,
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze_route():
    data = request.get_json()
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400
    return jsonify(analyze(text))


if __name__ == "__main__":
    app.run(debug=True)
