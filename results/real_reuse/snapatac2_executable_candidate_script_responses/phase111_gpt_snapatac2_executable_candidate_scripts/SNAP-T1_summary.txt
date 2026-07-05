#!/usr/bin/env python3
import argparse
import csv
import gzip
import hashlib
import json
import math
import os
import resource
import statistics
import time
from collections import Counter, defaultdict
from pathlib import Path


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def current_memory_mb():
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if os.name == "posix":
        if usage > 10_000_000:
            return usage / (1024.0 * 1024.0)
        return usage / 1024.0
    return usage / (1024.0 * 1024.0)


def stable_unit_value(text, salt):
    digest = hashlib.sha256((salt + "|" + text).encode("utf-8")).digest()
    value = int.from_bytes(digest[:8], "big") / float(2**64 - 1)
    return value * 2.0 - 1.0


def parse_fragment(fragment_path):
    cells = {}
    chrom_counts = Counter()
    total_fragments = 0
    malformed_rows = 0
    min_start = None
    max_end = None

    with gzip.open(fragment_path, "rt", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 4:
                malformed_rows += 1
                continue
            chrom, start_s, end_s, barcode = fields[:4]
            try:
                start = int(start_s)
                end = int(end_s)
            except ValueError:
                malformed_rows += 1
                continue
            if end < start:
                malformed_rows += 1
                continue

            if barcode not in cells:
                cells[barcode] = {
                    "fragments": 0,
                    "total_length": 0,
                    "chrom_counts": Counter(),
                    "min_start": start,
                    "max_end": end,
                }

            length = end - start
            record = cells[barcode]
            record["fragments"] += 1
            record["total_length"] += length
            record["chrom_counts"][chrom] += 1
            record["min_start"] = min(record["min_start"], start)
            record["max_end"] = max(record["max_end"], end)

            chrom_counts[chrom] += 1
            total_fragments += 1
            min_start = start if min_start is None else min(min_start, start)
            max_end = end if max_end is None else max(max_end, end)

    return {
        "cells": cells,
        "chrom_counts": chrom_counts,
        "total_fragments": total_fragments,
        "malformed_rows": malformed_rows,
        "min_start": min_start,
        "max_end": max_end,
    }


def write_cell_features(path, cells, chrom_order):
    fieldnames = [
        "cell_id",
        "fragment_count",
        "log1p_fragment_count",
        "mean_fragment_length",
        "chromosome_count",
        "dominant_chromosome",
        "dominant_chromosome_fraction",
        "genomic_span",
    ] + ["count_" + chrom for chrom in chrom_order]

    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for cell_id in sorted(cells):
            record = cells[cell_id]
            fragments = record["fragments"]
            chrom_counts = record["chrom_counts"]
            dominant_chromosome, dominant_count = chrom_counts.most_common(1)[0]
            row = {
                "cell_id": cell_id,
                "fragment_count": fragments,
                "log1p_fragment_count": f"{math.log1p(fragments):.10f}",
                "mean_fragment_length": f"{(record['total_length'] / fragments):.10f}",
                "chromosome_count": len(chrom_counts),
                "dominant_chromosome": dominant_chromosome,
                "dominant_chromosome_fraction": f"{(dominant_count / fragments):.10f}",
                "genomic_span": record["max_end"] - record["min_start"],
            }
            for chrom in chrom_order:
                row["count_" + chrom] = chrom_counts.get(chrom, 0)
            writer.writerow(row)


def jacobi_eigen_symmetric(matrix, max_iter=100, tol=1e-12):
    n = len(matrix)
    a = [row[:] for row in matrix]
    v = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

    for _ in range(max_iter):
        p, q = 0, 1
        max_abs = 0.0
        for i in range(n):
            for j in range(i + 1, n):
                value = abs(a[i][j])
                if value > max_abs:
                    max_abs = value
                    p, q = i, j
        if max_abs < tol:
            break

        if abs(a[p][p] - a[q][q]) < tol:
            angle = math.pi / 4.0
        else:
            angle = 0.5 * math.atan2(2.0 * a[p][q], a[q][q] - a[p][p])
        c = math.cos(angle)
        s = math.sin(angle)

        app = c * c * a[p][p] - 2.0 * s * c * a[p][q] + s * s * a[q][q]
        aqq = s * s * a[p][p] + 2.0 * s * c * a[p][q] + c * c * a[q][q]
        a[p][q] = 0.0
        a[q][p] = 0.0
        a[p][p] = app
        a[q][q] = aqq

        for r in range(n):
            if r != p and r != q:
                arp = c * a[r][p] - s * a[r][q]
                arq = s * a[r][p] + c * a[r][q]
                a[r][p] = a[p][r] = arp
                a[r][q] = a[q][r] = arq

        for r in range(n):
            vrp = c * v[r][p] - s * v[r][q]
            vrq = s * v[r][p] + c * v[r][q]
            v[r][p] = vrp
            v[r][q] = vrq

    eigenvalues = [a[i][i] for i in range(n)]
    eigenvectors = [[v[row][col] for row in range(n)] for col in range(n)]
    return eigenvalues, eigenvectors


def pca_scores(rows, dimensions=2):
    if not rows:
        return []

    n = len(rows)
    d = len(rows[0])
    if n == 1:
        return [[0.0 for _ in range(dimensions)]]

    means = [sum(row[j] for row in rows) / n for j in range(d)]
    centered = [[row[j] - means[j] for j in range(d)] for row in rows]

    stds = []
    for j in range(d):
        variance = sum(centered[i][j] ** 2 for i in range(n)) / max(1, n - 1)
        stds.append(math.sqrt(variance) if variance > 0 else 1.0)
    scaled = [[centered[i][j] / stds[j] for j in range(d)] for i in range(n)]

    covariance = []
    for i in range(d):
        row = []
        for j in range(d):
            row.append(sum(scaled[k][i] * scaled[k][j] for k in range(n)) / max(1, n - 1))
        covariance.append(row)

    eigenvalues, eigenvectors = jacobi_eigen_symmetric(covariance, max_iter=max(100, d * d * 20))
    order = sorted(range(d), key=lambda idx: eigenvalues[idx], reverse=True)

    scores = []
    for row in scaled:
        projected = []
        for component_index in order[:dimensions]:
            vector = eigenvectors[component_index]
            projected.append(sum(row[j] * vector[j] for j in range(d)))
        while len(projected) < dimensions:
            projected.append(0.0)
        scores.append(projected)
    return scores


def deterministic_fallback_embedding(cells, chrom_order):
    cell_ids = sorted(cells)
    rows = []
    for cell_id in cell_ids:
        record = cells[cell_id]
        fragments = record["fragments"]
        total_chrom = sum(record["chrom_counts"].values())
        features = [
            math.log1p(fragments),
            record["total_length"] / max(1, fragments),
            len(record["chrom_counts"]),
            record["max_end"] - record["min_start"],
        ]
        for chrom in chrom_order:
            count = record["chrom_counts"].get(chrom, 0)
            features.append(math.log1p(count))
            features.append(count / max(1, total_chrom))
        features.append(stable_unit_value(cell_id, "barcode"))
        rows.append(features)

    return cell_ids, pca_scores(rows, dimensions=2)


def try_snapatac2_embedding(fragment_path, artifact_dir):
    try:
        import snapatac2 as snap  # type: ignore
    except Exception as exc:
        return None, "snapatac2_import_failed: " + repr(exc)

    try:
        work_h5ad = str(Path(artifact_dir) / "snapatac2_fragment_input.h5ad")
        data = snap.pp.import_data(
            fragment_file=str(fragment_path),
            chrom_sizes=None,
            file=work_h5ad,
            sorted_by_barcode=False,
        )
        snap.pp.add_tile_matrix(data, bin_size=5000)
        snap.pp.select_features(data, n_features=min(1000, data.n_vars))
        snap.tl.spectral(data, n_comps=2)
        embedding = data.obsm.get("X_spectral")
        if embedding is None:
            return None, "snapatac2_no_X_spectral"
        cell_ids = [str(x) for x in data.obs_names]
        coords = [[float(row[0]), float(row[1] if len(row) > 1 else 0.0)] for row in embedding]
        return (cell_ids, coords), "snapatac2_spectral_embedding"
    except Exception as exc:
        return None, "snapatac2_pipeline_failed: " + repr(exc)


def write_embedding(path, cell_ids, coords, method):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["cell_id", "dim1", "dim2", "method"])
        writer.writeheader()
        for cell_id, coord in zip(cell_ids, coords):
            writer.writerow(
                {
                    "cell_id": cell_id,
                    "dim1": f"{coord[0]:.10f}",
                    "dim2": f"{coord[1]:.10f}",
                    "method": method,
                }
            )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--condition", required=True)
    parser.add_argument("--fragment", required=True)
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--result-json", required=True)
    args = parser.parse_args()

    start = time.perf_counter()
    artifact_dir = Path(args.artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)

    fragment_path = Path(args.fragment)
    embedding_path = artifact_dir / "embedding.csv"
    cell_features_path = artifact_dir / "cell_features.csv"
    fragment_summary_path = artifact_dir / "fragment_summary.json"

    parsed = parse_fragment(fragment_path)
    cells = parsed["cells"]
    chrom_order = sorted(parsed["chrom_counts"])

    snap_result, method_note = try_snapatac2_embedding(fragment_path, artifact_dir)
    if snap_result is not None:
        embedding_cell_ids, embedding_coords = snap_result
        embedding_method = "snapatac2_spectral"
    else:
        embedding_cell_ids, embedding_coords = deterministic_fallback_embedding(cells, chrom_order)
        embedding_method = "standard_library_fragment_feature_pca"

    write_cell_features(cell_features_path, cells, chrom_order)
    write_embedding(embedding_path, embedding_cell_ids, embedding_coords, embedding_method)

    fragment_counts = [record["fragments"] for record in cells.values()]
    fragment_summary = {
        "task_id": args.task_id,
        "condition": args.condition,
        "fragment_path": str(fragment_path),
        "fragment_sha256": sha256_file(fragment_path),
        "total_fragments": parsed["total_fragments"],
        "malformed_rows": parsed["malformed_rows"],
        "cell_count": len(cells),
        "chromosome_count": len(chrom_order),
        "chromosomes": chrom_order,
        "chromosome_fragment_counts": dict(sorted(parsed["chrom_counts"].items())),
        "min_start": parsed["min_start"],
        "max_end": parsed["max_end"],
        "fragment_count_min": min(fragment_counts) if fragment_counts else 0,
        "fragment_count_max": max(fragment_counts) if fragment_counts else 0,
        "fragment_count_mean": statistics.fmean(fragment_counts) if fragment_counts else 0.0,
        "embedding_method": embedding_method,
        "embedding_cell_count": len(embedding_cell_ids),
    }
    with open(fragment_summary_path, "w", encoding="utf-8") as handle:
        json.dump(fragment_summary, handle, indent=2, sort_keys=True)
        handle.write("\n")

    runtime_seconds = time.perf_counter() - start
    peak_memory_mb = current_memory_mb()

    result = {
        "method_steps": [
            "Loaded miniature SnapATAC2 fragment fixture from --fragment.",
            "Computed per-cell fragment, chromosome, fragment-length, and span features.",
            "Attempted SnapATAC2 spectral embedding when the package and minimal pipeline were available.",
            "Materialized deterministic PCA-style fallback embedding from fragment-derived features when SnapATAC2 was unavailable or failed.",
            "Wrote embedding.csv, cell_features.csv, and fragment_summary.json under --artifact-dir.",
        ],
        "embedding_artifacts": {
            "embedding_csv": str(embedding_path),
            "cell_features_csv": str(cell_features_path),
            "fragment_summary_json": str(fragment_summary_path),
            "embedding_method": embedding_method,
            "embedding_rows": len(embedding_cell_ids),
        },
        "runtime_seconds": runtime_seconds,
        "peak_memory_mb": peak_memory_mb,
        "notes": {
            "task_id": args.task_id,
            "condition": args.condition,
            "snapatac2_status": method_note,
            "fallback_is_deterministic": True,
            "completion_owned_by_runner": True,
        },
        "quality_metrics": {
            "total_fragments": parsed["total_fragments"],
            "cell_count": len(cells),
            "chromosome_count": len(chrom_order),
            "malformed_rows": parsed["malformed_rows"],
            "fragment_sha256": fragment_summary["fragment_sha256"],
        },
    }

    with open(args.result_json, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")


if __name__ == "__main__":
    main()
