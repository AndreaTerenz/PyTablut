from types import CellType
import numpy as np
import math 
from player import BasePlayer
from board import Board, CheckerType,CellType


def StreetKing(player):
    king=player.board.king
    for i in player.board.grid[:,king[1]]:
        if i.checker!=CheckerType.EMPTY or i.checker!=CheckerType.KING:
            return False
    for i in player.board.grid[king[0],:]:
        if i.checker!=CheckerType.EMPTY or i.checker!=CheckerType.KING:
            return False
    return True    

def Children(board):
    #deve un vettore con le Board figlie di Board
    return None

def Heuristic(player):
    king=player.board.king
    if player.role=="WHITE":
        escapes=player.board.grid[CellType.ESCAPE,CheckerType.EMPTY]
        distances=np.array([np.linalg.norm(king-i,2) for i in escapes])
        min_distance=int(np.min(distances))
        NeatenEnemies=...#lo ritorna la funzione della Chiara
        return int(min_distance+NeatenEnemies)
    elif player.role=="BLACK":
        NeatenEnemies=...# lo ritorna la funzione della Chiara
        king_eaten=...# lo ritorna la  funzione della Chiara
        if king_eaten==True:
            return -np.inf
        else:
            return -NeatenEnemies     
    #l heuristica deve ritornare un max se sei un bianco
    #il max sarà la distanza in R2 del re dalla strada di casa
    #deve avere un peso positivo se il posizionamento d una pedina bianca mangia una nera
    
    #l'heurisica deve avere minimo se la pedina nera 
    #deve ritornare un max se mangia una pedina bianca
    #sommato a quanto distano due pedine nere scelte random da ogni lato a mangiare il Re


def minmax(position,depth,alpha=-np.inf,beta=+np.inf,maximizingPlayer=None):
    #funziona in caso di un tree in cui ogni ogni nodo due figli, 
    #devo pensare se funziona anche con un nodo con più figli
    #ma penso di si, poco efficiente però.
    if depth==0 :
        return Heuristic(position)
    if maximizingPlayer=="WHITE":
        maxEval=-np.inf
        for child in Children(position):
            eval=minmax(child,depth-1,alpha,beta,"BLACK")
            maxEval=max(maxEval,eval)
            alpha=max(alpha,eval)
            if beta<=alpha:
                break
        return maxEval
    else:
        minEval=+np.inf
        for child in Children(position):
            eval=minmax(child,depth-1,alpha,beta,"WHITE")
            minEval=min(minEval,eval)
            beta=min(beta,eval)
            if beta<=alpha:
                break
        return minEval
    
                
                
        
        