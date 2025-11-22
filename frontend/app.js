const API = "http://127.0.0.1:8000";

const canvas = document.getElementById("graph-canvas");
const resultsBox = document.getElementById("results");
const sourceSelect = document.getElementById("source-select");
const SVG_NS = "http://www.w3.org/2000/svg";

let graphData = null;

// =========================================================
// PALETTE DE COULEURS (10 couleurs + génération automatique)
// =========================================================
const COLOR_MAP = {
    0: "#add8e6",
    1: "#ffe599",
    2: "#b6d7a8",
    3: "#f4cccc",
    4: "#c9daf8",
    5: "#d9d2e9",
    6: "#ead1dc",
    7: "#fff2cc",
    8: "#d0e0e3",
    9: "#cfe2f3"
};

function getColor(index) {
    if (COLOR_MAP[index]) return COLOR_MAP[index];

    // Couleur générée automatiquement si limite dépassée
    return `hsl(${(index * 47) % 360}, 70%, 75%)`;
}

// =========================================================
// LÉGENDE DYNAMIQUE
// =========================================================
function updateLegend(colorsUsed) {
    const legendList = document.getElementById("legend-list");
    legendList.innerHTML = "";

    for (const colorId in colorsUsed) {
        const color = colorsUsed[colorId];

        const li = document.createElement("li");
        li.innerHTML = `
            <span class="color-bubble" style="background:${color}"></span>
            Jour/équipe ${colorId}
        `;
        legendList.appendChild(li);
    }
}

// =========================================================
// CHARGER LE GRAPHE
// =========================================================
async function loadGraph() {
    const res = await fetch(`${API}/graph`);
    graphData = await res.json();

    drawGraph(graphData);
    fillSelects(graphData);
    updateGraphLists(graphData);
}

// =========================================================
// REMPLIR LES SELECTS
// =========================================================
function fillSelects(graph) {
    sourceSelect.innerHTML = "";
    const multi = document.getElementById("multi-targets");
    multi.innerHTML = "";

    for (const node in graph.nodes) {
        sourceSelect.appendChild(new Option(node, node));
        multi.appendChild(new Option(node, node));
    }
}

// =========================================================
// DESSIN DU GRAPHE (SVG)
// =========================================================
function drawGraph(graph) {
    const { nodes, edges } = graph;

    canvas.innerHTML = "";

    // --- Edges ---
    for (const u in edges) {
        edges[u].forEach(([v, w]) => {
            const [x1, y1] = [nodes[u].x, nodes[u].y];
            const [x2, y2] = [nodes[v].x, nodes[v].y];

            const line = document.createElementNS(SVG_NS, "line");
            line.setAttribute("x1", x1);
            line.setAttribute("y1", y1);
            line.setAttribute("x2", x2);
            line.setAttribute("y2", y2);
            line.setAttribute("stroke", "#999");
            line.setAttribute("stroke-width", 1);
            canvas.appendChild(line);

            const label = document.createElementNS(SVG_NS, "text");
            label.setAttribute("x", (x1 + x2) / 2);
            label.setAttribute("y", (y1 + y2) / 2 - 5);
            label.textContent = w;
            label.setAttribute("font-size", "13");
            canvas.appendChild(label);
        });
    }

    // --- Nodes ---
    for (const id in nodes) {
        const { x, y } = nodes[id];

        const circle = document.createElementNS(SVG_NS, "circle");
        circle.setAttribute("cx", x);
        circle.setAttribute("cy", y);
        circle.setAttribute("r", 22);
        circle.setAttribute("stroke", "black");
        circle.setAttribute("stroke-width", "2");
        circle.setAttribute("fill", "white");
        circle.id = `node-${id}`;
        canvas.appendChild(circle);

        const text = document.createElementNS(SVG_NS, "text");
        text.setAttribute("x", x);
        text.setAttribute("y", y + 5);
        text.textContent = id;
        text.setAttribute("font-size", "14");
        text.setAttribute("text-anchor", "middle");
        canvas.appendChild(text);
    }
}

// =========================================================
// COLORIAGE
// =========================================================
async function doColoring() {
    const res = await fetch(`${API}/algo/coloring`);
    const data = await res.json();

    const colorsUsed = {};

    for (const node in data.colors) {
        const colorId = data.colors[node];
        const color = getColor(colorId);
        colorsUsed[colorId] = color;

        document.getElementById(`node-${node}`).setAttribute("fill", color);
    }

    resultsBox.innerHTML = `
        <h3>Coloriage du graphe</h3>
        <p>${Object.keys(colorsUsed).length} couleurs utilisées.</p>
    `;

    updateLegend(colorsUsed);
}

// =========================================================
// DIJKSTRA MULTI-TARGET
// =========================================================
async function doDijkstraMulti() {
    const src = sourceSelect.value;
    const targets = [...document.getElementById("multi-targets").selectedOptions].map(o => o.value);

    if (targets.length === 0) return alert("Choisis au moins un point.");

    const res = await fetch(`${API}/algo/dijkstra/multi?src=${src}&targets=${targets.join(",")}`);
    const data = await res.json();

    resultsBox.innerHTML = `
        <h3>Chemin obtenu</h3>
        <p><strong>Total :</strong> ${data.total_distance}</p>
        <p><strong>Chemin :</strong> ${data.path.join(" → ")}</p>
    `;

    resetGraphAppearance();
    highlightPath(data.path);
}

// =========================================================
// CONTRAINTE : CHANGER LE POIDS D'UNE ARÊTE
// =========================================================
async function updateConstraint() {
    const edgeId = document.getElementById("constraintEdgeSelect").value;
    const value = parseFloat(document.getElementById("constraintValue").value);

    if (!edgeId || isNaN(value)) return alert("Valeurs invalides.");

    const res = await fetch(`${API}/graph/edge/update`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: edgeId, weight: value })
    });

    loadGraph();
}

// =========================================================
// AJOUT / SUPPRESSION NOEUDS / ARÊTES
// =========================================================
async function addNode() {
    const id = document.getElementById("addNodeId").value.trim();
    const x = parseFloat(document.getElementById("addNodeX").value);
    const y = parseFloat(document.getElementById("addNodeY").value);

    if (!id || isNaN(x) || isNaN(y)) return alert("Champs invalides.");

    const res = await fetch(`${API}/graph/node`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id, x, y })
    });

    loadGraph();
}

async function addEdge() {
    const u = document.getElementById("addEdgeSrc").value.trim();
    const v = document.getElementById("addEdgeDst").value.trim();
    const weight = parseFloat(document.getElementById("addEdgeWeight").value);

    if (!u || !v || isNaN(weight)) return alert("Champs invalides.");
    if (u === v) return alert("Impossible de relier un nœud à lui-même.");

    // Vérif dans graphData
    if (!graphData.nodes[u] || !graphData.nodes[v]) {
        return alert("Nœud inexistant.");
    }

    const neighbors = graphData.edges[u] || [];
    if (neighbors.some(e => e[0] === v)) {
        return alert("Arête déjà existante.");
    }

    await fetch(`${API}/graph/edge`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ u, v, weight })
    });

    loadGraph();
}

async function deleteNode() {
    const id = document.getElementById("deleteNodeSelect").value;

    await fetch(`${API}/graph/node?id=${id}`, { method: "DELETE" });
    loadGraph();
}

async function deleteEdge() {
    const edgeId = document.getElementById("deleteEdgeSelect").value;

    await fetch(`${API}/graph/edge?id=${edgeId}`, {
        method: "DELETE"
    });

    loadGraph();
}

// =========================================================
// HIGHLIGHT
// =========================================================
function resetGraphAppearance() {
    canvas.querySelectorAll("circle").forEach(n => {
        n.setAttribute("fill", "white");
        n.setAttribute("stroke", "black");
    });

    canvas.querySelectorAll("line").forEach(l => {
        l.setAttribute("stroke", "#999");
        l.setAttribute("stroke-width", 1);
    });
}

function highlightPath(path) {
    for (let i = 0; i < path.length; i++) {
        const node = path[i];
        document.getElementById(`node-${node}`).setAttribute("fill", "#fff5a3");

        if (i < path.length - 1) highlightEdge(path[i], path[i + 1]);
    }
}

function highlightEdge(a, b) {
    const A = graphData.nodes[a];
    const B = graphData.nodes[b];

    canvas.querySelectorAll("line").forEach(edge => {
        const x1 = parseInt(edge.getAttribute("x1"));
        const y1 = parseInt(edge.getAttribute("y1"));
        const x2 = parseInt(edge.getAttribute("x2"));
        const y2 = parseInt(edge.getAttribute("y2"));

        if ((x1 === A.x && y1 === A.y && x2 === B.x && y2 === B.y) ||
            (x1 === B.x && y1 === B.y && x2 === A.x && y2 === A.y)) {
            edge.setAttribute("stroke", "#1e90ff");
            edge.setAttribute("stroke-width", 4);
        }
    });
}

// =========================================================
// UPDATE LISTES DE SUPPRESSION
// =========================================================
function updateGraphLists(graph) {
    const nodeSelect = document.getElementById("deleteNodeSelect");
    nodeSelect.innerHTML = "";

    for (const id in graph.nodes) {
        nodeSelect.appendChild(new Option(id, id));
    }

    const edgeSelect = document.getElementById("deleteEdgeSelect");
    edgeSelect.innerHTML = "";

    const constraintSelect = document.getElementById("constraintEdgeSelect");
    constraintSelect.innerHTML = "";

    for (const src in graph.edges) {
        graph.edges[src].forEach(edge => {
            const dst = edge[0];
            const w = edge[1];
            const edgeId = edge[2]; // id dans la BDD

            edgeSelect.appendChild(new Option(`${src} → ${dst} (${w})`, edgeId));
            constraintSelect.appendChild(new Option(`${src} → ${dst} (actuel: ${w})`, edgeId));
        });
    }
}

// =========================================================
// EVENTS
// =========================================================
document.getElementById("btn-coloring").onclick = doColoring;
document.getElementById("btn-dijkstra-multi").onclick = doDijkstraMulti;

// =========================================================
// START
// =========================================================
loadGraph();
