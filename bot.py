from base.client.map import Map
from round1.round1 import get_first_50_moves
from cells_classification import *
from game_class import Game

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

    instant_win_moves = game.instant_win(gamemap)
    if instant_win_moves[0][0][0] != -1:
        game.moves = instant_win_moves
        game.moves_into_pt()

    while game.moves:
        x1, y1 = game.moves[0][0].x, game.moves[0][0].y
        if not is_my_cell(gamemap, x1, y1) or gamemap.grid[y1][x1].army <= 1:
            game.moves.pop(0)
        else:
            break

    if not game.moves:
        game.moves = game.get_next_moves(gamemap)
        game.moves_into_pt()
    if game.moves:
        bot.place_move(game.moves[0][0], game.moves[0][1])
        game.moves.pop(0)
