import argparse, csv, gzip, hashlib, json, math, os, sys
from collections import Counter, defaultdict

def stable_bin(chrom, start, bins):
    h = hashlib.sha1((chrom + ":" + str(start // 5000)).encode("utf-8")).digest()
    return int.from_bytes(h[:4], "little") % bins

def open_text(path):
    return gzip.open(path, "rt", encoding="utf-8", errors="replace") if path.endswith(".gz") else open(path, "r", encoding="utf-8", errors="replace")

def read_fragments(path, bins=512):
    counts = defaultdict(Counter)
    stats = {}
    total = skipped = 0
    chroms = Counter()
    with open_text(path) as fh:
        for line in fh:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 4:
                skipped += 1
                continue
            chrom, s, e, cell = parts[0], parts[1], parts[2], parts[3]
            try:
                start, end = int(s), int(e)
            except ValueError:
                skipped += 1
                continue
            if end < start:
                skipped += 1
                continue
            b = stable_bin(chrom, start, bins)
            counts[cell][b] += 1
            length = end - start
            rec = stats.setdefault(cell, {"n": 0, "bp": 0, "mito": 0})
            rec["n"] += 1
            rec["bp"] += length
            if chrom.lower() in ("chrm", "mt", "m", "mitochondria"):
                rec["mito"] += 1
            chroms[chrom] += 1
            total += 1
    return counts, stats, {"total_fragments": total, "skipped_records": skipped, "chromosomes": dict(chroms), "hash_bins": bins}

def fallback_embedding(cells, counts, stats, dims=5):
    out = []
    for c in cells:
        ctr = counts[c]
        n = stats[c]["n"]
        bp = stats[c]["bp"]
        uniq = len(ctr)
        vals = list(ctr.values()) or [0]
        mean_bp = bp / n if n else 0.0
        entropy = 0.0
        for v in vals:
            p = v / n if n else 0.0
            if p:
                entropy -= p * math.log(p)
        raw = [
            math.log1p(n),
            math.log1p(uniq),
            math.log1p(mean_bp),
            entropy,
            (stats[c]["mito"] / n) if n else 0.0,
        ]
        out.append(raw[:dims])
    return zscale(out, dims), "standard-library hashed fragment statistics fallback"

def zscale(rows, dims):
    if not rows:
        return []
    cols = list(zip(*rows))
    means = [sum(col) / len(col) for col in cols]
    sds = []
    for j, col in enumerate(cols):
        var = sum((x - means[j]) ** 2 for x in col) / max(1, len(col) - 1)
        sds.append(math.sqrt(var) or 1.0)
    return [[(row[j] - means[j]) / sds[j] for j in range(dims)] for row in rows]

def numpy_embedding(cells, counts, bins=512, dims=5):
    import numpy as np
    n = len(cells)
    x = np.zeros((n, bins), dtype=float)
    for i, c in enumerate(cells):
        for b, v in counts[c].items():
            x[i, b] = v
    df = (x > 0).sum(axis=0)
    idf = np.log1p(n / (1.0 + df))
    x *= idf
    norms = np.linalg.norm(x, axis=1)
    norms[norms == 0] = 1.0
    x = x / norms[:, None]
    degree = x.dot(x.T.dot(np.ones(n))) if n else np.array([])
    degree[degree <= 0] = 1.0
    x = x / np.sqrt(degree)[:, None]
    if n == 0:
        emb = np.zeros((0, dims))
    elif n == 1:
        emb = np.zeros((1, dims))
    else:
        u, s, vt = np.linalg.svd(x, full_matrices=False)
        start = 1 if u.shape[1] > 1 else 0
        take = min(dims, max(0, u.shape[1] - start))
        emb = np.zeros((n, dims), dtype=float)
        if take:
            emb[:, :take] = u[:, start:start + take] * s[start:start + take]
    return emb.tolist(), degree.tolist(), "numpy TF-IDF, row L2, degree-normalized matrix-free SVD"

def write_csvs(artifact_dir, cells, emb, counts, stats, degrees):
    os.makedirs(artifact_dir, exist_ok=True)
    emb_path = os.path.join(artifact_dir, "embedding.csv")
    feat_path = os.path.join(artifact_dir, "cell_features.csv")
    with open(emb_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        dims = len(emb[0]) if emb else 5
        w.writerow(["cell_id"] + ["dim%d" % (i + 1) for i in range(dims)])
        for c, row in zip(cells, emb):
            w.writerow([c] + ["%.10g" % float(v) for v in row])
    with open(feat_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["cell_id", "n_fragments", "n_unique_bins", "total_bp", "mean_fragment_bp", "frac_mito", "degree"])
        for i, c in enumerate(cells):
            n = stats[c]["n"]
            deg = degrees[i] if i < len(degrees) else 0.0
            w.writerow([c, n, len(counts[c]), stats[c]["bp"], "%.10g" % (stats[c]["bp"] / n if n else 0.0),
                        "%.10g" % (stats[c]["mito"] / n if n else 0.0), "%.10g" % float(deg)])
    return emb_path, feat_path

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-id", required=True)
    ap.add_argument("--condition", required=True)
    ap.add_argument("--fragment", required=True)
    ap.add_argument("--artifact-dir", required=True)
    ap.add_argument("--result-json", required=True)
    args = ap.parse_args(argv)

    bins, dims = 512, 5
    counts, stats, summary = read_fragments(args.fragment, bins=bins)
    cells = sorted(counts)
    used_numpy = False
    try:
        emb, degrees, method = numpy_embedding(cells, counts, bins=bins, dims=dims)
        used_numpy = True
    except Exception as e:
        emb, method = fallback_embedding(cells, counts, stats, dims=dims)
        degrees = [0.0] * len(cells)
        summary["numpy_error"] = repr(e)

    emb_path, feat_path = write_csvs(args.artifact_dir, cells, emb, counts, stats, degrees)
    summary.update({
        "task_id": args.task_id,
        "condition": args.condition,
        "fragment_path": args.fragment,
        "fragment_sha256": sha256_file(args.fragment),
        "n_cells": len(cells),
        "embedding_dimensions": dims,
        "method": method,
        "used_numpy": used_numpy,
        "embedding_csv": os.path.basename(emb_path),
        "cell_features_csv": os.path.basename(feat_path),
    })
    summary_path = os.path.join(args.artifact_dir, "fragment_summary.json")
    with open(summary_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True)

    result = {
        "task_id": args.task_id,
        "condition": args.condition,
        "notes": "Candidate-side diagnostic only; runner owns completed/runtime/peak-memory fields.",
        "method_steps": [
            "read locked fragment TSV/GZIP fixture",
            "aggregate per-cell hashed genomic-bin counts",
            "apply SnapATAC2-paper-inspired IDF scaling, row L2 normalization, degree normalization",
            "compute deterministic low-dimensional embedding using matrix-free SVD when numpy is available",
            "write embedding, cell feature, and fragment summary artifacts"
        ],
        "embedding_artifacts": {
            "embedding_csv": emb_path,
            "cell_features_csv": feat_path,
            "fragment_summary_json": summary_path,
            "n_cells": len(cells),
            "dimensions": dims
        },
        "quality_metrics": {
            "total_fragments": summary["total_fragments"],
            "skipped_records": summary["skipped_records"],
            "hash_bins": bins,
            "used_numpy": used_numpy
        }
    }
    with open(args.result_json, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)

if __name__ == "__main__":
    main()
