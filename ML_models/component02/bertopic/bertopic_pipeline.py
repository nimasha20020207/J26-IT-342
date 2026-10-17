


# from pathlib import Path
# import re
# import json
# import logging

# import numpy as np
# import pandas as pd

# from bertopic import BERTopic
# from sentence_transformers import SentenceTransformer
# from transformers import pipeline

# if __package__:
#     from .hazard_config import (
#         HAZARD_CATEGORIES,
#         ZERO_SHOT_THRESHOLD,
#         ZERO_SHOT_MODEL,
#         EMBEDDING_MODEL,
#         CLASSIFICATION_BATCH_SIZE,
#         MIN_TOPIC_SIZE,
#     )
# else:
#     from hazard_config import (
#         HAZARD_CATEGORIES,
#         ZERO_SHOT_THRESHOLD,
#         ZERO_SHOT_MODEL,
#         EMBEDDING_MODEL,
#         CLASSIFICATION_BATCH_SIZE,
#         MIN_TOPIC_SIZE,
#     )

# # --------------------------------------------------
# # 1. Paths and configuration
# # --------------------------------------------------

# BASE_DIR = Path(__file__).resolve().parent.parent
# DATA_DIR = BASE_DIR / "data"
# MODEL_DIR = BASE_DIR / "models"
# OUTPUT_DIR = BASE_DIR / "outputs"

# MODEL_DIR.mkdir(parents=True, exist_ok=True)
# OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# DATASETS = {
#     "facebook": DATA_DIR / "facebook.xlsx",
#     "news": DATA_DIR / "news.xlsx",
#     "tripadvisor": DATA_DIR / "tripadvisor.xlsx",
#     "hiking_sources": DATA_DIR / "hikingsources.xlsx",
# }

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s | %(levelname)s | %(message)s",
# )
# logger = logging.getLogger(__name__)


# # --------------------------------------------------
# # 2. Standardize Excel columns
# # --------------------------------------------------

# COLUMN_ALIASES = {
#     "record_id": [
#         "record_id", "record id", "id", "post_id",
#         "review_id", "article_id", "source_id",
#     ],
#     "date": [
#         "date", "published_date", "published date",
#         "created_at", "created at", "timestamp",
#         "event_date", "event date",
#     ],
#     "location": [
#         "location", "place", "trail", "trail_name",
#         "trail name", "destination", "region",
#     ],
#     "content": [
#         "content", "text", "review", "comment",
#         "description", "post", "article", "message",
#         "review_text", "review text",
#     ],
# }


# def normalize_column_name(value):
#     """Normalize a column name for matching."""
#     value = str(value).strip().lower()
#     value = re.sub(r"[^a-z0-9]+", "_", value)
#     return value.strip("_")


# def find_column(columns, aliases):
#     """Find a column by normalized name or common alias."""
#     normalized = {
#         normalize_column_name(col): col
#         for col in columns
#     }

#     for alias in aliases:
#         key = normalize_column_name(alias)
#         if key in normalized:
#             return normalized[key]

#     return None


# def load_one_dataset(source_name, file_path):
#     if not file_path.exists():
#         raise FileNotFoundError(
#             f"Dataset not found: {file_path}"
#         )

#     df = pd.read_excel(file_path)

#     if df.empty:
#         logger.warning("%s dataset is empty.", source_name)
#         return pd.DataFrame()

#     id_col = find_column(
#         df.columns, COLUMN_ALIASES["record_id"]
#     )
#     date_col = find_column(
#         df.columns, COLUMN_ALIASES["date"]
#     )
#     location_col = find_column(
#         df.columns, COLUMN_ALIASES["location"]
#     )
#     content_col = find_column(
#         df.columns, COLUMN_ALIASES["content"]
#     )

#     if content_col is None:
#         raise ValueError(
#             f"No content/text column found in {file_path.name}.\n"
#             f"Available columns: {list(df.columns)}\n"
#             "Add your actual content column name to "
#             "COLUMN_ALIASES['content']."
#         )

#     # Keep original values while creating a standard schema.
#     result = pd.DataFrame({
#         "record_id": (
#             df[id_col].astype("string")
#             if id_col else
#             pd.Series(
#                 [f"{source_name}_{i}" for i in range(len(df))],
#                 index=df.index,
#                 dtype="string",
#             )
#         ),
#         "date": (
#             df[date_col] if date_col else pd.NaT
#         ),
#         "location": (
#             df[location_col].astype("string")
#             if location_col else pd.NA
#         ),
#         "content": df[content_col].astype("string"),
#     })

#     result["source"] = source_name
#     result["source_file"] = file_path.name

#     # Preserve the date as a parsed date when possible.
#     result["date"] = pd.to_datetime(
#         result["date"], errors="coerce", utc=True
#     )

#     # Missing content becomes empty text.
#     result["content"] = result["content"].fillna("").str.strip()

#     return result


# def load_all_datasets():
#     frames = []

#     for source_name, file_path in DATASETS.items():
#         logger.info("Loading %s", file_path.name)
#         frame = load_one_dataset(source_name, file_path)
#         logger.info("Loaded %s records", len(frame))
#         frames.append(frame)

#     data = pd.concat(frames, ignore_index=True)

#     # Drop empty text.
#     data = data[data["content"].str.len() > 0].copy()

#     # Keep a cleaned representation for NLP.
#     # Do not remove negation words such as "not" and "no".
#     data["clean_text"] = (
#         data["content"]
#         .str.replace(r"https?://\S+|www\.\S+", " ", regex=True)
#         .str.replace(r"\s+", " ", regex=True)
#         .str.strip()
#     )

#     # Remove exact duplicate text only for modelling.
#     # Keep the full original dataset in the output for auditing.
#     data["duplicate_text"] = (
#         data["clean_text"].str.lower().str.strip()
#     )

#     data["is_duplicate_text"] = data.duplicated(
#         subset=["duplicate_text"], keep="first"
#     )

#     logger.info("Total non-empty records: %d", len(data))
#     logger.info(
#         "Exact duplicate text records: %d",
#         int(data["is_duplicate_text"].sum()),
#     )

#     return data.reset_index(drop=True)


# # --------------------------------------------------
# # 3. Zero-shot multi-label hazard classification
# # --------------------------------------------------

# def classify_hazards(data):
#     """
#     Score each report against all candidate categories.

#     Scores are model confidence scores, not calibrated
#     probabilities that a hazard will occur in real life.
#     """
#     logger.info("Loading zero-shot classifier: %s", ZERO_SHOT_MODEL)

#     classifier = pipeline(
#         task="zero-shot-classification",
#         model=ZERO_SHOT_MODEL,
#     )

#     # Avoid classifying repeated identical text multiple times.
#     unique_texts = data["duplicate_text"].drop_duplicates().tolist()

#     predictions_by_text = {}

#     for start in range(0, len(unique_texts), CLASSIFICATION_BATCH_SIZE):
#         batch = unique_texts[
#             start:start + CLASSIFICATION_BATCH_SIZE
#         ]

#         # The pipeline accepts a list of sequences.
#         outputs = classifier(
#             batch,
#             candidate_labels=HAZARD_CATEGORIES,
#             multi_label=True,
#             hypothesis_template=(
#                 "This hiking-related text discusses {}."
#             ),
#         )

#         if isinstance(outputs, dict):
#             outputs = [outputs]

#         for text, output in zip(batch, outputs):
#             score_map = dict(
#                 zip(output["labels"], output["scores"])
#             )

#             # Keep scores for every candidate label.
#             selected = [
#                 label
#                 for label in HAZARD_CATEGORIES
#                 if label != "no relevant hiking hazard"
#                 and score_map.get(label, 0.0) >= ZERO_SHOT_THRESHOLD
#             ]

#             # The no-hazard label is only a fallback when no
#             # hazard category crosses the starting threshold.
#             if not selected:
#                 selected = ["no relevant hiking hazard"]

#             predictions_by_text[text] = {
#                 "hazard_labels": selected,
#                 "hazard_scores": score_map,
#             }

#         logger.info(
#             "Classified %d / %d unique texts",
#             min(start + len(batch), len(unique_texts)),
#             len(unique_texts),
#         )

#     data["hazard_labels"] = data["duplicate_text"].map(
#         lambda text: predictions_by_text[text]["hazard_labels"]
#     )

#     data["hazard_scores"] = data["duplicate_text"].map(
#         lambda text: json.dumps(
#             predictions_by_text[text]["hazard_scores"],
#             ensure_ascii=False,
#         )
#     )

#     data["hazard_labels"] = data["hazard_labels"].apply(
#         lambda labels: "; ".join(labels)
#     )

#     return data


# # --------------------------------------------------
# # 4. BERTopic topic discovery
# # --------------------------------------------------

# def discover_topics(data):
#     """
#     Discover themes independently from hazard classification.

#     Topic IDs are not hazard category IDs.
#     """
#     # Use unique text so duplicate posts do not dominate topic discovery.
#     unique_rows = data.drop_duplicates(
#         subset=["duplicate_text"]
#     ).copy()

#     documents = unique_rows["clean_text"].tolist()

#     if len(documents) < 5:
#         logger.warning(
#             "Only %d unique documents. Topic discovery may be unreliable.",
#             len(documents),
#         )

#     logger.info("Loading embedding model: %s", EMBEDDING_MODEL)
#     embedding_model = SentenceTransformer(EMBEDDING_MODEL)

#     embeddings = embedding_model.encode(
#         documents,
#         show_progress_bar=True,
#         batch_size=32,
#         normalize_embeddings=True,
#     )

#     topic_model = BERTopic(
#         embedding_model=embedding_model,
#         min_topic_size=MIN_TOPIC_SIZE,
#         calculate_probabilities=False,
#         verbose=True,
#     )

#     topics, _ = topic_model.fit_transform(
#         documents,
#         embeddings=embeddings,
#     )

#     unique_rows["topic_id"] = topics

#     topic_info = topic_model.get_topic_info()

#     topic_words = {}
#     for topic_id in topic_info["Topic"].tolist():
#         if topic_id == -1:
#             topic_words[topic_id] = "Outlier / unassigned"
#             continue

#         words = topic_model.get_topic(topic_id) or []
#         topic_words[topic_id] = ", ".join(
#             word for word, _ in words[:8]
#         )

#     unique_rows["topic_keywords"] = unique_rows["topic_id"].map(
#         topic_words
#     )

#     # Map discovered themes back to all records by exact text.
#     topic_lookup = unique_rows.set_index(
#         "duplicate_text"
#     )[["topic_id", "topic_keywords"]]

#     data = data.copy()
#     data["topic_id"] = data["duplicate_text"].map(
#         topic_lookup["topic_id"]
#     )
#     data["topic_keywords"] = data["duplicate_text"].map(
#         topic_lookup["topic_keywords"]
#     )

#     # Save reusable model.
#     topic_model.save(
#         str(MODEL_DIR / "bertopic_hiking_model"),
#         serialization="safetensors",
#         save_ctfidf=True,
#     )

#     # Export topic summaries and HTML visualizations.
#     topic_info.to_csv(
#         OUTPUT_DIR / "topic_summary.csv",
#         index=False,
#     )

#     try:
#         topic_model.visualize_topics().write_html(
#             str(OUTPUT_DIR / "topic_visualization.html")
#         )
#         topic_model.visualize_barchart().write_html(
#             str(OUTPUT_DIR / "topic_barchart.html")
#         )
#     except Exception as exc:
#         logger.warning("Could not generate topic charts: %s", exc)

#     return data, topic_model


# # --------------------------------------------------
# # 5. Export results
# # --------------------------------------------------

# def export_results(data):
#     output = data.copy()

#     output["hazard_labels"] = output["hazard_labels"].fillna("")
#     output["topic_keywords"] = output["topic_keywords"].fillna("")

#     # Save the full processed dataset.
#     output.to_csv(
#         OUTPUT_DIR / "hazard_extraction_results.csv",
#         index=False,
#         encoding="utf-8-sig",
#     )

#     # Human-readable table of report-level predictions.
#     columns = [
#         "record_id",
#         "date",
#         "location",
#         "source",
#         "content",
#         "hazard_labels",
#         "hazard_scores",
#         "topic_id",
#         "topic_keywords",
#         "is_duplicate_text",
#     ]

#     output[columns].to_excel(
#         OUTPUT_DIR / "hazard_extraction_results.xlsx",
#         index=False,
#     )

#     logger.info(
#         "Saved results to %s",
#         OUTPUT_DIR / "hazard_extraction_results.csv",
#     )


# # --------------------------------------------------
# # 6. Main entry point
# # --------------------------------------------------

# def main():
#     data = load_all_datasets()

#     if data.empty:
#         raise ValueError("No usable text records were found.")

#     data = classify_hazards(data)
#     data, _ = discover_topics(data)
#     export_results(data)

#     logger.info("Pipeline completed successfully.")


# if __name__ == "__main__":
#     main()


from pathlib import Path
import re
import json
import logging

import pandas as pd
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from transformers import pipeline

if __package__:
    from .hazard_config import (
        HAZARD_CATEGORIES,
        ZERO_SHOT_THRESHOLD,
        ZERO_SHOT_MODEL,
        EMBEDDING_MODEL,
        CLASSIFICATION_BATCH_SIZE,
        MIN_TOPIC_SIZE,
    )
else:
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

BASE_DIR = Path(__file__).resolve().parent.parent
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
# 2. Keyword dictionary
# --------------------------------------------------
# These rules catch explicit words and common phrases. Expand them
# using the terminology found in your actual Sri Lankan hiking data.
#
# Keyword matching is evidence of a mention, not proof that a hazard
# occurred. In particular, the word "leech" alone does not prove that
# leech activity was high.

HAZARD_KEYWORDS = {
    "landslides": [
        r"\blandslides?\b",
        r"\bslope failure\b",
        r"\bland slips?\b",
        r"\bearth slips?\b",
    ],
    "rockfalls": [
        r"\brockfalls?\b",
        r"\bfalling rocks?\b",
        r"\brocks? fell\b",
        r"\brocks? falling\b",
    ],
    "slippery or muddy trails": [
        r"\bslippery\b",
        r"\bmuddy\b",
        r"\bmud(?:dy)? trails?\b",
        r"\bslippery trails?\b",
        r"\bslippery path\b",
        r"\bslippery rocks?\b",
    ],
    "dense fog or poor visibility": [
        r"\bdense fog\b",
        r"\bheavy fog\b",
        r"\bthick fog\b",
        r"\bfoggy\b",
        r"\bpoor visibility\b",
        r"\blow visibility\b",
        r"\bmisty\b",
    ],
    "high leech activity": [
        r"\bleeches\b",
        r"\bleech\b",
        r"\bleech activity\b",
        r"\bleeches everywhere\b",
        r"\bcovered in leeches\b",
        r"\blots of leeches\b",
        r"\bmany leeches\b",
    ],
    "leopard sightings": [
        r"\bleopards?\b",
    ],
    "monkey sightings": [
        r"\bmonkeys?\b",
    ],
    "bugs or wasps activity": [
        r"\bbugs?\b",
        r"\binsects?\b",
        r"\bwasps?\b",
        r"\bhornets?\b",
        r"\bbees?\b",
    ],
    "heavy rain": [
        r"\bheavy rain(?:fall)?\b",
        r"\btorrential rain\b",
        r"\bdownpours?\b",
        r"\bpouring rain\b",
        r"\bintense rain\b",
        r"\bvery heavy rain\b",
    ],
    "strong winds": [
        r"\bstrong winds?\b",
        r"\bhigh winds?\b",
        r"\bgusty winds?\b",
        r"\bpowerful winds?\b",
        r"\bwindy conditions\b",
    ],
    "trail obstructions": [
        r"\bblocked trails?\b",
        r"\btrail obstructions?\b",
        r"\bfallen trees?\b",
        r"\bfallen branches\b",
        r"\btrees? blocking (?:the )?(?:trail|path)\b",
        r"\bbranches blocking (?:the )?(?:trail|path)\b",
        r"\bblocked paths?\b",
        r"\bpath obstructed\b",
        r"\btrail obstructed\b",
        r"\bpath is blocked\b",
    ],
}

# Sentence boundaries used for a basic negation check. This is not a
# full linguistic negation model, but is safer than checking the whole
# report for "no" or "not".
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?;\n])\s+")

NEGATION_PATTERNS = [
    r"\bno\b",
    r"\bnot\b",
    r"\bnever\b",
    r"\bwithout\b",
    r"\bnone\b",
    r"\bneither\b",
    r"\bdid not\b",
    r"\bdidn't\b",
    r"\bwas not\b",
    r"\bwasn't\b",
    r"\bwere not\b",
    r"\bweren't\b",
    r"\bhas not been\b",
    r"\bhave not been\b",
    r"\bno signs of\b",
    r"\bno evidence of\b",
    r"\bnot seen\b",
    r"\bnot spotted\b",
]
NEGATION_RE = re.compile("|".join(NEGATION_PATTERNS), re.IGNORECASE)


def _mention_is_negated(sentence, match_start, match_end):
    """Conservatively detect common negation near a keyword mention."""
    before = sentence[max(0, match_start - 65):match_start]
    after = sentence[match_end:min(len(sentence), match_end + 45)]

    # Common forms before the mention: "no monkeys", "no signs of leopards".
    if NEGATION_RE.search(before):
        return True

    # Common forms after the mention: "monkeys were not seen".
    after_negation = re.search(
        r"^\s*(?:was|were|is|are|has been|have been)?\s*"
        r"(?:not seen|not spotted|absent|not present|never seen|"
        r"were not seen|was not seen|were not spotted|was not spotted)\b",
        after,
        flags=re.IGNORECASE,
    )
    if after_negation:
        return True

    return False


def find_keyword_hazards(text):
    """
    Return hazard labels with explicit, apparently non-negated mentions.

    This is a rule-based assist to zero-shot classification, not a
    substitute for reviewing ambiguous reports.
    """
    text = str(text or "")
    matched_hazards = []

    for hazard, patterns in HAZARD_KEYWORDS.items():
        found = False

        for sentence in SENTENCE_SPLIT_RE.split(text):
            for pattern in patterns:
                for match in re.finditer(pattern, sentence, flags=re.IGNORECASE):
                    if not _mention_is_negated(
                        sentence, match.start(), match.end()
                    ):
                        matched_hazards.append(hazard)
                        found = True
                        break
                if found:
                    break
            if found:
                break

    # Preserve order while removing duplicates.
    return list(dict.fromkeys(matched_hazards))


# --------------------------------------------------
# 3. Standardize Excel columns
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
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    df = pd.read_excel(file_path)

    if df.empty:
        logger.warning("%s dataset is empty.", source_name)
        return pd.DataFrame()

    id_col = find_column(df.columns, COLUMN_ALIASES["record_id"])
    date_col = find_column(df.columns, COLUMN_ALIASES["date"])
    location_col = find_column(df.columns, COLUMN_ALIASES["location"])
    content_col = find_column(df.columns, COLUMN_ALIASES["content"])

    if content_col is None:
        raise ValueError(
            f"No content/text column found in {file_path.name}.\n"
            f"Available columns: {list(df.columns)}\n"
            "Add your actual content column name to "
            "COLUMN_ALIASES['content']."
        )

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
        "date": df[date_col] if date_col else pd.NaT,
        "location": (
            df[location_col].astype("string")
            if location_col else pd.NA
        ),
        "content": df[content_col].astype("string"),
    })

    result["source"] = source_name
    result["source_file"] = file_path.name
    result["date"] = pd.to_datetime(
        result["date"], errors="coerce", utc=True
    )
    result["content"] = result["content"].fillna("").str.strip()
    return result


def load_all_datasets():
    frames = []

    for source_name, file_path in DATASETS.items():
        logger.info("Loading %s", file_path.name)
        frame = load_one_dataset(source_name, file_path)
        logger.info("Loaded %d records from %s", len(frame), file_path.name)
        frames.append(frame)

    if not frames:
        raise ValueError("No datasets are configured.")

    data = pd.concat(frames, ignore_index=True)
    data = data[data["content"].str.len() > 0].copy()

    # Remove URLs and repeated whitespace, but retain negation words.
    data["clean_text"] = (
        data["content"]
        .str.replace(r"https?://\S+|www\.\S+", " ", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    data["duplicate_text"] = data["clean_text"].str.lower().str.strip()
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
# 4. Hybrid hazard classification
# --------------------------------------------------

def classify_hazards(data):
    """
    Combine zero-shot scores and explicit keyword matches.

    Zero-shot scores are model scores, not calibrated probabilities.
    Keyword matches are retained separately for audit and review.
    """
    logger.info("Loading zero-shot classifier: %s", ZERO_SHOT_MODEL)
    classifier = pipeline(
        task="zero-shot-classification",
        model=ZERO_SHOT_MODEL,
    )

    # Avoid repeating model inference for identical text.
    unique_texts = data["duplicate_text"].drop_duplicates().tolist()
    predictions_by_text = {}

    candidate_labels = list(HAZARD_CATEGORIES)

    for start in range(0, len(unique_texts), CLASSIFICATION_BATCH_SIZE):
        batch = unique_texts[start:start + CLASSIFICATION_BATCH_SIZE]

        outputs = classifier(
            batch,
            candidate_labels=candidate_labels,
            multi_label=True,
            hypothesis_template=(
                "This hiking-related report mentions or describes {}."
            ),
        )

        if isinstance(outputs, dict):
            outputs = [outputs]

        for text, output in zip(batch, outputs):
            score_map = dict(zip(output["labels"], output["scores"]))

            # Keep labels that pass the model threshold, excluding the
            # fallback label from normal hazard selection.
            model_labels = [
                label for label in HAZARD_CATEGORIES
                if label != "no relevant hiking hazard"
                and score_map.get(label, 0.0) >= ZERO_SHOT_THRESHOLD
            ]

            # Match keywords against the report text itself.
            keyword_labels = find_keyword_hazards(text)

            # Union the two methods, preserving configured category order.
            selected_set = set(model_labels) | set(keyword_labels)
            selected = [
                label for label in HAZARD_CATEGORIES
                if label != "no relevant hiking hazard"
                and label in selected_set
            ]

            if not selected:
                selected = ["no relevant hiking hazard"]

            predictions_by_text[text] = {
                "hazard_labels": selected,
                "hazard_scores": score_map,
                "keyword_labels": keyword_labels,
                "model_labels": model_labels,
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
    data["keyword_labels"] = data["duplicate_text"].map(
        lambda text: "; ".join(
            predictions_by_text[text]["keyword_labels"]
        )
    )
    data["model_labels"] = data["duplicate_text"].map(
        lambda text: "; ".join(
            predictions_by_text[text]["model_labels"]
        )
    )

    data["hazard_labels"] = data["hazard_labels"].apply(
        lambda labels: "; ".join(labels)
    )
    return data


# --------------------------------------------------
# 5. BERTopic topic discovery
# --------------------------------------------------

def discover_topics(data):
    """Discover themes independently from hazard classification."""
    unique_rows = data.drop_duplicates(subset=["duplicate_text"]).copy()
    documents = unique_rows["clean_text"].tolist()

    if len(documents) == 0:
        raise ValueError("No documents are available for topic discovery.")

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

    unique_rows["topic_keywords"] = unique_rows["topic_id"].map(topic_words)

    topic_lookup = unique_rows.set_index("duplicate_text")[
        ["topic_id", "topic_keywords"]
    ]

    data = data.copy()
    data["topic_id"] = data["duplicate_text"].map(topic_lookup["topic_id"])
    data["topic_keywords"] = data["duplicate_text"].map(
        topic_lookup["topic_keywords"]
    )

    # Save the trained topic model and topic summaries.
    topic_model.save(
        str(MODEL_DIR / "bertopic_hiking_model"),
        serialization="safetensors",
        save_ctfidf=True,
    )
    topic_info.to_csv(OUTPUT_DIR / "topic_summary.csv", index=False)

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
# 6. Export results
# --------------------------------------------------

def export_results(data):
    output = data.copy()

    for column in [
        "hazard_labels", "hazard_scores", "keyword_labels",
        "model_labels", "topic_keywords",
    ]:
        if column in output.columns:
            output[column] = output[column].fillna("")

    csv_path = OUTPUT_DIR / "hazard_extraction_results.csv"
    xlsx_path = OUTPUT_DIR / "hazard_extraction_results.xlsx"

    output.to_csv(csv_path, index=False, encoding="utf-8-sig")

    columns = [
        "record_id",
        "date",
        "location",
        "source",
        "content",
        "hazard_labels",
        "keyword_labels",
        "model_labels",
        "hazard_scores",
        "topic_id",
        "topic_keywords",
        "is_duplicate_text",
    ]
    # Export only columns that exist, to avoid errors if a schema changes.
    output[[col for col in columns if col in output.columns]].to_excel(
        xlsx_path, index=False
    )

    logger.info("Saved CSV results to %s", csv_path)
    logger.info("Saved Excel results to %s", xlsx_path)


# --------------------------------------------------
# 7. Optional keyword sanity check
# --------------------------------------------------

def run_keyword_sanity_check():
    """Quick smoke test; this does not measure model accuracy."""
    examples = [
        "A monkey was seen near the hiking trail.",
        "A leopard crossed the path.",
        "There were leeches everywhere.",
        "Heavy rain made the trail muddy.",
        "Strong winds and fallen trees blocked the path.",
        "No monkeys were seen during the hike.",
    ]

    logger.info("Running keyword sanity check")
    for report in examples:
        logger.info(
            "Report: %s | Keyword labels: %s",
            report,
            find_keyword_hazards(report),
        )


# --------------------------------------------------
# 8. Main entry point
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
