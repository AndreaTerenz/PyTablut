import math
import multiprocessing
from time import sleep, time

import numpy as np

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

    def __king_to_escape(self, state):
        king = state.king

        if state.grid[king].type == CellType.ESCAPE:
            return True

        return len(state.available_escapes()) > 0

    def __black_block_escape(self, king, esc, blacks):
        rows_esc = [0,1,2,6,7,8]
        col_esc = [0,1,2,6,7,8]
        esc_r = 0
        esc_c = 0
        if king[0] in rows_esc:
            for b in blacks:
                if b[0] in rows_esc and b[0] == king[0]:
                    esc_r += 1
        if king[1] in col_esc:
            for b in blacks:
                if b[1] in col_esc and b[1] == king[1]:
                    esc_c += 1
        return esc_r >= 2 and esc_c >= 2

    def utility(self, state, player):
        def distance_between_cells(a, b, mode=""):
            """
            Small utility function to compute the Euclidean distance between two points A and B

            :param a: First point
            :param b: Second point
            :param mode:
            :return: distance or squared distance between A and B
            """
            ax, ay = a
            bx, by = b
            diff_x = abs(ax - bx)
            diff_y = abs(ay - by)

            if mode == "man":
                return diff_x + diff_y

            d_x_sq = diff_x ** 2
            d_y_sq = diff_y ** 2

            d_sq = d_x_sq + d_y_sq

            if mode == "esq":
                return d_sq

            return math.sqrt(d_sq)

        king = state.king
        mult = +1 if player == "WHITE" else -1

        if self.__king_to_escape(state):
            return np.inf * mult

        if king == (100, 100):
            return np.inf * -1 * mult
        esc = [(0, 1), (0, 2), (0, 6), (0, 7),
               (1, 0), (1, 8),
               (2, 0), (2, 8),
               (6, 0), (6, 8),
               (7, 0), (7, 8),
               (8, 1), (8, 2), (8, 6), (8, 7), ]
        if player == "WHITE":
            gr = state.grid

            escapes = [e for e in esc if gr[e].type == CellType.ESCAPE and gr[e].checker == CheckerType.EMPTY]

            blacks = state.blacks

            d_king_to_blacks = np.array([distance_between_cells(king, black, mode="man") for black in blacks])
            mean_d_king_to_blacks = np.mean(d_king_to_blacks)

            d_to_escapes = np.array([distance_between_cells(king, e, mode="man") for e in escapes])
            min_d_to_escapes = (np.min(d_to_escapes))

            param0 = 9 / min_d_to_escapes
            param1 = 16 - len(blacks)
            param2 = self.__king_in_danger(state)
            param3 = mean_d_king_to_blacks
            # param4 = numero di bianchi che proteggono il re.
            param4 = len([1 for w in state.whites if (w[0] == king[0] - 1 or w[0] == king[0] + 1) and (
                        w[1] == king[1] - 1 or w[1] == king[1] + 1)])
            # param5 = numero di escapes che vede il re se raggiunge una certa posizione
            param5 = len(state.available_escapes()) #[1 for e in escapes if king[0] == e[0] or king[1] == e[1]]
            w1 = 3
            w2 = 1
            w3 = 2
            w4 = 3
            return (param0 + param5) * 1 / len(blacks) + param1 * w1 - param2 * w2 + param3 * w3 + w4 * (4 - param4)

        if player == "BLACK":
            distances = np.array([distance_between_cells(king, b, mode="man") for b in state.blacks])
            d_mean = np.mean(distances)
            param0 = 9 - len(state.whites)
            param2 = self.__black_block_escape(king, esc, state.blacks)
            param1 = d_mean
            w0 = 1  # np.random.uniform(0, 1)
            w1 = 1  # np.random.uniform(0, 1)
            w2 = 5
            return param0 * w0 + param1 * w1 + param2 * w2

    def terminal_test(self, state):
        """Return True if this is a final state for the game."""
        return state.is_game_over()

    def to_move(self, state):
        """Return the player whose move it is in this state."""
        return state.to_move

    def display(self, state):
        self.board.print_grid()

    def run_minmax(self, depth, possible_moves):
        game_state = GameState(to_move=self.role,
                               utility=self.utility(self.board, self.role),
                               board=self.board,
                               moves=possible_moves)
        return alpha_beta_cutoff_search(game_state, self, depth)

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

        output = None
        time_left = 50

        try:
            for d in range(1, depth):
                print(f"Depth: {d} - Time left: {time_left}")
                with multiprocessing.Pool(processes = 1) as pool:
                    before = time()
                    res = pool.apply_async(self.run_minmax, (d, possible_moves))
                    output = res.get(timeout=time_left)
                    after = time()
                    time_left -= abs(before - after)

        except:
            return output


