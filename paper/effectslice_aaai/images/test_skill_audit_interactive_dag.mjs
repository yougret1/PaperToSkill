import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const playwrightPath = process.env.PLAYWRIGHT_PATH;
const edgePath = process.env.EDGE_PATH;
const htmlPath = path.resolve(
  process.env.DAG_HTML ??
    "paper/effectslice_aaai/images/SkillAudit_Interactive_DAG_index.html",
);
const outputDir = path.dirname(htmlPath);

if (!playwrightPath || !edgePath) {
  throw new Error("Set PLAYWRIGHT_PATH and EDGE_PATH.");
}

const { chromium } = await import(pathToFileURL(playwrightPath).href);
const browser = await chromium.launch({ executablePath: edgePath, headless: true });
const page = await browser.newPage({ viewport: { width: 1600, height: 900 } });
const consoleErrors = [];
page.on("console", (message) => {
  if (message.type() === "error") consoleErrors.push(message.text());
});
page.on("pageerror", (error) => consoleErrors.push(error.message));

try {
  await page.goto(pathToFileURL(htmlPath).href, { waitUntil: "load" });
  await page.waitForSelector(".node");

  const initialNodeCount = await page.locator(".node").count();
  const initialEdgeCount = await page.locator(".edge").count();
  if (initialNodeCount !== 5 || initialEdgeCount !== 5) {
    throw new Error(
      `Expected 5 nodes and 5 edges; got ${initialNodeCount} nodes and ${initialEdgeCount} edges.`,
    );
  }

  await page.screenshot({
    path: path.join(outputDir, "SkillAudit_Interactive_DAG_preview.png"),
  });

  await page.locator('[data-node-id="A3"]').click();
  const selectedFill = await page
    .locator('[data-node-id="A3"] circle')
    .evaluate((element) => getComputedStyle(element).fill);
  if (selectedFill !== "rgb(224, 87, 91)") {
    throw new Error(`Selected node fill is ${selectedFill}, not the required red.`);
  }

  const a2 = await page.locator('[data-node-id="A2"] circle').boundingBox();
  const a3 = await page.locator('[data-node-id="A3"] circle').boundingBox();
  if (!a2 || !a3) throw new Error("Could not resolve node bounds for drag test.");
  await page.mouse.move(a2.x + a2.width / 2, a2.y + a2.height / 2);
  await page.mouse.down();
  await page.mouse.move(a3.x + a3.width / 2, a3.y + a3.height / 2, { steps: 12 });
  await page.mouse.up();

  const addedEdgeCount = await page.locator(".edge.is-added").count();
  const addedEdge = page.locator('.edge.is-added[data-from="A2"][data-to="A3"]');
  if (addedEdgeCount !== 1 || (await addedEdge.count()) !== 1) {
    throw new Error("Dragging A2 to A3 did not create exactly one added edge.");
  }
  const dashPattern = await addedEdge.evaluate(
    (element) => getComputedStyle(element).strokeDasharray,
  );
  if (!dashPattern || dashPattern === "none") {
    throw new Error("The added edge is not dashed.");
  }

  await page.screenshot({
    path: path.join(outputDir, "SkillAudit_Interactive_DAG_preview_added_edge.png"),
  });

  const a5 = await page.locator('[data-node-id="A5"] circle').boundingBox();
  const a1 = await page.locator('[data-node-id="A1"] circle').boundingBox();
  if (!a5 || !a1) throw new Error("Could not resolve node bounds for cycle test.");
  await page.mouse.move(a5.x + a5.width / 2, a5.y + a5.height / 2);
  await page.mouse.down();
  await page.mouse.move(a1.x + a1.width / 2, a1.y + a1.height / 2, { steps: 12 });
  await page.mouse.up();
  const countAfterCycleAttempt = await page.locator(".edge.is-added").count();
  if (countAfterCycleAttempt !== 1) {
    throw new Error("A cycle-forming edge was incorrectly added.");
  }

  if (consoleErrors.length) {
    throw new Error(`Browser errors: ${consoleErrors.join(" | ")}`);
  }

  await page.setViewportSize({ width: 800, height: 450 });
  await page.reload({ waitUntil: "load" });
  await page.waitForSelector(".node");
  await page.screenshot({
    path: path.join(outputDir, "SkillAudit_Interactive_DAG_preview_800x450.png"),
  });

  const report = {
    viewport: "1600x900",
    compressedPreviewViewport: "800x450",
    initialNodeCount,
    initialEdgeCount,
    selectedFill,
    addedEdge: "A2 -> A3",
    addedEdgeCount,
    dashPattern,
    cycleAttempt: "A5 -> A1",
    cycleRejected: countAfterCycleAttempt === 1,
    consoleErrors,
  };
  await fs.writeFile(
    path.join(outputDir, "SkillAudit_Interactive_DAG_qa.json"),
    JSON.stringify(report, null, 2),
    "utf8",
  );
} finally {
  await browser.close();
}
