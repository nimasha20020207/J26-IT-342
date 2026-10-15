# import re
# import pandas as pd
# import numpy as np

# from bertopic import BERTopic
# from sentence_transformers import SentenceTransformer

# import spacy

# print("Loading datasets...")

# news = pd.read_excel("data/news.xlsx")
# facebook = pd.read_excel("data/facebook.xlsx")
# tripadvisor = pd.read_excel("data/tripadvisor.xlsx")
# hikingsources = pd.read_excel("data/hikingsources.xlsx")

# news = news.rename(columns={"content": "text"})
# facebook = facebook.rename(columns={"content": "text"})
# tripadvisor = tripadvisor.rename(columns={"content": "text"})
# hikingsources = hikingsources.rename(columns={"content": "text"})
# hikingsources["source"] = "HikingSources"

# news["source"] = "News"
# facebook["source"] = "Facebook"
# tripadvisor["source"] = "TripAdvisor"
# hikingsources["source"] = "HikingSources"


# df = pd.concat(
#     [news, facebook, tripadvisor, hikingsources],
#     ignore_index=True
# )

# print(f"Total records: {len(df)}")

# #text cleaning

# def clean_text(text):

#     text = str(text)

#     text = re.sub(r"http\S+", "", text)

#     text = re.sub(r"[^a-zA-Z0-9\s]", "", text)

#     return text.lower()


# df["clean_text"] = df["text"].apply(clean_text)

# print("Text cleaning completed")

# #creating embeddings
# print("Loading embedding model...")

# embedding_model = SentenceTransformer(
#     "all-MiniLM-L6-v2"
# )

# #training bertopic model
# print("Training BERTopic...")

# topic_model = BERTopic(
#     embedding_model=embedding_model,
#     calculate_probabilities=True,
#     verbose=True
# )

# topics, probs = topic_model.fit_transform(
#     df["clean_text"]
# )

# df["topic_id"] = topics

# #adding probability scores
# topic_probs = []

# for p in probs:
#     topic_probs.append(np.max(p))

# df["topic_probability"] = topic_probs


# #viewing topics
# info = topic_model.get_topic_info()

# print(info)

# info.to_csv(
#     "outputs/topic_info.csv",
#     index=False
# )

# #hazard mapping

# topic_to_hazard = {

#     0: "Landslide",

#     1: "Dense Fog",

#     2: "Slippery Trail",

#     3: "Flood",
    
#     4: "Rockfall",
    
#     5: "Leopard Sighting",
    
#     6: "Monkey Sighting",
    
#     7: "Bugs or Wasp sighting",
    
#     8: "Heavy wind",
    
#     -1: "Unknown"
# }
# df["hazard"] = df["topic_id"].map(
#     topic_to_hazard
# )

# #location extraction
# nlp = spacy.load("en_core_web_sm")

# def extract_location(text):

#     doc = nlp(text)

#     locations = []

#     for ent in doc.ents:

#         if ent.label_ in ["GPE", "LOC"]:

#             locations.append(ent.text)

#     if locations:
#         return locations[0]

#     return None

# df["location"] = df["text"].apply(
#     extract_location
# )

# #reliability scores
# SOURCE_RELIABILITY = {

#     "News": 0.95,

#     "Facebook": 0.65,

#     "TripAdvisor": 0.75,

#     "HikingSources": 0.85
# }

# df["reliability"] = df["source"].map(
#     SOURCE_RELIABILITY
# )

# #hazard scores
# df["hazard_score"] = (

#     df["topic_probability"]

#     *

#     df["reliability"]
# )

# #saving final dataset
# df.to_csv(
#     "outputs/final_nlp_output.csv",
#     index=False
# )

# print("Final dataset saved")

# #save model
# topic_model.save(
#     "models/bertopic_model"
# )

# print("Model saved")

# #visualization

# try:

#     fig = topic_model.visualize_topics()

#     fig.write_html(
#         "outputs/topics.html"
#     )

#     fig = topic_model.visualize_hierarchy()

#     fig.write_html(
#         "outputs/hierarchy.html"
#     )

#     print("Visualization completed")

# except Exception as e:

#     print(f"Visualization skipped: {e}")



import re
import pandas as pd
import numpy as np

from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

import nltk
from nltk.corpus import stopwords

# --------------------------------------------------
# Download stopwords (first run only)
# --------------------------------------------------

nltk.download("stopwords")

STOP_WORDS = set(stopwords.words("english"))

# --------------------------------------------------
# Load datasets
# --------------------------------------------------

print("Loading datasets...")

news = pd.read_excel("data/news.xlsx")
facebook = pd.read_excel("data/facebook.xlsx")
tripadvisor = pd.read_excel("data/tripadvisor.xlsx")
hikingsources = pd.read_excel("data/hikingsources.xlsx")

# --------------------------------------------------
# Standardize column names
# --------------------------------------------------

news = news.rename(columns={"content": "text"})
facebook = facebook.rename(columns={"content": "text"})
tripadvisor = tripadvisor.rename(columns={"content": "text"})
hikingsources = hikingsources.rename(columns={"content": "text"})

# --------------------------------------------------
# Add source labels
# --------------------------------------------------

news["source"] = "News"
facebook["source"] = "Facebook"
tripadvisor["source"] = "TripAdvisor"
hikingsources["source"] = "HikingSources"

# --------------------------------------------------
# Combine datasets
# --------------------------------------------------

df = pd.concat(
    [news, facebook, tripadvisor, hikingsources],
    ignore_index=True
)

print(f"Total records: {len(df)}")

# --------------------------------------------------
# Text cleaning
# --------------------------------------------------

def clean_text(text):

    text = str(text)

    text = re.sub(r"http\S+", "", text)

    text = re.sub(r"[^a-zA-Z\s]", "", text)

    text = text.lower()

    words = text.split()

    words = [
        word
        for word in words
        if word not in STOP_WORDS
    ]

    return " ".join(words)

df["clean_text"] = df["text"].apply(clean_text)

print("Text cleaning completed")

# --------------------------------------------------
# Embeddings
# --------------------------------------------------

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# --------------------------------------------------
# BERTopic
# --------------------------------------------------

print("Training BERTopic...")

topic_model = BERTopic(
    embedding_model=embedding_model,
    calculate_probabilities=True,
    min_topic_size=5,
    verbose=True
)

topics, probs = topic_model.fit_transform(
    df["clean_text"]
)

df["topic_id"] = topics

# --------------------------------------------------
# Topic probability
# --------------------------------------------------

topic_probs = []

for p in probs:
    topic_probs.append(np.max(p))

df["topic_probability"] = topic_probs

# --------------------------------------------------
# Topic information
# --------------------------------------------------

info = topic_model.get_topic_info()

print("\n========== TOPICS ==========")
print(info)

info.to_csv(
    "outputs/topic_info.csv",
    index=False
)

# --------------------------------------------------
# Hazard Mapping
# --------------------------------------------------

topic_to_hazard = {
    0: "Landslide",
    1: "Dense Fog",
    2: "Slippery Trail",
    3: "Flood",
    4: "Rockfall",
    5: "Leopard Sighting",
    6: "Monkey Sighting",
    7: "Bugs/Wasp Activity",
    8: "Heavy Wind",
    -1: "Unknown"
}

df["hazard"] = df["topic_id"].map(topic_to_hazard)

df["hazard"] = df["hazard"].fillna("Unclassified")

# --------------------------------------------------
# Reliability Scores
# --------------------------------------------------

SOURCE_RELIABILITY = {

    "News": 0.95,

    "Facebook": 0.65,

    "TripAdvisor": 0.75,

    "HikingSources": 0.85
}

df["reliability"] = df["source"].map(
    SOURCE_RELIABILITY
)

# --------------------------------------------------
# Hazard Score
# --------------------------------------------------

df["hazard_score"] = (
    df["topic_probability"]
    *
    df["reliability"]
)

# --------------------------------------------------
# Save Final Dataset
# --------------------------------------------------

df.to_csv(
    "outputs/final_nlp_output.csv",
    index=False
)

print("Final dataset saved")

# --------------------------------------------------
# Save Model
# --------------------------------------------------

topic_model.save(
    "models/bertopic_model"
)

print("Model saved")

# --------------------------------------------------
# Visualization
# --------------------------------------------------

try:

    fig = topic_model.visualize_topics()

    fig.write_html(
        "outputs/topics.html"
    )

    fig = topic_model.visualize_hierarchy()

    fig.write_html(
        "outputs/hierarchy.html"
    )

    print("Visualization completed")

except Exception as e:

    print(
        f"Visualization skipped: {e}"
    )

# --------------------------------------------------
# Preview Results
# --------------------------------------------------

print("\n========== DATA SAMPLE ==========")

print(
    df[
        [
            "source",
            "location",
            "topic_id",
            "hazard",
            "hazard_score"
        ]
    ].head()
)

print("\nPipeline completed successfully.")