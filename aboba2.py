import random

from base.client.constants import *
from base.client.map import Map


def is_valid_first_50(gamemap: Map, x, y):
    return gamemap.isValidPosition(x, y) and gamemap.grid[y][x].tile not in [TILE_MOUNTAIN,
                                                                             TILE_OBSTACLE] and not \
        gamemap.grid[y][x].isCity and not gamemap.grid[y][x].isGeneral


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
        get_pathes(general.x, general.y, -1, -1, gamemap, used, [], cnt_turns + 1, 15, 6)
        cnt_turns += 1

    for i in range(len(all_pathes)):
        random.shuffle(all_pathes[i])

    print("all_pathes len", sum([len(x) for x in all_pathes]), cnt_turns)


moves_first_50_turns = []


class Pt:
    def __init__(self, x, y):
        self.x = x
        self.y = y


best_first50_moves = (0, 0, [])

def brute(used, general_army, turn_num, cells_captured, prev_pathlen, all_moves):
    global best_first50_moves
    best_first50_moves = max(best_first50_moves, (cells_captured, 0, all_moves.copy()))
    left_limit = prev_pathlen // 2 - 1
    if turn_num >= 47:
        left_limit = min(left_limit, 1)
    if turn_num >= 40:
        left_limit = min(left_limit, 3)
    left_limit = max(left_limit, 1)
    for pathlen in range(left_limit, prev_pathlen):
        if turn_num + pathlen > 50:
            break

        best_pathes_now = dict()

        #random.shuffle(all_pathes[pathlen])

        for path in all_pathes[pathlen]:
            army_need = 1
            for xy in path:
                if used[xy[1]][xy[0]] == 0:
                    army_need += 1
            #direct = str(path[1])
            direct = 1 if used[path[1][1]][path[1][0]] else 0
            if direct not in best_pathes_now:
                best_pathes_now[direct] = []
            if not best_pathes_now[direct] or best_pathes_now[direct][0][0] < army_need:
                best_pathes_now[direct] = [(army_need, path)]
            elif best_pathes_now[direct][0][0] == army_need:
                best_pathes_now[direct].append((army_need, path))

        for key in best_pathes_now.keys():
            best_pathes_now[key] = best_pathes_now[key][:min(len(best_pathes_now[key]), 5)]

        for direct in best_pathes_now.keys():
            for army_need, path in best_pathes_now[direct]:
                for xy in path:
                    used[xy[1]][xy[0]] += 1
                cells_captured += army_need - 1
                for i in range(len(path) - 1):
                    all_moves.append((path[i], path[i + 1], army_need if i == 0 else 0))

                turn2 = get_turn_1(general_army, turn_num, army_need)
                turn3 = turn2 + len(path) - 1
                if turn3 <= 50:
                    turn_num_new = turn3 + 1
                    general_army_new = 1 + get_army_delta(turn2 + 1, turn3 + 1)
                    brute(used, general_army_new, turn_num_new, cells_captured, pathlen, all_moves)

                for i in range(len(path) - 1):
                    all_moves.pop()
                cells_captured -= army_need - 1
                for xy in path:
                    used[xy[1]][xy[0]] -= 1


def get_first_50_moves(gamemap: Map):
    global moves_first_50_turns, best_first50_moves
    best_first50_moves = (0, 0, [])
    init_valueable_pathes(gamemap)
    general = gamemap.generals[gamemap.player_index]
    used = [[0 for x in range(gamemap.cols)] for y in range(gamemap.rows)]
    used[general.y][general.x] = 1

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
