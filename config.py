# === Configuration ===
DEBUG_MODE = False

# Thresholds for fuzzy matching
THR_DEFAULT_1 = {"THR_CORRECT": 101, "THR_MISPRONOUNCE": 80} # 1-gram (word)
THR_DEFAULT_2 = {"THR_CORRECT": 95, "THR_MISPRONOUNCE": 70}  # bi-gram
# THR_DEFAULT_3 = {"THR_CORRECT": 85, "THR_MISPRONOUNCE": 60}  # tri-gram

THRESHOLDS = {
    1: THR_DEFAULT_1, 
    2: THR_DEFAULT_2
}

THRESHOLDS_OVERRIDE = {
    "alumni" : {
        1: THR_DEFAULT_1, 
        2: {"THR_CORRECT": 95, "THR_MISPRONOUNCE": 51},
    }
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