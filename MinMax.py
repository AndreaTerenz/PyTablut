from types import CellType
import numpy as np
import math 
from player import BasePlayer
from board import Board, CheckerType, CellType

def king_to_escape(player):
    king = player.board.king
    for i in player.board.grid[:, king[1]]:
        if i.checker != CheckerType.EMPTY or i.checker != CheckerType.KING:
            return False
    for i in player.board.grid[king[0], :]:
        if i.checker != CheckerType.EMPTY or i.checker != CheckerType.KING:
            return False
    return True


def get_children(player):
    """
    Fa un ciclo su

    :param board:
    :return:
    """

    if player.role == CheckerType.WHITE:
        checkers=player.board.whites+[player.board.king]
    elif player.role == CheckerType.BLACK:
        checkers= player.board.blacks
    moves=[[] for i in range(len(checkers))]

    return []


def heuristic(player):
    king = player.board.king
    if player.role == "WHITE":
        if king_to_escape(player):
            return +np.inf
        escapes = player.board.grid[CellType.ESCAPE,CheckerType.EMPTY]
        distances = np.array([np.linalg.norm(king-i,2) for i in escapes])
        min_distance = int(np.min(distances))
        NeatenEnemies= ... #lo ritorna la funzione della Chiara
        return int(min_distance+NeatenEnemies)
    if player.role == "BLACK":
        # if it can eat the king : return -inf

        NeatenEnemies=...# lo ritorna la funzione della Chiara
        king_eaten = player.board.king == (100,100)# lo ritorna la  funzione della Chiara
        if king_eaten:
            return -np.inf
        return -NeatenEnemies     


def antirole(role):
    if role == "WHITE":
        return "BLACK"
    return "WHITE"


def minmax(position, depth, alpha=-np.inf, beta=+np.inf, maximizingPlayer= None):
    #funziona in caso di un tree in cui ogni ogni nodo due figli, 
    #devo pensare se funziona anche con un nodo con più figli
    #ma penso di si, poco efficiente però.
    if depth == 0:
        return heuristic(position)
    if maximizingPlayer == position.role:
        maxEval = -np.inf
        for child in children(position):
            eval_ = minmax(child, depth-1, alpha, beta, antirole(child.role))
            maxEval = max(maxEval, eval_)
            alpha = max(alpha, eval_)
            if beta <= alpha:
                break
        return maxEval
    else:
        minEval = +np.inf
        for child in children(position):
            eval_=minmax(child, depth-1, alpha, beta, antirole(child.role))
            minEval=min(minEval, eval_)
            beta=min(beta, eval_)
            if beta <= alpha:
                break
        return minEval
