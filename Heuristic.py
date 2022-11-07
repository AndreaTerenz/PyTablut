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
        return 0


    ''' Piu il re è vicino ad un escape piu ha peso la distanza
    Piu il re è lontano dall'escape piu ha peso il numero di nemici.
    
    
    
    
    
    '''


def heuristic(player):
    king = player.board.king
    if player.role == "WHITE":
        if king[0]==100 and king[1]==100:
            return -np.inf
    #se il king è nell'escape ritorna piu infinito
        escapes = player.board.grid[CellType.ESCAPE,CheckerType.EMPTY]
        d_to_escapes = np.array([np.linalg.norm(king-i,2) for i in escapes])
        min_d_to_escapes = int(np.min(d_to_escapes))    

        Nenemies=len(player.board.blacks)

        param0=9/min_d_to_escapes
        param1=16-Nenemies
        param2=king_in_danger(player)
        return param0+param1+param2
    if player.role == "BLACK":
        if king[0]==100 and king[1]==100:
                return +np.inf
        blacks=player.board.blacks
        distances=np.array([np.linalg.norm(king-i,2) for i in blacks])
        d_mean=int(np.mean(distances))
        Nenemies = 9-len(player.board.whites)
        king_eaten = player.board.king == False
        return Nenemies+d_mean

