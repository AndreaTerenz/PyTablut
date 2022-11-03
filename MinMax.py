from types import CellType
import numpy as np
import math 
from player import BasePlayer
from board import Board, CheckerType, CellType


def StreetKing(player):
    king = player.board.king
    for i in player.board.grid[:, king[1]]:
        if i.checker != CheckerType.EMPTY or i.checker != CheckerType.KING:
            return False
    for i in player.board.grid[king[0], :]:
        if i.checker != CheckerType.EMPTY or i.checker != CheckerType.KING:
            return False
    return True

def Children(board):
    #deve un vettore con le Board figlie di Board
    return None


def Heuristic(player):
    king = player.board.king
    if StreetKing(player) == True:
        return +np.inf
    if player.role == "WHITE":
        escapes = player.board.grid[CellType.ESCAPE,CheckerType.EMPTY]
        distances = np.array([np.linalg.norm(king-i,2) for i in escapes])
        min_distance = int(np.min(distances))
        NeatenEnemies= ... #lo ritorna la funzione della Chiara
        return int(min_distance+NeatenEnemies)
    if player.role == "BLACK":
        NeatenEnemies=...# lo ritorna la funzione della Chiara
        king_eaten =...# lo ritorna la  funzione della Chiara
        if king_eaten == True:
            return -np.inf
        return -NeatenEnemies     


def Antirole(role):
    if role == "WHITE":
        return "BLACK"
    return "WHITE"


def minmax(position, depth, alpha=-np.inf, beta=+np.inf, maximizingPlayer= None):
    #funziona in caso di un tree in cui ogni ogni nodo due figli, 
    #devo pensare se funziona anche con un nodo con più figli
    #ma penso di si, poco efficiente però.
    if depth == 0:
        return Heuristic(position)
    if maximizingPlayer == position.role:
        maxEval = -np.inf
        for child in Children(position):
            eval_ = minmax(child, depth-1, alpha, beta, Antirole(position.role))
            maxEval = max(maxEval, eval_)
            alpha = max(alpha, eval_)
            if beta <= alpha:
                break
        return maxEval
    else:
        minEval = +np.inf
        for child in Children(position):
            eval_=minmax(child, depth-1, alpha, beta, Antirole(position.role))
            minEval=min(minEval, eval_)
            beta=min(beta, eval_)
            if beta <= alpha:
                break
        return minEval
