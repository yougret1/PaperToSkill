from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


RUN_ROOT = Path(__file__).resolve().parent

RETRIEVAL_ARTIFACTS = [
    "citation_search/stage1/retrieval/effectslice-citations-foundations.json",
    "citation_search/stage1/retrieval/effectslice-citations-skills.json",
    "citation_search/stage1/retrieval/effectslice-citations-reproduction.json",
    "citation_search/arxiv_exact.xml",
]

EXPECTED_ARXIV_IDS = {
    "2302.04761",
    "2310.05736",
    "2403.12968",
    "2504.01848",
    "2505.20662",
    "2509.06917",
    "2604.03964",
    "2604.05333",
    "2604.23853",
    "2605.10114",
    "2606.09316",
    "2606.17819",
}


def _entry(
    key: str,
    entry_type: str,
    title: str,
    author: str,
    year: int,
    date: str,
    purpose: str,
    source: str,
    identifier: str,
    **fields: str,
) -> dict[str, Any]:
    return {
        "key": key,
        "entry_type": entry_type,
        "title": title,
        "author": author,
        "year": year,
        "date": date,
        "purpose": purpose,
        "source": source,
        "identifier": identifier,
        "fields": fields,
    }


CITATIONS = [
    _entry(
        "zeller2002simplifying",
        "article",
        "Simplifying and Isolating Failure-Inducing Input",
        "Zeller, Andreas and Hildebrandt, Ralf",
        2002,
        "2002-02",
        "Foundational delta debugging and input minimization.",
        "https://api.crossref.org/works/10.1109/32.988498",
        "doi:10.1109/32.988498",
        journal="IEEE Transactions on Software Engineering",
        volume="28",
        number="2",
        pages="183--200",
        doi="10.1109/32.988498",
    ),
    _entry(
        "regehr2012creduce",
        "inproceedings",
        "Test-Case Reduction for C Compiler Bugs",
        "Regehr, John and Chen, Yang and Cuoq, Pascal and Eide, Eric and Ellison, Chucky and Yang, Xuejun",
        2012,
        "2012-06",
        "Structure-aware reduction and practical minimal test cases.",
        "https://api.crossref.org/works/10.1145/2254064.2254104",
        "doi:10.1145/2254064.2254104",
        booktitle="Proceedings of the 33rd ACM SIGPLAN Conference on Programming Language Design and Implementation",
        pages="335--346",
        doi="10.1145/2254064.2254104",
    ),
    _entry(
        "groce2016cause",
        "article",
        "Cause Reduction: Delta Debugging, Even without Bugs",
        "Groce, Alex and Alipour, Mohammad Amin and Zhang, Chaoqiang and Chen, Yang and Regehr, John",
        2016,
        "2016-03",
        "Reduction for preserving a general observed effect rather than a crash.",
        "https://api.crossref.org/works/10.1002/stvr.1574",
        "doi:10.1002/stvr.1574",
        journal="Software Testing, Verification and Reliability",
        volume="26",
        number="2",
        doi="10.1002/stvr.1574",
    ),
    _entry(
        "wellek2002equivalence",
        "book",
        "Testing Statistical Hypotheses of Equivalence",
        "Wellek, Stefan",
        2002,
        "2002-11-12",
        "Statistical basis for equivalence and noninferiority decisions.",
        "https://api.crossref.org/works/10.1201/9781420035964",
        "doi:10.1201/9781420035964",
        publisher="Chapman and Hall/CRC",
        doi="10.1201/9781420035964",
    ),
    _entry(
        "jiang2023llmlingua",
        "misc",
        "LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models",
        "Jiang, Huiqiang and Wu, Qianhui and Lin, Chin-Yew and Yang, Yuqing and Qiu, Lili",
        2023,
        "2023-10-09",
        "Prompt compression as a neighboring compact-context objective.",
        "citation_search/arxiv_exact.xml; https://arxiv.org/abs/2310.05736",
        "arxiv:2310.05736",
        eprint="2310.05736",
        archivePrefix="arXiv",
        primaryClass="cs.CL",
        url="https://arxiv.org/abs/2310.05736",
    ),
    _entry(
        "pan2024llmlingua2",
        "inproceedings",
        "LLMLingua-2: Data Distillation for Efficient and Faithful Task-Agnostic Prompt Compression",
        "Pan, Zhuoshi and Wu, Qianhui and Jiang, Huiqiang and Xia, Menglin and Luo, Xufang and Zhang, Jue and Lin, Qingwei and Ruhle, Victor and Yang, Yuqing and Lin, Chin-Yew and Zhao, H. Vicky and Qiu, Lili and Zhang, Dongmei",
        2024,
        "2024-03-19",
        "Faithfulness-oriented prompt compression and its evaluation boundary.",
        "citation_search/arxiv_exact.xml; https://api.crossref.org/works/10.18653/v1/2024.findings-acl.57",
        "doi:10.18653/v1/2024.findings-acl.57",
        booktitle="Findings of the Association for Computational Linguistics: ACL 2024",
        doi="10.18653/v1/2024.findings-acl.57",
        eprint="2403.12968",
        archivePrefix="arXiv",
    ),
    _entry(
        "shaposhnikov2026agenticskills",
        "misc",
        "A Framework for Evaluating Agentic Skills at Scale",
        "Shaposhnikov, Maksim and Fortuin, Nicolas and Stipcich, Simon and Gorinova, Maria I. and Heineike, Amy and Willoughby, Rob",
        2026,
        "2026-06-16",
        "Closest whole-skill marginal-utility evaluation framework.",
        "citation_search/arxiv_exact.xml; https://arxiv.org/abs/2606.17819",
        "arxiv:2606.17819",
        eprint="2606.17819",
        archivePrefix="arXiv",
        primaryClass="cs.AI",
        url="https://arxiv.org/abs/2606.17819",
    ),
    _entry(
        "shen2026skillfoundry",
        "misc",
        "SKILLFOUNDRY: Building Self-Evolving Agent Skill Libraries from Heterogeneous Scientific Resources",
        "Shen, Shuaike and Cheng, Wenduo and Ma, Mingqian and Turcan, Alistair and Zhang, Martin Jinye and Ma, Jian",
        2026,
        "2026-04-05",
        "Construction and validation of executable scientific skills.",
        "citation_search/arxiv_exact.xml; https://arxiv.org/abs/2604.03964",
        "arxiv:2604.03964",
        eprint="2604.03964",
        archivePrefix="arXiv",
        primaryClass="cs.AI",
        url="https://arxiv.org/abs/2604.03964",
    ),
    _entry(
        "pan2026anything2skill",
        "misc",
        "Anything2Skill: Compiling External Knowledge into Reusable Skills for Agents",
        "Pan, Qianjun and Yang, Yutao and Li, Junsong and Zhou, Jie and Chen, Kai and Li, Xin and Chen, Qin and He, Liang",
        2026,
        "2026-06-08",
        "Compilation of external evidence into reusable procedural artifacts.",
        "citation_search/arxiv_exact.xml; https://arxiv.org/abs/2606.09316",
        "arxiv:2606.09316",
        eprint="2606.09316",
        archivePrefix="arXiv",
        primaryClass="cs.AI",
        url="https://arxiv.org/abs/2606.09316",
    ),
    _entry(
        "yuan2026clawtrace",
        "misc",
        "ClawTrace: Cost-Aware Tracing for LLM Agent Skill Distillation",
        "Yuan, Boqin and Su, Yue and Song, Renchu and Yang, Sen and Qin, Jing",
        2026,
        "2026-04-26",
        "Trace-based, cost-aware skill distillation and pruning.",
        "citation_search/arxiv_exact.xml; https://arxiv.org/abs/2604.23853",
        "arxiv:2604.23853",
        eprint="2604.23853",
        archivePrefix="arXiv",
        primaryClass="cs.AI",
        url="https://arxiv.org/abs/2604.23853",
    ),
    _entry(
        "liu2026graphskills",
        "misc",
        "Graph-of-Skills: Dependency-Aware Structural Retrieval for Massive Agent Skills",
        "Liu, Dawei and Li, Zongxia and Du, Hongyang and Wu, Xiyang and Gui, Shihang and Kuang, Yongbei and Sun, Lichao",
        2026,
        "2026-04-07",
        "Dependency-aware retrieval of compact executable skill bundles.",
        "citation_search/arxiv_exact.xml; https://arxiv.org/abs/2604.05333",
        "arxiv:2604.05333",
        eprint="2604.05333",
        archivePrefix="arXiv",
        primaryClass="cs.AI",
        url="https://arxiv.org/abs/2604.05333",
    ),
    _entry(
        "meng2026skillrae",
        "misc",
        "SkillRAE: Agent Skill-Based Context Compilation for Retrieval-Augmented Execution",
        "Meng, Xiangcheng and Wang, Shu and Fang, Yixiang",
        2026,
        "2026-05-11",
        "Compact, grounded context compilation from skill libraries.",
        "citation_search/arxiv_exact.xml; https://arxiv.org/abs/2605.10114",
        "arxiv:2605.10114",
        eprint="2605.10114",
        archivePrefix="arXiv",
        primaryClass="cs.AI",
        url="https://arxiv.org/abs/2605.10114",
    ),
    _entry(
        "starace2025paperbench",
        "misc",
        "PaperBench: Evaluating AI's Ability to Replicate AI Research",
        "Starace, Giulio and Jaffe, Oliver and Sherburn, Dane and Aung, James and Chan, Jun Shern and Maksin, Leon and Dias, Rachel and Mays, Evan and Kinsella, Benjamin and Thompson, Wyatt and Heidecke, Johannes and Glaese, Amelia and Patwardhan, Tejal",
        2025,
        "2025-04-02",
        "Execution-verified benchmark for full research-paper replication.",
        "citation_search/arxiv_exact.xml; https://arxiv.org/abs/2504.01848",
        "arxiv:2504.01848",
        eprint="2504.01848",
        archivePrefix="arXiv",
        primaryClass="cs.AI",
        url="https://arxiv.org/abs/2504.01848",
    ),
    _entry(
        "zhao2025autoreproduce",
        "misc",
        "AutoReproduce: Automatic AI Experiment Reproduction with Paper Lineage",
        "Zhao, Xuanle and Sang, Zilin and Li, Yuxuan and Shi, Qi and Zhao, Weilun and Wang, Shuo and Zhang, Duzhen and Han, Xu and Liu, Zhiyuan and Sun, Maosong",
        2025,
        "2025-05-27",
        "End-to-end agentic research reproduction with paper lineage.",
        "citation_search/arxiv_exact.xml; https://arxiv.org/abs/2505.20662",
        "arxiv:2505.20662",
        eprint="2505.20662",
        archivePrefix="arXiv",
        primaryClass="cs.AI",
        url="https://arxiv.org/abs/2505.20662",
    ),
    _entry(
        "miao2025paper2agent",
        "misc",
        "Paper2Agent: Reimagining Research Papers as Interactive and Reliable AI Agents",
        "Miao, Jiacheng and Davis, Joe R. and Zhang, Yaohui and Pritchard, Jonathan K. and Zou, James",
        2025,
        "2025-09-08",
        "Paper-to-agent compilation and reliability-oriented validation.",
        "citation_search/arxiv_exact.xml; https://arxiv.org/abs/2509.06917",
        "arxiv:2509.06917",
        eprint="2509.06917",
        archivePrefix="arXiv",
        primaryClass="cs.AI",
        url="https://arxiv.org/abs/2509.06917",
    ),
    _entry(
        "schick2023toolformer",
        "misc",
        "Toolformer: Language Models Can Teach Themselves to Use Tools",
        "Schick, Timo and Dwivedi-Yu, Jane and Dessi, Roberto and Raileanu, Roberta and Lomeli, Maria and Hambro, Eric and Zettlemoyer, Luke and Cancedda, Nicola and Scialom, Thomas",
        2023,
        "2023-02-09",
        "Source paper for the API-call filtering reproduction task.",
        "citation_search/arxiv_exact.xml; https://arxiv.org/abs/2302.04761",
        "arxiv:2302.04761",
        eprint="2302.04761",
        archivePrefix="arXiv",
        primaryClass="cs.CL",
        url="https://arxiv.org/abs/2302.04761",
    ),
    _entry(
        "zhang2024snapatac2",
        "article",
        "A Fast, Scalable and Versatile Tool for Analysis of Single-Cell Omics Data",
        "Zhang, Kai and Zemke, Nathan R. and Armand, Ethan J. and Ren, Bing",
        2024,
        "2024-01",
        "Source paper for the matrix-free spectral embedding reproduction task.",
        "https://api.crossref.org/works/10.1038/s41592-023-02139-9",
        "doi:10.1038/s41592-023-02139-9",
        journal="Nature Methods",
        volume="21",
        pages="217--227",
        doi="10.1038/s41592-023-02139-9",
    ),
    _entry(
        "clopper1934binomial",
        "article",
        "The Use of Confidence or Fiducial Limits Illustrated in the Case of the Binomial",
        "Clopper, C. J. and Pearson, E. S.",
        1934,
        "1934",
        "Exact binomial confidence bounds used by the admission gate.",
        "https://api.crossref.org/works/10.1093/biomet/26.4.404",
        "doi:10.1093/biomet/26.4.404",
        journal="Biometrika",
        volume="26",
        number="4",
        pages="404--413",
        doi="10.1093/biomet/26.4.404",
    ),
    _entry(
        "holm1979sequential",
        "article",
        "A Simple Sequentially Rejective Multiple Test Procedure",
        "Holm, Sture",
        1979,
        "1979",
        "Family-wise error control for registered multiple comparisons.",
        "https://www.jstor.org/stable/4615733",
        "jstor:4615733",
        journal="Scandinavian Journal of Statistics",
        volume="6",
        number="2",
        pages="65--70",
        url="https://www.jstor.org/stable/4615733",
    ),
]


def _load_round(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "paper-search.results.v2":
        raise ValueError(f"unexpected paper-search schema: {path}")
    return {
        "query_id": payload["query_id"],
        "retrieved_at": payload["retrieved_at"],
        "evidence_quality": payload["evidence_quality"],
        "paper_count": len(payload["papers"]),
        "connector_status": {
            row["source"]: row["status"] for row in payload["connectors"]
        },
    }


def _validate_sources(root: Path) -> list[dict[str, Any]]:
    paths = [root / relative for relative in RETRIEVAL_ARTIFACTS]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise ValueError(f"citation retrieval artifacts are missing: {missing}")

    rounds = [_load_round(path) for path in paths[:3]]
    atom = {"a": "http://www.w3.org/2005/Atom"}
    arxiv_ids = {
        node.text.rsplit("/", 1)[-1].split("v", 1)[0]
        for node in ET.parse(paths[3]).findall("a:entry/a:id", atom)
        if node.text
    }
    missing_ids = sorted(EXPECTED_ARXIV_IDS - arxiv_ids)
    if missing_ids:
        raise ValueError(f"exact arXiv metadata is missing IDs: {missing_ids}")
    return rounds


def _render_entry(citation: dict[str, Any]) -> str:
    fields = {
        "title": citation["title"],
        "author": citation["author"],
        "year": str(citation["year"]),
        **citation["fields"],
    }
    lines = [f"@{citation['entry_type']}{{{citation['key']},"]
    lines.extend(f"  {name} = {{{value}}}," for name, value in fields.items())
    lines.append("}")
    return "\n".join(lines)


def build_citations(run_root: Path, output_dir: Path) -> dict[str, str]:
    root = Path(run_root).resolve()
    rounds = _validate_sources(root)
    keys = [citation["key"] for citation in CITATIONS]
    titles = [citation["title"].casefold() for citation in CITATIONS]
    if len(CITATIONS) != 19 or len(keys) != len(set(keys)) or len(titles) != len(set(titles)):
        raise ValueError("citation registry must contain 19 unique keys and titles")

    destination = Path(output_dir).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    bib_path = destination / "cached_citations.bib"
    progress_path = destination / "citations_progress.json"
    bib_path.write_text(
        "\n" + "\n\n".join(_render_entry(citation) for citation in CITATIONS) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    progress = {
        "schema_version": "effectslice-citation-progress.v1",
        "status": "complete",
        "completed_rounds": len(rounds),
        "entry_count": len(CITATIONS),
        "retrieval_artifacts": list(RETRIEVAL_ARTIFACTS),
        "search_rounds": rounds,
        "citations": [
            {
                name: citation[name]
                for name in (
                    "key",
                    "title",
                    "year",
                    "date",
                    "purpose",
                    "source",
                    "identifier",
                )
            }
            for citation in CITATIONS
        ],
        "limitations": [
            "Some broad-search connectors were rate-limited or timed out; exact arXiv IDs and DOI metadata were independently resolved for cited records.",
            "The bibliography supports a task-local methods paper and does not establish general EffectSlice effectiveness.",
        ],
    }
    progress_path.write_text(
        json.dumps(progress, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return {"bibtex": str(bib_path), "progress": str(progress_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build verified EffectSlice citations")
    parser.add_argument("--run-root", type=Path, default=RUN_ROOT)
    parser.add_argument("--output-dir", type=Path, default=RUN_ROOT)
    args = parser.parse_args()
    print(json.dumps(build_citations(args.run_root, args.output_dir), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
