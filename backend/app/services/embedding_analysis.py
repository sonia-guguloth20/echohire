"""
Feedback Embedding Analysis.

Question this answers: "Does written feedback on rejected candidates cluster
differently, in semantically meaningful ways, from feedback on accepted
candidates - and does that clustering correlate with a protected attribute?"

Approach:
  1. Embed all feedback text with a sentence-transformer (all-MiniLM-L6-v2 -
     small, fast, good enough for this; upgrade to a larger model later).
  2. Reduce dimensionality and cluster (KMeans) purely on the text.
  3. Cross-tabulate cluster assignment against outcome AND against the
     protected attribute. If rejected-candidate feedback disproportionately
     lands in a cluster that also skews heavily toward one gender/age group,
     that's a signal worth a human looking at feedback *language* patterns,
     not just outcome numbers - e.g. "assertive" praised in one group's
     feedback but "abrasive" for the same behavior in another's.

This is a screening signal, not proof on its own - always report it
alongside the Fisher/logistic results, never in isolation.
"""

from dataclasses import dataclass

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# Loaded lazily - this import is slow (~1-2s) and pulls model weights,
# so we don't want it to happen at module import time in every request.
_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    model = _get_model()
    return model.encode(texts, show_progress_bar=False)


@dataclass
class ClusterSkewResult:
    cluster_id: int
    size: int
    reject_rate: float
    dominant_attribute_value: str
    dominant_attribute_share: float  # e.g. 0.82 means 82% of this cluster is one group


def analyze_feedback_clusters(
    feedback_texts: list[str],
    outcomes: list[str],
    attribute_values: list[str],
    n_clusters: int = 4,
) -> dict:
    if len(feedback_texts) < n_clusters * 5:
        return {
            "warning": f"Need at least {n_clusters * 5} feedback entries for meaningful clustering; got {len(feedback_texts)}.",
            "clusters": [],
        }

    embeddings = embed_texts(feedback_texts)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(embeddings)

    try:
        sil_score = float(silhouette_score(embeddings, labels))
    except Exception:
        sil_score = None

    results = []
    for cluster_id in range(n_clusters):
        idx = [i for i, l in enumerate(labels) if l == cluster_id]
        if not idx:
            continue
        cluster_outcomes = [outcomes[i] for i in idx]
        cluster_attrs = [attribute_values[i] for i in idx]

        reject_rate = cluster_outcomes.count("rejected") / len(cluster_outcomes)

        attr_counts: dict[str, int] = {}
        for a in cluster_attrs:
            attr_counts[a] = attr_counts.get(a, 0) + 1
        dominant_value, dominant_count = max(attr_counts.items(), key=lambda kv: kv[1])

        results.append(
            ClusterSkewResult(
                cluster_id=cluster_id,
                size=len(idx),
                reject_rate=round(reject_rate, 3),
                dominant_attribute_value=dominant_value,
                dominant_attribute_share=round(dominant_count / len(idx), 3),
            )
        )

    return {
        "silhouette_score": sil_score,
        "clusters": [r.__dict__ for r in results],
        "interpretation_note": (
            "A cluster with both a high reject_rate AND a high dominant_attribute_share "
            "means rejected feedback for that semantic pattern is concentrated in one group. "
            "Pull sample feedback text from that cluster to see what language is driving it."
        ),
    }
