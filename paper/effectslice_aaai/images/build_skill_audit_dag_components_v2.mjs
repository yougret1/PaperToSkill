import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const INPUT = process.env.SKILLAUDIT_INPUT;
const OUTPUT_DIR = process.env.SKILLAUDIT_OUTPUT_DIR;
const ARTIFACT_TOOL_PATH = process.env.ARTIFACT_TOOL_PATH;

if (!INPUT || !OUTPUT_DIR || !ARTIFACT_TOOL_PATH) {
  throw new Error(
    "Set SKILLAUDIT_INPUT, SKILLAUDIT_OUTPUT_DIR, and ARTIFACT_TOOL_PATH.",
  );
}

const C = {
  ink: "#17212B",
  muted: "#657387",
  blue: "#3478DC",
  blueDark: "#164E8B",
  cyan: "#49BBD6",
  red: "#E0575B",
  border: "#CBD5E1",
  grid: "#E8EEF5",
  panel: "#FBFCFE",
  removed: "#E8EDF3",
  white: "#FFFFFF",
};

async function writeBlob(filePath, blob) {
  const bytes = new Uint8Array(await blob.arrayBuffer());
  await fs.writeFile(filePath, bytes);
  return bytes;
}

function sha256(bytes) {
  return crypto.createHash("sha256").update(bytes).digest("hex");
}

function addText(slide, name, value, left, top, width, height, options = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    name,
    position: { left, top, width, height },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = value;
  shape.text.style = {
    fontFamily: "Arial",
    fontSize: options.fontSize ?? 13,
    bold: options.bold ?? false,
    color: options.color ?? C.ink,
    alignment: options.alignment ?? "left",
    verticalAlignment: "middle",
  };
  return shape;
}

function addPanel(slide, name, left, top, width, height) {
  return slide.shapes.add({
    geometry: "roundRect",
    name,
    position: { left, top, width, height },
    fill: C.panel,
    line: { style: "solid", fill: C.border, width: 1 },
    borderRadius: "rounded-lg",
  });
}

function addNode(slide, name, label, centerX, centerY, options = {}) {
  const size = options.size ?? 30;
  const fill = options.fill ?? C.blue;
  const node = slide.shapes.add({
    geometry: "ellipse",
    name,
    position: {
      left: centerX - size / 2,
      top: centerY - size / 2,
      width: size,
      height: size,
    },
    fill,
    line: {
      style: "solid",
      fill: options.line ?? fill,
      width: options.lineWidth ?? 1.5,
    },
  });
  if (label) {
    node.text = label;
    node.text.style = {
      fontFamily: "Arial",
      fontSize: options.fontSize ?? 9,
      bold: true,
      color: options.textColor ?? C.white,
      alignment: "center",
      verticalAlignment: "middle",
    };
  }
  return node;
}

function connect(slide, source, target, options = {}) {
  const connector = slide.shapes.connect(source, target, {
    kind: options.kind ?? "straight",
    fromSide: options.fromSide,
    toSide: options.toSide,
    line: {
      style: options.style ?? "solid",
      fill: options.color ?? C.blueDark,
      width: options.width ?? 1.8,
    },
    tail: {
      type: options.head ?? "triangle",
      width: "sm",
      length: "sm",
    },
    cap: "round",
    join: "round",
  });
  connector.bringToFront();
  return connector;
}

function addGrid(slide, left, top, width, height, columns = 12, rows = 5) {
  for (let i = 1; i < columns; i += 1) {
    const x = left + (width * i) / columns;
    slide.shapes.add({
      geometry: "rect",
      name: `example-grid-v-${i}`,
      position: { left: x, top, width: 1, height },
      fill: C.grid,
      line: { style: "solid", fill: "none", width: 0 },
    });
  }
  for (let i = 1; i < rows; i += 1) {
    const y = top + (height * i) / rows;
    slide.shapes.add({
      geometry: "rect",
      name: `example-grid-h-${i}`,
      position: { left, top: y, width, height: 1 },
      fill: C.grid,
      line: { style: "solid", fill: "none", width: 0 },
    });
  }
}

function addExampleDag(slide) {
  const points = [
    [110, 310],
    [230, 245],
    [230, 365],
    [380, 225],
    [380, 315],
    [380, 395],
    [540, 265],
    [540, 365],
    [680, 315],
  ];
  const nodes = points.map(([x, y], index) =>
    addNode(slide, `example-node-a${index + 1}`, `${index + 1}`, x, y),
  );
  const edges = [
    [0, 1],
    [0, 2],
    [1, 3],
    [1, 4],
    [2, 4],
    [2, 5],
    [3, 6],
    [4, 6],
    [4, 7],
    [5, 7],
    [6, 8],
    [7, 8],
  ];
  for (const [from, to] of edges) {
    connect(slide, nodes[from], nodes[to]);
  }
}

function addNodeAndEdgeStyles(slide) {
  const nodeStyles = [
    { x: 820, fill: C.blue, line: C.blue, label: "ATOM", text: "A" },
    { x: 930, fill: C.cyan, line: C.cyan, label: "RETAINED", text: "A" },
    {
      x: 1040,
      fill: C.white,
      line: C.blue,
      label: "BOUNDARY",
      text: "A",
      textColor: C.blueDark,
      lineWidth: 2.5,
    },
    {
      x: 1150,
      fill: C.removed,
      line: "#AAB6C4",
      label: "REMOVED",
      text: "x",
      textColor: C.red,
    },
  ];
  for (const style of nodeStyles) {
    addNode(slide, `style-node-${style.label.toLowerCase()}`, style.text, style.x, 235, {
      fill: style.fill,
      line: style.line,
      textColor: style.textColor,
      lineWidth: style.lineWidth,
      size: 32,
      fontSize: 10,
    });
    addText(
      slide,
      `style-node-label-${style.label.toLowerCase()}`,
      style.label,
      style.x - 48,
      258,
      96,
      20,
      { fontSize: 9, bold: true, color: C.muted, alignment: "center" },
    );
  }

  const edgeSets = [
    { x1: 800, x2: 885, color: C.blueDark, style: "solid", label: "DIRECTED" },
    { x1: 955, x2: 1040, color: C.muted, style: "dashed", label: "DEPENDENCY" },
    { x1: 1110, x2: 1195, color: C.cyan, style: "solid", label: "HIGHLIGHT" },
  ];
  for (const edge of edgeSets) {
    const source = addNode(slide, `style-edge-${edge.label}-source`, "", edge.x1, 355, {
      fill: C.white,
      line: edge.color,
      lineWidth: 2,
      size: 18,
    });
    const target = addNode(slide, `style-edge-${edge.label}-target`, "", edge.x2, 355, {
      fill: edge.color,
      line: edge.color,
      size: 18,
    });
    connect(slide, source, target, {
      color: edge.color,
      style: edge.style,
      width: 2,
    });
    addText(
      slide,
      `style-edge-label-${edge.label.toLowerCase()}`,
      edge.label,
      edge.x1 - 12,
      380,
      edge.x2 - edge.x1 + 24,
      20,
      { fontSize: 9, bold: true, color: C.muted, alignment: "center" },
    );
  }
}

function addChain(slide) {
  const nodes = [95, 160, 225, 290].map((x, index) =>
    addNode(slide, `pattern-chain-${index + 1}`, "", x, 585, { size: 22 }),
  );
  for (let i = 0; i < nodes.length - 1; i += 1) {
    connect(slide, nodes[i], nodes[i + 1]);
  }
}

function addBranch(slide) {
  const root = addNode(slide, "pattern-branch-root", "", 380, 585, { size: 22 });
  const upper = addNode(slide, "pattern-branch-upper", "", 470, 550, { size: 22 });
  const lower = addNode(slide, "pattern-branch-lower", "", 470, 620, { size: 22 });
  const leaf = addNode(slide, "pattern-branch-leaf", "", 555, 585, { size: 22 });
  connect(slide, root, upper);
  connect(slide, root, lower);
  connect(slide, upper, leaf);
  connect(slide, lower, leaf);
}

function addMerge(slide) {
  const upper = addNode(slide, "pattern-merge-upper", "", 665, 550, { size: 22 });
  const lower = addNode(slide, "pattern-merge-lower", "", 665, 620, { size: 22 });
  const merge = addNode(slide, "pattern-merge-center", "", 765, 585, { size: 22 });
  const leaf = addNode(slide, "pattern-merge-leaf", "", 855, 585, { size: 22 });
  connect(slide, upper, merge);
  connect(slide, lower, merge);
  connect(slide, merge, leaf);
}

function addClosure(slide) {
  slide.shapes.add({
    geometry: "roundRect",
    name: "pattern-closure-boundary",
    position: { left: 945, top: 540, width: 205, height: 90 },
    fill: "#F3FBFD",
    line: { style: "dashed", fill: C.cyan, width: 1.5 },
    borderRadius: "rounded-lg",
  });
  const left = addNode(slide, "pattern-closure-prerequisite-1", "", 975, 585, {
    size: 22,
    fill: C.cyan,
  });
  const upper = addNode(slide, "pattern-closure-prerequisite-2", "", 1040, 560, {
    size: 22,
    fill: C.cyan,
  });
  const lower = addNode(slide, "pattern-closure-prerequisite-3", "", 1040, 610, {
    size: 22,
    fill: C.cyan,
  });
  const target = addNode(slide, "pattern-closure-target", "", 1120, 585, {
    size: 24,
    fill: C.blue,
  });
  addNode(slide, "pattern-closure-unrelated", "", 1190, 585, {
    size: 22,
    fill: C.removed,
    line: "#AAB6C4",
  });
  connect(slide, left, upper, { color: C.cyan });
  connect(slide, left, lower, { color: C.cyan });
  connect(slide, upper, target, { color: C.cyan });
  connect(slide, lower, target, { color: C.cyan });
}

function addComponentSlide(presentation) {
  while (presentation.slides.items.length > 2) {
    presentation.slides.items.at(-1).delete();
  }

  const slide = presentation.slides.items[1].duplicate();
  slide.shapes.deleteAll();
  for (const image of [...slide.images.items]) image.delete();
  for (const table of [...slide.tables.items]) table.delete();
  for (const chart of [...slide.charts.items]) chart.delete();
  slide.background.fill = C.white;

  addText(slide, "dag-components-title", "EDITABLE DAG COMPONENTS", 42, 34, 520, 38, {
    fontSize: 25,
    bold: true,
  });
  addText(
    slide,
    "dag-components-subtitle",
    "Native PowerPoint shapes  |  copy, recolor, reconnect",
    42,
    72,
    520,
    24,
    { fontSize: 12, color: C.muted },
  );
  slide.shapes.add({
    geometry: "rect",
    name: "dag-components-title-rule",
    position: { left: 42, top: 112, width: 1196, height: 2 },
    fill: C.blue,
    line: { style: "solid", fill: "none", width: 0 },
  });

  addPanel(slide, "example-dag-panel", 42, 145, 700, 300);
  addText(slide, "example-dag-label", "EXAMPLE DAG", 60, 158, 180, 24, {
    fontSize: 12,
    bold: true,
    color: C.blueDark,
  });
  addGrid(slide, 60, 194, 664, 228);
  addExampleDag(slide);

  addPanel(slide, "styles-panel", 762, 145, 476, 300);
  addText(slide, "styles-panel-title", "NODE & EDGE STYLES", 780, 158, 220, 24, {
    fontSize: 12,
    bold: true,
    color: C.blueDark,
  });
  addText(slide, "nodes-label", "NODES", 780, 190, 100, 20, {
    fontSize: 10,
    bold: true,
    color: C.muted,
  });
  addText(slide, "edges-label", "EDGES", 780, 302, 100, 20, {
    fontSize: 10,
    bold: true,
    color: C.muted,
  });
  addNodeAndEdgeStyles(slide);

  addPanel(slide, "patterns-panel", 42, 468, 1196, 198);
  addText(slide, "patterns-title", "COPY-READY PATTERNS", 60, 480, 250, 24, {
    fontSize: 12,
    bold: true,
    color: C.blueDark,
  });
  for (const x of [330, 620, 910]) {
    slide.shapes.add({
      geometry: "rect",
      name: `patterns-divider-${x}`,
      position: { left: x, top: 512, width: 1, height: 132 },
      fill: C.border,
      line: { style: "solid", fill: "none", width: 0 },
    });
  }
  const patternLabels = [
    [60, "CHAIN"],
    [350, "BRANCH"],
    [640, "MERGE"],
    [930, "CLOSURE"],
  ];
  for (const [x, label] of patternLabels) {
    addText(slide, `pattern-label-${label.toLowerCase()}`, label, x, 514, 160, 20, {
      fontSize: 10,
      bold: true,
      color: C.muted,
    });
  }
  addChain(slide);
  addBranch(slide);
  addMerge(slide);
  addClosure(slide);

  return slide;
}

async function main() {
  await fs.mkdir(OUTPUT_DIR, { recursive: true });
  const { FileBlob, PresentationFile } = await import(
    pathToFileURL(ARTIFACT_TOOL_PATH).href
  );
  const presentation = await PresentationFile.importPptx(await FileBlob.load(INPUT));

  const beforeHashes = [];
  for (const [index, slide] of presentation.slides.items.slice(0, 2).entries()) {
    const stem = `before-slide-${String(index + 1).padStart(2, "0")}`;
    const bytes = await writeBlob(
      path.join(OUTPUT_DIR, `${stem}.png`),
      await presentation.export({ slide, format: "png", scale: 1 }),
    );
    beforeHashes.push(sha256(bytes));
    const layout = await slide.export({ format: "layout" });
    await fs.writeFile(
      path.join(OUTPUT_DIR, `${stem}.layout.json`),
      await layout.text(),
      "utf8",
    );
  }

  addComponentSlide(presentation);

  const afterHashes = [];
  for (const [index, slide] of presentation.slides.items.entries()) {
    const stem = `after-slide-${String(index + 1).padStart(2, "0")}`;
    const bytes = await writeBlob(
      path.join(OUTPUT_DIR, `${stem}.png`),
      await presentation.export({ slide, format: "png", scale: 1 }),
    );
    if (index < 2) afterHashes.push(sha256(bytes));
    const layout = await slide.export({ format: "layout" });
    await fs.writeFile(
      path.join(OUTPUT_DIR, `${stem}.layout.json`),
      await layout.text(),
      "utf8",
    );
  }

  await writeBlob(
    path.join(OUTPUT_DIR, "after-montage.webp"),
    await presentation.export({ format: "webp", montage: true, scale: 1 }),
  );

  const inspect = await presentation.inspect({
    kind: "slide,layout,textbox,shape,image,table,chart",
    include: "id,slide,name,title,textPreview,bbox,bboxUnit,isPlaceholder",
    maxChars: 50000,
  });
  await fs.writeFile(
    path.join(OUTPUT_DIR, "after-inspect.ndjson"),
    inspect.ndjson,
    "utf8",
  );

  const pptxPath = path.join(OUTPUT_DIR, "SkillAudit_Main_Figure_v3_3.pptx");
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(pptxPath);

  const savedPresentation = await PresentationFile.importPptx(
    await FileBlob.load(pptxPath),
  );
  const savedHashes = [];
  for (const [index, slide] of savedPresentation.slides.items.entries()) {
    const stem = `saved-slide-${String(index + 1).padStart(2, "0")}`;
    const bytes = await writeBlob(
      path.join(OUTPUT_DIR, `${stem}.png`),
      await savedPresentation.export({ slide, format: "png", scale: 1 }),
    );
    savedHashes.push(sha256(bytes));
    const layout = await slide.export({ format: "layout" });
    await fs.writeFile(
      path.join(OUTPUT_DIR, `${stem}.layout.json`),
      await layout.text(),
      "utf8",
    );
  }
  await writeBlob(
    path.join(OUTPUT_DIR, "saved-montage.webp"),
    await savedPresentation.export({ format: "webp", montage: true, scale: 1 }),
  );
  const savedInspect = await savedPresentation.inspect({
    kind: "slide,layout,textbox,shape,image,table,chart",
    include: "id,slide,name,title,textPreview,bbox,bboxUnit,isPlaceholder",
    maxChars: 50000,
  });
  await fs.writeFile(
    path.join(OUTPUT_DIR, "saved-inspect.ndjson"),
    savedInspect.ndjson,
    "utf8",
  );

  const qa = {
    slideCount: savedPresentation.slides.items.length,
    slideFrame: savedPresentation.slides.items[0].frame,
    preservedSlideHashes: beforeHashes.map((hash, index) => ({
      slide: index + 1,
      before: hash,
      after: afterHashes[index],
      unchanged: hash === afterHashes[index],
      savedUnchanged: hash === savedHashes[index],
    })),
    componentSlide: {
      nativeShapes: savedPresentation.slides.items[2].shapes.items.length,
      images: savedPresentation.slides.items[2].images.items.length,
      tables: savedPresentation.slides.items[2].tables.items.length,
      charts: savedPresentation.slides.items[2].charts.items.length,
    },
    output: pptxPath,
  };
  await fs.writeFile(
    path.join(OUTPUT_DIR, "qa.json"),
    JSON.stringify(qa, null, 2),
    "utf8",
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
