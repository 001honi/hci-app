# === Configuration ===
# Thresholds for fuzzy matching
THRESHOLDS = {
    1: {"THR_CORRECT": 101, "THR_MISPRONOUNCE": 80}, # 1-gram (word)
    2: {"THR_CORRECT": 95, "THR_MISPRONOUNCE": 60}, # bi-gram
    3: {"THR_CORRECT": 85, "THR_MISPRONOUNCE": 60}, # tri-gram
}


challenging_words = [ "thorough", "vocabulary", "comfortable", "rural", "squirrel", "sixth", "clothes", "world" ]

# In a thorough exploration of the English vocabulary, 
# one might find it quite comfortable to discuss the rural landscapes where squirrels dart around. 
# However, the sixth challenge arises when trying to describe the clothes worn by people around the world.


konglish_words = [
    "cup",
    "TV",
    "refrigerator",
    "cellphone",
    "computer",
    "internet",
    "laptop",
    "keyboard",
    "mouse",
    "meeting",
    "freelancer",
    "underwear",
    "shampoo",
    "hair",
    "style",
    "icecream",
    "cheese",
    "butter",
    "cola",
    "sports",
    "dance",
    "camera",
    "comedy",
    "leader",
    "service",
    "virus",
    "printer",
    "email"
]

