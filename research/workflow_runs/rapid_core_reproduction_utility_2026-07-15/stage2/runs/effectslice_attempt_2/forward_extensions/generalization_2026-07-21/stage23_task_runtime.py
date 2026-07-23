from __future__ import annotations

import hashlib
import json
import math
import random
import re
from collections import defaultdict, deque
from typing import Any, Callable


def canonical_json(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _rng(task_id: str, seed: str) -> random.Random:
    digest = hashlib.sha256(f"EffectSlice-FG1\0{task_id}\0{seed}".encode()).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def _round(value: float) -> float:
    return round(float(value), 8)


def _stable_top(scores: list[float], count: int, forced: set[int]) -> list[int]:
    if count < len(forced):
        raise ValueError("target is smaller than the forced set")
    ranked = sorted(range(len(scores)), key=lambda index: (-scores[index], index))
    selected = set(forced)
    for index in ranked:
        if len(selected) >= count:
            break
        selected.add(index)
    return sorted(selected)


def _coarse_budget(case: dict[str, Any]) -> dict[str, Any]:
    segments = case["segments"]
    budget = int(case["budget"])
    allocations = [int(row["minimum"]) for row in segments]
    capacities = [int(row["capacity"]) for row in segments]
    if any(a < 0 or a > c for a, c in zip(allocations, capacities, strict=True)):
        raise ValueError("invalid segment quota")
    if sum(allocations) > budget or budget > sum(capacities):
        raise ValueError("infeasible budget")
    while sum(allocations) < budget:
        eligible = [i for i, value in enumerate(allocations) if value < capacities[i]]
        index = min(
            eligible,
            key=lambda i: (
                -float(segments[i]["importance"]) / (allocations[i] + 1),
                i,
            ),
        )
        allocations[index] += 1
    return {
        "allocations": allocations,
        "by_name": {row["name"]: allocations[i] for i, row in enumerate(segments)},
        "total": sum(allocations),
    }


def _iterative_compression(case: dict[str, Any]) -> dict[str, Any]:
    rounds = case["round_scores"]
    targets = [int(value) for value in case["round_targets"]]
    forced = {int(value) for value in case.get("forced", [])}
    if len(rounds) != len(targets) or not rounds:
        raise ValueError("round schedule mismatch")
    current = list(range(len(rounds[0])))
    history: list[list[int]] = []
    for scores, target in zip(rounds, targets, strict=True):
        if len(scores) != len(rounds[0]) or target > len(current):
            raise ValueError("invalid round")
        ranked = sorted(current, key=lambda i: (-float(scores[i]), i))
        selected = {i for i in current if i in forced}
        if len(selected) > target:
            raise ValueError("forced tokens exceed target")
        for index in ranked:
            if len(selected) >= target:
                break
            selected.add(index)
        current = sorted(selected)
        history.append(current[:])
    return {"history": history, "retained_indices": current}


def _word_alignment(case: dict[str, Any]) -> dict[str, Any]:
    groups = [[int(v) for v in group] for group in case["word_token_indices"]]
    labels = [int(v) for v in case["word_labels"]]
    if len(groups) != len(labels):
        raise ValueError("word/label mismatch")
    token_count = int(case["token_count"])
    token_labels: list[int | None] = [None] * token_count
    for group, label in zip(groups, labels, strict=True):
        for index in group:
            if not 0 <= index < token_count or token_labels[index] is not None:
                raise ValueError("invalid or overlapping token alignment")
            token_labels[index] = label
    if any(value is None for value in token_labels):
        raise ValueError("alignment does not cover every token")
    return {"token_labels": token_labels, "kept_indices": [i for i, v in enumerate(token_labels) if v == 1]}


def _budgeted_reconstruction(case: dict[str, Any]) -> dict[str, Any]:
    groups = [[int(v) for v in group] for group in case["word_token_indices"]]
    scores = [float(v) for v in case["word_scores"]]
    forced = {int(v) for v in case.get("forced_words", [])}
    budget = int(case["token_budget"])
    if len(groups) != len(scores) or any(i < 0 or i >= len(groups) for i in forced):
        raise ValueError("invalid reconstruction input")
    selected = set(forced)
    used = sum(len(groups[i]) for i in selected)
    if used > budget:
        raise ValueError("forced words exceed token budget")
    for index in sorted(range(len(groups)), key=lambda i: (-scores[i], i)):
        if index in selected:
            continue
        if used + len(groups[index]) <= budget:
            selected.add(index)
            used += len(groups[index])
    token_indices = sorted(index for word in selected for index in groups[word])
    return {"selected_words": sorted(selected), "retained_token_indices": token_indices, "tokens_used": used}


def _cosine(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right, strict=True))
    lnorm = math.sqrt(sum(a * a for a in left))
    rnorm = math.sqrt(sum(b * b for b in right))
    return 0.0 if lnorm == 0.0 or rnorm == 0.0 else numerator / (lnorm * rnorm)


def _context_scores(case: dict[str, Any]) -> dict[str, Any]:
    vectors = [[float(v) for v in row] for row in case["sentence_vectors"]]
    query = [float(v) for v in case["query_vector"]]
    alpha = float(case["context_weight"])
    if not vectors or any(len(row) != len(query) for row in vectors):
        raise ValueError("embedding shape mismatch")
    base = [_cosine(row, query) for row in vectors]
    scores = []
    for index, value in enumerate(base):
        neighbors = [base[j] for j in (index - 1, index + 1) if 0 <= j < len(base)]
        context = sum(neighbors) / len(neighbors) if neighbors else 0.0
        scores.append(_round((1.0 - alpha) * value + alpha * context))
    return {"scores": scores, "ranking": sorted(range(len(scores)), key=lambda i: (-scores[i], i))}


def _sentence_knapsack(case: dict[str, Any]) -> dict[str, Any]:
    lengths = [int(v) for v in case["lengths"]]
    scores = [float(v) for v in case["scores"]]
    budget = int(case["budget"])
    if len(lengths) != len(scores) or any(value <= 0 for value in lengths):
        raise ValueError("invalid sentence inventory")
    states: dict[int, tuple[float, tuple[int, ...]]] = {0: (0.0, ())}
    for index, (length, score) in enumerate(zip(lengths, scores, strict=True)):
        updated = dict(states)
        for used, (total_score, chosen) in states.items():
            new_used = used + length
            if new_used > budget:
                continue
            candidate = (total_score + score, chosen + (index,))
            prior = updated.get(new_used)
            if prior is None or (-candidate[0], candidate[1]) < (-prior[0], prior[1]):
                updated[new_used] = candidate
        states = updated
    used, (score, chosen) = min(states.items(), key=lambda item: (-item[1][0], item[0], item[1][1]))
    return {"selected_indices": list(chosen), "tokens_used": used, "total_score": _round(score)}


def _test_subset(case: dict[str, Any], subset: list[str]) -> str:
    required = set(case["required_failure_items"])
    unresolved = set(case.get("unresolved_without", []))
    selected = set(subset)
    if unresolved and not unresolved.issubset(selected):
        return "UNRESOLVED"
    return "FAIL" if required.issubset(selected) else "PASS"


def _ddmin(case: dict[str, Any]) -> dict[str, Any]:
    current = list(case["items"])
    if _test_subset(case, current) != "FAIL":
        raise ValueError("initial configuration must fail")
    granularity = 2
    tests = 1
    while len(current) >= 2:
        chunk_size = math.ceil(len(current) / granularity)
        chunks = [current[i : i + chunk_size] for i in range(0, len(current), chunk_size)]
        reduced = False
        for chunk in chunks:
            outcome = _test_subset(case, chunk)
            tests += 1
            if outcome == "FAIL":
                current = chunk
                granularity = max(granularity - 1, 2)
                reduced = True
                break
        if reduced:
            continue
        for chunk in chunks:
            complement = [item for item in current if item not in set(chunk)]
            outcome = _test_subset(case, complement)
            tests += 1
            if outcome == "FAIL":
                current = complement
                granularity = max(granularity - 1, 2)
                reduced = True
                break
        if reduced:
            continue
        if granularity >= len(current):
            break
        granularity = min(len(current), 2 * granularity)
    return {"minimal_failure": current, "tests": tests, "outcome": _test_subset(case, current)}


def _difference_isolation(case: dict[str, Any]) -> dict[str, Any]:
    passing = set(case["passing"])
    failing = list(case["failing"])
    delta = [item for item in failing if item not in passing]
    local = {
        "items": delta,
        "required_failure_items": case["required_difference"],
        "unresolved_without": case.get("unresolved_difference", []),
    }
    result = _ddmin(local)
    return {"isolated_difference": result["minimal_failure"], "tests": result["tests"]}


def _pass_fixed_point(case: dict[str, Any]) -> dict[str, Any]:
    text = str(case["text"])
    passes = case["passes"]
    max_rounds = int(case["max_rounds"])
    applications: list[str] = []
    for _ in range(max_rounds):
        changed = False
        for row in passes:
            before = text
            text = text.replace(str(row["old"]), str(row["new"]), 1)
            if text != before:
                applications.append(str(row["name"]))
                changed = True
        if not changed:
            return {"text": text, "applications": applications, "fixed_point": True}
    return {"text": text, "applications": applications, "fixed_point": False}


def _chunk_reduction(case: dict[str, Any]) -> dict[str, Any]:
    current = list(case["items"])
    required = set(case["required_failure_items"])
    granularity = 2
    attempts = 0
    while len(current) > 1:
        size = math.ceil(len(current) / granularity)
        changed = False
        for start in range(0, len(current), size):
            candidate = current[:start] + current[start + size :]
            attempts += 1
            if required.issubset(candidate):
                current = candidate
                granularity = max(2, granularity - 1)
                changed = True
                break
        if changed:
            continue
        if granularity >= len(current):
            break
        granularity = min(len(current), granularity * 2)
    return {"reduced_items": current, "attempts": attempts, "one_minimal": all(not required.issubset(current[:i] + current[i + 1 :]) for i in range(len(current)))}


def _grammar_reduce(case: dict[str, Any]) -> dict[str, Any]:
    nodes = {str(row["id"]): dict(row) for row in case["nodes"]}
    required = set(case["required_symbols"])
    removed: list[str] = []
    for node_id in sorted(nodes, key=lambda value: (-int(nodes[value]["depth"]), value)):
        node = nodes[node_id]
        if not node.get("removable") or node["symbol"] in required:
            continue
        children = [row for row in nodes.values() if row.get("parent") == node_id and row["id"] not in removed]
        if children:
            continue
        remaining_symbols = {row["symbol"] for key, row in nodes.items() if key not in set(removed + [node_id])}
        if required.issubset(remaining_symbols):
            removed.append(node_id)
    return {"retained_node_ids": sorted(set(nodes) - set(removed)), "removed_node_ids": removed}


def _reduction_queue(case: dict[str, Any]) -> dict[str, Any]:
    nodes = {str(row["id"]): dict(row) for row in case["nodes"]}
    retained = set(nodes)
    queue = deque(sorted(nodes, key=lambda node_id: (-int(nodes[node_id]["depth"]), node_id)))
    visited: list[str] = []
    while queue:
        node_id = queue.popleft()
        if node_id not in retained:
            continue
        visited.append(node_id)
        node = nodes[node_id]
        children = {key for key, row in nodes.items() if row.get("parent") == node_id}
        if node.get("removable") and not (children & retained) and float(node["utility"]) <= float(case["utility_threshold"]):
            retained.remove(node_id)
            parent = node.get("parent")
            if parent in retained:
                queue.append(parent)
    return {"retained_node_ids": sorted(retained), "visit_order": visited}


def _idf(case: dict[str, Any]) -> dict[str, Any]:
    matrix = [[int(v) for v in row] for row in case["matrix"]]
    if not matrix or any(len(row) != len(matrix[0]) for row in matrix):
        raise ValueError("matrix shape mismatch")
    n_rows = len(matrix)
    df = [sum(1 for row in matrix if row[j] != 0) for j in range(len(matrix[0]))]
    idf = [math.log(1.0 + n_rows / (1.0 + value)) for value in df]
    weighted = [[_round(value * idf[j]) for j, value in enumerate(row)] for row in matrix]
    degrees = [_round(sum(row)) for row in weighted]
    return {"idf": [_round(v) for v in idf], "weighted_matrix": weighted, "row_degree": degrees}


def _spectral_operator(case: dict[str, Any]) -> dict[str, Any]:
    matrix = [[float(v) for v in row] for row in case["matrix"]]
    idf = [float(v) for v in case["idf"]]
    vector = [float(v) for v in case["vector"]]
    if not matrix or len(vector) != len(matrix) or len(idf) != len(matrix[0]):
        raise ValueError("operator shape mismatch")
    weighted = [[row[j] * idf[j] for j in range(len(idf))] for row in matrix]
    degrees = [max(sum(value * value for value in row), 1e-12) for row in weighted]
    scaled = [vector[i] / math.sqrt(degrees[i]) for i in range(len(vector))]
    feature = [sum(weighted[i][j] * scaled[i] for i in range(len(matrix))) for j in range(len(idf))]
    projected = [sum(weighted[i][j] * feature[j] for j in range(len(idf))) / math.sqrt(degrees[i]) for i in range(len(matrix))]
    return {"result": [_round(v) for v in projected], "degree": [_round(v) for v in degrees]}


def _edge_table(case: dict[str, Any]) -> tuple[dict[tuple[str, str], float], dict[str, float]]:
    weights: dict[tuple[str, str], float] = defaultdict(float)
    degree: dict[str, float] = defaultdict(float)
    for left, right, value in case["edges"]:
        a, b, weight = str(left), str(right), float(value)
        weights[(a, b)] += weight
        weights[(b, a)] += weight
        degree[a] += weight
        degree[b] += weight
    return weights, degree


def _local_move(case: dict[str, Any]) -> dict[str, Any]:
    weights, degree = _edge_table(case)
    communities = {str(k): str(v) for k, v in case["communities"].items()}
    resolution = float(case["resolution"])
    total = sum(degree.values())
    moves: list[dict[str, str]] = []
    for node in sorted(communities):
        current = communities[node]
        candidate_communities = sorted({communities[other] for a, other in weights if a == node} | {current})
        community_degree = {community: sum(degree[n] for n, label in communities.items() if label == community) for community in candidate_communities}
        def gain(community: str) -> float:
            internal = sum(weights.get((node, other), 0.0) for other, label in communities.items() if label == community)
            return internal - resolution * degree[node] * community_degree[community] / max(total, 1e-12)
        best = min(candidate_communities, key=lambda community: (-gain(community), community))
        if gain(best) > gain(current) + 1e-12:
            communities[node] = best
            moves.append({"node": node, "from": current, "to": best})
    return {"communities": communities, "moves": moves}


def _aggregate(case: dict[str, Any]) -> dict[str, Any]:
    refinement = {str(k): str(v) for k, v in case["refinement"].items()}
    edge_weights: dict[tuple[str, str], float] = defaultdict(float)
    for left, right, weight in case["edges"]:
        a, b = refinement[str(left)], refinement[str(right)]
        key = tuple(sorted((a, b)))
        edge_weights[key] += float(weight)
    rows = [[a, b, _round(weight)] for (a, b), weight in sorted(edge_weights.items())]
    members: dict[str, list[str]] = defaultdict(list)
    for node, group in refinement.items():
        members[group].append(node)
    return {"aggregate_edges": rows, "members": {key: sorted(value) for key, value in sorted(members.items())}}


def _mst(case: dict[str, Any]) -> dict[str, Any]:
    nodes = [str(v) for v in case["nodes"]]
    core = {str(k): float(v) for k, v in case["core_distance"].items()}
    edges = []
    for left, right, distance in case["distances"]:
        a, b = str(left), str(right)
        value = max(core[a], core[b], float(distance))
        edges.append((value, min(a, b), max(a, b)))
    parent = {node: node for node in nodes}
    def find(node: str) -> str:
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node
    selected = []
    for weight, left, right in sorted(edges):
        a, b = find(left), find(right)
        if a == b:
            continue
        parent[b] = a
        selected.append([left, right, _round(weight)])
        if len(selected) == len(nodes) - 1:
            break
    if len(selected) != len(nodes) - 1:
        raise ValueError("graph is disconnected")
    return {"mst_edges": selected, "total_weight": _round(sum(row[2] for row in selected))}


def _condensed_stability(case: dict[str, Any]) -> dict[str, Any]:
    min_size = int(case["min_cluster_size"])
    clusters = []
    for row in case["clusters"]:
        size = int(row["size"])
        if size < min_size:
            continue
        birth = float(row["birth_lambda"])
        deaths = [float(v) for v in row["point_exit_lambdas"]]
        stability = sum(max(0.0, value - birth) for value in deaths)
        clusters.append({"cluster_id": str(row["cluster_id"]), "stability": _round(stability), "size": size})
    clusters.sort(key=lambda row: (-row["stability"], row["cluster_id"]))
    selected: list[str] = []
    blocked: set[str] = set()
    parent = {str(k): (None if v is None else str(v)) for k, v in case["parent"].items()}
    for row in clusters:
        cluster = row["cluster_id"]
        if cluster in blocked:
            continue
        selected.append(cluster)
        ancestor = parent.get(cluster)
        while ancestor is not None:
            blocked.add(ancestor)
            ancestor = parent.get(ancestor)
    return {"clusters": clusters, "selected_cluster_ids": sorted(selected)}


def _api_filter(case: dict[str, Any]) -> dict[str, Any]:
    threshold = float(case["threshold"])
    accepted = []
    diagnostics = []
    for row in case["calls"]:
        gain = float(row["loss_without_call"]) - float(row["loss_with_call"])
        normalized = gain / max(int(row["prediction_tokens"]), 1)
        keep = normalized >= threshold and bool(row.get("parseable", True))
        diagnostics.append({"call_id": row["call_id"], "normalized_gain": _round(normalized), "accepted": keep})
        if keep:
            accepted.append(row["call_id"])
    return {"accepted_call_ids": accepted, "diagnostics": diagnostics}


def _interleave(case: dict[str, Any]) -> dict[str, Any]:
    tokens = list(case["tokens"])
    candidates = sorted(case["calls"], key=lambda row: (-float(row["score"]), int(row["start"]), str(row["call_id"])))
    occupied: set[int] = set()
    selected = []
    for row in candidates:
        span = set(range(int(row["start"]), int(row["end"])))
        if span & occupied:
            continue
        occupied |= span
        selected.append(row)
    output = tokens[:]
    for row in sorted(selected, key=lambda value: int(value["start"]), reverse=True):
        start, end = int(row["start"]), int(row["end"])
        output[start:end] = list(row["replacement_tokens"])
    return {"selected_call_ids": [row["call_id"] for row in sorted(selected, key=lambda value: int(value["start"]))], "tokens": output}


def _reflection_memory(case: dict[str, Any]) -> dict[str, Any]:
    capacity = int(case["capacity"])
    entries: dict[str, dict[str, Any]] = {}
    for index, trial in enumerate(case["trials"]):
        signature = str(trial["signature"])
        entries[signature] = {"signature": signature, "reflection": str(trial["reflection"]), "success": bool(trial["success"]), "last_trial": index}
    retained = sorted(entries.values(), key=lambda row: (row["success"], -row["last_trial"], row["signature"]))[:capacity]
    retained.sort(key=lambda row: row["last_trial"])
    return {"memory": retained, "signatures": [row["signature"] for row in retained]}


def _retry_controller(case: dict[str, Any]) -> dict[str, Any]:
    attempts = case["attempts"]
    max_attempts = int(case["max_attempts"])
    if not attempts:
        return {"decision": "retry", "next_attempt": 1, "memory_append": None}
    last = attempts[-1]
    if bool(last["success"]):
        decision = "stop_success"
    elif len(attempts) >= max_attempts:
        decision = "stop_budget"
    elif str(last["failure_signature"]) in {str(row["failure_signature"]) for row in attempts[:-1]}:
        decision = "stop_repeated_failure"
    else:
        decision = "retry"
    memory = None if last.get("reflection") in (None, "") else {"signature": str(last["failure_signature"]), "reflection": str(last["reflection"])}
    return {"decision": decision, "next_attempt": len(attempts) + (1 if decision == "retry" else 0), "memory_append": memory}


def _trajectory_parser(case: dict[str, Any]) -> dict[str, Any]:
    pattern = re.compile(r"^(Thought|Action|Observation|Final):\s*(.*)$")
    expected = "Thought"
    trajectory = []
    for line_number, line in enumerate(case["lines"], start=1):
        match = pattern.fullmatch(str(line))
        if not match:
            return {"valid": False, "error_line": line_number, "trajectory": trajectory}
        kind, content = match.groups()
        if kind == "Final":
            if expected not in {"Thought", "Action"} or line_number != len(case["lines"]):
                return {"valid": False, "error_line": line_number, "trajectory": trajectory}
            trajectory.append({"type": kind.lower(), "content": content})
            return {"valid": True, "error_line": None, "trajectory": trajectory}
        if kind != expected:
            return {"valid": False, "error_line": line_number, "trajectory": trajectory}
        trajectory.append({"type": kind.lower(), "content": content})
        expected = {"Thought": "Action", "Action": "Observation", "Observation": "Thought"}[kind]
    return {"valid": expected == "Thought", "error_line": None if expected == "Thought" else len(case["lines"]), "trajectory": trajectory}


def _react_loop(case: dict[str, Any]) -> dict[str, Any]:
    state = str(case["initial_state"])
    transitions = case["transitions"]
    observations = {str(k): str(v) for k, v in case["tool_observations"].items()}
    trace = []
    for step in range(int(case["max_steps"])):
        row = transitions.get(state)
        if row is None:
            return {"status": "invalid_state", "final": None, "trace": trace}
        if row["kind"] == "final":
            return {"status": "completed", "final": row["value"], "trace": trace}
        action = str(row["action"])
        if action not in observations:
            return {"status": "tool_error", "final": None, "trace": trace}
        observation = observations[action]
        trace.append({"step": step + 1, "state": state, "action": action, "observation": observation})
        state = str(row["next_by_observation"].get(observation, row["default_next"]))
    return {"status": "max_steps", "final": None, "trace": trace}


SOLVERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "NLP-LLM-01": _coarse_budget,
    "NLP-LLM-02": _iterative_compression,
    "NLP-LL2-01": _word_alignment,
    "NLP-LL2-02": _budgeted_reconstruction,
    "NLP-CSE-01": _context_scores,
    "NLP-CSE-02": _sentence_knapsack,
    "SE-DD-01": _ddmin,
    "SE-DD-02": _difference_isolation,
    "SE-CR-01": _pass_fixed_point,
    "SE-CR-02": _chunk_reduction,
    "SE-PE-01": _grammar_reduce,
    "SE-PE-02": _reduction_queue,
    "DATA-SNAP-01": _idf,
    "DATA-SNAP-02": _spectral_operator,
    "DATA-LEI-01": _local_move,
    "DATA-LEI-02": _aggregate,
    "DATA-HDB-01": _mst,
    "DATA-HDB-02": _condensed_stability,
    "AGENT-TF-01": _api_filter,
    "AGENT-TF-02": _interleave,
    "AGENT-RF-01": _reflection_memory,
    "AGENT-RF-02": _retry_controller,
    "AGENT-RA-01": _trajectory_parser,
    "AGENT-RA-02": _react_loop,
}


def solve(task_id: str, case: dict[str, Any]) -> dict[str, Any]:
    if task_id not in SOLVERS:
        raise KeyError(f"unknown task: {task_id}")
    return SOLVERS[task_id](json.loads(json.dumps(case)))


def generate_case(task_id: str, seed: str) -> dict[str, Any]:
    rng = _rng(task_id, seed)
    n = 5 + rng.randrange(3)
    if task_id == "NLP-LLM-01":
        segments = [{"name": f"s{i}", "importance": 1 + rng.randrange(9), "minimum": 1, "capacity": 3 + rng.randrange(5)} for i in range(4)]
        return {"segments": segments, "budget": min(sum(row["capacity"] for row in segments), 7 + rng.randrange(7))}
    if task_id == "NLP-LLM-02":
        count = 8
        targets = [6, 4]
        return {"round_scores": [[_round(rng.random()) for _ in range(count)] for _ in targets], "round_targets": targets, "forced": [rng.randrange(count)]}
    if task_id == "NLP-LL2-01":
        sizes = [1 + rng.randrange(3) for _ in range(4)]
        groups, cursor = [], 0
        for size in sizes:
            groups.append(list(range(cursor, cursor + size)))
            cursor += size
        return {"word_token_indices": groups, "word_labels": [rng.randrange(2) for _ in groups], "token_count": cursor}
    if task_id == "NLP-LL2-02":
        groups, cursor = [], 0
        for _ in range(6):
            size = 1 + rng.randrange(3)
            groups.append(list(range(cursor, cursor + size)))
            cursor += size
        return {"word_token_indices": groups, "word_scores": [_round(rng.random()) for _ in groups], "forced_words": [0], "token_budget": max(len(groups[0]), cursor // 2)}
    if task_id == "NLP-CSE-01":
        return {"sentence_vectors": [[rng.randrange(-3, 4) for _ in range(4)] for _ in range(n)], "query_vector": [rng.randrange(-3, 4) for _ in range(4)], "context_weight": 0.25}
    if task_id == "NLP-CSE-02":
        return {"lengths": [1 + rng.randrange(5) for _ in range(n)], "scores": [_round(0.1 + rng.random()) for _ in range(n)], "budget": 7 + rng.randrange(6)}
    if task_id == "SE-DD-01":
        items = [f"d{i}" for i in range(8)]
        return {"items": items, "required_failure_items": sorted(rng.sample(items, 2)), "unresolved_without": [items[0]] if rng.randrange(3) == 0 else []}
    if task_id == "SE-DD-02":
        common = [f"c{i}" for i in range(3)]
        delta = [f"x{i}" for i in range(6)]
        return {"passing": common, "failing": common + delta, "required_difference": sorted(rng.sample(delta, 2)), "unresolved_difference": []}
    if task_id == "SE-CR-01":
        return {"text": "aaaa bb cc", "passes": [{"name": "halve-a", "old": "aa", "new": "a"}, {"name": "drop-b", "old": "bb", "new": "b"}, {"name": "drop-c", "old": " cc", "new": ""}], "max_rounds": 8}
    if task_id == "SE-CR-02":
        items = [f"t{i}" for i in range(10)]
        return {"items": items, "required_failure_items": sorted(rng.sample(items, 2))}
    if task_id in {"SE-PE-01", "SE-PE-02"}:
        nodes = [{"id": "root", "parent": None, "symbol": "root", "depth": 0, "removable": False, "utility": 1.0}]
        for i in range(1, 7):
            nodes.append({"id": f"n{i}", "parent": "root" if i < 4 else f"n{1 + i % 3}", "symbol": f"s{i % 3}", "depth": 1 if i < 4 else 2, "removable": i % 2 == 0, "utility": _round(rng.random())})
        return {"nodes": nodes, "required_symbols": ["root", "s1"]} if task_id == "SE-PE-01" else {"nodes": nodes, "utility_threshold": 0.55}
    if task_id == "DATA-SNAP-01":
        return {"matrix": [[rng.randrange(2) for _ in range(5)] for _ in range(6)]}
    if task_id == "DATA-SNAP-02":
        matrix = [[rng.randrange(2) for _ in range(5)] for _ in range(6)]
        return {"matrix": matrix, "idf": [_round(0.5 + rng.random()) for _ in range(5)], "vector": [_round(rng.uniform(-1, 1)) for _ in range(6)]}
    if task_id == "DATA-LEI-01":
        nodes = [f"v{i}" for i in range(6)]
        edges = [[nodes[i], nodes[(i + 1) % len(nodes)], 1 + rng.randrange(3)] for i in range(len(nodes))]
        edges += [["v0", "v2", 2], ["v3", "v5", 2]]
        return {"edges": edges, "communities": {node: str(i // 2) for i, node in enumerate(nodes)}, "resolution": 1.0}
    if task_id == "DATA-LEI-02":
        nodes = [f"v{i}" for i in range(6)]
        edges = [[nodes[i], nodes[(i + 1) % 6], 1 + rng.randrange(3)] for i in range(6)]
        return {"edges": edges, "refinement": {node: f"g{i // 2}" for i, node in enumerate(nodes)}}
    if task_id == "DATA-HDB-01":
        nodes = [f"p{i}" for i in range(5)]
        distances = [[nodes[i], nodes[j], _round(0.1 + rng.random())] for i in range(5) for j in range(i + 1, 5)]
        return {"nodes": nodes, "core_distance": {node: _round(0.2 + rng.random() / 2) for node in nodes}, "distances": distances}
    if task_id == "DATA-HDB-02":
        return {"min_cluster_size": 3, "clusters": [{"cluster_id": "c0", "size": 7, "birth_lambda": 0.2, "point_exit_lambdas": [0.4, 0.6, 0.9]}, {"cluster_id": "c1", "size": 4, "birth_lambda": 0.5, "point_exit_lambdas": [0.7, 1.0, 1.2]}, {"cluster_id": "c2", "size": 2, "birth_lambda": 0.8, "point_exit_lambdas": [1.1]}], "parent": {"c0": None, "c1": "c0", "c2": "c0"}}
    if task_id == "AGENT-TF-01":
        return {"threshold": 0.05, "calls": [{"call_id": f"call{i}", "loss_without_call": _round(1 + rng.random()), "loss_with_call": _round(rng.random()), "prediction_tokens": 2 + rng.randrange(5), "parseable": rng.randrange(8) != 0} for i in range(6)]}
    if task_id == "AGENT-TF-02":
        return {"tokens": [f"t{i}" for i in range(10)], "calls": [{"call_id": "a", "start": 1, "end": 3, "score": 0.8, "replacement_tokens": ["<a>"]}, {"call_id": "b", "start": 2, "end": 5, "score": 0.9, "replacement_tokens": ["<b>"]}, {"call_id": "c", "start": 7, "end": 9, "score": 0.7, "replacement_tokens": ["<c>"]}]}
    if task_id == "AGENT-RF-01":
        return {"capacity": 3, "trials": [{"signature": f"e{rng.randrange(4)}", "reflection": f"r{i}", "success": rng.randrange(3) == 0} for i in range(7)]}
    if task_id == "AGENT-RF-02":
        count = 1 + rng.randrange(4)
        attempts = [{"success": False, "failure_signature": f"e{i % 3}", "reflection": f"adjust-{i}"} for i in range(count)]
        if rng.randrange(4) == 0:
            attempts[-1]["success"] = True
        return {"attempts": attempts, "max_attempts": 4}
    if task_id == "AGENT-RA-01":
        lines = ["Thought: inspect", "Action: lookup", "Observation: found", "Thought: answer", "Final: done"]
        if rng.randrange(5) == 0:
            lines[2] = "Thought: invalid order"
        return {"lines": lines}
    if task_id == "AGENT-RA-02":
        return {"initial_state": "s0", "max_steps": 4, "tool_observations": {"lookup": "ok", "check": "yes"}, "transitions": {"s0": {"kind": "action", "action": "lookup", "next_by_observation": {"ok": "s1"}, "default_next": "bad"}, "s1": {"kind": "action", "action": "check", "next_by_observation": {"yes": "done"}, "default_next": "bad"}, "done": {"kind": "final", "value": "accepted"}, "bad": {"kind": "final", "value": "rejected"}}}
    raise KeyError(task_id)


def build_registry(task_id: str, registry_id: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    cases = []
    expected = []
    for index in range(64):
        seed = f"fg1-{task_id}-{registry_id}-{index:03d}"
        payload = generate_case(task_id, seed)
        payload["_case_nonce"] = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]
        case_id = f"fg1-{task_id.lower()}-{registry_id.lower()}-{index:03d}"
        cases.append({"case_id": case_id, "seed": seed, "payload": payload})
        expected.append({"case_id": case_id, "output": solve(task_id, payload)})
    return cases, expected
