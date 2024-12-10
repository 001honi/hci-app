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
    "societal" : {
        1: {"THR_CORRECT": 101, "THR_MISPRONOUNCE": 47}, 
        2: THR_DEFAULT_2,
    },
}

challenging_words = [ 
    "honor", 
    "robotics", 
    "february", 
    "impactful",
    "economy", 
    "library", 
    "laboratories",
    "growth",
    "archive",
    "societal",
    ]



