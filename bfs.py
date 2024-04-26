from cells_classification import *
from base.client.constants import *
from classes import Pt
from heapq import *


def bfs_simple_cells(gamemap: Map, start_cell, final_cell):
    dist = [[10 ** 9 for x in range(gamemap.cols)] for y in range(gamemap.rows)]
    pred = [[(-1, -1) for x in range(gamemap.cols)] for y in range(gamemap.rows)]

    dist[start_cell[1]][start_cell[0]] = 0

    heap = [(0, start_cell)]

    while heap:
        d, xy = heappop(heap)
        x, y = xy
        if dist[y][x] != d:
            continue
        for direction in DIRECTIONS:
            x2, y2 = x + direction[0], y + direction[1]
            w = 1
            if is_my_cell(gamemap, x2, y2):
                w = 3
            if is_simple_cell(gamemap, x2, y2) and d + w < dist[y2][x2]:
                dist[y2][x2] = d + w
                pred[y2][x2] = (x, y)
                heappush(heap, (dist[y2][x2], (x2, y2)))

    x, y = final_cell
    path = []
    while x != -1:
        path.append((x, y))
        x, y = pred[y][x]
    path.reverse()
    moves = []
    for i in range(len(path) - 1):
        moves.append((Pt(path[i][0], path[i][1]), Pt(path[i + 1][0], path[i + 1][1])))
    return moves
