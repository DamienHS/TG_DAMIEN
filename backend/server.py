from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib.parse import urlparse, parse_qs
import psycopg2

from graph import Graph
from dijkstra import dijkstra
from coloring import greedy_coloring

# ============================================================
# PostgreSQL Connection
# ============================================================
conn = psycopg2.connect(
    dbname="wastegraph",
    user="postgres",
    password="1234",
    host="localhost",
    port=5432
)
cursor = conn.cursor()


# ============================================================
# Load graph from DB for Dijkstra / Coloring
# ============================================================
def load_graph_from_db():
    g = Graph()

    cursor.execute("SELECT id, x, y, capacity FROM nodes")
    for node_id, x, y, cap in cursor.fetchall():
        g.add_node(node_id, x=x, y=y, capacity=cap)

    cursor.execute("SELECT src, dst, weight FROM edges")
    for src, dst, weight in cursor.fetchall():
        g.add_edge(src, dst, weight)

    return g


# ============================================================
# JSON Response
# ============================================================
def json_response(handler, data, status=200):
    payload = json.dumps(data).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", len(payload))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.end_headers()
    handler.wfile.write(payload)


# ============================================================
# HTTP Handler
# ============================================================
class MyHandler(BaseHTTPRequestHandler):

    # ---------------------------------------------------------
    # GET
    # ---------------------------------------------------------
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        # ===== GET GRAPH (with IDs on edges) =====
        if path == "/graph":
            cursor.execute("SELECT id, x, y FROM nodes")
            rows = cursor.fetchall()
            nodes = {nid: {"x": x, "y": y} for nid, x, y in rows}

            cursor.execute("SELECT id, src, dst, weight FROM edges")
            rows = cursor.fetchall()

            edges = {}
            for edge_id, src, dst, w in rows:
                edges.setdefault(src, []).append([dst, w, edge_id])

            return json_response(self, {"nodes": nodes, "edges": edges})

        # ===== DIJKSTRA =====
        if path == "/algo/dijkstra":
            src = params.get("src", [""])[0]
            dst = params.get("dst", [""])[0]

            graph = load_graph_from_db()
            result = dijkstra(graph, src, dst)
            return json_response(self, {"result": result})

        # ===== COLORING =====
        if path == "/algo/coloring":
            graph = load_graph_from_db()
            colors = greedy_coloring(graph)
            return json_response(self, {"colors": colors})

        # ===== DIJKSTRA MULTI =====
        if path == "/algo/dijkstra/multi":
            src = params.get("src", [""])[0]
            targets = params.get("targets", [""])[0].split(",")

            graph = load_graph_from_db()
            full_path = []
            total = 0
            current = src

            for t in targets:
                p, dist = dijkstra(graph, current, t)
                if full_path:
                    p = p[1:]
                full_path.extend(p)
                total += dist
                current = t

            return json_response(self, {
                "path": full_path,
                "points_to_visit": targets,
                "total_distance": total
            })

        # ===== HOMEPAGE =====
        if path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b"<h1>WasteGraph API Running</h1>")
            return

        self.send_error(404, "Not found")


    # ---------------------------------------------------------
    # POST
    # ---------------------------------------------------------
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        length = int(self.headers["Content-Length"])
        data = json.loads(self.rfile.read(length).decode())

        # ===== UPDATE EDGE WEIGHT =====
        if path == "/graph/edge/update":
            edge_id = data["id"]
            new_weight = data["weight"]

            cursor.execute(
                "UPDATE edges SET weight=%s WHERE id=%s",
                (new_weight, edge_id)
            )
            conn.commit()

            return json_response(self, {"status": "edge-updated"})

        # ===== ADD NODE =====
        if path == "/graph/node":
            cursor.execute(
                """INSERT INTO nodes (id, x, y, capacity)
                   VALUES (%s, %s, %s, %s)
                   ON CONFLICT (id) DO NOTHING""",
                (data["id"], data["x"], data["y"], None)
            )
            conn.commit()
            return json_response(self, {"status": "node-added"})

        # ===== ADD EDGE =====
        if path == "/graph/edge":
            u = data["u"]
            v = data["v"]
            weight = data["weight"]

            # Check if edge exists
            cursor.execute(
                "SELECT 1 FROM edges WHERE (src=%s AND dst=%s) OR (src=%s AND dst=%s)",
                (u, v, v, u)
            )

            if cursor.fetchone():
                return json_response(self, {"status": "edge-already-exists"})

            cursor.execute(
                "INSERT INTO edges (src, dst, weight) VALUES (%s, %s, %s)",
                (u, v, weight)
            )
            conn.commit()

            return json_response(self, {"status": "edge-added"})

        self.send_error(404, "Not found")


    # ---------------------------------------------------------
    # DELETE
    # ---------------------------------------------------------
    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        # ===== DELETE NODE =====
        if path == "/graph/node":
            node_id = params.get("id", [""])[0]

            cursor.execute("DELETE FROM edges WHERE src=%s OR dst=%s", (node_id, node_id))
            cursor.execute("DELETE FROM nodes WHERE id=%s", (node_id,))
            conn.commit()

            return json_response(self, {"deleted-node": node_id})

        # ===== DELETE EDGE (via ID) =====
        if path == "/graph/edge":
            edge_id = params.get("id", [""])[0]

            cursor.execute("DELETE FROM edges WHERE id=%s", (edge_id,))
            conn.commit()

            return json_response(self, {"deleted-edge": edge_id})

        self.send_error(404, "Not found")


    # ---------------------------------------------------------
    # OPTIONS (CORS)
    # ---------------------------------------------------------
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


# ============================================================
# RUN SERVER
# ============================================================
def run():
    server = HTTPServer(("localhost", 8000), MyHandler)
    print("Serveur lancé sur http://localhost:8000 ...")
    server.serve_forever()


if __name__ == "__main__":
    run()
