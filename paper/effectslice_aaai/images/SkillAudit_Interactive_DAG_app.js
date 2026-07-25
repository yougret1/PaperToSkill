(() => {
  "use strict";

  const SVG_NS = "http://www.w3.org/2000/svg";
  const NODE_RADIUS = 42;
  const ARROW_CLEARANCE = 14;
  const DRAG_THRESHOLD = 10;

  const nodes = [
    { id: "A1", x: 210, y: 455 },
    { id: "A2", x: 520, y: 205 },
    { id: "A3", x: 620, y: 690 },
    { id: "A4", x: 1000, y: 355 },
    { id: "A5", x: 1370, y: 555 },
  ];

  const edges = [
    { from: "A1", to: "A2", added: false },
    { from: "A1", to: "A3", added: false },
    { from: "A2", to: "A4", added: false },
    { from: "A3", to: "A4", added: false },
    { from: "A4", to: "A5", added: false },
  ];

  const svg = document.getElementById("dag");
  const edgeLayer = document.getElementById("edges");
  const draftLayer = document.getElementById("draft-edge");
  const nodeLayer = document.getElementById("nodes");
  const status = document.getElementById("status");

  let selectedNodeId = null;
  let dragState = null;

  const nodeById = (id) => nodes.find((node) => node.id === id);

  function svgElement(tag, attributes = {}) {
    const element = document.createElementNS(SVG_NS, tag);
    for (const [name, value] of Object.entries(attributes)) {
      element.setAttribute(name, String(value));
    }
    return element;
  }

  function pointFromEvent(event) {
    const point = svg.createSVGPoint();
    point.x = event.clientX;
    point.y = event.clientY;
    const matrix = svg.getScreenCTM();
    return matrix ? point.matrixTransform(matrix.inverse()) : { x: 0, y: 0 };
  }

  function shortenedLine(source, target, targetClearance = ARROW_CLEARANCE) {
    const dx = target.x - source.x;
    const dy = target.y - source.y;
    const length = Math.hypot(dx, dy) || 1;
    const ux = dx / length;
    const uy = dy / length;
    return {
      x1: source.x + ux * NODE_RADIUS,
      y1: source.y + uy * NODE_RADIUS,
      x2: target.x - ux * (NODE_RADIUS + targetClearance),
      y2: target.y - uy * (NODE_RADIUS + targetClearance),
    };
  }

  function renderEdges() {
    edgeLayer.replaceChildren();
    for (const edge of edges) {
      const source = nodeById(edge.from);
      const target = nodeById(edge.to);
      edgeLayer.append(
        svgElement("line", {
          ...shortenedLine(source, target),
          class: edge.added ? "edge is-added" : "edge",
          "data-from": edge.from,
          "data-to": edge.to,
        }),
      );
    }
  }

  function renderNodes() {
    nodeLayer.replaceChildren();
    for (const node of nodes) {
      const group = svgElement("g", {
        class: `node${selectedNodeId === node.id ? " is-selected" : ""}`,
        "data-node-id": node.id,
        "aria-label": `Node ${node.id}`,
        role: "button",
      });
      group.append(
        svgElement("circle", { cx: node.x, cy: node.y, r: NODE_RADIUS }),
      );
      const label = svgElement("text", { x: node.x, y: node.y });
      label.textContent = node.id;
      group.append(label);
      group.addEventListener("pointerdown", beginDrag);
      nodeLayer.append(group);
    }
  }

  function setDropTarget(nodeId) {
    for (const element of nodeLayer.querySelectorAll(".node")) {
      element.classList.toggle(
        "is-drop-target",
        Boolean(nodeId) && element.dataset.nodeId === nodeId,
      );
    }
  }

  function nearestNode(point, excludedId = null) {
    let nearest = null;
    let nearestDistance = NODE_RADIUS + 16;
    for (const node of nodes) {
      if (node.id === excludedId) continue;
      const distance = Math.hypot(point.x - node.x, point.y - node.y);
      if (distance <= nearestDistance) {
        nearest = node;
        nearestDistance = distance;
      }
    }
    return nearest;
  }

  function drawDraft(source, pointer) {
    const distance = Math.hypot(pointer.x - source.x, pointer.y - source.y);
    if (distance <= NODE_RADIUS + ARROW_CLEARANCE) {
      draftLayer.replaceChildren();
      return;
    }
    draftLayer.replaceChildren(
      svgElement("line", {
        ...shortenedLine(source, pointer, 0),
        class: "draft",
      }),
    );
  }

  function beginDrag(event) {
    if (event.button !== 0) return;
    event.preventDefault();
    const sourceId = event.currentTarget.dataset.nodeId;
    selectedNodeId = sourceId;
    dragState = {
      pointerId: event.pointerId,
      sourceId,
      start: pointFromEvent(event),
      moved: false,
    };
    svg.setPointerCapture(event.pointerId);
    renderNodes();
  }

  function edgeExists(from, to) {
    return edges.some((edge) => edge.from === from && edge.to === to);
  }

  function hasPath(from, to) {
    const adjacency = new Map(nodes.map((node) => [node.id, []]));
    for (const edge of edges) adjacency.get(edge.from).push(edge.to);
    const stack = [from];
    const visited = new Set();
    while (stack.length) {
      const current = stack.pop();
      if (current === to) return true;
      if (visited.has(current)) continue;
      visited.add(current);
      stack.push(...adjacency.get(current));
    }
    return false;
  }

  function canAddEdge(from, to) {
    return from !== to && !edgeExists(from, to) && !hasPath(to, from);
  }

  function flashInvalid(nodeId) {
    const element = nodeLayer.querySelector(`[data-node-id="${nodeId}"]`);
    if (!element) return;
    element.classList.remove("is-invalid");
    requestAnimationFrame(() => element.classList.add("is-invalid"));
    window.setTimeout(() => element.classList.remove("is-invalid"), 520);
  }

  function finishDrag(event) {
    if (!dragState || dragState.pointerId !== event.pointerId) return;
    const target = nearestNode(pointFromEvent(event), dragState.sourceId);
    if (dragState.moved && target) {
      if (canAddEdge(dragState.sourceId, target.id)) {
        edges.push({ from: dragState.sourceId, to: target.id, added: true });
        renderEdges();
        status.textContent = `Added dependency ${dragState.sourceId} to ${target.id}.`;
      } else {
        flashInvalid(target.id);
        status.textContent = "The dependency was not added because it was invalid or cyclic.";
      }
    } else if (!dragState.moved) {
      status.textContent = `Selected node ${dragState.sourceId}.`;
    }
    cleanupDrag(event.pointerId);
  }

  function cleanupDrag(pointerId) {
    if (svg.hasPointerCapture(pointerId)) svg.releasePointerCapture(pointerId);
    dragState = null;
    draftLayer.replaceChildren();
    setDropTarget(null);
  }

  svg.addEventListener("pointermove", (event) => {
    if (!dragState || dragState.pointerId !== event.pointerId) return;
    const pointer = pointFromEvent(event);
    const distance = Math.hypot(
      pointer.x - dragState.start.x,
      pointer.y - dragState.start.y,
    );
    if (distance >= DRAG_THRESHOLD) dragState.moved = true;
    if (!dragState.moved) return;
    drawDraft(nodeById(dragState.sourceId), pointer);
    setDropTarget(nearestNode(pointer, dragState.sourceId)?.id ?? null);
  });

  svg.addEventListener("pointerup", finishDrag);
  svg.addEventListener("pointercancel", (event) => {
    if (dragState?.pointerId === event.pointerId) cleanupDrag(event.pointerId);
  });

  renderEdges();
  renderNodes();
})();
