import aima.games as ag 
from player import BasePlayer
from board import Board, CheckerType, CellType
import numpy as np


class Tablut(ag.Game):
    def __init__(self,player):
        self.initial=ag.GameState(to_move=player.board.role,utility=0,board=player.board.grid,moves=[(0,0),(0,0)])
        
    def actions(self, state):
        """Return a list of the allowable moves at this point."""
        moves = list()
        if self.initial.to_move == "WHITE":
            for checker in self.player.board.whites:
                r, c = checker
                checker_moves = self.player.moves_for_cell(r, c)
                moves.append(checker_moves)
            return moves

        elif self.initial.to_move == "BLACK":
            for checker in self.player.board.blacks:
                r, c = checker
                checker_moves = self.player.moves_for_cell(r,c)
            moves.append(checker_moves)
            return moves


    def result(self, state, move):
        """Return the state that results from making a move from a state."""
        move_from=move[0]
        move_to=move[1]
        board=state.apply_move(move_from,move_to,self.initial.to_move)
        return board.grid
    
    
    def __king_in_danger(state):
        king=state.king
        enemies_in_column=0
        enemies_in_row=0
        for i in state.grid[:,king[1]]:
            if  i.checker == CheckerType.BLACK:
                enemies_in_column+=1
                break
        for i in state.grid[king[0],:]:
            if i.checker == CheckerType.BLACK:
                enemies_in_row+=1
                break
        if enemies_in_row != 0 and enemies_in_column != 0:
            return -int(enemies_in_row+enemies_in_column)
        else :
            return 0
    
    
    def utility(self, state, player):
        king = state.king
        if player == "WHITE":
            if king[0]==100 and king[1]==100:
                return -np.inf
        #se il king è nell'escape ritorna piu infinito
            escapes = state.grid[CellType.ESCAPE,CheckerType.EMPTY]
            d_to_escapes = np.array([np.linalg.norm(king-i,2) for i in escapes])
            min_d_to_escapes = int(np.min(d_to_escapes))    
            Nenemies=len(state.blacks)
            param0=9/min_d_to_escapes
            param1=16-Nenemies
            param2=self.__king_in_danger(state)
            return param0+param1-param2
        if player == "BLACK":
            if king[0]==100 and king[1]==100:
                    return +np.inf
            blacks=state.blacks
            distances=np.array([np.linalg.norm(king-i,2) for i in blacks])
            d_mean=int(np.mean(distances))
            Nenemies = 9-len(state.whites)
            return Nenemies+d_mean

    def terminal_test(self, state):
        """Return True if this is a final state for the game."""
        return state.is_game_over()


    def to_move(self, state):
        """Return the player whose move it is in this state."""
        return self.initial.to_move


    def display(self, state):
        state.print_grid()
        
    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)
    
        
        