import copy
import random
import sys
import time
import math
import copy
sys.path.append('src')
from common import board

tic = time.time()

# Heuristica diferença de moedas: OK
#coin_heuristic_value = (max_coins - min_coins) / (max_coins + min_coins)

# Heuristica mobilidade: OK
# if (max_moves + min_moves) != 0 then mobility_heuristic_value = (max_moves - min_moves) / (max_moves + min_moves) else mobility_heuristic_value = 0

# Heuristica cantos capturados: OK
# if (max_corner + min_corner) != 0 then corner_heuristic_value = (max_corner - min_corner) / (max_corner + min_corner) else corner_heuristic_value = 0


def heur_table(state, color):
    """ Heuristic that returns the sum of the values on the table
    :param: state, char
    :return: int

    table
     |100 | -20 | 10 | 5  | 5   | 10 | -20 | 100 |
     |-20 | -50 | -2 | -2 | -2  | -2 | -50 | -20 |
     |10  | -2  | -1 | -1 | -1  | -1 | -2  |  10 |
     |5   | -2  | -1 | -1 | -1  | -1 | -2  |  5  |
     |5   | -2  | -1 | -1 | -1  | -1 | -2  |  5  |
     |10  | -2  | -1 | -1 | -1  | -1 | -2  |  10 |
     |-20 | -50 | -2 | -2 | -2  | -2 | -50 | -20 |
     |100 | -20 | 10 |  5 |  5  | 10 | -20 | 100 |
    """

    actual_color = 0
    if color == 'black':
        actual_color = state.BLACK
    else:
        actual_color = state.WHITE


    table = [[100, -20, 10,  5,  5, 10, -20, 100],
             [-20, -50, -2, -2, -2, -2, -50, -20],
             [10 , -2 , -1, -1, -1, -1, -2 ,  10],
             [5  , -2 , -1, -1, -1, -1, -2 ,   5],
             [5  , -2 , -1, -1, -1, -1, -2 ,   5],
             [10 , -2 , -1, -1, -1, -1, -2 ,  10],
             [-20, -50, -2, -2, -2, -2, -50, -20],
             [100, -20, 10,  5,  5, 10, -20, 100]]

    sum = 0
    for i in range(len(state.tiles)):
        for j in range(len(state.tiles[i])):
            if state.tiles[i][j] == actual_color:
                sum += table[i][j]

    return sum

def heur_corner_count(state, color):
    """ Heuristic that returns the ratio of the number of corners
    :param: state, char
    :return: int
    """
    # It only goes from 0,0 to 7,7
    corners = [(0,0), (0,7), (7,0), (7,7)]
    opp = 0
    mine = 0
    for c in corners:
        x, y = c
        if state.tiles[x][y] == color:
            mine += 1
        elif state.tiles[x][y] == state.opponent(color):
            opp += 1

    if (mine + opp) != 0 :
        c_value = 100*(mine - opp)/(mine + opp)
        return c_value
    else:
        return 0

def heur_win(state, color):
    """ Heuristic that returns a surely win or lose
    :param: state, char
    :return: int
    """
    opp_pieces = state.piece_count[state.opponent(color)]
    my_pieces = state.piece_count[color]
    empty_pieces = state.piece_count[state.EMPTY]
    winning = opp_pieces == 0 or \
        (empty_pieces == 0 and my_pieces > opp_pieces)
    loosing = my_pieces == 0 or \
        (empty_pieces == 0 and opp_pieces > my_pieces)
    if winning:
        return 1
    elif loosing:
        return -1
    else:
        return 0

def heur_mob_count(state, color):
    """ Heuristic that return the ratio of possible moves
    :param: state, char
    :return: int
    """
    opp = state.legal_moves(state.opponent(color))
    mine = state.legal_moves(color)
    opp = len(opp)
    mine = len(mine)

    if (mine + opp) != 0:
        mob_heur_value = 100*(mine - opp) / (mine + opp)
    else:
        mob_heur_value = 0

    return mob_heur_value

def heur_coins_count(state, color):
    """ Heuristic that return the ratio of coins
    :param: state, char
    :return: int
    """
    opp = state.piece_count[state.opponent(color)]
    my_count = state.piece_count[color]

    coin_heur_value = 100*(my_count - opp) / (opp + my_count)

    return coin_heur_value

def general_heur(state, color):
    """ Weights of each heuristic
    :param: state, char
    :return: int
    """
    return 0.025 * heur_coins_count(state,color) + \
           0.3 * heur_mob_count(state,color) + \
           0.3 * heur_table(state, color) + \
           1 * heur_corner_count(state, color) + \
           10000 * heur_win(state, color)

def sorting_table(move):
    """ Sorting function for sorting the moves, trying to prune more
    :param: (int,int)
    :return: int
    """
    table = [[100, -20, 10,  5,  5, 10, -20, 100],
             [-20, -50, -2, -2, -2, -2, -50, -20],
             [10 , -2 , -1, -1, -1, -1, -2 ,  10],
             [5  , -2 , -1, -1, -1, -1, -2 ,   5],
             [5  , -2 , -1, -1, -1, -1, -2 ,   5],
             [10 , -2 , -1, -1, -1, -1, -2 ,  10],
             [-20, -50, -2, -2, -2, -2, -50, -20],
             [100, -20, 10,  5,  5, 10, -20, 100]]
    x, y = move
    return table[x][y]

def minimax(state, color, max_time, depth):
    """
    Returns a minimax move given the current state
    :param state:
    :return: (int, int)
    """

    move = (-1, -1)
    alpha = -math.inf
    beta = math.inf
    next_move = state.legal_moves(color)
    next_move.sort(reverse=True,key=sorting_table)
    v = -math.inf
    for st in next_move:
        # Time is over!!!
        toc = time.time() - tic
        if toc + 0.05 >= max_time:
            return random.choice(state.legal_moves(color))
        state.process_move(st, color)
        v = max(v , value_min(state, alpha, beta, state.opponent(color), depth-1, max_time))
        state.unprocess_move()
        if v > alpha:
            alpha = v
            move = st

    return move

def cutoff(state, depth, max_time):
    """
    Stop the minimax if the depth is 0 or the time is over
    or the game is over
    :param: state, int, float
    :return: bool
    """

    toc = time.time() - tic
    return depth == 0 or\
           state.piece_count[state.EMPTY] == 0 or\
           toc + 0.05 >= max_time

def value_max(state, alpha, beta, color, depth, max_time):
    """
    Returns a supporting value given the current state and alpha and beta values
    :return: int
    """
    global prunned
    global calculated

    if cutoff(state, depth, max_time):
        return general_heur(state, color)

    next_move = state.legal_moves(color)
    next_move.sort(reverse=True,key=sorting_table)
    v = -math.inf
    for st in next_move:
        state.process_move(st, color)
        calculated += 1
        v = max(v, value_min(state, alpha, beta, state.opponent(color), depth-1, max_time))
        state.unprocess_move()
        alpha = max(alpha, v)
        if beta <= alpha:
            prunned += 1
            break
    return alpha

def value_min(state, alpha, beta, color, depth, max_time):
    """
    Returns a supporting value given the current state and alpha and beta values
    :return: int
    """
    global prunned
    global calculated

    if cutoff(state, depth, max_time):
        return general_heur(state, state.opponent(color))

    next_move = state.legal_moves(color)
    next_move.sort(reverse=True,key=sorting_table)
    v = math.inf
    for st in next_move:
        state.process_move(st, color)
        calculated += 1
        v = min(v, value_max(state, alpha, beta, state.opponent(color), depth-1, max_time))
        state.unprocess_move()
        beta = min(beta, v)
        if beta <= alpha:
            prunned += 1
            break
    return beta

def make_move(the_board, color):
    """
    Returns a move made by using the minimax algorithm 
    :param: state, char
    :return: (int, int)
    """
    color = board.Board.WHITE if color == 'white' else board.Board.BLACK

    max_time = 1
    current_depth = 2
    global prunned
    global calculated

    calculated = 0
    prunned = 0

    legal_moves = the_board.legal_moves(color)

    toc = time.time() - tic
    move = minimax(the_board, color, max_time, 1)
    while(toc + 0.05 <= max_time):
        last_move = copy.deepcopy(move)
        move = minimax(the_board, color, max_time, current_depth)
        current_depth += 1
        toc = time.time() - tic

    return last_move if len(legal_moves) > 0 else (-1, -1)

if __name__ == '__main__':
    b = board.from_file(sys.argv[1])
    f = open('move.txt', 'w')
    f.write('%d,%d' % make_move(b, sys.argv[2]))
    f.close()
