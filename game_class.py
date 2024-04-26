from gather_army import gather_army
from point_funcs import dot_product
from expand import expand
from cells_classification import *
from base.client.constants import *
from classes import Pt
from bfs import bfs_simple_cells
import random


class Game:
    def __init__(self):
        self.no_move_until = 0
        self.rows = 0
        self.cols = 0
        self.moves_first_50_turns = []
        self.moves = []
        self.turn = 0
        self.enemy_general = (-1, -1)
        self.not_enemy_general = []
        self.my_general = (-1, -1)
        self.enemy_territory = []
        self.prev_fog = []
        self.empty_first = []
        self.my_army = 0
        self.my_territory = 0

        self.cnt_expands = 0
        self.enemy_know_my_general = False

        self.investigation_cell = (-1, -1)


    def moves_into_pt(self):
        if not self.moves:
            return
        if type(self.moves[0][0]) == tuple:
            self.moves = [(Pt(v1[0], v1[1]), Pt(v2[0], v2[1])) for v1, v2 in self.moves]

    def print_not_generals(self):
        s = [['_' for x in range(self.cols)] for y in range(self.rows)]
        for x, y in self.not_enemy_general:
            s[y][x] = '#'
        print('\n'.join(map(lambda x: ''.join(x), s)))

    def print_empty_first(self, gamemap: Map):
        s = [['_' if self.empty_first[y][x] == 0 else '#' for x in range(self.cols)] for y in range(self.rows)]
        for y in range(self.rows):
            for x in range(self.cols):
                if is_enemy_cell(gamemap, x, y) and s[y][x] == '_':
                    s[y][x] = '&'
        print('\n'.join(map(lambda x: ''.join(x), s)))

    def update_enemy(self, gamemap: Map):
        # self.print_not_generals()
        # self.print_empty_first(gamemap)
        self.turn = gamemap.turn
        if not self.enemy_territory:
            self.enemy_territory = [[0 for x in range(gamemap.cols)] for y in range(gamemap.rows)]
            self.prev_fog = [[1 for x in range(gamemap.cols)] for y in range(gamemap.rows)]
            self.empty_first = [[0 for x in range(gamemap.cols)] for y in range(gamemap.rows)]
            self.rows = gamemap.rows
            self.cols = gamemap.cols
            my_general = gamemap.generals[gamemap.player_index]
            self.my_general = (my_general.x, my_general.y)
        self.my_army = 0
        self.my_territory = 0
        for y in range(gamemap.rows):
            for x in range(gamemap.cols):
                if self.prev_fog[y][x] == 1 and gamemap.grid[y][x].tile == TILE_EMPTY:
                    self.empty_first[y][x] = 1
                if gamemap.grid[y][x].tile != TILE_FOG:
                    self.prev_fog[y][x] = 0
                if (not gamemap.grid[y][x].isGeneral or (x, y) == self.my_general) and (
                        x, y) not in self.not_enemy_general and gamemap.grid[y][x].tile not in [
                    TILE_OBSTACLE, TILE_FOG]:
                    self.not_enemy_general.append((x, y))
                if gamemap.grid[y][x].tile == TILE_FOG:
                    continue
                if gamemap.grid[y][x].isGeneral and (x, y) != self.my_general:
                    self.enemy_general = (x, y)
                if is_my_cell(gamemap, x, y):
                    self.my_army += gamemap.grid[y][x].army
                    self.my_territory += 1
                self.enemy_territory[y][x] = int(is_enemy_cell(gamemap, x, y))

        for dx, dy in EXPANDED_DIRECTIONS:
            x2, y2 = self.my_general[0] + dx, self.my_general[1] + dy
            if is_enemy_cell(gamemap, x2, y2):
                self.enemy_know_my_general = True


    def get_enemy_central_cell(self):
        if self.enemy_general != (-1, -1):
            return self.enemy_general
        smx, smy = 0, 0
        cnt = 0
        for y in range(len(self.enemy_territory)):
            for x in range(len(self.enemy_territory[0])):
                if abs(y - self.my_general[1]) + abs(x - self.my_general[0]) <= 6:
                    continue
                if self.enemy_territory[y][x]:
                    smx += x
                    smy += y
                    cnt += 1
        if cnt == 0:
            return self.cols // 2, self.rows // 2
        return smx // cnt, smy // cnt

    def get_nearest_probable_general(self, gamemap: Map, x, y, empty_first_considered=True):

        def ok_cell(x_, y_):
            if x_ < 0 or x_ >= gamemap.cols or y_ < 0 or y_ >= gamemap.rows:
                return False
            if is_my_cell(gamemap, x, y):
                return True
            return gamemap.grid[y_][x_].tile not in [TILE_OBSTACLE, TILE_MOUNTAIN] and not \
            gamemap.grid[y_][x_].isCity and (not self.empty_first[y_][x_] or not empty_first_considered)

        if not ok_cell(x, y):
            return 10000

        dist = [[10000 for x in range(self.cols)] for y in range(self.rows)]
        dist[y][x] = 0
        q = [(x, y)]
        while q:
            vx, vy = q[0]
            q.pop(0)
            for dx, dy in DIRECTIONS:
                ux, uy = vx + dx, vy + dy
                if ok_cell(ux, uy) and dist[uy][ux] > dist[vy][vx] + 1:
                    dist[uy][ux] = dist[vy][vx] + 1
                    if (ux, uy) not in self.not_enemy_general:
                        return dist[uy][ux]
                    q.append((ux, uy))
        return 10000

    def get_nearest_enemy_cell(self, gamemap: Map, x, y):
        def ok_cell(x_, y_):
            if x_ < 0 or x_ >= gamemap.cols or y_ < 0 or y_ >= gamemap.rows:
                return False
            return gamemap.grid[y_][x_].tile not in [TILE_OBSTACLE, TILE_MOUNTAIN]

        dist = [[10000 for x in range(self.cols)] for y in range(self.rows)]
        dist[y][x] = 0
        q = [(x, y)]
        while q:
            vx, vy = q[0]
            q.pop(0)
            for dx, dy in DIRECTIONS:
                ux, uy = vx + dx, vy + dy
                if ok_cell(ux, uy) and dist[uy][ux] > dist[vy][vx] + 1:
                    dist[uy][ux] = dist[vy][vx] + 1
                    if self.enemy_territory[uy][ux]:
                        return dist[uy][ux]
                    q.append((ux, uy))
        return 10000


    def get_enemy_known_territory(self):
        return sum([sum(self.enemy_territory[i]) for i in range(self.rows)])

    def investigate_territory_early(self, gamemap: Map):
        target_cell = self.get_enemy_central_cell()
        my_cells = []
        for y in range(self.rows):
            for x in range(self.cols):
                if is_my_cell(gamemap, x, y):
                    my_cells.append((x, y))
        my_cells.sort(key=lambda xy: abs(xy[0] - target_cell[0]) + abs(xy[1] - target_cell[1]))
        my_cells = my_cells[:min(len(my_cells), max(7, len(my_cells) // 5))]
        best_for_gather = ((-1, []), (-1, -1))
        for cell in my_cells:
            enemy_known_territory = self.get_enemy_known_territory()
            army_limit = 10 if enemy_known_territory == 0 else 20 if enemy_known_territory <= 5 else 40
            gather_cur = gather_army(gamemap, cell, 20, army_limit)
            if gather_cur[0] > best_for_gather[0][0]:
                best_for_gather = (gather_cur, cell)

        gather_cell = best_for_gather[1]

        best_cells = []
        for y in range(self.rows):
            for x in range(self.cols):
                if is_simple_cell(gamemap, x, y) and (x, y) not in self.not_enemy_general:
                    best_cells.append((x, y))
        best_cells.sort(
            key=lambda xy: dot_product(
                (target_cell[0] - self.my_general[0], target_cell[1] - self.my_general[1]),
                (xy[0] - self.my_general[0], xy[1] - self.my_general[1])),
            reverse=True)
        best_cells = best_cells[:min(len(best_cells), 5)]

        final_cell = random.choice(best_cells)

        return best_for_gather[0][1] + bfs_simple_cells(gamemap, gather_cell, final_cell)


    def init_investigate_territory(self, gamemap: Map):
        my_cells = []
        for y in range(self.rows):
            for x in range(self.cols):
                if is_my_cell(gamemap, x, y):
                    flag = False
                    for dx, dy in EXPANDED_DIRECTIONS:
                        x2, y2 = x + dx, y + dy
                        if is_enemy_cell(gamemap, x2, y2):
                            flag = True
                    if flag:
                        my_cells.append((self.get_nearest_probable_general(gamemap, x, y), (x, y)))
        my_cells.sort()
        gather_cell = random.choice(my_cells[:min(len(my_cells), 3)])[1]
        army_limit = (self.my_army - self.my_territory) // 2
        gather_path = gather_army(gamemap, gather_cell, 25, army_limit)[1]
        self.investigation_cell = gather_cell
        return gather_path

    def investigate_territory_step_by_step(self, gamemap: Map):
        if self.enemy_general != (-1, -1):
            self.investigation_cell = (-1, -1)
            return [(-1, -1)]
        ix, iy = self.investigation_cell
        print("investigation cell:", self.investigation_cell)
        if not is_my_cell(gamemap, ix, iy):
            self.investigation_cell = (-1, -1)
            return [(-1, -1)]
        my_army = gamemap.grid[iy][ix].army - 1
        best = (1000, (-1, -1))
        for dx, dy in DIRECTIONS:
            x, y = ix + dx, iy + dy
            if not is_enemy_cell(gamemap, x, y):
                continue
            if self.enemy_territory[y][x] and gamemap.grid[y][x].army < my_army:
                best = min(best, (self.get_nearest_probable_general(gamemap, x, y), (x, y)))
        if best[0] > 100:
            for dx, dy in DIRECTIONS:
                x, y = ix + dx, iy + dy
                if not is_enemy_cell(gamemap, x, y):
                    continue
                if self.enemy_territory[y][x] and gamemap.grid[y][x].army < my_army:
                    best = min(best, (self.get_nearest_probable_general(gamemap, x, y, False), (x, y)))
            print(gamemap.turn, "empty_first", best)
        if best[0] > 100:
            dist1 = self.get_nearest_enemy_cell(gamemap, ix, iy)
            if my_army / dist1 >= 3:
                for dx, dy in DIRECTIONS:
                    x, y = ix + dx, iy + dy
                    if is_simple_cell(gamemap, x, y) and self.get_nearest_enemy_cell(gamemap, x, y) < dist1:
                        self.investigation_cell = (x, y)
                        return [((ix, iy), (x, y))]
        print(gamemap.turn, best)
        if best[1][0] == -1:
            self.investigation_cell = (-1, -1)
            return [(-1, -1)]
        self.investigation_cell = best[1]
        return [((ix, iy), best[1])]

    def instant_win(self, gamemap: Map):
        if self.enemy_general == (-1, -1):
            return [((-1, -1), (-1, -1))]
        enemy_army = gamemap.grid[self.enemy_general[1]][self.enemy_general[0]].army
        for dx, dy in DIRECTIONS:
            x = self.enemy_general[0] + dx
            y = self.enemy_general[1] + dy
            if is_my_cell(gamemap, x, y) and gamemap.grid[y][x].army > enemy_army:
                return [((x, y), self.enemy_general)]
        return [((-1, -1), (-1, -1))]


    def get_next_moves(self, gamemap: Map):
        instant_win_moves = self.instant_win(gamemap)
        if instant_win_moves[0][0][0] != -1:
            return instant_win_moves
        enemy_known_territory = self.get_enemy_known_territory()
        # print(enemy_known_territory, self.enemy_general)
        if self.turn == 50:
            turns_limit = 50 - gamemap.turn % 50
            moves = expand(gamemap, self.get_enemy_central_cell(), min(turns_limit, 20))
            if moves:
                # self.cnt_expands += len(moves)
                return moves
        if enemy_known_territory == 0:
            return self.investigate_territory_early(gamemap)
        if self.investigation_cell != (-1, -1):
            moves = self.investigate_territory_step_by_step(gamemap)
            if moves[0][0] != -1:
                return moves

        danger_cells = []

        mn_dist_to_general = float('inf')
        mx_army_dist10 = 0

        for y in range(self.rows):
            for x in range(self.cols):
                dist = abs(x - self.my_general[0]) + abs(y - self.my_general[1])
                mn_dist_to_general = min(mn_dist_to_general, dist)
                if self.enemy_territory[y][x] and dist <= 7:
                    mx_army_dist10 = max(mx_army_dist10, gamemap.grid[y][x].army - dist + 2)
                if self.enemy_territory[y][x] and dist <= 5:
                    danger_cells.append((x, y))
        danger_cells.sort(
            key=lambda xy: abs(xy[0] - self.my_general[0]) + abs(xy[1] - self.my_general[1]))

        if danger_cells:
            return gather_army(gamemap, danger_cells[0], 10,
                               gamemap.grid[danger_cells[0][1]][danger_cells[0][0]].army + 1)[1]

        if mn_dist_to_general < 6 and gamemap.grid[self.my_general[1]][
            self.my_general[0]].army < mx_army_dist10 + 5:
            return gather_army(gamemap, self.my_general, 20, mx_army_dist10 + 3)[1]

        if self.enemy_general != (-1, -1):
            if random.randint(1, 3) == 1:
                return expand(gamemap, self.enemy_general, 20)
            else:
                return gather_army(gamemap, self.enemy_general, 40, 10 ** 9)[1]

        if random.randint(1, 2) == 1 and self.cnt_expands < 26 and (not self.enemy_know_my_general or self.cnt_expands < 5):
            moves = expand(gamemap, self.enemy_general, min(30 - self.cnt_expands, 7))
            self.cnt_expands += len(moves)
            if moves:
                return moves
        return self.init_investigate_territory(gamemap)
