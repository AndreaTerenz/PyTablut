import numpy as np

import aima.games as ag
from board import CheckerType, CellType, Board


class Tablut(ag.Game):
    def __init__(self, role):
        self.board = Board()
        self.role = role
        self.opponent = "BLACK" if role == "WHITE" else "WHITE"

        self.initial = ag.GameState(to_move=self.role, utility=self.utility(self.board, self.role),
                                    board=self.board.grid, moves=self.actions(self.board))

    def actions(self, state):  # il problema e' qui, e' sempre qui
        """Return a list of the allowable moves at this point."""
        moves = []
        checkers = self.board.get_checkers_for_role(self.role)

        for checker in checkers:
            r, c = checker
            checker_moves = self.board.moves_for_cell(r, c)
            to_append = [[(r, c), move] for move in checker_moves]
            moves += to_append

        return moves

    def result(self, state, move):
        """Return the state that results from making a move from a state."""
        move_from = move[0]
        move_to = move[1]

        board_result = self.board.apply_move(move_from, move_to, self.role)
        return board_result.to_string_grid()
    
    def __king_in_danger(self,state):

        king=self.board.king
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
            return (enemies_in_row+enemies_in_column)

        else :
            return 0
    

    def utility(self, state, player):

        king = self.board.king
        if player == "WHITE":
            if king[0] == 100 and king[1] == 100:
                # se il king è nell'escape ritorna piu infinito
                return -np.inf

            gr = self.board.grid
            esc = [(0, 1), (0, 2), (0, 6), (0, 7),
                   (1, 0), (1, 8),
                   (2, 0), (2, 8),
                   (6, 0), (6, 8),
                   (7, 0), (7, 8),
                   (8, 1), (8, 2), (8, 6), (8, 7), ]
            escapes = [e for e in esc if gr[e].type == CellType.ESCAPE and gr[e].checker == CheckerType.EMPTY]

            d_to_escapes = np.array([np.linalg.norm(np.array(king) - np.array(e), 2) for e in escapes])
            min_d_to_escapes = int(np.min(d_to_escapes))

            Nenemies = len(self.board.blacks)
            param0 = 9 / min_d_to_escapes
            param1 = 16 - Nenemies
            param2 = self.__king_in_danger(self.board)

            return param0 + param1 - param2
        if player == "BLACK":
            if king[0]==100 and king[1]==100:
                    return +np.inf
            blacks=self.board.blacks
            distances=np.array([np.linalg.norm((np.array(king)-np.array(b)),2) for b in blacks])
            d_mean=int(np.mean(distances))
            Nenemies = 9-len(self.board.whites)
            return Nenemies+d_mean

    def terminal_test(self, state):
        """Return True if this is a final state for the game."""
        return self.board.is_game_over()


    def to_move(self, state):
        """Return the player whose move it is in this state."""
        return state.to_move


    def display(self, state):
        self.board.print_grid()
        
    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)
        