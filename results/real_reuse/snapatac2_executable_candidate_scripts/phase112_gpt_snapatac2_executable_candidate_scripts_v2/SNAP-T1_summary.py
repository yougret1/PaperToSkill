#!/usr/bin/env python3
import argparse
import csv
import gzip
import hashlib
import json
import math
import os
import sys
import time
import tracemalloc
from collections import Counter, defaultdict


BIN_SIZE = 50000


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def open_maybe_gzip(path):
    with open(path, "rb") as fh:
        magic = fh.read(2)
    if magic == b"\x1f\x8b":
        return gzip.open(path, "rt", encoding="utf-8", newline="")
    return open(path, "rt", encoding="utf-8", newline="")


def parse_fragment_line(line):
    parts = line.rstrip("\n").split("\t")
    if len(parts) < 4:
        return None

    chrom = parts[0]
    try:
        start = int(parts[1])
        end = int(parts[2])
    except ValueError:
        return None

    if start < 0 or end < start:
        return None

    # SnapATAC2 fragment files are usually chrom, start, end, barcode, count.
    # Some fixtures can include extra columns; barcode remains the fourth field.
    barcode = parts[3].strip()
    if not barcode:
        barcode = "unknown_cell"

    count = 1
    if len(parts) >= 5:
        try:
            count = max(1, int(float(parts[4])))
        except ValueError:
            count = 1

    return chrom, start, end, barcode, count


def load_fragment_features(fragment_path):
    cell_total = Counter()
    cell_bp = Counter()
    cell_chroms = defaultdict(set)
    cell_bins = defaultdict(Counter)
    chrom_counts = Counter()
    bin_document_frequency = Counter()

    total_rows = 0
    parsed_rows = 0
    total_weighted_fragments = 0
    min_start = None
    max_end = None

    with open_maybe_gzip(fragment_path) as fh:
        for line in fh:
            if not line.strip() or line.startswith("#"):
                continue
            total_rows += 1
            parsed = parse_fragment_line(line)
            if parsed is None:
                continue

            chrom, start, end, barcode, count = parsed
            parsed_rows += 1
            total_weighted_fragments += count
            frag_len = max(0, end - start)
            bin_id = "{}:{}".format(chrom, start // BIN_SIZE)

            cell_total[barcode] += count
            cell_bp[barcode] += frag_len * count
            cell_chroms[barcode].add(chrom)
            cell_bins[barcode][bin_id] += count
            chrom_counts[chrom] += count

            if min_start is None or start < min_start:
                min_start = start
            if max_end is None or end > max_end:
                max_end = end

    for barcode, bins in cell_bins.items():
        for bin_id in bins:
            bin_document_frequency[bin_id] += 1

    cells = sorted(cell_total)
    bins = sorted(bin_document_frequency)

    summary = {
        "fragment_path": os.path.abspath(fragment_path),
        "fragment_sha256": sha256_file(fragment_path),
        "bin_size": BIN_SIZE,
        "input_rows": total_rows,
        "parsed_fragment_rows": parsed_rows,
        "weighted_fragments": total_weighted_fragments,
        "n_cells": len(cells),
        "n_chromosomes": len(chrom_counts),
        "n_bins": len(bins),
        "chromosome_fragment_counts": dict(sorted(chrom_counts.items())),
        "min_start": min_start,
        "max_end": max_end,
    }

    return cells, bins, cell_total, cell_bp, cell_chroms, cell_bins, bin_document_frequency, summary


def build_tfidf_matrix(cells, bins, cell_total, cell_bins, bin_document_frequency):
    n_cells = len(cells)
    n_bins = len(bins)
    bin_index = {b: i for i, b in enumerate(bins)}

    try:
        import numpy as np
    except Exception:
        return None, None, "numpy_unavailable"

    matrix = np.zeros((n_cells, n_bins), dtype=float)
    for row, cell in enumerate(cells):
        denom = float(cell_total[cell]) if cell_total[cell] else 1.0
        for bin_id, count in cell_bins[cell].items():
            col = bin_index[bin_id]
            tf = float(count) / denom
            idf = math.log(1.0 + float(n_cells) / (1.0 + float(bin_document_frequency[bin_id])))
            matrix[row, col] = tf * idf

    norms = np.linalg.norm(matrix, axis=1)
    norms[norms == 0.0] = 1.0
    matrix = matrix / norms[:, None]
    return matrix, np, "tfidf_l2"


def compute_embedding(cells, matrix, np_module):
    if not cells:
        return [], "empty_input"

    n_cells = len(cells)
    if n_cells == 1:
        return [(cells[0], 0.0, 0.0)], "single_cell_zero_embedding"

    if matrix is None or np_module is None:
        coords = []
        denom = max(1, n_cells - 1)
        for i, cell in enumerate(cells):
            coords.append((cell, float(i) / float(denom), 0.0))
        return coords, "rank_order_fallback_no_numpy"

    np = np_module

    try:
        from sklearn.decomposition import TruncatedSVD
        n_components = min(2, max(1, min(matrix.shape) - 1))
        if n_components < 1:
            raise ValueError("matrix too small for TruncatedSVD")
        svd = TruncatedSVD(n_components=n_components, random_state=0)
        emb = svd.fit_transform(matrix)
        method = "tfidf_l2_truncated_svd_sklearn"
    except Exception:
        centered = matrix - matrix.mean(axis=0, keepdims=True)
        try:
            u, s, _ = np.linalg.svd(centered, full_matrices=False)
            n_components = min(2, u.shape[1])
            emb = u[:, :n_components] * s[:n_components]
            method = "tfidf_l2_dense_svd_numpy"
        except Exception:
            scores = matrix.sum(axis=1)
            emb = scores.reshape((-1, 1))
            n_components = 1
            method = "tfidf_l2_row_sum_fallback"

    if emb.shape[1] == 1:
        emb = np.column_stack([emb[:, 0], np.zeros(n_cells, dtype=float)])
    elif emb.shape[1] == 0:
        emb = np.zeros((n_cells, 2), dtype=float)

    coords = []
    for i, cell in enumerate(cells):
        x = float(emb[i, 0])
        y = float(emb[i, 1])
        if not math.isfinite(x):
            x = 0.0
        if not math.isfinite(y):
            y = 0.0
        coords.append((cell, x, y))

    return coords, method


def write_embedding_csv(path, coords):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["cell_id", "snap_tfidf_svd_1", "snap_tfidf_svd_2"])
        for cell, x, y in coords:
            writer.writerow([cell, "{:.10g}".format(x), "{:.10g}".format(y)])


def write_cell_features_csv(path, cells, cell_total, cell_bp, cell_chroms, cell_bins):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "cell_id",
            "total_fragments",
            "unique_bins",
            "unique_chromosomes",
            "total_fragment_bp",
            "mean_fragment_length",
        ])
        for cell in cells:
            total = int(cell_total[cell])
            total_bp = int(cell_bp[cell])
            mean_len = float(total_bp) / float(total) if total else 0.0
            writer.writerow([
                cell,
                total,
                len(cell_bins[cell]),
                len(cell_chroms[cell]),
                total_bp,
                "{:.6g}".format(mean_len),
            ])


def safe_artifact_path(artifact_dir, filename):
    root = os.path.abspath(artifact_dir)
    path = os.path.abspath(os.path.join(root, filename))
    if os.path.commonpath([root, path]) != root:
        raise ValueError("artifact path escapes artifact directory")
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(description="SNAP-T1 executable candidate")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--condition", required=True)
    parser.add_argument("--fragment", required=True)
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--result-json", required=True)
    args = parser.parse_args(argv)

    start = time.perf_counter()
    tracemalloc.start()

    os.makedirs(args.artifact_dir, exist_ok=True)
    embedding_path = safe_artifact_path(args.artifact_dir, "embedding.csv")
    cell_features_path = safe_artifact_path(args.artifact_dir, "cell_features.csv")
    summary_path = safe_artifact_path(args.artifact_dir, "fragment_summary.json")

    snapatac2_available = False
    snapatac2_version = None
    try:
        import snapatac2  # noqa: F401
        snapatac2_available = True
        snapatac2_version = getattr(snapatac2, "__version__", None)
    except Exception:
        pass

    status = "ok"
    error = None
    embedding_method = None
    matrix_method = None

    try:
        cells, bins, cell_total, cell_bp, cell_chroms, cell_bins, bin_df, summary = load_fragment_features(args.fragment)
        matrix, np_module, matrix_method = build_tfidf_matrix(cells, bins, cell_total, cell_bins, bin_df)
        coords, embedding_method = compute_embedding(cells, matrix, np_module)

        write_embedding_csv(embedding_path, coords)
        write_cell_features_csv(cell_features_path, cells, cell_total, cell_bp, cell_chroms, cell_bins)

        summary.update({
            "task_id": args.task_id,
            "condition": args.condition,
            "snapatac2_import_available": snapatac2_available,
            "snapatac2_version": snapatac2_version,
            "matrix_method": matrix_method,
            "embedding_method": embedding_method,
            "artifacts": {
                "embedding_csv": os.path.abspath(embedding_path),
                "cell_features_csv": os.path.abspath(cell_features_path),
                "fragment_summary_json": os.path.abspath(summary_path),
            },
        })

        with open(summary_path, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2, sort_keys=True)

    except Exception as exc:
        status = "error"
        error = "{}: {}".format(type(exc).__name__, exc)
        raise
    finally:
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        elapsed = time.perf_counter() - start

        result = {
            "task_id": args.task_id,
            "condition": args.condition,
            "status": status,
            "method_steps": [
                "read locked fragment TSV/GZIP fixture",
                "aggregate per-cell fragment, chromosome, and genomic-bin features",
                "apply SnapATAC-style TF-IDF weighting with L2 normalization",
                "compute deterministic two-dimensional spectral/SVD embedding with fallbacks",
                "write required machine-readable artifacts",
            ],
            "embedding_artifacts": {
                "embedding_csv": os.path.abspath(embedding_path),
                "cell_features_csv": os.path.abspath(cell_features_path),
                "fragment_summary_json": os.path.abspath(summary_path),
            },
            "candidate_runtime_seconds": elapsed,
            "candidate_peak_memory_mb_tracemalloc": peak / (1024.0 * 1024.0),
            "snapatac2_import_available": snapatac2_available,
            "snapatac2_version": snapatac2_version,
            "matrix_method": matrix_method,
            "embedding_method": embedding_method,
            "notes": [
                "The script does not set completed=true; the locked runner owns final completion after execution and artifact validation.",
                "No network access, package installation, subprocess package managers, POSIX-only resource APIs, or writes outside requested outputs are used.",
            ],
        }
        if error is not None:
            result["error"] = error

        result_dir = os.path.dirname(os.path.abspath(args.result_json))
        if result_dir:
            os.makedirs(result_dir, exist_ok=True)
        with open(args.result_json, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
