from cells_classification import *
from classes import Pt

def expand(gamemap: Map, target_cell, turns_lim):
    print(target_cell)
    g = [[] for v in range(gamemap.rows * gamemap.cols)]
    left_part = []
    for y in range(gamemap.rows):
        for x in range(gamemap.cols):
            enemy = is_enemy_cell(gamemap, x, y)
            empty = is_empty_cell(gamemap, x, y)
            if not enemy and not empty:
                continue
            for dx, dy in DIRECTIONS:
                x2 = x + dx
                y2 = y + dy
                if not is_my_cell(gamemap, x2, y2):
                    continue
                if (enemy and gamemap.grid[y][x].army < gamemap.grid[y2][x2].army) or (empty and gamemap.grid[y2][x2].army > 1):
                    g[x * gamemap.rows + y].append(x2 * gamemap.rows + y2)
                    if not left_part or left_part[-1][1] != x * gamemap.rows + y:
                        left_part.append((abs(x - target_cell[0]) + abs(y - target_cell[1]),
                                          x * gamemap.rows + y))

    match = [-1] * (gamemap.rows * gamemap.cols)
    used = [0] * (gamemap.rows * gamemap.cols)
    def dfs(v, c):
        if used[v] == c:
            return 0
        used[v] = c
        for u in g[v]:
            if match[u] == -1:
                match[u] = v
                return 1
        for u in g[v]:
            if dfs(match[u], c):
                match[u] = v
                return 1
        return 0

    left_part.sort()
    match_sz = 0
    next_c = 1
    for dist, v in left_part:
        match_sz += dfs(v, next_c)
        next_c += 1
        if match_sz >= turns_lim:
            break

    r_match = [-1] * (gamemap.rows * gamemap.cols)

    for v in range(gamemap.rows * gamemap.cols):
        if match[v] != -1:
            r_match[match[v]] = v

    moves = []
    for dist, v in left_part:
        if r_match[v] != -1:
            moves.append((divmod(r_match[v], gamemap.rows), divmod(v, gamemap.rows)))

    return [(Pt(c1[0], c1[1]), Pt(c2[0], c2[1])) for c1, c2 in moves]