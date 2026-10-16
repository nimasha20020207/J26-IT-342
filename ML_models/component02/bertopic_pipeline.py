
# import re
# import pandas as pd
# import numpy as np

# from bertopic import BERTopic
# from sentence_transformers import SentenceTransformer

# import nltk
# from nltk.corpus import stopwords

# # --------------------------------------------------
# # Download stopwords (first run only)
# # --------------------------------------------------

# nltk.download("stopwords")

# STOP_WORDS = set(stopwords.words("english"))

# # --------------------------------------------------
# # Load datasets
# # --------------------------------------------------

# print("Loading datasets...")

# news = pd.read_excel("data/news.xlsx")
# facebook = pd.read_excel("data/facebook.xlsx")
# tripadvisor = pd.read_excel("data/tripadvisor.xlsx")
# hikingsources = pd.read_excel("data/hikingsources.xlsx")

# # --------------------------------------------------
# # Standardize column names
# # --------------------------------------------------

# news = news.rename(columns={"content": "text"})
# facebook = facebook.rename(columns={"content": "text"})
# tripadvisor = tripadvisor.rename(columns={"content": "text"})
# hikingsources = hikingsources.rename(columns={"content": "text"})

# # --------------------------------------------------
# # Add source labels
# # --------------------------------------------------

# news["source"] = "News"
# facebook["source"] = "Facebook"
# tripadvisor["source"] = "TripAdvisor"
# hikingsources["source"] = "HikingSources"

# # --------------------------------------------------
# # Combine datasets
# # --------------------------------------------------

# df = pd.concat(
#     [news, facebook, tripadvisor, hikingsources],
#     ignore_index=True
# )

# print(f"Total records: {len(df)}")

# # --------------------------------------------------
# # Text cleaning
# # --------------------------------------------------

# def clean_text(text):

#     text = str(text)

#     text = re.sub(r"http\S+", "", text)

#     text = re.sub(r"[^a-zA-Z\s]", "", text)

#     text = text.lower()

#     words = text.split()

#     words = [
#         word
#         for word in words
#         if word not in STOP_WORDS
#     ]

#     return " ".join(words)

# df["clean_text"] = df["text"].apply(clean_text)

# print("Text cleaning completed")

# # --------------------------------------------------
# # Embeddings
# # --------------------------------------------------

# print("Loading embedding model...")

# embedding_model = SentenceTransformer(
#     "all-MiniLM-L6-v2"
# )

# # --------------------------------------------------
# # BERTopic
# # --------------------------------------------------

# print("Training BERTopic...")

# topic_model = BERTopic(
#     embedding_model=embedding_model,
#     calculate_probabilities=True,
#     min_topic_size=5,
#     verbose=True
# )

# topics, probs = topic_model.fit_transform(
#     df["clean_text"]
# )

# df["topic_id"] = topics

# # --------------------------------------------------
# # Topic probability
# # --------------------------------------------------

# topic_probs = []

# for p in probs:
#     topic_probs.append(np.max(p))

# df["topic_probability"] = topic_probs

# # --------------------------------------------------
# # Topic information
# # --------------------------------------------------

# info = topic_model.get_topic_info()

# print("\n========== TOPICS ==========")
# print(info)

# info.to_csv(
#     "outputs/topic_info.csv",
#     index=False
# )

# # --------------------------------------------------
# # Hazard Mapping
# # --------------------------------------------------

# topic_to_hazard = {
#     0: "Landslide",
#     1: "Dense Fog",
#     2: "Slippery Trail",
#     3: "Flood",
#     4: "Rockfall",
#     5: "Leopard Sighting",
#     6: "Monkey Sighting",
#     7: "Bugs/Wasp Activity",
#     8: "Heavy Wind",
#     -1: "Unknown"
# }

# df["hazard"] = df["topic_id"].map(topic_to_hazard)

# df["hazard"] = df["hazard"].fillna("Unclassified")

# # --------------------------------------------------
# # Reliability Scores
# # --------------------------------------------------

# SOURCE_RELIABILITY = {

#     "News": 0.95,

#     "Facebook": 0.65,

#     "TripAdvisor": 0.75,

#     "HikingSources": 0.85
# }

# df["reliability"] = df["source"].map(
#     SOURCE_RELIABILITY
# )

# # --------------------------------------------------
# # Hazard Score
# # --------------------------------------------------

# df["hazard_score"] = (
#     df["topic_probability"]
#     *
#     df["reliability"]
# )

# # --------------------------------------------------
# # Save Final Dataset
# # --------------------------------------------------

# df.to_csv(
#     "outputs/final_nlp_output.csv",
#     index=False
# )

# print("Final dataset saved")

# # --------------------------------------------------
# # Save Model
# # --------------------------------------------------

# topic_model.save(
#     "models/bertopic_model"
# )

# print("Model saved")

# # --------------------------------------------------
# # Visualization
# # --------------------------------------------------

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

#     print(
#         f"Visualization skipped: {e}"
#     )

# # --------------------------------------------------
# # Preview Results
# # --------------------------------------------------

# print("\n========== DATA SAMPLE ==========")

# print(
#     df[
#         [
#             "source",
#             "location",
#             "topic_id",
#             "hazard",
#             "hazard_score"
#         ]
#     ].head()
# )

# print("\nPipeline completed successfully.")


# bertopic_pipeline.py

from pathlib import Path
import re
import json
import logging

import numpy as np
import pandas as pd

from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from transformers import pipeline

from hazard_config import (
    HAZARD_CATEGORIES,
    ZERO_SHOT_THRESHOLD,
    ZERO_SHOT_MODEL,
    EMBEDDING_MODEL,
    CLASSIFICATION_BATCH_SIZE,
    MIN_TOPIC_SIZE,
)

# --------------------------------------------------
# 1. Paths and configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
OUTPUT_DIR = BASE_DIR / "outputs"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DATASETS = {
    "facebook": DATA_DIR / "facebook.xlsx",
    "news": DATA_DIR / "news.xlsx",
    "tripadvisor": DATA_DIR / "tripadvisor.xlsx",
    "hiking_sources": DATA_DIR / "hikingsources.xlsx",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


# --------------------------------------------------
# 2. Standardize Excel columns
# --------------------------------------------------

COLUMN_ALIASES = {
    "record_id": [
        "record_id", "record id", "id", "post_id",
        "review_id", "article_id", "source_id",
    ],
    "date": [
        "date", "published_date", "published date",
        "created_at", "created at", "timestamp",
        "event_date", "event date",
    ],
    "location": [
        "location", "place", "trail", "trail_name",
        "trail name", "destination", "region",
    ],
    "content": [
        "content", "text", "review", "comment",
        "description", "post", "article", "message",
        "review_text", "review text",
    ],
}


def normalize_column_name(value):
    """Normalize a column name for matching."""
    value = str(value).strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def find_column(columns, aliases):
    """Find a column by normalized name or common alias."""
    normalized = {
        normalize_column_name(col): col
        for col in columns
    }

    for alias in aliases:
        key = normalize_column_name(alias)
        if key in normalized:
            return normalized[key]

    return None


def load_one_dataset(source_name, file_path):
    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    df = pd.read_excel(file_path)

    if df.empty:
        logger.warning("%s dataset is empty.", source_name)
        return pd.DataFrame()

    id_col = find_column(
        df.columns, COLUMN_ALIASES["record_id"]
    )
    date_col = find_column(
        df.columns, COLUMN_ALIASES["date"]
    )
    location_col = find_column(
        df.columns, COLUMN_ALIASES["location"]
    )
    content_col = find_column(
        df.columns, COLUMN_ALIASES["content"]
    )

    if content_col is None:
        raise ValueError(
            f"No content/text column found in {file_path.name}.\n"
            f"Available columns: {list(df.columns)}\n"
            "Add your actual content column name to "
            "COLUMN_ALIASES['content']."
        )

    # Keep original values while creating a standard schema.
    result = pd.DataFrame({
        "record_id": (
            df[id_col].astype("string")
            if id_col else
            pd.Series(
                [f"{source_name}_{i}" for i in range(len(df))],
                index=df.index,
                dtype="string",
            )
        ),
        "date": (
            df[date_col] if date_col else pd.NaT
        ),
        "location": (
            df[location_col].astype("string")
            if location_col else pd.NA
        ),
        "content": df[content_col].astype("string"),
    })

    result["source"] = source_name
    result["source_file"] = file_path.name

    # Preserve the date as a parsed date when possible.
    result["date"] = pd.to_datetime(
        result["date"], errors="coerce", utc=True
    )

    # Missing content becomes empty text.
    result["content"] = result["content"].fillna("").str.strip()

    return result


def load_all_datasets():
    frames = []

    for source_name, file_path in DATASETS.items():
        logger.info("Loading %s", file_path.name)
        frame = load_one_dataset(source_name, file_path)
        logger.info("Loaded %s records", len(frame))
        frames.append(frame)

    data = pd.concat(frames, ignore_index=True)

    # Drop empty text.
    data = data[data["content"].str.len() > 0].copy()

    # Keep a cleaned representation for NLP.
    # Do not remove negation words such as "not" and "no".
    data["clean_text"] = (
        data["content"]
        .str.replace(r"https?://\S+|www\.\S+", " ", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # Remove exact duplicate text only for modelling.
    # Keep the full original dataset in the output for auditing.
    data["duplicate_text"] = (
        data["clean_text"].str.lower().str.strip()
    )

    data["is_duplicate_text"] = data.duplicated(
        subset=["duplicate_text"], keep="first"
    )

    logger.info("Total non-empty records: %d", len(data))
    logger.info(
        "Exact duplicate text records: %d",
        int(data["is_duplicate_text"].sum()),
    )

    return data.reset_index(drop=True)


# --------------------------------------------------
# 3. Zero-shot multi-label hazard classification
# --------------------------------------------------

def classify_hazards(data):
    """
    Score each report against all candidate categories.

    Scores are model confidence scores, not calibrated
    probabilities that a hazard will occur in real life.
    """
    logger.info("Loading zero-shot classifier: %s", ZERO_SHOT_MODEL)

    classifier = pipeline(
        task="zero-shot-classification",
        model=ZERO_SHOT_MODEL,
    )

    # Avoid classifying repeated identical text multiple times.
    unique_texts = data["duplicate_text"].drop_duplicates().tolist()

    predictions_by_text = {}

    for start in range(0, len(unique_texts), CLASSIFICATION_BATCH_SIZE):
        batch = unique_texts[
            start:start + CLASSIFICATION_BATCH_SIZE
        ]

        # The pipeline accepts a list of sequences.
        outputs = classifier(
            batch,
            candidate_labels=HAZARD_CATEGORIES,
            multi_label=True,
            hypothesis_template=(
                "This hiking-related text discusses {}."
            ),
        )

        if isinstance(outputs, dict):
            outputs = [outputs]

        for text, output in zip(batch, outputs):
            score_map = dict(
                zip(output["labels"], output["scores"])
            )

            # Keep scores for every candidate label.
            selected = [
                label
                for label in HAZARD_CATEGORIES
                if label != "no relevant hiking hazard"
                and score_map.get(label, 0.0) >= ZERO_SHOT_THRESHOLD
            ]

            # The no-hazard label is only a fallback when no
            # hazard category crosses the starting threshold.
            if not selected:
                selected = ["no relevant hiking hazard"]

            predictions_by_text[text] = {
                "hazard_labels": selected,
                "hazard_scores": score_map,
            }

        logger.info(
            "Classified %d / %d unique texts",
            min(start + len(batch), len(unique_texts)),
            len(unique_texts),
        )

    data["hazard_labels"] = data["duplicate_text"].map(
        lambda text: predictions_by_text[text]["hazard_labels"]
    )

    data["hazard_scores"] = data["duplicate_text"].map(
        lambda text: json.dumps(
            predictions_by_text[text]["hazard_scores"],
            ensure_ascii=False,
        )
    )

    data["hazard_labels"] = data["hazard_labels"].apply(
        lambda labels: "; ".join(labels)
    )

    return data


# --------------------------------------------------
# 4. BERTopic topic discovery
# --------------------------------------------------

def discover_topics(data):
    """
    Discover themes independently from hazard classification.

    Topic IDs are not hazard category IDs.
    """
    # Use unique text so duplicate posts do not dominate topic discovery.
    unique_rows = data.drop_duplicates(
        subset=["duplicate_text"]
    ).copy()

    documents = unique_rows["clean_text"].tolist()

    if len(documents) < 5:
        logger.warning(
            "Only %d unique documents. Topic discovery may be unreliable.",
            len(documents),
        )

    logger.info("Loading embedding model: %s", EMBEDDING_MODEL)
    embedding_model = SentenceTransformer(EMBEDDING_MODEL)

    embeddings = embedding_model.encode(
        documents,
        show_progress_bar=True,
        batch_size=32,
        normalize_embeddings=True,
    )

    topic_model = BERTopic(
        embedding_model=embedding_model,
        min_topic_size=MIN_TOPIC_SIZE,
        calculate_probabilities=False,
        verbose=True,
    )

    topics, _ = topic_model.fit_transform(
        documents,
        embeddings=embeddings,
    )

    unique_rows["topic_id"] = topics

    topic_info = topic_model.get_topic_info()

    topic_words = {}
    for topic_id in topic_info["Topic"].tolist():
        if topic_id == -1:
            topic_words[topic_id] = "Outlier / unassigned"
            continue

        words = topic_model.get_topic(topic_id) or []
        topic_words[topic_id] = ", ".join(
            word for word, _ in words[:8]
        )

    unique_rows["topic_keywords"] = unique_rows["topic_id"].map(
        topic_words
    )

    # Map discovered themes back to all records by exact text.
    topic_lookup = unique_rows.set_index(
        "duplicate_text"
    )[["topic_id", "topic_keywords"]]

    data = data.copy()
    data["topic_id"] = data["duplicate_text"].map(
        topic_lookup["topic_id"]
    )
    data["topic_keywords"] = data["duplicate_text"].map(
        topic_lookup["topic_keywords"]
    )

    # Save reusable model.
    topic_model.save(
        str(MODEL_DIR / "bertopic_hiking_model"),
        serialization="safetensors",
        save_ctfidf=True,
    )

    # Export topic summaries and HTML visualizations.
    topic_info.to_csv(
        OUTPUT_DIR / "topic_summary.csv",
        index=False,
    )

    try:
        topic_model.visualize_topics().write_html(
            str(OUTPUT_DIR / "topic_visualization.html")
        )
        topic_model.visualize_barchart().write_html(
            str(OUTPUT_DIR / "topic_barchart.html")
        )
    except Exception as exc:
        logger.warning("Could not generate topic charts: %s", exc)

    return data, topic_model


# --------------------------------------------------
# 5. Export results
# --------------------------------------------------

def export_results(data):
    output = data.copy()

    output["hazard_labels"] = output["hazard_labels"].fillna("")
    output["topic_keywords"] = output["topic_keywords"].fillna("")

    # Save the full processed dataset.
    output.to_csv(
        OUTPUT_DIR / "hazard_extraction_results.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # Human-readable table of report-level predictions.
    columns = [
        "record_id",
        "date",
        "location",
        "source",
        "content",
        "hazard_labels",
        "hazard_scores",
        "topic_id",
        "topic_keywords",
        "is_duplicate_text",
    ]

    output[columns].to_excel(
        OUTPUT_DIR / "hazard_extraction_results.xlsx",
        index=False,
    )

    logger.info(
        "Saved results to %s",
        OUTPUT_DIR / "hazard_extraction_results.csv",
    )


# --------------------------------------------------
# 6. Main entry point
# --------------------------------------------------

def main():
    data = load_all_datasets()

    if data.empty:
        raise ValueError("No usable text records were found.")

    data = classify_hazards(data)
    data, _ = discover_topics(data)
    export_results(data)

    logger.info("Pipeline completed successfully.")


if __name__ == "__main__":
    main()
