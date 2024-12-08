# === Configuration ===
# Thresholds for fuzzy matching
THRESHOLDS = {
    1: {"THR_CORRECT": 101, "THR_MISPRONOUNCE": 80}, # 1-gram (word)
    2: {"THR_CORRECT": 95, "THR_MISPRONOUNCE": 70}, # bi-gram
    3: {"THR_CORRECT": 85, "THR_MISPRONOUNCE": 60}, # tri-gram
}


challenging_words = [ 
    "renowned", 
    "robotics", 
    "february", 
    "alumni",
    "entrepreneuiral", 
    "patents", 
    "societal",
    "through",
    "regularly",
    "library",
    "economy",
    "laboratories",
    "cafeteria",
    "interdisciplinary",
    "squirrel"
    ]