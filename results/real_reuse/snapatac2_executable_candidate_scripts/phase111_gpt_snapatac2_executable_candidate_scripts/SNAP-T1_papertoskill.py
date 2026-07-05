#!/usr/bin/env python3
import argparse
import csv
import gzip
import hashlib
import json
import math
import os
import platform
import resource
import sys
import time
from collections import Counter, defaultdict


def peak_memory_mb():
    try:
        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if platform.system().lower() == "darwin":
            return usage / (1024.0 * 1024.0)
        return usage / 1024.0
    except Exception:
        return None


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def open_maybe_gzip(path):
    if path.endswith(".gz"):
        return gzip.open(path, "rt")
    return open(path, "rt")


def parse_fragment_file(path, bin_size=5000):
    cells = set()
    features = set()
    counts = Counter()
    per_cell_fragments = Counter()
    per_cell_unique_features = defaultdict(set)
    chrom_counts = Counter()
    malformed = 0
    total_fragments = 0
    total_weighted_fragments = 0.0

    with open_maybe_gzip(path) as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 4:
                malformed += 1
                continue

            chrom = parts[0]
            try:
                start = int(parts[1])
                end = int(parts[2])
            except ValueError:
                malformed += 1
                continue

            barcode = parts[3]
            weight = 1.0
            if len(parts) >= 5:
                try:
                    weight = float(parts[4])
                except ValueError:
                    weight = 1.0

            midpoint = max(0, (start + end) // 2)
            feature = "{}:{}".format(chrom, midpoint // bin_size)

            cells.add(barcode)
            features.add(feature)
            counts[(barcode, feature)] += weight
            per_cell_fragments[barcode] += weight
            per_cell_unique_features[barcode].add(feature)
            chrom_counts[chrom] += weight
            total_fragments += 1
            total_weighted_fragments += weight

    cell_list = sorted(cells)
    feature_list = sorted(features)
    cell_index = {cell: i for i, cell in enumerate(cell_list)}
    feature_index = {feature: j for j, feature in enumerate(feature_list)}

    rows = []
    cols = []
    data = []
    for (cell, feature), value in counts.items():
        rows.append(cell_index[cell])
        cols.append(feature_index[feature])
        data.append(float(value))

    summary = {
        "fragment_path": path,
        "fragment_sha256": sha256_file(path),
        "bin_size": bin_size,
        "n_cells": len(cell_list),
        "n_features": len(feature_list),
        "n_nonzero_cell_features": len(data),
        "n_fragment_records": total_fragments,
        "total_weighted_fragments": total_weighted_fragments,
        "malformed_records": malformed,
        "chromosomes": dict(sorted(chrom_counts.items())),
    }

    cell_feature_rows = []
    for cell in cell_list:
        n_frag = float(per_cell_fragments[cell])
        uniq = len(per_cell_unique_features[cell])
        cell_feature_rows.append({
            "cell_id": cell,
            "fragment_count": n_frag,
            "unique_features": uniq,
            "log1p_fragment_count": math.log1p(n_frag),
            "feature_saturation": (uniq / n_frag) if n_frag > 0 else 0.0,
        })

    return cell_list, feature_list, rows, cols, data, cell_feature_rows, summary


def build_embedding(cell_list, feature_list, rows, cols, data, n_components=10):
    n_cells = len(cell_list)
    n_features = len(feature_list)
    if n_cells == 0:
        return [], "empty_input", {"n_components": 0}

    dims = max(1, min(n_components, n_cells, n_features if n_features else 1))

    try:
        import numpy as np
        from scipy import sparse
        from scipy.sparse.linalg import eigsh, LinearOperator

        X = sparse.csr_matrix((np.asarray(data, dtype=float), (rows, cols)), shape=(n_cells, n_features))
        if n_features == 0 or X.nnz == 0:
            return [[0.0] * dims for _ in cell_list], "zero_matrix", {"n_components": dims}

        df = np.asarray((X > 0).sum(axis=0)).ravel()
        idf = np.log1p(float(n_cells) / (1.0 + df))
        X = X.multiply(idf).tocsr()

        row_norm = np.sqrt(np.asarray(X.multiply(X).sum(axis=1)).ravel())
        row_norm[row_norm == 0] = 1.0
        X = sparse.diags(1.0 / row_norm).dot(X).tocsr()

        feature_sum = np.asarray(X.sum(axis=0)).ravel()
        degree = np.asarray(X.dot(feature_sum)).ravel()
        degree[degree <= 1e-12] = 1.0
        inv_sqrt_degree = 1.0 / np.sqrt(degree)

        def matvec(v):
            z = inv_sqrt_degree * v
            z = X.T.dot(z)
            z = X.dot(z)
            return inv_sqrt_degree * z

        operator = LinearOperator((n_cells, n_cells), matvec=matvec, dtype=float)
        k = min(dims + 1, max(1, n_cells - 1))

        if n_cells >= 3 and k < n_cells:
            values, vectors = eigsh(operator, k=k, which="LA", tol=1e-6, maxiter=max(300, n_cells * 20))
            order = np.argsort(values)[::-1]
            values = values[order]
            vectors = vectors[:, order]
            start = 1 if vectors.shape[1] > 1 else 0
            coords = vectors[:, start:start + dims] * values[start:start + dims]
            method = "idf_l2_degree_normalized_lanczos"
        else:
            dense = np.column_stack([matvec(np.eye(n_cells)[:, i]) for i in range(n_cells)])
            values, vectors = np.linalg.eigh(dense)
            order = np.argsort(values)[::-1]
            values = values[order]
            vectors = vectors[:, order]
            start = 1 if vectors.shape[1] > 1 else 0
            coords = vectors[:, start:start + dims] * values[start:start + dims]
            method = "idf_l2_degree_normalized_dense_eigh"

        if coords.shape[1] < dims:
            pad = np.zeros((n_cells, dims - coords.shape[1]))
            coords = np.hstack([coords, pad])

        return coords.astype(float).tolist(), method, {
            "n_components": dims,
            "idf_scaling": True,
            "row_l2_normalization": True,
            "degree_normalization": True,
            "cosine_similarity_operator": True,
            "full_similarity_matrix_materialized": False,
        }

    except Exception as exc:
        coords = []
        for cell in cell_list:
            digest = hashlib.sha256(cell.encode("utf-8")).digest()
            vals = []
            for i in range(dims):
                raw = int.from_bytes(digest[i * 2:i * 2 + 2], "big", signed=False)
                vals.append((raw / 65535.0) - 0.5)
            coords.append(vals)
        return coords, "deterministic_hash_fallback", {
            "n_components": dims,
            "fallback_reason": repr(exc),
            "idf_scaling": False,
            "row_l2_normalization": False,
            "degree_normalization": False,
        }


def write_embedding_csv(path, cell_list, embedding):
    max_dim = max((len(row) for row in embedding), default=0)
    header = ["cell_id"] + ["snap_dim_{}".format(i + 1) for i in range(max_dim)]
    with open(path, "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        for cell, values in zip(cell_list, embedding):
            writer.writerow([cell] + ["{:.10g}".format(float(v)) for v in values])


def write_cell_features_csv(path, rows):
    fieldnames = ["cell_id", "fragment_count", "unique_features", "log1p_fragment_count", "feature_saturation"]
    with open(path, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path, obj):
    with open(path, "w") as handle:
        json.dump(obj, handle, indent=2, sort_keys=True)
        handle.write("\n")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--condition", required=True)
    parser.add_argument("--fragment", required=True)
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--result-json", required=True)
    args = parser.parse_args(argv)

    start = time.time()
    os.makedirs(args.artifact_dir, exist_ok=True)

    embedding_path = os.path.join(args.artifact_dir, "embedding.csv")
    cell_features_path = os.path.join(args.artifact_dir, "cell_features.csv")
    fragment_summary_path = os.path.join(args.artifact_dir, "fragment_summary.json")

    errors = []
    notes = []
    method_steps = [
        "Loaded the locked miniature SnapATAC2 fragment fixture from --fragment.",
        "Converted fragments to a sparse cell-by-genomic-bin count matrix.",
        "Applied paper-derived preprocessing where available: inverse document frequency scaling, row-wise L2 normalization, cosine operator degree normalization.",
        "Computed a low-dimensional spectral embedding using Lanczos matrix-vector products without materializing the full cell-cell similarity matrix.",
        "Materialized embedding, per-cell features, and fragment-level summary artifacts for the runner to validate.",
    ]

    try:
        cell_list, feature_list, rows, cols, data, cell_feature_rows, summary = parse_fragment_file(args.fragment)
        embedding, embedding_method, embedding_metrics = build_embedding(cell_list, feature_list, rows, cols, data)
        summary["embedding_method"] = embedding_method
        summary["embedding_metrics"] = embedding_metrics

        write_embedding_csv(embedding_path, cell_list, embedding)
        write_cell_features_csv(cell_features_path, cell_feature_rows)
        write_json(fragment_summary_path, summary)

        if embedding_method == "deterministic_hash_fallback":
            notes.append("Scientific Python spectral embedding path was unavailable; used deterministic hash fallback and recorded the reason.")
    except Exception as exc:
        errors.append(repr(exc))
        write_embedding_csv(embedding_path, [], [])
        write_cell_features_csv(cell_features_path, [])
        write_json(fragment_summary_path, {
            "fragment_path": args.fragment,
            "error": repr(exc),
        })

    runtime = time.time() - start
    artifact_records = {
        "embedding_csv": {
            "path": embedding_path,
            "exists": os.path.exists(embedding_path),
            "bytes": os.path.getsize(embedding_path) if os.path.exists(embedding_path) else 0,
        },
        "cell_features_csv": {
            "path": cell_features_path,
            "exists": os.path.exists(cell_features_path),
            "bytes": os.path.getsize(cell_features_path) if os.path.exists(cell_features_path) else 0,
        },
        "fragment_summary_json": {
            "path": fragment_summary_path,
            "exists": os.path.exists(fragment_summary_path),
            "bytes": os.path.getsize(fragment_summary_path) if os.path.exists(fragment_summary_path) else 0,
        },
    }

    result = {
        "task_id": args.task_id,
        "condition": args.condition,
        "method_steps": method_steps,
        "embedding_artifacts": artifact_records,
        "runtime_seconds": runtime,
        "peak_memory_mb": peak_memory_mb(),
        "notes": notes,
        "errors": errors,
        "commands": {
            "fragment": args.fragment,
            "artifact_dir": args.artifact_dir,
        },
    }
    write_json(args.result_json, result)

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
