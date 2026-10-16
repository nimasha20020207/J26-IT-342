
# hazard_config.py

# Candidate categories for the Sri Lankan hiking hazard project.
# Review these against your actual dataset and project requirements.

HAZARD_CATEGORIES = [
    "landslide or slope failure",
    "flooding or flash flood",
    "slippery trail or muddy ground",
    "rockfall or falling rocks",
    "fallen trees or branches",
    "heavy rainfall",
    "lightning or thunderstorm",
    "dense fog or poor visibility",
    "forest fire or wildfire",
    "leech activity",
    "dangerous wildlife encounter",
    "strong winds",
    "extreme heat or heat stress",
    "river crossing danger",
    "trail erosion or trail collapse",
    "blocked trail or other trail obstruction",
    "navigation difficulty or getting lost",
    "no relevant hiking hazard"
]

# A report can receive multiple hazard labels.
# This is a starting threshold, not a validated universal value.
ZERO_SHOT_THRESHOLD = 0.35

# Model used to score candidate labels against report text.
ZERO_SHOT_MODEL = "facebook/bart-large-mnli"

# Sentence-transformer embedding model used by BERTopic.
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Keep input batches manageable on a typical development computer.
CLASSIFICATION_BATCH_SIZE = 8

# Minimum number of records to form a BERTopic topic.
MIN_TOPIC_SIZE = 5
