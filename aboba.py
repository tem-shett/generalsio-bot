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
               turns_partly=True):
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

    get_pathes(general.x, general.y, -1, -1, gamemap, used, [], 5 + 1, 5)

    cnt_turns = 0
    while sum([len(x) for x in all_pathes]) < 500:
        get_pathes(general.x, general.y, -1, -1, gamemap, used, [], cnt_turns + 1, 15)
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

dp = []


def calc_dp(turn_num, general_army):
    cnt_calc = 0
    for cells_captured in range(25, 0, -1):
        random.shuffle(dp[turn_num][general_army][cells_captured])
        for used, prev_pathlen, all_moves in dp[turn_num][general_army][cells_captured]:
            cnt_calc += 1
            if cnt_calc > 500:
                break
            for pathlen in range(1, min(prev_pathlen, 52 - turn_num)):
                for path in all_pathes[pathlen]:
                    new_used = used.copy()
                    army_need = 1
                    for x, y in path:
                        if (x * 1000 + y) not in used:
                            new_used.add(x * 1000 + y)
                            army_need += 1
                    turn2 = get_turn_1(general_army, turn_num, army_need)
                    turn3 = turn2 + len(path) - 1
                    if turn3 <= 50:
                        new_cells_captured = cells_captured + army_need - 1
                        all_moves_new = all_moves.copy()
                        for i in range(len(path) - 1):
                            all_moves_new.append((path[i], path[i + 1], army_need if i == 0 else 0))
                        turn_num_new = turn3 + 1
                        general_army_new = 1 + get_army_delta(turn2 + 1, turn3 + 1)
                        dp[turn_num_new][general_army_new][new_cells_captured].append(
                            (new_used, pathlen, all_moves_new))


# def brute(used, general_army, turn_num, cells_captured, prev_pathlen, all_moves):
#     global best_first50_moves
#     best_first50_moves = max(best_first50_moves, (cells_captured, 0, all_moves.copy()))
#     for pathlen in range(prev_pathlen // 2, prev_pathlen):
#
#         best_pathes_now = []
#
#         for path in all_pathes[pathlen]:
#             army_need = 1
#             for xy in path:
#                 if used[xy[1]][xy[0]] == 0:
#                     army_need += 1
#             if not best_pathes_now or best_pathes_now[0][0] < army_need:
#                 best_pathes_now = [(army_need, path)]
#             elif best_pathes_now[0][0] == army_need:
#                 best_pathes_now.append((army_need, path))
#
#         best_pathes_now = best_pathes_now[:min(len(best_pathes_now), 10)]
#
#         for army_need, path in best_pathes_now:
#             for xy in path:
#                 used[xy[1]][xy[0]] += 1
#             cells_captured += army_need - 1
#             for i in range(len(path) - 1):
#                 all_moves.append((path[i], path[i + 1], army_need if i == 0 else 0))
#
#             turn2 = get_turn_1(general_army, turn_num, army_need)
#             turn3 = turn2 + len(path) - 1
#             if turn3 <= 50:
#                 turn_num_new = turn3 + 1
#                 general_army_new = 1 + get_army_delta(turn2 + 1, turn3 + 1)
#                 brute(used, general_army_new, turn_num_new, cells_captured, pathlen, all_moves)
#
#             for i in range(len(path) - 1):
#                 all_moves.pop()
#             cells_captured -= army_need - 1
#             for xy in path:
#                 used[xy[1]][xy[0]] -= 1


# def get_first_50_moves(gamemap: Map):
#     global moves_first_50_turns
#     init_valueable_pathes(gamemap)
#     general = gamemap.generals[gamemap.player_index]
#     used = [[0 for x in range(gamemap.cols)] for y in range(gamemap.rows)]
#     used[general.x][general.y] = 1
#
#     brute(used, 1, 1, 1, 19, [])
#
#     with open('first50_res.txt', 'a') as f:
#         f.write(str(best_first50_moves) + '\n')
#     print(best_first50_moves)
#
#     moves_first_50_turns = [(Pt(pt1[0], pt1[1]), Pt(pt2[0], pt2[1]), army) for pt1, pt2, army in
#                             best_first50_moves[2]]

def get_first_50_moves(gamemap: Map):
    global moves_first_50_turns, best_first50_moves, dp
    dp = [[[[] for cells_captured in range(26)] for general_army in range(20)] for turn_num in
          range(52)]
    init_valueable_pathes(gamemap)
    general = gamemap.generals[gamemap.player_index]
    used = {general.x * 1000 + general.y}
    dp[1][1][1].append((used, 19, []))

    best_first50_moves = (0, 0, [])

    for turn_num in range(1, 50):
        for general_army in range(1, 18):
            calc_dp(turn_num, general_army)
            for cells_captured in range(best_first50_moves[0] + 1, 26):
                if dp[turn_num][general_army][cells_captured]:
                    best_first50_moves = (
                        cells_captured, 0, dp[turn_num][general_army][cells_captured][0][2])
            dp[turn_num][general_army].clear()

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
