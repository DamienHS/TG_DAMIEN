import json
import http.client

nodes = {
    "DEPOT": (100, 200),
    "B": (250, 100),
    "G": (430, 80),
    "D": (220, 230),
    "A": (140, 330),
    "C": (350, 250),
    "F": (450, 320),
    "E": (330, 330)
}

edges = [
    ("DEPOT", "B", 2.3),
    ("DEPOT", "A", 2.0),
    ("B", "G", 1.2),
    ("G", "C", 1.5),
    ("B", "D", 2.7),
    ("C", "F", 1.9),
    ("C", "D", 1.8),
    ("D", "A", 2.2),
    ("A", "E", 3.0),
    ("D", "E", 2.5)
]

conn = http.client.HTTPConnection("localhost", 8000)

# Ajouter nodes
for node, (x, y) in nodes.items():
    payload = json.dumps({"id": node, "x": x, "y": y})
    conn.request("POST", "/graph/node", body=payload, headers={
        "Content-Type": "application/json"
    })
    res = conn.getresponse()
    print(res.status, res.read().decode())

# Ajouter edges
for u, v, w in edges:
    payload = json.dumps({"u": u, "v": v, "weight": w})
    conn.request("POST", "/graph/edge", body=payload, headers={
        "Content-Type": "application/json"
    })
    res = conn.getresponse()
    print(res.status, res.read().decode())

conn.close()
