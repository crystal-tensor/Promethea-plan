#!/usr/bin/env python3
"""Inject frozen 100-problem metadata into QuantumEDU Research.tsx."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


TYPE_BLOCK = """type ProblemMetadata = {
  disciplineSupergroup: string;
  disciplineCluster: string;
  sourceLineageGroup: string;
  sourceLineage: string;
  unresolvedAge: string;
  coreDifficulty: string;
  priorApproachesAndMilestones: string;
  frozenProjectPositioning: string;
};

"""


def q(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def metadata_block(records: list[dict[str, object]]) -> str:
    lines = ["const problemMetadata: Record<number, ProblemMetadata> = {"]
    for record in records:
        rid = int(record["id"])
        lines.extend(
            [
                f"  {rid}: {{",
                f"    disciplineSupergroup: {q(str(record['discipline_supergroup']))},",
                f"    disciplineCluster: {q(str(record['discipline_cluster']))},",
                f"    sourceLineageGroup: {q(str(record['source_lineage_group']))},",
                f"    sourceLineage: {q(str(record['source_lineage']))},",
                f"    unresolvedAge: {q(str(record['unresolved_age']))},",
                f"    coreDifficulty: {q(str(record['core_difficulty']))},",
                f"    priorApproachesAndMilestones: {q(str(record['prior_approaches_and_milestones']))},",
                f"    frozenProjectPositioning: {q(str(record['frozen_project_positioning']))},",
                "  },",
            ]
        )
    lines.append("};")
    return "\n".join(lines) + "\n\n"


def replace_between(text: str, start_pattern: str, end_pattern: str, replacement: str) -> str:
    pattern = re.compile(start_pattern + r".*?" + end_pattern, re.DOTALL)
    updated, count = pattern.subn(lambda _match: replacement + end_pattern, text, count=1)
    if count != 1:
        raise ValueError(f"Could not replace block starting with {start_pattern!r}")
    return updated


def update_research_tsx(target: Path, catalog: dict[str, object]) -> None:
    text = target.read_text(encoding="utf-8")
    records = catalog["records"]
    if not isinstance(records, list) or len(records) != 100:
        raise ValueError("Catalog must contain exactly 100 records")

    if "type ProblemMetadata = {" in text:
        text = re.sub(
            r"type ProblemMetadata = \{\n.*?\};\n\n",
            TYPE_BLOCK,
            text,
            count=1,
            flags=re.DOTALL,
        )
    else:
        anchor = "type TopTrack = {"
        text = text.replace(anchor, TYPE_BLOCK + anchor, 1)

    block = metadata_block(records)
    if "const problemMetadata: Record<number, ProblemMetadata> = {" in text:
        text = replace_between(
            text,
            r"const problemMetadata: Record<number, ProblemMetadata> = \{",
            r"function problemBrief",
            block,
        )
    else:
        text = text.replace("function problemBrief", block + "function problemBrief", 1)

    new_problem_brief = """function problemBrief(problem: Problem) {
  const topTrack = topTracks.find((track) => track.problemId === problem.id);
  const dossier = topTrack ? topDossiers[topTrack.bId] : undefined;
  const metadata = problemMetadata[problem.id];
  const categoryBrief = categoryBriefs[problem.category];
  const categoryEvidence = categoryEvidenceFrames[problem.category];
  const metadataPrior = metadata?.priorApproachesAndMilestones
    ? [metadata.priorApproachesAndMilestones]
    : categoryEvidence.priorRoutes;
  const metadataMilestone = metadata?.frozenProjectPositioning
    ? [metadata.frozenProjectPositioning]
    : categoryEvidence.milestones;

  return {
    disciplineSupergroup: metadata?.disciplineSupergroup ?? problem.category.replace(/^[A-J]\\.\\s*/, ''),
    disciplineCluster: metadata?.disciplineCluster ?? problem.category.replace(/^[A-J]\\.\\s*/, ''),
    sourceLineageGroup: metadata?.sourceLineageGroup ?? 'Research tradition',
    source: dossier?.proposedBy ?? metadata?.sourceLineage ?? categoryEvidence.source,
    age: dossier?.unresolvedAge ?? metadata?.unresolvedAge ?? categoryEvidence.age,
    blocker: dossier?.difficulty ?? metadata?.coreDifficulty ?? categoryBrief.blocker,
    move: dossier?.ourRoute ?? metadata?.frozenProjectPositioning ?? categoryBrief.researchMove,
    priorRoutes: dossier?.priorRoutes ?? metadataPrior,
    milestones: dossier?.milestones ?? metadataMilestone,
    completionProcess: dossier?.completionProcess ?? categoryEvidence.completionProcess,
  };
}

"""
    text = replace_between(
        text,
        r"function problemBrief\(problem: Problem\) \{",
        r"const heroModules",
        new_problem_brief,
    )

    text = text.replace(
        "100 个世界级难题、Top 10 攻关方向、",
        "100 个世界级难题冻结版、Top 10 攻关方向、",
        1,
    )
    text = text.replace(
        '<Metric label="Current Gate" value="B7/T8" tone="border-lime-300/40" />',
        '<Metric label="Catalog Lock" value="100-Lock" tone="border-lime-300/40" />',
        1,
    )
    text = text.replace(
        "  '  research/problem_catalog_100.md',\n",
        "  '  research/problem_catalog_100.md',\n  '  research/problem_catalog_100.json',\n",
        1,
    )
    text = text.replace(
        "['Current phase', 'B1 -> B7'],\n                ['Latest gate', 'T-B7-008'],\n                ['Next gate', 'T-B7-009'],",
        "['Current phase', '100 catalog frozen'],\n                ['Latest gate', 'B2 same-hardware schedule'],\n                ['Next gate', 'B1-B10 technical gates'],",
        1,
    )
    text = text.replace(
        "B1-B10 技术门槛、多智能体 PR 协作协议，以及从技术证据到论文、专利、融资、工具化的后置路径。",
        "B1-B10 技术门槛、多智能体 PR 协作协议，以及从技术证据到论文、专利、融资、工具化的后置路径。",
        1,
    )
    text = text.replace(
        "这不是宣称“官方世界 Top100”，而是一个可审计候选池：从数学公开难题、量子计算核心瓶颈、\n"
        "                工程挑战、生命科学、气候安全、密码安全和长期文明风险中抽取，并允许研究者提交 PR 修正排序和史料。",
        "这不是宣称“官方世界 Top100”，而是一个冻结的研究候选池：从数学公开难题、量子计算核心瓶颈、\n"
        "                工程挑战、生命科学、气候安全、密码安全和长期文明风险中抽取。100 问题目录到此停止扩展和重排，后续 PR 只接受史料勘误；真正研究投入转入 B1-B10 技术攻关。",
        1,
    )
    text = text.replace(
        "  { bId: 'B2', problemId: 22, title: '低开销量子纠错', lane: 'Technical system spine', maturity: 27, status: 'Stim/PyMatching baseline + real biased schedule sweep: candidate hits +4, volume win 0。', nextGate: 'Same-hardware schedule/code candidate with Wilson-bounded volume reduction.', icon: ShieldCheck },",
        "  { bId: 'B2', problemId: 22, title: '低开销量子纠错', lane: 'Technical system spine', maturity: 31, status: 'Stim/PyMatching baseline + biased sweep 后，same-hardware reduced-round schedule candidate 首次给出 Wilson target-volume positive diagnostic：120 configs / 360,000 shots，candidate-met 22 -> 30，22 个 volume-improved rows，max reduction 3.0x。', nextGate: 'Stress-test reduced-round candidate with larger shots, more distances, and noise-mismatch; require non-aggressive or physically motivated variant to survive.', icon: ShieldCheck },",
        1,
    )
    text = text.replace(
        "  { bId: 'B7', problemId: 21, title: '容错架构 co-design', lane: 'Technical system spine', maturity: 46, status: '最新边界：w8_21 same-skeleton exact small-block synthesis 做了 55 个固定角候选、每个 16 seeds，0 个通过；最佳 a=pi/2 残差 3.936e-02，本地 rank=5。', nextGate: 'T-B7-009: broaden beyond same skeleton，给出 <5 arbitrary rotations 的重写或更强 minimality note。', icon: Network },",
        "  { bId: 'B7', problemId: 21, title: '容错架构 co-design', lane: 'Technical system spine', maturity: 47, status: 'w8_21 已完成 same-skeleton、broad two-CNOT、Euler-local two-CNOT、three-CNOT 四轮搜索，累计 43,480 optimizer runs，0 exact candidate；当前结论是 scoped minimality note，不声明全局 KAK 下界。', nextGate: 'Move away from w8_21 local rewrite; advance B1/B2/B7 only through mechanisms that survive STV ledger.', icon: Network },",
        1,
    )

    old_search = """      const queryMatches =
        !normalized ||
        `${problem.id} ${problem.title} ${problem.desc} ${problem.category}`.toLowerCase().includes(normalized);
"""
    new_search = """      const metadata = problemMetadata[problem.id];
      const searchable = `${problem.id} ${problem.title} ${problem.desc} ${problem.category} ${metadata?.disciplineSupergroup ?? ''} ${metadata?.disciplineCluster ?? ''} ${metadata?.sourceLineageGroup ?? ''} ${metadata?.sourceLineage ?? ''} ${metadata?.coreDifficulty ?? ''} ${metadata?.priorApproachesAndMilestones ?? ''}`;
      const queryMatches = !normalized || searchable.toLowerCase().includes(normalized);
"""
    text = text.replace(old_search, new_search, 1)

    old_detail = """                      <div>
                        <div className="font-mono text-[10px] uppercase tracking-normal text-cyan-200">谁提出 / 来源</div>
                        <p className="mt-1 text-xs leading-5 text-zinc-500">{detail.source}</p>
                      </div>
"""
    new_detail = """                      <div>
                        <div className="font-mono text-[10px] uppercase tracking-normal text-lime-200">学科组群</div>
                        <p className="mt-1 text-xs leading-5 text-zinc-500">{detail.disciplineSupergroup}</p>
                        <p className="mt-1 text-[11px] leading-4 text-zinc-600">{detail.disciplineCluster}</p>
                      </div>
                      <div>
                        <div className="font-mono text-[10px] uppercase tracking-normal text-fuchsia-200">来源组群</div>
                        <p className="mt-1 text-xs leading-5 text-zinc-500">{detail.sourceLineageGroup}</p>
                      </div>
                      <div>
                        <div className="font-mono text-[10px] uppercase tracking-normal text-cyan-200">谁提出 / 来源</div>
                        <p className="mt-1 text-xs leading-5 text-zinc-500">{detail.source}</p>
                      </div>
"""
    text = text.replace(old_detail, new_detail, 1)
    duplicate_detail = """                      <div>
                        <div className="font-mono text-[10px] uppercase tracking-normal text-lime-200">学科组群</div>
                        <p className="mt-1 text-xs leading-5 text-zinc-500">{detail.disciplineCluster}</p>
                      </div>
                      <div>
                        <div className="font-mono text-[10px] uppercase tracking-normal text-lime-200">学科组群</div>
                        <p className="mt-1 text-xs leading-5 text-zinc-500">{detail.disciplineSupergroup}</p>
                        <p className="mt-1 text-[11px] leading-4 text-zinc-600">{detail.disciplineCluster}</p>
                      </div>
"""
    normalized_detail = """                      <div>
                        <div className="font-mono text-[10px] uppercase tracking-normal text-lime-200">学科组群</div>
                        <p className="mt-1 text-xs leading-5 text-zinc-500">{detail.disciplineSupergroup}</p>
                        <p className="mt-1 text-[11px] leading-4 text-zinc-600">{detail.disciplineCluster}</p>
                      </div>
"""
    text = text.replace(duplicate_detail, normalized_detail, 1)
    source_group_detail = """                      <div>
                        <div className="font-mono text-[10px] uppercase tracking-normal text-fuchsia-200">来源组群</div>
                        <p className="mt-1 text-xs leading-5 text-zinc-500">{detail.sourceLineageGroup}</p>
                      </div>
"""
    text = text.replace(
        normalized_detail + source_group_detail + normalized_detail + source_group_detail,
        normalized_detail + source_group_detail,
        1,
    )
    duplicate_pair_pattern = re.compile(
        r"(?P<pair>\s{22}<div>\n"
        r"\s{24}<div className=\"font-mono text-\[10px\] uppercase tracking-normal text-lime-200\">学科组群</div>\n"
        r"\s{24}<p className=\"mt-1 text-xs leading-5 text-zinc-500\">\{detail\.disciplineSupergroup\}</p>\n"
        r"\s{24}<p className=\"mt-1 text-\[11px\] leading-4 text-zinc-600\">\{detail\.disciplineCluster\}</p>\n"
        r"\s{22}</div>\n"
        r"\s{22}<div>\n"
        r"\s{24}<div className=\"font-mono text-\[10px\] uppercase tracking-normal text-fuchsia-200\">来源组群</div>\n"
        r"\s{24}<p className=\"mt-1 text-xs leading-5 text-zinc-500\">\{detail\.sourceLineageGroup\}</p>\n"
        r"\s{22}</div>\n)(?P=pair)",
    )
    text = duplicate_pair_pattern.sub(r"\g<pair>", text, count=1)

    target.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=Path("research/problem_catalog_100.json"))
    parser.add_argument(
        "--target",
        type=Path,
        default=Path("/Users/avalok/work/QuantumEDU/website/src/pages/Research.tsx"),
    )
    args = parser.parse_args()

    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    update_research_tsx(args.target, catalog)
    print(f"updated {args.target}")


if __name__ == "__main__":
    main()
