from __future__ import annotations

from typing import Any


PAPER_EVIDENCE: dict[str, dict[str, Any]] = {
    "nlp_llmlingua": {
        "upstream_sha256": "0cd06ff6bf440d4a560937195c03dc56a1234ede8eec48129164c940262c90d8",
        "url": "https://aclanthology.org/2023.emnlp-main.825.pdf",
        "sections": [
            "Section 4.1, Budget Controller: the coarse-to-fine controller assigns different compression ratios to instruction, demonstrations, and the question under a target prompt budget.",
            "Section 4.2, Iterative Token-level Prompt Compression: token importance is estimated conditionally and tokens are pruned over iterations while the retained sequence preserves source order.",
        ],
    },
    "nlp_llmlingua2": {
        "upstream_sha256": "8c0fcd9baa621ef7951c45838eefe841356a8d6e1eb025cecd92373930f536d9",
        "url": "https://aclanthology.org/2024.findings-acl.57.pdf",
        "sections": [
            "Sections 3.1 and 4.1: compression is formulated as token classification, with labels distilled at word level and aligned back to the original tokenizer representation.",
            "Section 4.2, Compression Strategy: word decisions are reconstructed into retained token indices and a budgeted sequence in original order, with forced material preserved.",
        ],
    },
    "nlp_context_sentence_compression": {
        "upstream_sha256": "f70ceed61b3f734216c6fa0a29f5fc0fdf4cda42a3fe91778862c6b0f41a66baf",
        "url": "https://aclanthology.org/N19-1172.pdf",
        "sections": [
            "Section 3.3, Context-aware sentence encoding: a sentence representation is combined with neighboring context so its salience is not evaluated in isolation.",
            "Section 3.4, Inference: sentence-level scores are converted to a length-constrained extract, requiring a deterministic selection rule when several subsets have equal utility.",
        ],
    },
    "se_delta_debugging": {
        "upstream_sha256": "7ed0c812e1b3212f3956f5a624ac9103a00468ab665cae00784520d866e11c8aa",
        "url": "https://www.st.cs.uni-saarland.de/publications/files/zeller-esec-1999.pdf",
        "sections": [
            "The ddmin procedure repeatedly partitions a failing configuration, tests subsets and complements, adapts granularity, and treats UNRESOLVED as distinct from PASS and FAIL.",
            "Difference isolation starts from a passing and a failing configuration, operates on their difference, and returns a 1-minimal failure-inducing change under the registered oracle.",
        ],
    },
    "se_creduce": {
        "upstream_sha256": "a351d4eba11d7c167a5fd801b4b886dffde78b7c85566d7514d83547e42da360",
        "url": "https://embed.cs.utah.edu/creduce/pldi14_creduce.pdf",
        "sections": [
            "Sections 3.2 and 4 describe reduction as repeated passes whose accepted transformations are scheduled again until a global fixed point is reached.",
            "Generalized delta debugging removes chunks at an adaptive granularity, keeps a change only when the interestingness condition survives, and terminates at a locally irreducible result.",
        ],
    },
    "se_perses": {
        "upstream_sha256": "19c1beaccabf665ea1e60f943754e47d95cb50694ea0f4289e3cac92fd72df2c",
        "url": "https://web.cs.ucdavis.edu/~su/publications/icse18-perses.pdf",
        "sections": [
            "Section 4.2 reduces a program through grammar-valid parse-tree transformations, attempting deeper nodes first while preserving syntactic validity and the test property.",
            "Section 4.5 uses a fixpoint reduction mode: successful tree changes update the work queue so newly reducible ancestors and neighboring nodes are reconsidered.",
        ],
    },
    "data_snapatac2": {
        "upstream_sha256": "34ac99920bd570befad0993bb5f0bf0e66444ef09e4a670fcdc51e58815c56a7",
        "url": "https://doi.org/10.1038/s41592-023-02139-9",
        "sections": [
            "The spectral workflow applies inverse-document-frequency weighting to a sparse cell-by-feature matrix and derives normalization degrees from the weighted representation.",
            "The dimensionality-reduction implementation exposes a matrix-free spectral operator, applying the normalized product to a vector without materializing the dense cell-by-cell matrix.",
        ],
    },
    "data_leiden": {
        "upstream_sha256": "49d6a4d5092f68ef7a43fabb1975364a114ec76d21d2ef9ce738007f003ee58a",
        "url": "https://www.nature.com/articles/s41598-019-41695-z.pdf",
        "sections": [
            "Section III describes the fast local-moving phase: nodes are considered, gains for neighboring communities are evaluated, and a positive best move is accepted with deterministic bookkeeping.",
            "The Leiden algorithm alternates local moving, refinement, and aggregation; refined communities become aggregate nodes and edge weights are summed between their memberships.",
        ],
    },
    "data_hdbscan": {
        "upstream_sha256": "9338398c56bb6a231606af02729c41bee259aafdbddab2d6e5b68ee43400a960d",
        "auxiliary_sha256": "2733b5719400c9cff671d417ed363b41c1742347f7a896d12778f5e4ff11edb1",
        "url": "https://www.theoj.org/joss-papers/joss.00205/10.21105.joss.00205.pdf",
        "auxiliary_url": "https://hdbscan.readthedocs.io/en/latest/how_hdbscan_works.html",
        "sections": [
            "The implementation guide defines mutual-reachability distance as the maximum of the two core distances and the pairwise distance, then builds a deterministic minimum spanning tree.",
            "The hierarchy is condensed using a minimum cluster size; cluster stability integrates point persistence above birth lambda and supports a deterministic flat-cluster selection.",
        ],
    },
    "agent_toolformer": {
        "upstream_sha256": "1fa619f443e107690b9fb722a72ab361825cfda5346436c90cb23acb3c7bfbb6",
        "url": "https://arxiv.org/pdf/2302.04761",
        "sections": [
            "The filtering stage compares language-model loss with and without each sampled API call over subsequent tokens and retains calls whose normalized improvement exceeds a threshold.",
            "Accepted calls are inserted into the token sequence in source order; overlapping candidates need an explicit score and position tie rule so one deterministic interleaving is produced.",
        ],
    },
    "agent_reflexion": {
        "upstream_sha256": "d9b56dbbc440b5fe1b45c63b56e90ba9f856acbf1c896153679a312de9ffb6ef",
        "url": "https://arxiv.org/pdf/2303.11366",
        "sections": [
            "Reflexion stores natural-language reflections from prior trials in episodic memory; bounded memory requires deterministic deduplication and retention of recent diagnostic failures.",
            "The trial loop acts, evaluates feedback, reflects after failure, and retries subject to an attempt budget; success, exhaustion, and repeated failure are distinct stopping states.",
        ],
    },
    "agent_react": {
        "upstream_sha256": "f285b0971ae4a790e402fb93966bed3adde2cf0a04977d08b2b40d6ab0cace69",
        "url": "https://arxiv.org/pdf/2210.03629",
        "sections": [
            "ReAct trajectories interleave Thought, Action, and Observation records before a terminal answer; a parser must enforce the ordering and reject malformed or premature records.",
            "The controller dispatches an action, records the tool observation, selects the next reasoning state, and stops on a final answer, tool error, invalid state, or registered step budget.",
        ],
    },
}


TASK_RULES: dict[str, list[str]] = {
    "NLP-LLM-01": ["Initialize every segment at its minimum quota.", "Reject budgets below the quota sum or above total capacity.", "While budget remains, give one token to the segment maximizing importance divided by its next allocated position.", "Break equal priorities by original segment order.", "Return allocations, the name mapping, and the conserved total."],
    "NLP-LLM-02": ["Begin with all original token indices active.", "At each round, rank only currently active indices by descending supplied score.", "Insert forced indices before filling remaining positions.", "Preserve original order in every retained mask and reject infeasible targets.", "Return the per-round masks and the final retained indices."],
    "NLP-LL2-01": ["Require one word label for every registered word group.", "Broadcast each word label to every token index in that group.", "Reject overlapping, out-of-range, or uncovered token indices.", "Keep token indices whose broadcast label equals one.", "Return the full token-label vector and retained indices."],
    "NLP-LL2-02": ["Treat a word group as indivisible when accounting token cost.", "Select forced words first and reject an infeasible forced set.", "Rank remaining words by descending supplied score and then source position.", "Accept a word only when its entire token group fits the residual budget.", "Return words and tokens in original order with exact token usage."],
    "NLP-CSE-01": ["Compute cosine similarity between each sentence vector and the query.", "Use zero similarity if either norm is zero.", "For each position average the available immediate-neighbor similarities.", "Blend own and neighbor scores using the registered context weight.", "Round scores and rank by descending score then source index."],
    "NLP-CSE-02": ["Enumerate sentence inclusion with a zero-one dynamic program over token cost.", "Never split a sentence or exceed the budget.", "Maximize summed salience.", "Break equal utility by fewer used tokens and then lexicographic source indices.", "Return selected indices, used tokens, and summed score."],
    "SE-DD-01": ["Require the initial configuration to produce FAIL.", "Partition at the current granularity and test subsets before complements.", "Only FAIL permits reduction; PASS and UNRESOLVED do not.", "Decrease granularity after reduction and otherwise double it up to current size.", "Return the 1-minimal failure, test count, and terminal outcome."],
    "SE-DD-02": ["Compute the ordered change set present in failing but absent from passing.", "Run ddmin only on this difference.", "Preserve the registered PASS/FAIL/UNRESOLVED oracle semantics.", "Retain source order through every subset and complement.", "Return the isolated difference and number of tests."],
    "SE-CR-01": ["Apply passes in their registered order.", "Each pass performs at most its first eligible rewrite per sweep.", "Record only passes that change the artifact.", "Repeat full sweeps until none changes or the round budget is consumed.", "Return the artifact, application trace, and fixed-point flag."],
    "SE-CR-02": ["Start chunk removal at granularity two.", "Try chunks from left to right and accept removal only if required failure items remain.", "Restart after an accepted removal with slightly coarser granularity.", "Double granularity when no removal succeeds and stop at singleton granularity.", "Return the reduced items, attempt count, and an explicit one-minimal check."],
    "SE-PE-01": ["Consider deeper parse-tree nodes before shallower nodes.", "Never remove the root, a required symbol, or a node with retained children.", "Tentatively remove a node only if all required symbols remain represented.", "Use node ID as the stable tie break at equal depth.", "Return sorted retained IDs and the actual removal order."],
    "SE-PE-02": ["Initialize a queue in descending depth and stable node-ID order.", "Skip nodes already removed.", "Remove only a removable leaf whose utility is at most the threshold.", "After removal enqueue its retained parent for reconsideration.", "Return retained IDs and the complete visit order."],
    "DATA-SNAP-01": ["Validate a nonempty rectangular matrix.", "For each feature count rows with a nonzero entry.", "Compute IDF as log(1 + number_of_rows / (1 + document_frequency)).", "Multiply every entry by its feature IDF and sum weighted rows for degree.", "Round and return IDF, weighted matrix, and row degrees."],
    "DATA-SNAP-02": ["Multiply each feature column by its supplied IDF.", "Define each row degree as the squared norm with a positive numerical floor.", "Apply inverse square-root degree scaling to the input vector.", "Compute X times X-transpose through two sparse-style matrix-vector products and rescale rows.", "Return the rounded operator result and degrees without constructing a pairwise matrix."],
    "DATA-LEI-01": ["Build symmetric weighted adjacency and node degrees.", "Visit nodes in stable node-ID order.", "Evaluate the registered resolution-adjusted gain for neighboring communities plus the current one.", "Move only on a strictly positive improvement and break ties by community ID.", "Update labels immediately and return labels plus the ordered move ledger."],
    "DATA-LEI-02": ["Map each original node to exactly one refined community.", "Map every edge endpoint through that refinement.", "Canonicalize each aggregate endpoint pair so undirected duplicates coincide.", "Sum all weights for each aggregate pair including self-loops.", "Return sorted aggregate edges and sorted membership lists."],
    "DATA-HDB-01": ["For each pair compute mutual reachability as max(core_left, core_right, distance).", "Canonicalize undirected endpoints.", "Sort by reachability then endpoint IDs.", "Run Kruskal with deterministic union-find until n minus one edges are selected.", "Reject disconnected inputs and return selected edges plus total weight."],
    "DATA-HDB-02": ["Drop clusters smaller than the minimum cluster size.", "For each retained cluster sum max(0, exit_lambda - birth_lambda) over its points.", "Rank clusters by decreasing stability and cluster ID.", "Select a cluster only when no already selected descendant blocks it, then block its ancestors.", "Return all retained stability rows and sorted selected IDs."],
    "AGENT-TF-01": ["For each call subtract loss with the call from loss without it.", "Normalize gain by at least one prediction token.", "Require both parseability and normalized gain at or above threshold.", "Keep diagnostics in supplied call order.", "Return accepted call IDs and rounded per-call diagnostics."],
    "AGENT-TF-02": ["Rank candidates by descending score, start position, then call ID.", "Greedily reject any span overlapping an already selected span.", "Order accepted calls by source start for reporting.", "Apply replacements from right to left so earlier offsets do not shift.", "Return selected IDs and the exact interleaved token stream."],
    "AGENT-RF-01": ["Process trials in chronological order.", "Deduplicate memory by failure signature, retaining the newest reflection.", "When capacity binds, prioritize failures before successes, then recency and signature.", "Restore chronological order in the final memory.", "Return complete retained entries and their signatures."],
    "AGENT-RF-02": ["With no prior attempt request attempt one.", "Stop immediately after success.", "Stop on the registered attempt budget or a repeated failure signature.", "Otherwise request exactly the next attempt.", "Append a nonempty reflection with its signature and return decision, next index, and memory update."],
    "AGENT-RA-01": ["Parse only complete Thought, Action, Observation, or Final records.", "Require Thought then Action then Observation for each nonterminal cycle.", "Permit Final only at the end and only at a reasoning boundary.", "On the first violation return its one-based line and the valid prefix.", "Return lowercase typed trajectory records and an explicit validity flag."],
    "AGENT-RA-02": ["Start at the registered initial state.", "A final state terminates without a tool call.", "An action state dispatches its named tool and records the exact observation.", "Select the observation-specific successor or the default; distinguish missing tools and states.", "Stop on completion or max steps and return status, final value, and trace."],
}


def atom_texts(task: dict[str, Any]) -> list[str]:
    task_id = str(task["task_id"])
    rules = TASK_RULES[task_id]
    contracts = ", ".join(str(value) for value in task["hard_contracts"])
    return [
        f"Implement `{task['name']}` through `solve(case)` for this bounded objective: {task['bounded_objective']}",
        f"Stay inside this mechanism boundary: {task['mechanism_boundary']} Validate every required field before computing a result.",
        *rules,
        f"Treat these registered properties as hard contracts rather than soft preferences: {contracts}.",
        "Use only quantities present in the case payload. Do not call a language model, network service, random generator, wall clock, or environment-dependent resource.",
        "Preserve every source identifier needed to audit the decision, and compute aggregate values from the returned primitive decisions rather than from a second approximation.",
        "Do not mutate the input. All ranking and traversal ties use the source position or identifier specified above; never depend on hash-map iteration.",
        "Return only JSON-serializable values with the exact named fields. Raise ValueError for an infeasible or structurally invalid case instead of silently repairing it.",
    ]
