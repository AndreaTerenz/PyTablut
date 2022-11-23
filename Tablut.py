import math

import numpy as np
from icecream import ic

from aima.games import Game, GameState, alpha_beta_cutoff_search
from board import CheckerType, CellType, Board


class Tablut(Game):
    def __init__(self, role, board=Board()):
        self.board = board
        self.role = role
        self.opponent = "BLACK" if role == "WHITE" else "WHITE"

        self.initial = GameState(to_move=self.role, utility=self.utility(self.board, self.role),
                                 board=self.board.grid, moves=self.actions(self.board))

    def actions(self, state):  # il problema e' qui, e' sempre qui
        """Return a list of the allowable moves at this point."""
        if type(state) == GameState:
            state = state.board
        moves = []
        checkers = state.get_checkers_for_role(self.role)

        for checker in checkers:
            r, c = checker
            checker_moves = state.moves_for_cell(r, c)
            to_append = [[(r, c), move] for move in checker_moves]
            moves += to_append

        return moves

    def result(self, state, move):
        """Return the state that results from making a move from a state."""
        if type(state) == GameState:
            state = state.board
        move_from = move[0]
        move_to = move[1]

        board_result = state.apply_move(move_from, move_to, self.role)
        return board_result  # .to_string_grid()
    
    def __king_in_danger(self,state):

        king=state.king
        enemies_in_column=0
        enemies_in_row=0

        for i in state.grid[:, king[1]]:
            if i.checker == CheckerType.BLACK:
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

    def __king_to_escape(self,state):
        king = state.king

        if state.grid[king].type == CellType.ESCAPE:
            return True

        return len(state.available_escapes()) > 0

    def utility(self, state, player):
        king = state.king
        mult = +1 if player == "WHITE" else -1

        if self.__king_to_escape(state):
            return np.inf * mult

        if king == (100, 100):
            return np.inf * -1 * mult

        def distance_between_cells(a, b, squared=False):
            """
            Small utility function to compute the Euclidean distance between two points A and B

            :param a: First point
            :param b: Second point
            :param squared: if True, return the squared distance (default is false)
            :return: distance or squared distance between A and B
            """

            d_x_sq = (a[0] - b[0]) ** 2
            d_y_sq = (a[1] - b[1]) ** 2

            d_sq = d_x_sq + d_y_sq

            return d_sq if squared else math.sqrt(d_sq)

        # Per controllare alla svelta cosa cambia con pesi casuali
        random_weights = False  # E' triste che giochi DECISAMENTE meglio con questa a True....

        if player == "WHITE":
            gr = state.grid
            ic.enable()
            escapes = [(0, 1), (0, 2), (0, 6), (0, 7),
                       (1, 0), (1, 8),
                       (2, 0), (2, 8),
                       (6, 0), (6, 8),
                       (7, 0), (7, 8),
                       (8, 1), (8, 2), (8, 6), (8, 7), ]
            ic(escapes)
            escapes = [e for e in escapes if gr[e].type == CellType.ESCAPE and gr[e].checker == CheckerType.EMPTY]
            ic(escapes)
            d_to_escapes = np.array([distance_between_cells(king, e, squared=True) for e in escapes])

            min_d_to_escapes = int(np.min(ic(d_to_escapes)))
            ic.disable()
            Nenemies = len(state.blacks)
            param0 = 9 / math.sqrt(min_d_to_escapes)
            param1 = 16 - Nenemies
            param2 = self.__king_in_danger(state)
            w0 = 5 if not random_weights else np.random.uniform(0, 1)
            w1 = 1 if not random_weights else np.random.uniform(0, 1)
            w2 = 1 if not random_weights else np.random.uniform(0, 1)
            return param0 * w0 + param1 * w1 - param2 * w2
        if player == "BLACK":
            blacks = state.blacks
            distances = np.array([distance_between_cells(king, b, squared=True) for b in blacks])
            d_mean = int(math.sqrt(np.mean(distances)))
            Nenemies = 9 - len(state.whites)
            w0 = 1 if not random_weights else np.random.uniform(0, 1)
            w1 = 1 if not random_weights else np.random.uniform(0, 1)
            return Nenemies * w0 + d_mean * w1

    def terminal_test(self, state):
        """Return True if this is a final state for the game."""
        return state.is_game_over()

    def to_move(self, state):
        """Return the player whose move it is in this state."""
        return state.to_move

    def display(self, state):
        self.board.print_grid()

    def search_move(self, depth):
        # Avoid minmax if possible
        possible_moves = self.actions(self.board)
        escapes = self.board.available_escapes()

        if len(escapes) > 0:
            if self.role == "WHITE":
                return self.board.king, escapes[0]
            elif self.role == "BLACK":
                if len(escapes) == 1:
                    k_pos = self.board.king
                    esc = escapes[0]

                    # 0 == vertically (because king.row == escape.row)
                    # 1 == horizontally (because king.column == escape.column)
                    # Do I need to move vertically or horizontally to block the king?

                    def is_between(a, m, b) -> bool:
                        """
                        Check if a cell M is between two other cells A and B. A and B must be on the same
                        row or on the same line

                        :param a: position A
                        :param m: position M to be checked
                        :param b: position B
                        """

                        ar, ac = a
                        br, bc = b

                        if not (ar == br or ac == bc):
                            return False

                        if ar == br and ac == bc:
                            return m == a

                        mr, mc = m

                        return (min(ar, br) <= mr <= max(ar, br) and ac == mc == bc) \
                               or (ar == mr == br and min(ac, bc) <= mc <= max(ac, bc))

                    pm = [move for move in possible_moves if is_between(k_pos, move[1], esc)]

                    if len(pm) > 0:
                        return pm[0]
                else:
                    pass

        game_state = GameState(to_move=self.role,
                               utility=self.utility(self.board, self.role),
                               board=self.board,
                               moves=possible_moves)
        return alpha_beta_cutoff_search(game_state, self, depth)
