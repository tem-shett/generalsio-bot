from base.client.map import Map
from round1.round1 import get_first_50_moves

no_move_until = 0

moves_first_50_turns = []

def make_move(bot, gamemap: Map):
    global moves_first_50_turns, no_move_until
    if gamemap.turn == 1:
        return
    if gamemap.turn == 2:
        moves_first_50_turns = []
        no_move_until = 0
        moves_first_50_turns = get_first_50_moves(gamemap)
        return
    if gamemap.turn < 50:
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
