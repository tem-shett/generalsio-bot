import random

from base.client.constants import *
from base.client.map import Map
from datetime import datetime
import itertools


def is_valid_first_50(gamemap: Map, x, y):
    return gamemap.isValidPosition(x, y) and gamemap.grid[y][x].tile not in [TILE_MOUNTAIN,
                                                                             TILE_OBSTACLE] and not \
        gamemap.grid[y][x].isCity and not gamemap.grid[y][x].isGeneral


def get_turn_1(cur_army, turn, need_army):
    if need_army <= cur_army:
        return turn
    return (need_army - cur_army) * 2 + turn - (turn % 2)


def get_army_delta(turn1, turn2):
    turn11 = turn1 + turn1 % 2
    turn22 = turn2 - turn2 % 2
    if turn11 > turn22:
        return 0
    return (turn22 - turn11) // 2 + 1


all_pathes = [[] for _ in range(20)]


def get_pathes(x, y, prev_x, prev_y, gamemap: Map, used, path, turns_left, moves_left,
               turns_partly_from=0):
    global all_pathes
    used[y][x] = 1
    path.append((x, y))
    if turns_partly_from <= len(path) - 1 or turns_left == 0:
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
                get_pathes(xx, yy, x, y, gamemap, used, path, turns_left - turn_used,
                           moves_left - 1)
    used[y][x] = 0
    path.pop()


def init_valueable_pathes(gamemap: Map):
    global all_pathes
    for i in range(len(all_pathes)):
        all_pathes[i].clear()
    general = gamemap.generals[gamemap.player_index]
    used = [[0 for x in range(gamemap.cols)] for y in range(gamemap.rows)]

    get_pathes(general.x, general.y, -1, -1, gamemap, used, [], 6 + 1, 5)

    cnt_turns = 0
    while sum([len(x) for x in all_pathes]) < 600:
        get_pathes(general.x, general.y, -1, -1, gamemap, used, [], cnt_turns + 1, 16, 6)
        cnt_turns += 1

    all_pathes[16] = all_pathes[16][:min(2, len(all_pathes[16]))]
    for i in range(len(all_pathes)):
        random.shuffle(all_pathes[i])

    print("all_pathes len", sum([len(x) for x in all_pathes]), cnt_turns)


defining_cells = [[] for _ in range(20)]


def get_defining_cells_fixed_len(lenpath):
    candidates = []
    for num in range(1, lenpath + 1):
        for path in all_pathes[lenpath]:
            if len(candidates) >= 12:
                break
            if (path[num], num) not in candidates:
                candidates.append((path[num], num))
    print(lenpath, len(all_pathes[lenpath]), candidates)
    for comb_len in [4, 3, 5, 2, 1]:
        best_comb = (0, ())
        for comb in itertools.combinations(candidates, comb_len):
            cnt = [0] * comb_len
            all_cover = True
            for path in all_pathes[lenpath]:
                path_cover = False
                for i in range(len(comb)):
                    if comb[i][0] == path[comb[i][1]]:
                        path_cover = True
                        cnt[i] += 1
                        break
                if not path_cover:
                    all_cover = False
                    break
            if all_cover and min(cnt) >= 1:
                best_comb = max(best_comb, (min(cnt), comb))
        if best_comb[0] > 0:
            return best_comb[1]
    return []


def init_defining_cells():
    global defining_cells
    defining_cells = [[] for _ in range(20)]
    for lenpath in range(1, len(all_pathes)):
        defining_cells[lenpath] = get_defining_cells_fixed_len(lenpath)
        print(defining_cells[lenpath])


moves_first_50_turns = []


class Pt:
    def __init__(self, x, y):
        self.x = x
        self.y = y


brute_start_time = datetime.now()
best_first50_moves = (0, 0, [])

cnt_time_queries = 0
time_ok = True


def check_time():
    global cnt_time_queries, time_ok
    if not time_ok:
        return False
    if cnt_time_queries == 10000:
        cnt_time_queries = 0
        if (datetime.now() - brute_start_time).total_seconds() > 7:
            time_ok = False
    cnt_time_queries += 1
    return time_ok


def calc_cells_nearby(used, all_moves):
    if not all_moves:
        return 0
    cells = [x[1] for x in all_moves]
    cells.append(all_moves[0][0])
    cnt_cells_nearby = 0
    for_rollback = []
    for x, y in cells:
        for dx, dy in DIRECTIONS:
            x2, y2 = x + dx, y + dy
            if 0 <= x2 < len(used[0]) and 0 <= y2 < len(used) and used[y2][x2] < 100:
                cnt_cells_nearby += 1
                used[y2][x2] += 100
                for_rollback.append((x2, y2))
    for x, y in for_rollback:
        used[y][x] -= 100
    return cnt_cells_nearby


def brute(used, general_army, turn_num, cells_captured, prev_pathlen, all_moves):
    global best_first50_moves
    if best_first50_moves[0] <= cells_captured:
        best_first50_moves = max(best_first50_moves, (
            cells_captured, calc_cells_nearby(used, all_moves), all_moves.copy()))
        # best_first50_moves = max(best_first50_moves, (
        #     cells_captured, 0, all_moves.copy()))
    if not check_time():
        return
    left_limit = prev_pathlen // 2 - 1
    if turn_num >= 47:
        left_limit = min(left_limit, 1)
    if turn_num >= 40:
        left_limit = min(left_limit, 3)
    left_limit = max(left_limit, 1)
    for pathlen in range(left_limit, prev_pathlen):
        if turn_num + pathlen > 50 or not all_pathes[pathlen]:
            break

        best_pathes_now = [[] for _ in range(len(defining_cells[pathlen]))]

        # random.shuffle(all_pathes[pathlen])

        for path in all_pathes[pathlen]:
            army_need = 1
            for xy in path:
                if used[xy[1]][xy[0]] == 0:
                    army_need += 1
            direct = -1
            for i in range(len(defining_cells[pathlen])):
                x = defining_cells[pathlen][i]
                if path[x[1]] == x[0]:
                    direct = i
                    break
            # if direct == -1:
            #     print(pathlen, 'aboba')
            #     exit(1)
            # direct = 1 if used[path[1][1]][path[1][0]] else 0
            if not best_pathes_now[direct] or best_pathes_now[direct][0][0] < army_need:
                best_pathes_now[direct] = [(army_need, path)]
            elif best_pathes_now[direct][0][0] == army_need:
                best_pathes_now[direct].append((army_need, path))

        for key in range(len(best_pathes_now)):
            best_pathes_now[key] = best_pathes_now[key][:min(len(best_pathes_now[key]), 2)]

        for direct in range(len(best_pathes_now)):
            for army_need, path in best_pathes_now[direct]:
                for xy in path:
                    used[xy[1]][xy[0]] += 1
                cells_captured += army_need - 1

                turn2 = get_turn_1(general_army, turn_num, army_need)

                for i in range(len(path) - 1):
                    all_moves.append((path[i], path[i + 1], turn2 if i == 0 else 0))

                turn3 = turn2 + len(path) - 1
                if turn3 <= 50:
                    turn_num_new = turn3
                    general_army_new = 1 + get_army_delta(turn2 + 1, turn3)
                    brute(used, general_army_new, turn_num_new, cells_captured, pathlen, all_moves)

                for i in range(len(path) - 1):
                    all_moves.pop()
                cells_captured -= army_need - 1
                for xy in path:
                    used[xy[1]][xy[0]] -= 1


def get_first_50_moves(gamemap: Map):
    global moves_first_50_turns, best_first50_moves, brute_start_time, cnt_time_queries, time_ok
    best_first50_moves = (0, 0, [])
    init_valueable_pathes(gamemap)
    init_defining_cells()
    general = gamemap.generals[gamemap.player_index]
    used = [[0 if is_valid_first_50(gamemap, x, y) else 100 for x in range(gamemap.cols)] for y in
            range(gamemap.rows)]
    used[general.y][general.x] = 1

    brute_start_time = datetime.now()
    cnt_time_queries = 0
    time_ok = True
    brute(used, 1, 1, 1, 18, [])

    with open('first50_res.txt', 'a') as f:
        f.write(str(best_first50_moves) + '\n')
    print(best_first50_moves)

    moves_first_50_turns = [(Pt(pt1[0], pt1[1]), Pt(pt2[0], pt2[1]), army) for pt1, pt2, army in
                            best_first50_moves[2]]


no_move_until = 0


def make_move(bot, gamemap: Map):
    global moves_first_50_turns, no_move_until
    if gamemap.turn == 1:
        return
    if gamemap.turn == 2:
        moves_first_50_turns = []
        no_move_until = 0
        get_first_50_moves(gamemap)
        # bot.surrender()
        return
    if gamemap.turn <= 50:
        if no_move_until > gamemap.turn:
            return
        no_move_until = gamemap.turn
        if len(moves_first_50_turns) > 0 and moves_first_50_turns[0][2] <= gamemap.turn:
            bot.place_move(moves_first_50_turns[0][0], moves_first_50_turns[0][1])
            moves_first_50_turns.pop(0)
            no_move_until += 1
            while len(moves_first_50_turns) > 0 and moves_first_50_turns[0][2] == 0:
                bot.place_move(moves_first_50_turns[0][0], moves_first_50_turns[0][1])
                moves_first_50_turns.pop(0)
                no_move_until += 1
        return
    bot.surrender()
