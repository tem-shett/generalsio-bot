from base.client.map import Map
from round1.round1 import get_first_50_moves
from gather_army import gather_army
from expand import expand
from cells_classification import *
from base.client.constants import *
from classes import Pt
from heapq import *

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

    def update_enemy(self, gamemap: Map):
        self.turn = gamemap.turn
        if not self.enemy_territory:
            self.enemy_territory = [[0 for x in range(gamemap.cols)] for y in range(gamemap.rows)]
            self.rows = gamemap.rows
            self.cols = gamemap.cols
            my_general = gamemap.generals[gamemap.player_index]
            self.my_general = (my_general.x, my_general.y)
        for y in range(gamemap.rows):
            for x in range(gamemap.cols):
                if (not gamemap.grid[y][x].isGeneral or (x, y) == self.my_general) and (
                x, y) not in self.not_enemy_general and gamemap.grid[y][x].tile not in [
                    TILE_OBSTACLE, TILE_FOG]:
                    self.not_enemy_general.append((x, y))
                if gamemap.grid[y][x].tile == TILE_FOG:
                    continue
                if gamemap.grid[y][x].isGeneral and (x, y) != self.my_general:
                    self.enemy_general = (x, y)
                self.enemy_territory[y][x] = int(is_enemy_cell(gamemap, x, y))

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

    def get_enemy_known_territory(self):
        return sum([sum(self.enemy_territory[i]) for i in range(self.rows)])

    def investigate_territory(self, gamemap: Map):
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

    def get_next_moves(self, gamemap: Map):

        enemy_known_territory = self.get_enemy_known_territory()
        print(enemy_known_territory, self.enemy_general)
        if enemy_known_territory <= 1 or self.turn == 50:
            turns_limit = 50 - gamemap.turn % 50
            moves = expand(gamemap, self.get_enemy_central_cell(), min(turns_limit, 20))
            if moves:
                return moves
        if enemy_known_territory <= 1:
            return self.investigate_territory(gamemap)
        danger_cells = []

        mn_dist_to_general = float('inf')
        mx_army_dist10 = 0

        for y in range(self.rows):
            for x in range(self.cols):
                dist = abs(x - self.my_general[0]) + abs(y - self.my_general[1])
                mn_dist_to_general = min(mn_dist_to_general, dist)
                if self.enemy_territory[y][x] and dist <= 7:
                    mx_army_dist10 = max(mx_army_dist10, gamemap.grid[y][x].army)
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

        if random.randint(1, 2) == 1:
            moves = expand(gamemap, self.enemy_general, 20)
            if moves:
                return moves
        return self.investigate_territory(gamemap)


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


def dot_product(xy1, xy2):
    return xy1[0] * xy2[0] + xy1[1] * xy2[1]


game = Game()


def make_move(bot, gamemap: Map):
    global game
    if gamemap.turn == 1:
        game = Game()
        return
    game.update_enemy(gamemap)
    if game.no_move_until > gamemap.turn:
        return
    if gamemap.turn == 2:
        game.moves_first_50_turns = get_first_50_moves(gamemap)
        return
    if gamemap.turn < 50:
        no_move_until = gamemap.turn
        if len(game.moves_first_50_turns) > 0 and game.moves_first_50_turns[0][2] <= gamemap.turn:
            bot.place_move(game.moves_first_50_turns[0][0], game.moves_first_50_turns[0][1])
            game.moves_first_50_turns.pop(0)
            no_move_until += 1
            while len(game.moves_first_50_turns) > 0 and game.moves_first_50_turns[0][2] == 0:
                bot.place_move(game.moves_first_50_turns[0][0], game.moves_first_50_turns[0][1])
                game.moves_first_50_turns.pop(0)
                no_move_until += 1
        return

    while game.moves:
        x1, y1 = game.moves[0][0].x, game.moves[0][0].y
        if not is_my_cell(gamemap, x1, y1) or gamemap.grid[y1][x1].army <= 1:
            game.moves.pop(0)
        else:
            break

    if not game.moves:
        game.moves = game.get_next_moves(gamemap)
    if game.moves:
        bot.place_move(game.moves[0][0], game.moves[0][1])
        game.moves.pop(0)

    # if gamemap.turn == 50:

    # tl = random.choice(list(gamemap.tiles[gamemap.player_index]))
    # print(tl.x, tl.y)

    # moves = gather_army(gamemap, (tl.x, tl.y), 50)
    # moves = expand(gamemap, game.get_enemy_central_cell(), 50)
    # print(moves)
    # for el in moves:
    #     bot.place_move(el[0], el[1])
    #
    # if gamemap.turn > 100:
    #     tl = random.choice(list(gamemap.tiles[gamemap.player_index]))
    #     print(tl.x, tl.y)
    #
    #     moves = gather_army(gamemap, (tl.x, tl.y), 50)
    #     for el in moves:
    #         bot.place_move(el[0], el[1])
