import cv2, math, random
import numpy as np
from collections import defaultdict


class Graph:
    def __init__(self):
        self.nodes = set()
        self.nodes_pos = {}
        self.edges = defaultdict(list)
        self.distances = {}
        self.distances_names = {}

    def add_node(self, value):
        self.nodes.add(value)

    def add_edge(self, from_node, to_node, distance, name):
        self.edges[from_node].append(to_node)
        #self.edges[to_node].append(from_node)
        self.distances[(from_node, to_node)] = distance
        self.distances_names[(from_node, to_node)] = name


def dijsktra(graph, initial):
    nodeslen = len(graph.nodes)
    r = 100
    image = np.zeros((768, 1024, 3), np.uint8)
    i = 0
    center = 500
    for node in graph.nodes:
        angle = math.radians(360 * i / nodeslen)
        x = r * np.cos(angle)
        y = r * np.sin(angle)
        graph.nodes_pos[node] = (int(center + x), int(center + y))
        image = cv2.circle(image, (int(center + x), int(center + y)), 2, (255, 255, 255), 5)
        i += 1
    
    for node in graph.edges:
        fromPos = graph.nodes_pos[node]
        for tonode in graph.edges[node]:
            toPos = graph.nodes_pos[tonode]
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            image = cv2.arrowedLine(image, fromPos, toPos, (r, g, b), 2)
            x = (fromPos[0] + toPos[0]) / 2
            y = (fromPos[1] + toPos[1]) / 2
            cv2.putText(image, graph.distances_names[(node, tonode)], (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX , 0.5, (255, 0, 0), 1)

    cv2.imshow('img', image)
    cv2.waitKey(0)

    visited = {initial: 0}
    path = {}

    nodes = set(graph.nodes)

    """while nodes: 
        min_node = None
        for node in nodes:
            if node in visited:
                if min_node is None:
                    min_node = node
                elif visited[node] < visited[min_node]:
                    min_node = node

        if min_node is None:
            break

    nodes.remove(min_node)
    current_weight = visited[min_node]

    for edge in graph.edges[min_node]:
        weight = current_weight + graph.distance[(min_node, edge)]
        if edge not in visited or weight < visited[edge]:
            visited[edge] = weight
            path[edge] = min_node"""

    return visited, path
