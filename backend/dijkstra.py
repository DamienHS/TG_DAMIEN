import heapq

def dijkstra(graph, src, dst=None):

    if src not in graph.nodes:
        return [], float("inf")

    dist = {node: float("inf") for node in graph.nodes}
    dist[src] = 0

    prev = {node: None for node in graph.nodes}

    pq = [(0, src)]

    while pq:
        current_dist, node = heapq.heappop(pq)

        if current_dist > dist[node]:
            continue

        for neighbor, weight in graph.edges[node]:
            new_dist = dist[node] + weight

            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                prev[neighbor] = node
                heapq.heappush(pq, (new_dist, neighbor))

    if dst is not None:
        if dist[dst] == float("inf"):
            return [], float("inf")

        path = []
        current = dst
        while current is not None:
            path.append(current)
            current = prev[current]
        path.reverse()

        return path, dist[dst]

    return dist, prev
