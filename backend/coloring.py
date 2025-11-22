def greedy_coloring(graph):
    colors = {}

    for node in graph.nodes:
        used = {
            colors[neighbor]
            for neighbor, _ in graph.edges[node]
            if neighbor in colors
        }

        color = 0
        while color in used:
            color += 1

        colors[node] = color

    return colors
