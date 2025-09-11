from typing import List
import json
from pathlib import Path
import re
from difflib import SequenceMatcher


HSN_CODES = [
    {"code": "8708", "desc": "Parts and accessories of motor vehicles", "gst": 28.0, "type": "HSN"},
    {"code": "6204", "desc": "Women's or girls' suits, ensembles, jackets, dresses", "gst": 5.0, "type": "HSN"},
    {"code": "6205", "desc": "Men's or boys' shirts", "gst": 5.0, "type": "HSN"},
    {"code": "1006", "desc": "Rice", "gst": 5.0, "type": "HSN"},
    {"code": "8528", "desc": "Monitors and projectors, reception apparatus for television", "gst": 18.0, "type": "HSN"},
    {"code": "8518", "desc": "Microphones and loudspeakers; sound amplifiers", "gst": 18.0, "type": "HSN"},
    {"code": "998314", "desc": "IT and consulting services", "gst": 18.0, "type": "SAC"},
]

# Try to load extended dataset if available
_DATA_FILE = Path(__file__).resolve().parent / "hsn_data.json"
if _DATA_FILE.exists():
    try:
        with _DATA_FILE.open("r", encoding="utf-8") as f:
            extra = json.load(f)
            if isinstance(extra, list):
                cleaned = [
                    {
                        "code": str(it.get("code", "")).strip(),
                        "desc": str(it.get("desc", "")).strip(),
                        "gst": float(it.get("gst", 0)),
                        "type": (it.get("type") or ("SAC" if str(it.get("code", "")).startswith("99") else "HSN")),
                    }
                    for it in extra
                    if it.get("code") and it.get("desc")
                ]
                if cleaned:
                    HSN_CODES = cleaned
    except Exception:
        pass


def suggest_hsn(query: str) -> List[dict]:
    q = (query or "").lower().strip()
    if not q:
        return []

    # Tokenization; ignore short alpha tokens to reduce noise, keep numeric tokens
    raw_tokens = re.findall(r"[\w]+", q)
    tokens: List[str] = []
    for t in raw_tokens:
        if t.isdigit():
            tokens.append(t)
        elif len(t) >= 3:
            tokens.append(t)
    synonyms = {
        "tv": ["television", "led", "lcd"],
        "brake": ["brake", "brakes", "pad", "pads"],
        "saree": ["saree", "sari", "cotton"],
        "shirt": ["shirt", "shirts"],
        "rice": ["rice", "basmati"],
        "oil": ["engine oil", "lubricant"],
        "speaker": ["speaker", "sound bar", "soundbar"],
        "laptop": ["laptop", "computer", "automatic data processing", "machines"],
        "computer": ["computer", "laptop", "automatic data processing", "machines", "computing"],
        "phone": ["mobile", "cellphone", "smartphone"],
        "consulting": ["consulting", "consultation", "it", "software"],
        "marketing": ["advertising", "digital marketing"],
        "construction": ["works contract", "civil", "construction"],
        "electronic": ["electronic", "electrical", "apparatus"],
        "machine": ["machine", "machines", "equipment"],
        "software": ["software", "programs", "data processing"],
    }
    expanded_terms = set(tokens)
    for t in list(tokens):
        for s in synonyms.get(t, []):
            expanded_terms.add(s)

    def norm(s: str) -> str:
        return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", (s or "").lower())).strip()

    q_norm = norm(q)

    def score(h):
        code = str(h['code'])
        desc = (h['desc'] or "").lower()
        words = re.findall(r"[a-z0-9]+", desc)
        desc_norm = norm(desc)
        sc = 0
        
        # Prioritize actual products over services
        # HSN codes (products) should rank higher than SAC codes (services) for goods
        is_hsn_product = not code.startswith('99')  # HSN codes don't start with 99
        is_service_description = any(word in desc for word in ['service', 'services', 'repair', 'maintenance', 'consulting'])
        
        if is_hsn_product and not is_service_description:
            sc += 50  # Boost for actual products
        elif is_service_description:
            sc -= 20  # Penalty for service descriptions when looking for goods
        
        # Exact/phrase boosts
        if q_norm and desc_norm == q_norm:
            sc += 250
        if q_norm and desc_norm.startswith(q_norm):
            sc += 120
        if q in desc:
            sc += 80

        for t in expanded_terms:
            # Strong weight for code prefix match
            if t.isdigit() and code.startswith(t):
                sc += 200
                continue
            # Whole-word match
            if t in words:
                sc += 90
            # Word prefix match
            if any(w.startswith(t) for w in words):
                sc += 60
            # Substring match
            if t in desc:
                sc += 15
            # Fuzzy closeness
            best_ratio = 0.0
            for w in words[:40]:
                r = SequenceMatcher(None, t, w).ratio()
                if r > best_ratio:
                    best_ratio = r
            if best_ratio >= 0.9:
                sc += 15
            elif best_ratio >= 0.8:
                sc += 8
        return sc

    scored = [(score(h), h) for h in HSN_CODES]
    scored = [t for t in scored if t[0] > 0]
    scored.sort(key=lambda x: (-x[0], hsn_sort_key(x[1])))
    results: List[dict] = []
    for s, h in scored[:10]:
        conf = 60 + min(40, s // 20)  # rough confidence scaled
        results.append({"code": h["code"], "desc": h["desc"], "gst": h["gst"], "type": h["type"], "confidence": conf})
    return results


def hsn_sort_key(h):
    return (h["type"], h["code"])
