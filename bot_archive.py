import random

from base.client.constants import *
from base.client.map import Map, _shuffle


def dist(pt1, pt2):
    return abs(pt1[0] - pt2[0]) + abs(pt1[1] - pt2[1])


def is_valid_first_50(gamemap: Map, x, y):
    return gamemap.isValidPosition(x, y) and gamemap.grid[y][x].tile not in [TILE_MOUNTAIN,
                                                                             TILE_OBSTACLE] and not \
        gamemap.grid[y][x].isCity and not gamemap.grid[y][x].isGeneral


def clc_dif(dist1, dist2):
    return (dist1[0] - dist2[0]) ** 2 + (dist1[1] - dist2[1]) ** 2


# def find_path(x, y, main_direction: (int, int), gamemap: Map, cur_army_grid, path, turns_left):
#     path.append((x, y))
#     turns_left -= 1
#     if len(path) >= 3 and path[-1] == path[-3]:
#         path.pop()
#         return 0
#     new_cell = int(cur_army_grid[y][x] == 0)
#     cur_army_grid[y][x] += 1
#     if turns_left == -1:
#         return new_cell
#     xx, yy = x + main_direction[0], y + main_direction[1]
#     if is_valid_first_50(gamemap, xx, yy) and cur_army_grid[yy][xx] == 0:
#         return find_path(xx, yy, main_direction, gamemap, cur_army_grid, path,
#                          turns_left) + new_cell
#     for direction in _shuffle(DIRECTIONS):
#         if clc_dif(direction, main_direction) == 2:
#             xx, yy = x + direction[0], y + direction[1]
#             if is_valid_first_50(gamemap, xx, yy) and cur_army_grid[yy][xx] == 0:
#                 return find_path(xx, yy, main_direction, gamemap, cur_army_grid, path,
#                                  turns_left) + new_cell
#     xx, yy = x + main_direction[0], y + main_direction[1]
#     if is_valid_first_50(gamemap, xx, yy):
#         return find_path(xx, yy, main_direction, gamemap, cur_army_grid, path,
#                          turns_left) + new_cell
#     for direction in _shuffle(DIRECTIONS):
#         if clc_dif(direction, main_direction) == 2:
#             xx, yy = x + direction[0], y + direction[1]
#             if is_valid_first_50(gamemap, xx, yy):
#                 return find_path(xx, yy, main_direction, gamemap, cur_army_grid, path,
#                                  turns_left) + new_cell
#     return new_cell


def get_rand_element(choice_arr):
    sm = sum([x[1] for x in choice_arr])
    rnd = random.randint(0, sm - 1)
    for x in choice_arr:
        if rnd < x[1]:
            return x[0]
        rnd -= x[1]
    exit(1)


# def find_path(x, y, prev_x, prev_y, gamemap: Map, cur_army_grid, path, turns_left):
#     path.append((x, y))
#     turns_left -= 1
#     new_cell = int(cur_army_grid[y][x] == 0)
#     cur_army_grid[y][x] += 1
#     if turns_left == -1:
#         return new_cell
#     next_choice = []
#     for direction in DIRECTIONS:
#         xx, yy = x + direction[0], y + direction[1]
#         if is_valid_first_50(gamemap, xx, yy) and (xx != prev_x or yy != prev_y):
#             val = 250 if (x - prev_x, y - prev_y) == direction else 90
#             if cur_army_grid[yy][xx] != 0:
#                 val //= 8
#             next_choice.append(((xx, yy), val))
#     if next_choice:
#         xx, yy = get_rand_element(next_choice)
#         return find_path(xx, yy, x, y, gamemap, cur_army_grid, path, turns_left) + new_cell
#     return new_cell


def find_path(x, y, prev_x, prev_y, gamemap: Map, cur_army_grid, path, turns_left, new_cells_left):
    path.append((x, y))
    turns_left -= 1
    new_cell = int(cur_army_grid[y][x] == 0)
    new_cells_left -= new_cell
    cur_army_grid[y][x] += 1
    if turns_left == -1 or new_cells_left == 0:
        return new_cell
    next_choice = []
    for direction in DIRECTIONS:
        xx, yy = x + direction[0], y + direction[1]
        if is_valid_first_50(gamemap, xx, yy) and (xx != prev_x or yy != prev_y):
            val = 300 if (x - prev_x, y - prev_y) == direction else 90
            if cur_army_grid[yy][xx] != 0:
                val = 15
            next_choice.append(((xx, yy), val))
    if next_choice:
        xx, yy = get_rand_element(next_choice)
        return find_path(xx, yy, x, y, gamemap, cur_army_grid, path, turns_left,
                         new_cells_left) + new_cell
    return new_cell


def get_turn_1(cur_army, turn, need_army):
    if need_army <= cur_army:
        return turn
    return (need_army - cur_army) * 2 + turn - (turn % 2)


def get_army_delta(turn1, turn2):
    turn11 = turn1 - turn1 % 2 + 2
    turn22 = turn2 - turn2 % 2
    if turn11 > turn22:
        return 0
    return (turn22 - turn11) // 2 + 1


turns_limit_arr = []


def gen_seqs(lrs, ind, left, arr):
    global turns_limit_arr
    if len(arr) >= 2 and arr[-2] * 2 < arr[-1]:
        return
    if ind >= len(lrs):
        if left <= 1:
            turns_limit_arr.append(arr.copy())
        return
    for i in range(max(lrs[ind][0], arr[-1] if arr else 0), min(lrs[ind][1], left) + 1):
        arr.append(i)
        gen_seqs(lrs, ind + 1, left - i, arr)
        arr.pop()


def init_turns_limit_arr():
    global turns_limit_arr
    turns_limit_arr = []
    lrs = [(2, 2), (3, 4), (5, 8), (7, 16)]
    gen_seqs(lrs, 0, 25, [])
    print(len(turns_limit_arr))
    lrs = [(2, 2), (3, 4), (4, 8), (4, 12), (6, 14)]
    gen_seqs(lrs, 0, 25, [])
    print(len(turns_limit_arr))
    lrs = [(1, 1), (2, 2), (3, 4), (4, 10), (4, 15)]
    gen_seqs(lrs, 0, 25, [])
    print(len(turns_limit_arr))


all_pathes = [[] for _ in range(20)]

def get_pathes(x, y, prev_x, prev_y, gamemap: Map, used, path, turns_left, moves_left, turns_partly=True):
    global all_pathes
    used[y][x] = 1
    path.append((x, y))
    if turns_partly or turns_left == 0:
        all_pathes[len(path) - 1].append(path.copy())
    if moves_left == 0:
        used[y][x] = 0
        path.pop()
        return
    for direction in DIRECTIONS:
        xx, yy = x + direction[0], y + direction[1]
        if is_valid_first_50(gamemap, xx, yy) and not used[yy][xx]:
            turn_used = 1 - int(direction[0] == x - prev_x and direction[1] == y - prev_y)
            if turns_left - turn_used >= 0:
                get_pathes(xx, yy, x, y, gamemap, used, path, turns_left - turn_used, moves_left - 1)
    used[y][x] = 0
    path.pop()


def init_valueable_pathes(gamemap: Map):
    global all_pathes
    all_pathes.clear()
    general = gamemap.generals[gamemap.player_index]
    used = [[0 for x in range(gamemap.cols)] for y in range(gamemap.rows)]

    get_pathes(general.x, general.y, -1, -1, gamemap, used, [], 5 + 1, 5)

    cnt_turns = 0
    while sum([len(x) for x in all_pathes]) < 1000:
        get_pathes(general.x, general.y, -1, -1, gamemap, used, [], cnt_turns + 1, 15)
        cnt_turns += 1

    print("all_pathes len", sum([len(x) for x in all_pathes]), cnt_turns)


def get_first_50_moves(gamemap: Map):
    best_first50_moves = (0, 0, [])

    def brute(used, general_army, turn_num, cells_captured, prev_pathlen, all_moves):
        global best_first50_moves
        best_first50_moves = max(best_first50_moves, (cells_captured, 0, all_moves.copy()))
        for pathlen in range(1, prev_pathlen + 1):
            for path in all_pathes[pathlen]:
                army_need = 1
                for xy in path:
                    if used[xy[1]][xy[0]] == 0:
                        army_need += 1
                    used[xy[1]][xy[0]] += 1
                cells_captured += army_need - 1
                for i in range(len(path) - 1):
                    all_moves.append((path[i], path[i + 1], army_need if i == 0 else 0))

                turn2 = get_turn_1(general_army, turn_num, army_need)
                turn3 = turn2 + len(path) - 1
                if turn3 <= 50:
                    turn_num_new = turn3 + 1
                    general_army_new = 1 + get_army_delta(turn2 + 1, turn3 + 1)
                    brute(used, general_army_new, turn_num_new, cells_captured, pathlen)

                for i in range(len(path) - 1):
                    all_moves.pop()
                cells_captured -= army_need - 1
                for xy in path:
                    used[xy[1]][xy[0]] -= 1





def iteration(gamemap: Map):
    general = gamemap.generals[gamemap.player_index]
    general = (general.x, general.y)
    center = (gamemap.rows // 2, gamemap.cols // 2)
    cur_army_grid = [[0 for x in range(gamemap.cols)] for y in range(gamemap.rows)]
    cur_army_grid[general[1]][general[0]] = 1
    general_army = 1
    turn_num = 1
    all_moves = []

    turns_limit = random.choice(turns_limit_arr).copy()

    while turns_limit:
        # valid_directions = [direction for direction in DIRECTIONS if is_valid_first_50(gamemap, general[0] + direction[0], general[1] + direction[1])]
        # if not valid_directions:
        #    valid_directions = DIRECTIONS
        main_direction = random.choice(DIRECTIONS)
        path = []
        turns_lim = turns_limit.pop()
        army_need = find_path(general[0], general[1], -1, -1, gamemap, cur_army_grid, path,
                              turns_lim + turns_lim // 2, turns_lim) + 1
        if len(all_moves) == 0 and len(path) < 7:
            break
        while len(path) > 1:
            turn2 = get_turn_1(general_army, turn_num, army_need)
            turn3 = turn2 + len(path) - 1
            if turn3 <= 50:
                for i in range(len(path) - 1):
                    all_moves.append((path[i], path[i + 1], army_need if i == 0 else 0))
                turn_num = turn3 + 1
                general_army = 1 + get_army_delta(turn2 + 1, turn3 + 1)
                break
            else:
                cur_army_grid[path[-1][1]][path[-1][0]] -= 1
                if cur_army_grid[path[-1][1]][path[-1][0]] == 0:
                    army_need -= 1
                path.pop()
        if len(path) <= 1:
            break
    area, area_nearby = 0, 0
    for j in range(len(cur_army_grid)):
        for i in range(len(cur_army_grid[0])):
            if cur_army_grid[j][i] > 0:
                area += 1
                for direction in DIRECTIONS:
                    ii, jj = i + direction[0], j + direction[1]
                    if is_valid_first_50(gamemap, ii, jj):
                        if cur_army_grid[jj][ii] == 0:
                            area_nearby += 1
                            cur_army_grid[jj][ii] = -1
    return area, area_nearby, all_moves


moves_first_50_turns = []


class Pt:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def first_50_moves(gamemap: Map):
    global moves_first_50_turns

    best = (0, 0, [])
    for _ in range(2 * 10 ** 5):
        best = max(best, iteration(gamemap))
    print(best)
    with open('first50_res.txt', 'a') as f:
        f.write(str(best) + '\n')
    moves_first_50_turns = [(Pt(pt1[0], pt1[1]), Pt(pt2[0], pt2[1]), army) for pt1, pt2, army in
                            best[2]]


no_move_until = 0




def make_move(bot, gamemap: Map):
    global moves_first_50_turns, no_move_until
    if gamemap.turn == 1:
        init_turns_limit_arr()
        return
    if gamemap.turn == 2:
        init_valueable_pathes(gamemap)
        print(len(turns_limit_arr))
        moves_first_50_turns = []
        no_move_until = 0
        first_50_moves(gamemap)
        # bot.surrender()
        return
    if gamemap.turn <= 50:
        if no_move_until > gamemap.turn:
            return
        no_move_until = gamemap.turn
        if len(moves_first_50_turns) > 0 and moves_first_50_turns[0][2] <= gamemap.generals[
            gamemap.player_index].army:
            bot.place_move(moves_first_50_turns[0][0], moves_first_50_turns[0][1])
            moves_first_50_turns.pop(0)
            no_move_until += 1
            while len(moves_first_50_turns) > 0 and moves_first_50_turns[0][2] == 0:
                bot.place_move(moves_first_50_turns[0][0], moves_first_50_turns[0][1])
                moves_first_50_turns.pop(0)
                no_move_until += 1
        return
    bot.surrender()
