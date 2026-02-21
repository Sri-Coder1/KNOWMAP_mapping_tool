const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "login.html";
}

const graphSelect = document.getElementById("savedGraphsDropdown");
const loadBtn = document.getElementById("loadGraphsBtn");
const entitiesBox = document.getElementById("entitiesBox");
const crossLinksBox = document.getElementById("crossLinksBox");
const canvas = document.getElementById("graphCanvas");
const ctx = canvas.getContext("2d");

// ===============================
// LOAD SAVED GRAPHS BUTTON
// ===============================
loadBtn.addEventListener("click", loadSavedGraphs);

async function loadSavedGraphs() {
    try {
        const response = await fetch("/my-graphs", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        const graphs = await response.json();

        graphSelect.innerHTML = "<option value=''>-- Select Graph --</option>";

        graphs.forEach(graph => {
            const option = document.createElement("option");
            option.value = graph.id;
            option.textContent = `${graph.topic} (${graph.source})`;
            graphSelect.appendChild(option);
        });

    } catch (error) {
        console.error("Failed to load graphs:", error);
    }
}

// ===============================
// WHEN USER SELECTS A GRAPH
// ===============================
graphSelect.addEventListener("change", async function () {

    const graphId = this.value;
    if (!graphId) return;

    try {
        const response = await fetch(`/graph/${graphId}`, {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        if (!response.ok) {
            alert("Graph not found.");
            return;
        }

        const data = await response.json();

        displayEntities(data.entities);
        displayCrossLinks(data.cross_domain_links);
        drawGraph(data.graph);

    } catch (error) {
        console.error("Error loading graph:", error);
    }
});

// ===============================
// DISPLAY ENTITIES
// ===============================
function displayEntities(entities) {

    entitiesBox.innerHTML = "";

    entities.forEach(entity => {
        const div = document.createElement("div");
        div.textContent = entity;
        entitiesBox.appendChild(div);
    });
}

// ===============================
// DISPLAY CROSS LINKS
// ===============================
function displayCrossLinks(links) {

    crossLinksBox.innerHTML = "";

    links.forEach(link => {
        const div = document.createElement("div");
        div.textContent = `${link.source} → ${link.target}`;
        crossLinksBox.appendChild(div);
    });
}

// ===============================
// DRAW GRAPH
// ===============================
function drawGraph(graph) {

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const nodes = graph.nodes;
    const edges = graph.edges;

    const positions = {};

    nodes.forEach(node => {
        positions[node.id] = {
            x: Math.random() * 700 + 100,
            y: Math.random() * 500 + 50
        };

        ctx.beginPath();
        ctx.arc(positions[node.id].x, positions[node.id].y, 12, 0, 2 * Math.PI);
        ctx.fillStyle = "#ff9900";
        ctx.fill();

        ctx.fillStyle = "#000";
        ctx.fillText(node.id, positions[node.id].x + 15, positions[node.id].y);
    });

    edges.forEach(edge => {
        ctx.beginPath();
        ctx.moveTo(positions[edge.source].x, positions[edge.source].y);
        ctx.lineTo(positions[edge.target].x, positions[edge.target].y);
        ctx.strokeStyle = "#232f3e";
        ctx.stroke();
    });
}

// ===============================
// LOGOUT
// ===============================
function logout() {
    localStorage.removeItem("token");
    window.location.href = "login.html";
}
