from base.client.map import Map
from base.client.constants import *
from copy import deepcopy
from classes import Pt
from heapq import *


def is_valid(gamemap: Map, x, y):
    if not gamemap.isValidPosition(x, y):
        return False
    if gamemap.grid[y][x].tile == gamemap.player_index:
        return True
    return gamemap.grid[y][x].tile not in [TILE_MOUNTAIN, TILE_OBSTACLE] and not gamemap.grid[y][
        x].isCity and not gamemap.grid[y][x].isGeneral


def build_graph(gamemap: Map, gather_xy, general_ban):
    general = gamemap.generals[gamemap.player_index]
    dist = [[1000 for x in range(gamemap.cols)] for y in range(gamemap.rows)]
    pred = [[(-1, -1) for x in range(gamemap.cols)] for y in range(gamemap.rows)]
    dist[gather_xy[1]][gather_xy[0]] = 0
    heap = [(0, gather_xy)]
    while heap:
        d, xy = heappop(heap)
        x, y = xy
        if dist[y][x] != d:
            continue
        for direct in DIRECTIONS:
            x2 = x + direct[0]
            y2 = y + direct[1]
            if x2 == general.x and y2 == general.y and general_ban:
                continue
            if is_valid(gamemap, x2, y2):
                cost = 3
                if gamemap.grid[y2][x2].tile == gamemap.player_index and gamemap.grid[y2][x2].army > 0:
                    cost = 1 / gamemap.grid[y2][x2].army
                if d + cost < dist[y2][x2]:
                    dist[y2][x2] = d + cost
                    heappush(heap, (dist[y2][x2], (x2, y2)))
                    pred[y2][x2] = (x, y)
    g = [[] for _ in range(gamemap.cols * gamemap.rows)]
    delta_army = [0 for _ in range(gamemap.cols * gamemap.rows)]
    for y in range(gamemap.rows):
        for x in range(gamemap.cols):
            if gamemap.grid[y][x].tile == gamemap.player_index:
                delta = gamemap.grid[y][x].army - 1
            elif gamemap.grid[y][x].tile == TILE_EMPTY:
                delta = -1
            else:
                delta = -(gamemap.grid[y][x].army + 1)
            delta_army[x * gamemap.rows + y] = delta
            if pred[y][x] != (-1, -1):
                xp, yp = pred[y][x]
                g[xp * gamemap.rows + yp].append(x * gamemap.rows + y)
    return delta_army, g


def gather_army(gamemap: Map, gather_xy, turns_limit, army_limit, general_ban=False):
    delta_army, g = build_graph(gamemap, gather_xy, general_ban)
    dp = [[delta_army[v] for turns_num in range(turns_limit + 1)] for v in
          range(gamemap.rows * gamemap.cols)]
    prev = [[[] for turns_num in range(turns_limit + 1)] for _ in
            range(gamemap.rows * gamemap.cols)]

    def dfs(v):
        for u in g[v]:
            dfs(u)
            ndp = dp[v].copy()
            nprev = deepcopy(prev[v])
            for el in nprev:
                el.append(-1)
            for last_turns in range(0, turns_limit + 1):
                for turns in range(last_turns + 1, turns_limit + 1):
                    val = dp[v][turns - last_turns - 1] + dp[u][last_turns]
                    if val > ndp[turns]:
                        ndp[turns] = val
                        nprev[turns] = prev[v][turns - last_turns - 1] + [last_turns]
            dp[v], ndp = ndp, dp[v]
            prev[v], nprev = nprev, prev[v]

    start_v = gather_xy[0] * gamemap.rows + gather_xy[1]
    dfs(start_v)

    all_moves = []

    def get_moves(v, turns):
        for i in range(len(g[v])):
            u = g[v][i]
            left_turns = prev[v][turns][i]
            if left_turns != -1:
                get_moves(u, left_turns)
                all_moves.append((u, v))

    while turns_limit > 0 and (
            dp[start_v][turns_limit] == dp[start_v][turns_limit - 1] or dp[start_v][
        turns_limit - 1] >= army_limit):
        turns_limit -= 1

    get_moves(start_v, turns_limit)

    all_moves_pt = []
    for u, v in all_moves:
        all_moves_pt.append((Pt(u // gamemap.rows, u % gamemap.rows),
                             Pt(v // gamemap.rows, v % gamemap.rows)))

    return dp[start_v][turns_limit], all_moves_pt
