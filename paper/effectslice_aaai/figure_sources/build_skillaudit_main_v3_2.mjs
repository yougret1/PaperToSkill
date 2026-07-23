import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Presentation, PresentationFile, layers, shape, text } from "@oai/artifact-tool";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const OUT = process.env.SKILLAUDIT_OUT ?? path.join(SCRIPT_DIR, "rendered", "v3-2");
const ICON_DEPENDENCY = path.join(SCRIPT_DIR, "assets", "skillaudit_icon_dependency_gpt.png");
const ICON_FREEZE = path.join(SCRIPT_DIR, "assets", "skillaudit_icon_freeze_gpt.png");
const ICON_EVIDENCE = path.join(SCRIPT_DIR, "assets", "skillaudit_icon_evidence_gpt.png");

const C = {
  ink: "#17212B",
  muted: "#637080",
  line: "#AEB9C5",
  soft: "#F3F5F7",
  blue: "#3578E5",
  blueDark: "#174A87",
  blueSoft: "#EAF2FF",
  cyan: "#55BFE6",
  cyanSoft: "#E9F8FD",
  green: "#239B63",
  greenSoft: "#EAF8F1",
  red: "#D85B62",
  redSoft: "#FFF0F1",
  white: "#FFFFFF",
};

function t(value, name, left, top, width, height, size, opt = {}) {
  return text([value], {
    name,
    position: { left, top },
    width,
    height,
    style: {
      fontSize: `${size}px`,
      typeface: "Arial",
      color: opt.color ?? C.ink,
      bold: opt.bold ?? false,
      alignment: opt.alignment ?? "center",
      verticalAlignment: opt.verticalAlignment ?? "middle",
      autoFit: "shrinkText",
      wrap: "square",
      insets: { top: 0, right: 0, bottom: 0, left: 0 },
    },
  });
}

function rect(name, left, top, width, height, fill, stroke = "none", strokeWidth = 0) {
  return shape({
    name,
    geometry: "rect",
    position: { left, top },
    width,
    height,
    fill,
    line: { style: "solid", fill: stroke, width: strokeWidth },
  });
}

function round(name, left, top, width, height, fill, stroke = "none", strokeWidth = 0) {
  return shape({
    name,
    geometry: "roundRect",
    position: { left, top },
    width,
    height,
    fill,
    line: { style: "solid", fill: stroke, width: strokeWidth },
    borderRadius: "rounded-lg",
  });
}

function circle(name, left, top, size, fill, stroke = "none", strokeWidth = 0) {
  return shape({
    name,
    geometry: "ellipse",
    position: { left, top },
    width: size,
    height: size,
    fill,
    line: { style: "solid", fill: stroke, width: strokeWidth },
  });
}

function line(name, left, top, width, color = C.line, strokeWidth = 2, dashed = false) {
  return shape({
    name,
    geometry: "straightConnector1",
    position: { left, top },
    width,
    height: 0.01,
    fill: "none",
    line: { style: dashed ? "dash" : "solid", fill: color, width: strokeWidth },
  });
}

function verticalLine(name, left, top, height, color = C.line, strokeWidth = 1, dashed = true) {
  return shape({
    name,
    geometry: "straightConnector1",
    position: { left, top },
    width: 0.01,
    height,
    fill: "none",
    line: { style: dashed ? "dash" : "solid", fill: color, width: strokeWidth },
  });
}

function arrow(nodes, name, x1, y, x2, color = C.line, strokeWidth = 2) {
  nodes.push(line(`${name}-line`, x1, y, Math.max(2, x2 - x1 - 9), color, strokeWidth));
  nodes.push(shape({
    name: `${name}-head`,
    geometry: "chevron",
    position: { left: x2 - 10, top: y - 6 },
    width: 10,
    height: 12,
    fill: color,
    line: { style: "solid", fill: color, width: 0 },
  }));
}

function documentIcon(nodes, prefix, x, y, width, height, fill, stroke, bars) {
  nodes.push(rect(`${prefix}-shadow`, x - 7, y - 7, width, height, C.white, C.line, 1));
  nodes.push(rect(`${prefix}-page`, x, y, width, height, fill, stroke, 2));
  for (let i = 0; i < bars; i += 1) {
    const barWidth = i === bars - 1 ? width * 0.46 : width * 0.66;
    nodes.push(rect(`${prefix}-bar-${i}`, x + 13, y + 20 + i * 15, barWidth, 4, stroke));
  }
}

function abstractAtomRow(nodes, prefix, x, y, accent, removed = false) {
  nodes.push(line(`${prefix}-edge-a`, x + 18, y + 10, 26, C.line, 2));
  nodes.push(line(`${prefix}-edge-b`, x + 78, y + 10, 26, C.line, 2));
  nodes.push(circle(`${prefix}-a`, x, y, 20, accent));
  nodes.push(circle(`${prefix}-b`, x + 34, y, 20, removed ? C.white : accent, removed ? C.red : "none", removed ? 2 : 0));
  nodes.push(t(removed ? "x" : "", `${prefix}-b-label`, x + 34, y, 20, 20, 10, { color: C.red, bold: true }));
  nodes.push(t("...", `${prefix}-ellipsis`, x + 56, y - 2, 22, 20, 12, { color: C.muted, bold: true }));
  nodes.push(circle(`${prefix}-c`, x + 104, y, 20, accent));
}

function addBaseFigure(slide) {
  const nodes = [];

  nodes.push(t("SkillAudit", "title", 42, 24, 240, 44, 34, { bold: true, alignment: "left" }));
  nodes.push(t("Traceable validation of simplified paper-derived agent skill specifications", "subtitle", 270, 34, 730, 28, 17, { color: C.muted, alignment: "left" }));

  nodes.push(verticalLine("input-process-divider", 626, 112, 526, C.line, 1, true));
  nodes.push(verticalLine("process-output-divider", 1018, 112, 526, C.line, 1, true));
  nodes.push(line("upstream-rule", 42, 126, 558, C.blue, 2));
  nodes.push(line("validation-rule", 644, 126, 352, C.blue, 3));
  nodes.push(line("outputs-rule", 1034, 126, 198, C.ink, 2));
  nodes.push(t("UPSTREAM INPUTS", "upstream-zone-title", 42, 96, 558, 24, 14, { color: C.blue, bold: true, alignment: "left" }));
  nodes.push(t("SKILLAUDIT VALIDATION", "validation-zone-title", 644, 96, 352, 24, 14, { color: C.blue, bold: true, alignment: "left" }));
  nodes.push(t("OUTPUTS", "outputs-zone-title", 1034, 96, 198, 24, 14, { color: C.ink, bold: true, alignment: "left" }));

  arrow(nodes, "paper-to-full", 132, 290, 194, C.blue);
  arrow(nodes, "full-to-reducer", 310, 290, 360, C.blue);
  arrow(nodes, "reducer-to-candidate", 444, 290, 490, C.cyan);
  arrow(nodes, "candidate-to-validation", 606, 290, 654, C.cyan);
  arrow(nodes, "validation-to-output", 1008, 290, 1030, C.ink);
  arrow(nodes, "validation-to-evidence", 1008, 520, 1030, C.ink);

  nodes.push(t("SOURCE", "source-kicker", 42, 154, 90, 22, 12, { color: C.blue, bold: true }));
  documentIcon(nodes, "paper", 50, 194, 72, 96, C.white, C.ink, 4);
  nodes.push(t("Research\npaper", "paper-label", 38, 302, 100, 50, 16, { bold: true }));
  nodes.push(t("source spans", "paper-note", 36, 354, 104, 20, 11, { color: C.muted }));

  nodes.push(t("FULL", "full-kicker", 194, 154, 116, 22, 12, { color: C.blue, bold: true }));
  documentIcon(nodes, "full", 210, 190, 84, 108, C.blueSoft, C.blue, 5);
  nodes.push(t("Full skill  F", "full-label", 186, 306, 130, 26, 17, { bold: true }));
  abstractAtomRow(nodes, "full-atoms", 188, 350, C.blue, false);
  nodes.push(t("procedural atoms", "full-atoms-label", 184, 378, 136, 20, 11, { color: C.muted }));

  nodes.push(round("reducer", 360, 232, 84, 118, C.soft, C.line, 1));
  nodes.push(circle("reducer-core", 383, 247, 38, C.white, C.ink, 2));
  nodes.push(t("-", "reducer-minus", 383, 244, 38, 38, 28, { bold: true }));
  nodes.push(t("Upstream\nreducer", "reducer-label", 366, 292, 72, 42, 14, { bold: true }));
  nodes.push(t("delete / merge / rewrite", "reducer-note", 336, 364, 132, 22, 10, { color: C.muted }));

  nodes.push(t("CANDIDATE", "candidate-kicker", 486, 154, 126, 22, 12, { color: C.cyan, bold: true }));
  documentIcon(nodes, "candidate", 502, 190, 84, 108, C.cyanSoft, C.cyan, 3);
  nodes.push(t("Candidate  S", "candidate-label", 484, 306, 126, 26, 17, { bold: true }));
  abstractAtomRow(nodes, "candidate-atoms", 480, 350, C.cyan, true);
  nodes.push(t("selected and frozen before testing", "candidate-note", 466, 378, 154, 28, 10, { color: C.muted }));

  nodes.push(round("evaluation-package", 348, 476, 200, 132, C.white, C.ink, 1));
  nodes.push(rect("evaluation-tab", 370, 464, 72, 18, C.ink));
  nodes.push(t("EVALUATION PACKAGE  E", "evaluation-title", 362, 494, 172, 24, 13, { bold: true }));
  nodes.push(t("task / workspace / held-out tests\nscorer / model / tools\nbudget / acceptance criteria", "evaluation-fields", 360, 528, 176, 66, 11, { color: C.muted }));

  nodes.push(round("validation-shell", 640, 146, 368, 468, C.white, C.blue, 3));
  nodes.push(rect("validation-header", 640, 146, 368, 48, C.blue));
  nodes.push(t("SkillAudit protocol", "validation-title", 658, 157, 332, 26, 19, { color: C.white, bold: true }));

  nodes.push(round("stage-map", 654, 214, 102, 250, C.blueSoft, C.blue, 1));
  nodes.push(round("stage-freeze", 766, 214, 102, 250, C.soft, C.line, 1));
  nodes.push(round("stage-run", 878, 214, 116, 250, C.cyanSoft, C.cyan, 1));
  nodes.push(circle("stage-map-index", 662, 222, 24, C.blue));
  nodes.push(circle("stage-freeze-index", 774, 222, 24, C.blueDark));
  nodes.push(circle("stage-run-index", 886, 222, 24, C.cyan));
  nodes.push(t("1", "stage-map-index-text", 662, 222, 24, 24, 12, { color: C.white, bold: true }));
  nodes.push(t("2", "stage-freeze-index-text", 774, 222, 24, 24, 12, { color: C.white, bold: true }));
  nodes.push(t("3", "stage-run-index-text", 886, 222, 24, 24, 12, { color: C.white, bold: true }));

  nodes.push(t("MAP", "stage-map-title", 662, 304, 86, 22, 13, { color: C.blue, bold: true }));
  nodes.push(t("Source spans\nAtoms + dependency DAG", "stage-map-detail", 662, 334, 86, 48, 10, { color: C.muted }));
  nodes.push(t("provenance +\nprerequisites", "stage-map-note", 662, 400, 86, 40, 10, { color: C.blueDark, bold: true }));

  nodes.push(t("FREEZE", "stage-freeze-title", 774, 304, 86, 22, 13, { color: C.blueDark, bold: true }));
  nodes.push(t("Candidate S\nTask + tests\nModel + tools\nCriteria", "stage-freeze-detail", 774, 332, 86, 76, 10, { color: C.muted }));
  nodes.push(t("sealed before\ntesting", "stage-freeze-note", 774, 410, 86, 34, 10, { color: C.blueDark, bold: true }));

  nodes.push(t("RUN", "stage-run-title", 888, 256, 96, 22, 13, { color: C.cyan, bold: true }));
  const laneY = [290, 342, 394];
  const laneCode = ["B", "F", "S"];
  const laneFill = [C.white, C.blueSoft, C.cyanSoft];
  const laneStroke = [C.line, C.blue, C.cyan];
  for (let i = 0; i < 3; i += 1) {
    nodes.push(circle(`lane-${i}-head`, 890, laneY[i], 22, laneFill[i], laneStroke[i], 2));
    nodes.push(rect(`lane-${i}-body`, 894, laneY[i] + 24, 14, 12, laneStroke[i]));
    nodes.push(t(laneCode[i], `lane-${i}-code`, 916, laneY[i] + 4, 22, 24, 16, { color: laneStroke[i], bold: true }));
    nodes.push(t(">", `lane-${i}-arrow`, 938, laneY[i] + 3, 16, 24, 15, { color: C.line, bold: true }));
    nodes.push(round(`lane-${i}-terminal`, 954, laneY[i] - 2, 32, 34, C.white, C.line, 1));
    nodes.push(t(">_", `lane-${i}-terminal-text`, 956, laneY[i] + 3, 28, 24, 11, { bold: true }));
  }
  nodes.push(t("independent run / condition", "stage-run-note", 886, 430, 100, 24, 9, { color: C.muted }));

  nodes.push(round("decision-gate", 654, 492, 340, 98, C.cyanSoft, C.cyan, 1));
  nodes.push(circle("decision-gate-index", 662, 500, 24, C.green));
  nodes.push(t("4", "decision-gate-index-text", 662, 500, 24, 24, 12, { color: C.white, bold: true }));
  nodes.push(circle("decision-gate-check", 680, 536, 38, C.white, C.green, 2));
  nodes.push(t("OK", "decision-gate-check-text", 680, 536, 38, 38, 12, { color: C.green, bold: true }));
  nodes.push(t("VERIFY", "decision-gate-title", 728, 502, 248, 22, 13, { color: C.green, bold: true, alignment: "left" }));
  nodes.push(t("Held-out results + integrity", "decision-gate-subtitle", 728, 530, 248, 22, 12, { color: C.blueDark, bold: true, alignment: "left" }));
  nodes.push(t("against frozen acceptance criteria", "decision-gate-note", 728, 556, 248, 18, 10, { color: C.muted, alignment: "left" }));

  nodes.push(t("DECISION", "decision-kicker", 1034, 154, 198, 22, 12, { bold: true }));
  nodes.push(round("decision-box", 1034, 184, 198, 188, C.soft, C.line, 1));
  nodes.push(round("accept", 1052, 206, 162, 42, C.greenSoft, C.green, 1));
  nodes.push(t("Accept", "accept-label", 1052, 214, 162, 26, 18, { color: C.green, bold: true }));
  nodes.push(round("reject", 1052, 260, 162, 42, C.redSoft, C.red, 1));
  nodes.push(t("Reject", "reject-label", 1052, 268, 162, 26, 18, { color: C.red, bold: true }));
  nodes.push(round("invalid", 1052, 314, 162, 42, C.white, C.line, 1));
  nodes.push(t("Invalid", "invalid-label", 1052, 322, 162, 26, 18, { color: C.muted, bold: true }));

  nodes.push(t("EVIDENCE", "evidence-kicker", 1034, 408, 198, 22, 12, { color: C.blue, bold: true }));
  nodes.push(t("Auditable record", "evidence-title", 1038, 552, 190, 24, 14, { bold: true }));
  nodes.push(t("source / config / results / rationale", "evidence-fields", 1038, 582, 190, 22, 10, { color: C.muted }));

  nodes.push(t("Candidate construction", "zone-left", 150, 660, 420, 22, 12, { color: C.muted }));
  nodes.push(t("Traceable validation", "zone-mid", 640, 660, 368, 22, 12, { color: C.blue, bold: true }));
  nodes.push(t("Decision + evidence", "zone-right", 1034, 660, 198, 22, 12, { color: C.muted }));

  slide.compose(layers({ name: "skillaudit-main-figure-v3-2-base", width: "fill", height: "fill" }, nodes), {
    frame: { left: 0, top: 0, width: 1280, height: 720 },
    baseUnit: 1,
  });
}

async function addGeneratedIcons(slide) {
  const dependencyBytes = await fs.readFile(ICON_DEPENDENCY);
  const freezeBytes = await fs.readFile(ICON_FREEZE);
  const evidenceBytes = await fs.readFile(ICON_EVIDENCE);
  const common = {
    contentType: "image/png",
    fit: "contain",
    geometry: "rect",
    prompt: "Three isolated AAAI-style scientific pictograms: source document with dependency graph, locked test-boundary package, and auditable evidence certificate; no workflow arrows or text.",
  };

  slide.images.add({
    ...common,
    blob: dependencyBytes,
    alt: "Generated component icon: source document and dependency graph",
    position: { left: 666, top: 242, width: 82, height: 66 },
  });
  slide.images.add({
    ...common,
    blob: freezeBytes,
    alt: "Generated component icon: locked validation boundary package",
    position: { left: 778, top: 242, width: 82, height: 66 },
  });
  slide.images.add({
    ...common,
    blob: evidenceBytes,
    alt: "Generated component icon: auditable evidence certificate",
    position: { left: 1080, top: 436, width: 106, height: 104 },
  });
}

async function saveBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

async function main() {
  await fs.mkdir(OUT, { recursive: true });
  const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  addBaseFigure(slide);
  await addGeneratedIcons(slide);
  slide.compose(layers({ name: "skillaudit-main-figure-v3-2-stage-arrows", width: "fill", height: "fill" }, [
    line("visible-package-freeze-route", 548, 478, 269, C.blueDark, 1, true),
    shape({
      name: "visible-package-freeze-head",
      geometry: "triangle",
      position: { left: 811, top: 466 },
      width: 12,
      height: 10,
      fill: C.blueDark,
      line: { style: "solid", fill: C.blueDark, width: 0 },
    }),
    shape({
      name: "visible-stage-arrow-1",
      geometry: "chevron",
      position: { left: 757, top: 344 },
      width: 8,
      height: 12,
      fill: C.blue,
      line: { style: "solid", fill: C.blue, width: 0 },
    }),
    shape({
      name: "visible-stage-arrow-2",
      geometry: "chevron",
      position: { left: 869, top: 344 },
      width: 8,
      height: 12,
      fill: C.blue,
      line: { style: "solid", fill: C.blue, width: 0 },
    }),
    shape({
      name: "run-to-verify-head",
      geometry: "downArrow",
      position: { left: 928, top: 466 },
      width: 12,
      height: 18,
      fill: C.cyan,
      line: { style: "solid", fill: C.cyan, width: 0 },
    }),
  ]), {
    frame: { left: 0, top: 0, width: 1280, height: 720 },
    baseUnit: 1,
  });

  await saveBlob(path.join(OUT, "SkillAudit_Main_Figure_v3_2.png"), await presentation.export({ slide, format: "png", scale: 2 }));
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(path.join(OUT, "SkillAudit_Main_Figure_v3_2.layout.json"), await layout.text(), "utf8");
  const inspect = await presentation.inspect({ kind: "slide,textbox,shape,image", maxChars: 26000 });
  await fs.writeFile(path.join(OUT, "SkillAudit_Main_Figure_v3_2.inspect.ndjson"), inspect.ndjson, "utf8");
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(path.join(OUT, "SkillAudit_Main_Figure_v3_2.pptx"));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
