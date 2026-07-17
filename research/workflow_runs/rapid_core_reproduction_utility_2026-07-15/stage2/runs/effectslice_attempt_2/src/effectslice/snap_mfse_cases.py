from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


BLOCK_SIZES = {
    "development": 4,
    "eligibility": 21,
    "discovery": 16,
    "confirmation": 59,
    "confirmation_v2": 64,
}

BLOCK_SEED_BASES = {
    "development": 10_000,
    "eligibility": 20_000,
    "discovery": 30_000,
    "confirmation": 40_000,
    "confirmation_v2": 50_000,
}


def _validated_counts(counts: np.ndarray, n_components: int) -> np.ndarray:
    matrix = np.asarray(counts, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] < 3 or matrix.shape[1] < 2:
        raise ValueError("counts must be a two-dimensional cell-by-feature matrix")
    if not np.isfinite(matrix).all():
        raise ValueError("counts must be finite")
    if np.any(matrix < 0):
        raise ValueError("counts must be nonnegative")
    if (
        isinstance(n_components, bool)
        or not isinstance(n_components, (int, np.integer))
        or n_components < 1
        or n_components >= matrix.shape[0]
    ):
        raise ValueError("n_components must be between one and n_cells - 1")
    if np.any(np.linalg.norm(matrix, axis=1) == 0):
        raise ValueError("counts cannot contain an all-zero cell row")
    return matrix


def _paper_matrix(counts: np.ndarray, n_components: int) -> tuple[np.ndarray, np.ndarray]:
    matrix = _validated_counts(counts, n_components)
    n_cells = matrix.shape[0]
    document_frequency = np.count_nonzero(matrix, axis=0)
    idf = np.log(n_cells / (1.0 + document_frequency))
    x = matrix * idf
    row_norms = np.linalg.norm(x, axis=1)
    if np.any(row_norms <= 0) or not np.isfinite(row_norms).all():
        raise ValueError("paper IDF scaling produced a non-normalizable row")
    x = x / row_norms[:, None]
    degree = x @ (x.T @ np.ones(n_cells, dtype=np.float64)) - np.ones(
        n_cells, dtype=np.float64
    )
    if np.any(degree <= 0) or not np.isfinite(degree).all():
        raise ValueError("paper similarity graph has a nonpositive degree")
    x_tilde = x / np.sqrt(degree)[:, None]
    normalized_similarity = x_tilde @ x_tilde.T - np.diag(1.0 / degree)
    return normalized_similarity, degree


def paper_reference_embedding(
    counts: np.ndarray,
    n_components: int,
) -> tuple[np.ndarray, np.ndarray]:
    normalized_similarity, _ = _paper_matrix(counts, n_components)
    values, vectors = np.linalg.eigh(normalized_similarity)
    order = np.argsort(values)[::-1][:n_components]
    return values[order], vectors[:, order]


def compare_embedding(
    counts: np.ndarray,
    candidate_values: np.ndarray,
    candidate_vectors: np.ndarray,
    *,
    expected_values: np.ndarray,
    expected_vectors: np.ndarray,
    eigenvalue_atol: float = 1e-6,
    projector_atol: float = 1e-5,
) -> dict[str, Any]:
    matrix = np.asarray(counts, dtype=np.float64)
    values = np.asarray(candidate_values, dtype=np.float64)
    vectors = np.asarray(candidate_vectors, dtype=np.float64)
    reference_values = np.asarray(expected_values, dtype=np.float64)
    reference_vectors = np.asarray(expected_vectors, dtype=np.float64)
    expected_shape = (matrix.shape[0], reference_values.shape[0])
    shape_ok = values.shape == reference_values.shape and vectors.shape == expected_shape
    finite = bool(np.isfinite(values).all() and np.isfinite(vectors).all())
    if not shape_ok or not finite:
        return {
            "passed": False,
            "shape_ok": shape_ok,
            "finite": finite,
            "eigenvalues_ok": False,
            "eigenvalue_error": None,
            "projector_ok": False,
            "projector_error": None,
        }
    eigenvalue_error = float(np.max(np.abs(values - reference_values)))
    eigenvalues_ok = bool(
        np.allclose(values, reference_values, rtol=0.0, atol=eigenvalue_atol)
        and np.all(values[:-1] >= values[1:] - eigenvalue_atol)
    )
    candidate_basis, _ = np.linalg.qr(vectors)
    reference_basis, _ = np.linalg.qr(reference_vectors)
    candidate_projector = candidate_basis @ candidate_basis.T
    reference_projector = reference_basis @ reference_basis.T
    projector_error = float(
        np.linalg.norm(candidate_projector - reference_projector, ord="fro")
        / math.sqrt(reference_values.shape[0])
    )
    projector_ok = projector_error <= projector_atol
    return {
        "passed": bool(shape_ok and finite and eigenvalues_ok and projector_ok),
        "shape_ok": shape_ok,
        "finite": finite,
        "eigenvalues_ok": eigenvalues_ok,
        "eigenvalue_error": eigenvalue_error,
        "projector_ok": projector_ok,
        "projector_error": projector_error,
    }


def generate_case(case: dict[str, Any]) -> np.ndarray:
    required = {
        "seed",
        "n_cells",
        "n_features",
        "n_components",
        "cluster_count",
    }
    if not required.issubset(case):
        raise ValueError("case specification is incomplete")
    seed = int(case["seed"])
    n_cells = int(case["n_cells"])
    n_features = int(case["n_features"])
    cluster_count = int(case["cluster_count"])
    if n_cells < 6 or n_features < cluster_count * 3 or cluster_count < 2:
        raise ValueError("case dimensions are invalid")
    rng = np.random.default_rng(seed)
    labels = np.arange(n_cells, dtype=int) % cluster_count
    rng.shuffle(labels)
    counts = rng.binomial(1, 0.12, size=(n_cells, n_features)).astype(np.float64)
    marker_width = max(3, n_features // (cluster_count * 2))
    for row_index, label in enumerate(labels):
        start = label * marker_width
        end = min(start + marker_width, n_features)
        counts[row_index, start:end] += rng.integers(1, 4, size=end - start)
        counts[row_index, -1] += 1.0
    return np.ascontiguousarray(counts, dtype=np.float64)


def _case_spec(block: str, index: int) -> dict[str, Any]:
    seed = BLOCK_SEED_BASES[block] + index
    cluster_count = 2 + (index % 3)
    n_cells = 10 + 2 * (index % 5)
    n_features = 18 + 2 * (index % 7)
    n_components = 2 + (index % 2)
    case = {
        "case_id": f"snap-mfse:{block}:{index + 1:03d}",
        "seed": seed,
        "n_cells": n_cells,
        "n_features": n_features,
        "n_components": n_components,
        "cluster_count": cluster_count,
    }
    counts = generate_case(case)
    paper_reference_embedding(counts, n_components)
    case["counts_sha256"] = hashlib.sha256(counts.tobytes()).hexdigest()
    return case


def build_case_registry(output_path: Path) -> dict[str, Any]:
    blocks = {
        block: [_case_spec(block, index) for index in range(size)]
        for block, size in BLOCK_SIZES.items()
    }
    payload: dict[str, Any] = {
        "schema_version": "effectslice-snap-mfse-case-registry.v1",
        "generator": "numpy.default_rng.clustered_counts.v1",
        "paper_equation": "idf=log(n/(1+df)); W_tilde matvec is X_tilde(X_tilde^T v)-D^-1 v",
        "blocks": blocks,
        "evidence_boundary": (
            "Frozen numerical case registry. Development, eligibility, discovery, and "
            "confirmation blocks are disjoint and are not model-visible."
        ),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    payload["registry_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    path = Path(output_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return payload
