from types import CellType
import numpy as np
import random as rd
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

def king_in_danger(player):
    king=player.board.king
    enemies_in_column=0
    enemies_in_row=0
    for i in player.board.grid[::-1,king[1]]:
        if  i.checker == CheckerType.BLACK:
            enemies_in_column+=1
            break
    for i in player.board.grid[king[0],::-1]:
        if i.checker == CheckerType.BLACK:
            enemies_in_row+=1
            break
    if enemies_in_row != 0 and enemies_in_column != 0:
        return -int(enemies_in_row+enemies_in_column)
    else :
        return 1
    


def heuristic(player):
    king = player.board.king
    if player.role == "WHITE":
        escapes = player.board.grid[CellType.ESCAPE,CheckerType.EMPTY]
        d_to_escapes = np.array([np.linalg.norm(king-i,2) for i in escapes])
        min_d_to_escapes = int(np.min(d_to_escapes))    
        Nenemies=len(player.board.blacks)
        param0=1/min_d_to_escapes
        param1=1/Nenemies
        param2=king_in_danger(player)
        w0=rd.gauss(0,1)
        w1=rd.gauss(0,1)
        w2=rd.gauss(0,1)
        return param0*w0+param1*w1+param2*w2
    if player.role == "BLACK":
        w0=rd.gauss(0,1)
        Nenemies=len(player.board.whites)
        king_eaten = player.board.king== False
        if king_eaten==False:
            return None
        return w0*Nenemies