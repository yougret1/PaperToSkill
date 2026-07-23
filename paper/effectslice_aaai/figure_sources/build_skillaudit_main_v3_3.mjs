import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Presentation, PresentationFile, layers, shape, text } from "@oai/artifact-tool";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const OUT = process.env.SKILLAUDIT_OUT ?? path.join(SCRIPT_DIR, "rendered", "v3-3");
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

function upArrow(nodes, name, x, yTop, yBottom, color = C.blueDark) {
  nodes.push(verticalLine(`${name}-line`, x, yTop + 10, yBottom - yTop - 10, color, 1, true));
  nodes.push(shape({
    name: `${name}-head`,
    geometry: "triangle",
    position: { left: x - 6, top: yTop },
    width: 12,
    height: 10,
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

function stageIndex(nodes, index, x, y, fill) {
  nodes.push(circle(`stage-${index}-index`, x, y, 22, fill));
  nodes.push(t(String(index), `stage-${index}-index-text`, x, y, 22, 22, 11, { color: C.white, bold: true }));
}

function decisionRow(nodes, prefix, y, fill, stroke, title, note, titleColor) {
  nodes.push(round(prefix, 1040, y, 186, 54, fill, stroke, 1));
  nodes.push(rect(`${prefix}-rail`, 1040, y, 6, 54, stroke));
  nodes.push(t(title, `${prefix}-title`, 1056, y + 6, 154, 21, 15, { color: titleColor, bold: true, alignment: "left" }));
  nodes.push(t(note, `${prefix}-note`, 1056, y + 29, 154, 16, 13, { color: C.muted, alignment: "left" }));
}

function addBaseFigure(slide) {
  const nodes = [];

  // Connectors are added before the entities so the visual flow stays behind labels and cards.
  nodes.push(verticalLine("upstream-protocol-divider", 572, 108, 530, C.line, 1, true));
  nodes.push(verticalLine("protocol-output-divider", 1022, 108, 530, C.line, 1, true));
  arrow(nodes, "paper-to-full", 132, 288, 160, C.blue);
  arrow(nodes, "full-to-reducer", 276, 288, 314, C.blue);
  arrow(nodes, "reducer-to-candidate", 400, 288, 422, C.cyan);
  arrow(nodes, "candidate-to-map", 546, 288, 580, C.cyan);
  arrow(nodes, "map-to-freeze", 688, 340, 696, C.blue);
  arrow(nodes, "freeze-to-run", 794, 340, 802, C.blueDark);
  arrow(nodes, "run-to-verify", 914, 340, 922, C.cyan);
  nodes.push(line("verify-to-decision-a", 1006, 330, 20, C.ink, 2));
  nodes.push(verticalLine("verify-to-decision-b", 1026, 174, 156, C.ink, 2, false));
  arrow(nodes, "verify-to-decision-c", 1026, 174, 1038, C.ink, 2);
  nodes.push(line("verify-to-evidence-a", 1006, 418, 12, C.blueDark, 1));
  nodes.push(verticalLine("verify-to-evidence-b", 1018, 418, 116, C.blueDark, 1, false));
  arrow(nodes, "verify-to-evidence-c", 1018, 534, 1032, C.blueDark, 1);
  nodes.push(line("package-to-freeze-a", 544, 518, 201, C.blueDark, 1, true));
  upArrow(nodes, "package-to-freeze-b", 745, 494, 518, C.blueDark);

  nodes.push(t("SkillAudit", "title", 42, 24, 236, 44, 34, { bold: true, alignment: "left" }));
  nodes.push(t("Traceable validation of simplified paper-derived agent skill specifications", "subtitle", 270, 34, 740, 28, 17, { color: C.muted, alignment: "left" }));

  nodes.push(line("upstream-rule", 42, 126, 506, C.blue, 2));
  nodes.push(line("protocol-rule", 588, 126, 418, C.blue, 3));
  nodes.push(line("outputs-rule", 1034, 126, 198, C.ink, 2));
  nodes.push(t("UPSTREAM PREPARATION", "upstream-zone-title", 42, 96, 506, 24, 16, { color: C.blue, bold: true, alignment: "left" }));
  nodes.push(t("SKILLAUDIT PROTOCOL", "protocol-zone-title", 588, 96, 418, 24, 16, { color: C.blue, bold: true, alignment: "left" }));
  nodes.push(t("OUTPUTS", "outputs-zone-title", 1034, 96, 198, 24, 16, { color: C.ink, bold: true, alignment: "left" }));

  nodes.push(t("SOURCE", "source-kicker", 42, 154, 90, 22, 13, { color: C.blue, bold: true }));
  documentIcon(nodes, "paper", 50, 192, 72, 96, C.white, C.ink, 4);
  nodes.push(t("Research\npaper", "paper-label", 38, 300, 100, 50, 16, { bold: true }));
  nodes.push(t("source spans", "paper-note", 36, 352, 104, 20, 13, { color: C.muted }));

  nodes.push(t("FULL", "full-kicker", 160, 154, 116, 22, 13, { color: C.blue, bold: true }));
  documentIcon(nodes, "full", 174, 188, 84, 108, C.blueSoft, C.blue, 5);
  nodes.push(t("Full spec.  F", "full-label", 152, 304, 130, 26, 17, { bold: true }));
  abstractAtomRow(nodes, "full-atoms", 154, 348, C.blue, false);
  nodes.push(t("procedural atoms", "full-atoms-label", 150, 376, 136, 20, 13, { color: C.muted }));

  nodes.push(round("reducer", 314, 230, 86, 118, C.soft, C.line, 1));
  nodes.push(circle("reducer-core", 338, 245, 38, C.white, C.ink, 2));
  nodes.push(t("-", "reducer-minus", 338, 242, 38, 38, 28, { bold: true }));
  nodes.push(t("Simplification\nmethod", "reducer-label", 321, 290, 72, 42, 14, { bold: true }));
  nodes.push(t("delete / merge / rewrite", "reducer-note", 288, 362, 138, 22, 13, { color: C.muted }));

  nodes.push(t("CANDIDATE", "candidate-kicker", 416, 154, 126, 22, 13, { color: C.cyan, bold: true }));
  documentIcon(nodes, "candidate", 432, 188, 84, 108, C.cyanSoft, C.cyan, 3);
  nodes.push(t("Candidate spec.  S", "candidate-label", 404, 304, 146, 26, 17, { bold: true }));
  abstractAtomRow(nodes, "candidate-atoms", 410, 348, C.cyan, true);
  nodes.push(t("fixed before evaluation", "candidate-note", 402, 376, 146, 24, 13, { color: C.muted }));

  nodes.push(t("outside SkillAudit", "upstream-boundary-note", 388, 410, 160, 18, 13, { color: C.muted, alignment: "right" }));

  nodes.push(round("evaluation-package", 300, 458, 244, 138, C.white, C.ink, 1));
  nodes.push(rect("evaluation-tab", 320, 448, 78, 16, C.ink));
  nodes.push(t("EVALUATION PACKAGE  E", "evaluation-title", 316, 476, 212, 24, 15, { bold: true }));
  nodes.push(t("task + workspace + held-out tests\nscorer + model + tools\nbudget + acceptance criteria", "evaluation-fields", 314, 512, 216, 66, 14, { color: C.muted }));

  nodes.push(round("protocol-shell", 580, 146, 438, 468, C.soft, C.blue, 2));
  nodes.push(t("prespecified, sealed validation boundary", "protocol-boundary-label", 598, 158, 402, 24, 14, { color: C.blueDark, bold: true }));

  nodes.push(round("stage-map", 592, 204, 96, 300, C.white, C.blue, 1));
  nodes.push(round("stage-freeze", 696, 204, 98, 300, C.white, C.blueDark, 1));
  nodes.push(round("stage-run", 802, 204, 112, 300, C.white, C.cyan, 1));
  nodes.push(round("stage-verify", 922, 204, 84, 300, C.white, C.green, 1));
  stageIndex(nodes, 1, 598, 212, C.blue);
  stageIndex(nodes, 2, 702, 212, C.blueDark);
  stageIndex(nodes, 3, 808, 212, C.cyan);
  stageIndex(nodes, 4, 928, 212, C.green);

  nodes.push(t("MAP", "stage-map-title", 600, 300, 80, 22, 16, { color: C.blue, bold: true }));
  nodes.push(t("source spans\nprocedural atoms\ndependency DAG", "stage-map-detail", 600, 328, 80, 72, 14, { color: C.muted }));
  nodes.push(round("closure-check", 600, 420, 80, 58, C.blueSoft, C.blue, 1));
  nodes.push(t("CHECK", "closure-check-title", 606, 426, 68, 18, 12, { color: C.blueDark, bold: true }));
  nodes.push(t("provenance +\nclosure", "closure-check-note", 606, 446, 68, 26, 14, { color: C.blueDark }));

  nodes.push(t("FREEZE", "stage-freeze-title", 704, 300, 82, 22, 16, { color: C.blueDark, bold: true }));
  nodes.push(t("F + S\nTask + tests\nModel + tools\nAcceptance rule", "stage-freeze-detail", 704, 328, 82, 94, 14, { color: C.muted }));
  nodes.push(t("sealed before\ntesting", "stage-freeze-note", 708, 440, 74, 34, 13, { color: C.blueDark, bold: true }));

  nodes.push(t("RUN", "stage-run-title", 810, 244, 96, 22, 16, { color: C.cyan, bold: true }));
  nodes.push(t("same task; independent runs", "stage-run-subtitle", 810, 268, 96, 28, 13, { color: C.muted }));
  const laneY = [306, 356, 406];
  const laneCode = ["B", "F", "S"];
  const laneLabel = ["No spec.", "Full spec.", "Simplified spec."];
  const laneFill = [C.white, C.blueSoft, C.cyanSoft];
  const laneStroke = [C.line, C.blue, C.cyan];
  for (let i = 0; i < 3; i += 1) {
    nodes.push(round(`lane-${i}`, 808, laneY[i], 100, 40, laneFill[i], laneStroke[i], 1));
    nodes.push(circle(`lane-${i}-code-bg`, 814, laneY[i] + 9, 22, C.white, laneStroke[i], 1));
    nodes.push(t(laneCode[i], `lane-${i}-code`, 814, laneY[i] + 9, 22, 22, 14, { color: laneStroke[i], bold: true }));
    nodes.push(t(laneLabel[i], `lane-${i}-label`, 840, laneY[i] + 4, 64, 32, 14, { color: C.ink, alignment: "left" }));
  }
  nodes.push(t("score + hard contract", "stage-run-note", 810, 466, 96, 18, 13, { color: C.muted }));

  nodes.push(t("VERIFY", "stage-verify-title", 928, 244, 72, 22, 16, { color: C.green, bold: true }));
  nodes.push(circle("integrity-check-bg", 946, 294, 36, C.greenSoft, C.green, 2));
  nodes.push(t("OK", "integrity-check-number", 946, 294, 36, 36, 11, { color: C.green, bold: true }));
  nodes.push(t("Integrity\ncomplete?", "integrity-check-label", 928, 336, 72, 40, 12, { color: C.ink, bold: true }));
  nodes.push(circle("sla-check-bg", 946, 390, 36, C.blueSoft, C.blue, 2));
  nodes.push(t("SLA", "sla-check-number", 946, 390, 36, 36, 10, { color: C.blue, bold: true }));
  nodes.push(t("Frozen SLA\nmet?", "sla-check-label", 928, 432, 72, 40, 12, { color: C.ink, bold: true }));
  nodes.push(t("decide only after\nintegrity", "stage-verify-note", 930, 474, 68, 26, 12, { color: C.muted }));

  nodes.push(round("audit-trace-strip", 606, 530, 386, 56, C.white, C.line, 1));
  nodes.push(t("TRACE", "audit-trace-title", 618, 542, 52, 20, 13, { color: C.blueDark, bold: true }));
  nodes.push(t("source  |  frozen config  |  results  |  rationale", "audit-trace-fields", 678, 542, 302, 20, 14, { color: C.muted, alignment: "left" }));

  nodes.push(t("DECISION", "decision-kicker", 1034, 154, 198, 22, 13, { bold: true }));
  decisionRow(nodes, "accept", 190, C.greenSoft, C.green, "Accept", "valid run; criteria met", C.green);
  decisionRow(nodes, "reject", 252, C.redSoft, C.red, "Reject", "valid run; criteria missed", C.red);
  decisionRow(nodes, "invalid", 314, C.white, C.line, "Invalid", "incomplete or malformed run", C.muted);

  nodes.push(t("EVIDENCE", "evidence-kicker", 1034, 438, 198, 22, 13, { color: C.blue, bold: true }));
  nodes.push(t("Auditable record", "evidence-title", 1038, 570, 190, 24, 15, { bold: true }));
  nodes.push(t("source / config / results / rationale", "evidence-fields", 1038, 602, 190, 22, 13, { color: C.muted }));

  slide.compose(layers({ name: "skillaudit-main-figure-v3-3-base", width: "fill", height: "fill" }, nodes), {
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
    prompt: "Isolated AAAI-style scientific pictogram used only as a local component; no workflow arrows or text.",
  };

  slide.images.add({
    ...common,
    blob: dependencyBytes,
    alt: "Generated component icon: source document and dependency graph",
    position: { left: 608, top: 240, width: 64, height: 52 },
  });
  slide.images.add({
    ...common,
    blob: freezeBytes,
    alt: "Generated component icon: locked validation boundary package",
    position: { left: 713, top: 240, width: 64, height: 52 },
  });
  slide.images.add({
    ...common,
    blob: evidenceBytes,
    alt: "Generated component icon: auditable evidence certificate",
    position: { left: 1092, top: 468, width: 82, height: 88 },
  });
}

function addVisibleConnectors(slide) {
  slide.compose(layers({ name: "skillaudit-main-figure-v3-3-visible-connectors", width: "fill", height: "fill" }, [
    shape({
      name: "candidate-to-protocol-visible-head",
      geometry: "chevron",
      position: { left: 570, top: 282 },
      width: 10,
      height: 12,
      fill: C.cyan,
      line: { style: "solid", fill: C.cyan, width: 0 },
    }),
    shape({
      name: "visible-stage-arrow-map-freeze",
      geometry: "chevron",
      position: { left: 688, top: 334 },
      width: 8,
      height: 12,
      fill: C.blue,
      line: { style: "solid", fill: C.blue, width: 0 },
    }),
    shape({
      name: "visible-stage-arrow-freeze-run",
      geometry: "chevron",
      position: { left: 794, top: 334 },
      width: 8,
      height: 12,
      fill: C.blueDark,
      line: { style: "solid", fill: C.blueDark, width: 0 },
    }),
    shape({
      name: "visible-stage-arrow-run-verify",
      geometry: "chevron",
      position: { left: 914, top: 334 },
      width: 8,
      height: 12,
      fill: C.cyan,
      line: { style: "solid", fill: C.cyan, width: 0 },
    }),
    line("visible-package-freeze-route", 544, 518, 201, C.blueDark, 1, true),
    verticalLine("visible-package-freeze-rise", 745, 504, 14, C.blueDark, 1, true),
    shape({
      name: "visible-package-freeze-head",
      geometry: "triangle",
      position: { left: 739, top: 494 },
      width: 12,
      height: 10,
      fill: C.blueDark,
      line: { style: "solid", fill: C.blueDark, width: 0 },
    }),
  ]), {
    frame: { left: 0, top: 0, width: 1280, height: 720 },
    baseUnit: 1,
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
  addVisibleConnectors(slide);

  await saveBlob(path.join(OUT, "SkillAudit_Main_Figure_v3_3.png"), await presentation.export({ slide, format: "png", scale: 2 }));
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(path.join(OUT, "SkillAudit_Main_Figure_v3_3.layout.json"), await layout.text(), "utf8");
  const inspect = await presentation.inspect({ kind: "slide,textbox,shape,image", maxChars: 32000 });
  await fs.writeFile(path.join(OUT, "SkillAudit_Main_Figure_v3_3.inspect.ndjson"), inspect.ndjson, "utf8");
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(path.join(OUT, "SkillAudit_Main_Figure_v3_3.pptx"));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
