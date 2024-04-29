import heapq
import numpy as np


def _heuristic_(a, b):
    return np.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)


def a_star(array, start_xy, goal_xy):
    start = start_xy[1], start_xy[0]
    goal = goal_xy[1], goal_xy[0]
    neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    close_set = set()
    came_from = {}
    g_score = {start: 0}
    f_score = {start: _heuristic_(start, goal)}
    open_heap = []

    heapq.heappush(open_heap, (f_score[start], start))

    while open_heap:
        current = heapq.heappop(open_heap)[1]

        if current == goal:
            data = []
            while current in came_from:
                data.insert(0, (current[1], current[0]))
                current = came_from[current]
            return data

        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            if 0 <= neighbor[0] < array.shape[0]:
                if 0 <= neighbor[1] < array.shape[1]:
                    tentative_g_score = g_score[current] + array[neighbor]
                    if neighbor in close_set and tentative_g_score >= g_score.get(neighbor, 0):
                        continue

                    if tentative_g_score < g_score.get(neighbor, 0) or neighbor not in [i[1] for i in open_heap]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + _heuristic_(neighbor, goal)
                        heapq.heappush(open_heap, (f_score[neighbor], neighbor))
