import multiprocessing
import traceback
from time import time

import numpy as np

from aima.games import Game, GameState, alpha_beta_cutoff_search
from board import CheckerType, CellType, Board, is_between, get_cell_neighbors, distance_between_cells


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

    def __king_in_danger(self, state):

        king = state.king
        enemies_in_column = 0
        enemies_in_row = 0

        for i in state.grid[:, king[1]]:
            if i.checker == CheckerType.BLACK:
                enemies_in_column += 1
                break

        for i in state.grid[king[0], :]:
            if i.checker == CheckerType.BLACK:
                enemies_in_row += 1
                break

        if enemies_in_row != 0 and enemies_in_column != 0:
            return (enemies_in_row + enemies_in_column)

        else:
            return 0

    def king_sees_escape(self, state):
        king = state.king

        if state.grid[king].type == CellType.ESCAPE:
            return True

        return len(state.available_escapes()) > 0

    def __black_block_escape(self, king, esc, blacks):
        rows_esc = [0, 1, 2, 6, 7, 8]
        col_esc = [0, 1, 2, 6, 7, 8]
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
        king = state.king
        mult = +1 if player == "WHITE" else -1

        if king == Board.KING_FUCCED:
            return np.inf * -mult  # +inf for BLACK; -inf for WHITE

        if self.king_sees_escape(state):
            return np.inf * mult  # +inf for WHITE; -inf for BLACK

        esc = [(0, 1), (0, 2), (0, 6), (0, 7),
               (1, 0), (1, 8),
               (2, 0), (2, 8),
               (6, 0), (6, 8),
               (7, 0), (7, 8),
               (8, 1), (8, 2), (8, 6), (8, 7), ]

        whites_count = len(state.whites)
        blacks_count = len(state.blacks)

        d_king_to_blacks = np.array([distance_between_cells(king, black, mode="man") for black in state.blacks])
        mean_d_king_to_blacks = np.mean(d_king_to_blacks)

        if player == "WHITE":
            escapes = [e for e in esc if
                       state.grid[e].type == CellType.ESCAPE and state.grid[e].checker == CheckerType.EMPTY]

            d_to_escapes = np.array([distance_between_cells(king, e, mode="man") for e in escapes])
            min_d_to_escapes = (np.min(d_to_escapes))

            param0 = 9 / min_d_to_escapes
            param1 = 16 - blacks_count
            param2 = self.__king_in_danger(state)
            param3 = mean_d_king_to_blacks
            # param4 = numero di bianchi che proteggono il re.
            param4 = len([1 for w in state.whites if (abs(w[0] - king[0]) == 1 and w[1] == king[1]) or (
                        w[0] == king[0] and abs(w[1] - king[1]) == 1)])
            # param5 = numero di escapes che vede il re se raggiunge una certa posizione
            param5 = len(state.available_escapes())  # [1 for e in escapes if king[0] == e[0] or king[1] == e[1]]
            param6 = whites_count

            w6 = whites_count + blacks_count
            w0 = 25 - blacks_count - whites_count
            w1 = w6
            w2 = 10
            w3 = w0
            w4 = w0

            return (param0 + param5) * w0 + param1 * w1 - param2 * w2 + param3 * w3 + w4 * (4 - param4) + w6 * param6
        if player == "BLACK":
            param0 = 9 - whites_count
            param1 = mean_d_king_to_blacks
            param2 = self.__black_block_escape(king, esc, state.blacks)
            param3 = blacks_count

            w0 = whites_count + blacks_count
            w1 = 25 - blacks_count - whites_count
            w2 = 25 - blacks_count - whites_count
            w3 = w0

            return param0 * w0 + param1 * w1 + param2 * w2 + param3 * w3

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
        move, score = alpha_beta_cutoff_search(game_state, self, depth)

        return move, score

    def quick_search(self):
        possible_moves = self.actions(self.board)
        escapes = self.board.available_escapes()
        k_pos = self.board.king

        # Check escapes
        if len(escapes) > 0:
            if self.role == "WHITE":
                return self.board.king, escapes[0]
            elif self.role == "BLACK":
                if len(escapes) == 1:
                    pm = [move for move in possible_moves if is_between(k_pos, move[1], escapes[0])]

                    if len(pm) > 0:
                        return pm[0]

        if self.role == "BLACK":
            king_neighb = get_cell_neighbors(k_pos[0], k_pos[1])
            black_neighb = [n for n in king_neighb if self.board[n].checker == CheckerType.BLACK]
            empty_neighb = [n for n in king_neighb if self.board[n].checker == CheckerType.EMPTY]
            king_borders_castle = len([n for n in king_neighb if self.board[n].type == CellType.CASTLE]) == 1

            if len(black_neighb) >= 2:
                cell_to_fill = None

                if self.board[k_pos].type == CellType.CASTLE and len(black_neighb) == 3 and len(empty_neighb) == 1:
                    # King almost surrounded in castle
                    # Only one possible cell left to fill
                    cell_to_fill = empty_neighb[0]
                elif king_borders_castle and len(black_neighb) >= 2 and len(empty_neighb) == 1:
                    cell_to_fill = empty_neighb[0]
                elif len(black_neighb) >= 1 and len(empty_neighb) >= 1:
                    kr, kc = k_pos

                    if kr >= 1 \
                            and (self.board[(kr - 1, kc)].type == CellType.CAMP or self.board[
                        (kr - 1, kc)].checker == CheckerType.BLACK) \
                            and self.board[(kr + 1, kc)].checker == CheckerType.EMPTY:
                        cell_to_fill = (kr + 1, kc)
                    elif kr <= 7 \
                            and (self.board[(kr + 1, kc)].type == CellType.CAMP or self.board[
                        (kr - 1, kc)].checker == CheckerType.BLACK) \
                            and self.board[(kr - 1, kc)].checker == CheckerType.EMPTY:
                        cell_to_fill = (kr - 1, kc)
                    elif kc >= 1 \
                            and (self.board[(kr, kc - 1)].type == CellType.CAMP or self.board[
                        (kr - 1, kc)].checker == CheckerType.BLACK) \
                            and self.board[(kr, kc + 1)].checker == CheckerType.EMPTY:
                        cell_to_fill = (kr, kc + 1)
                    elif kc <= 7 \
                            and (self.board[(kr, kc + 1)].type == CellType.CAMP or self.board[
                        (kr - 1, kc)].checker == CheckerType.BLACK) \
                            and self.board[(kr, kc - 1)].checker == CheckerType.EMPTY:
                        cell_to_fill = (kr, kc - 1)

                if not cell_to_fill is None:
                    pm = [move for move in possible_moves if move[1] == cell_to_fill]

                    if len(pm) > 0:
                        return pm[0]

        return None

    def search_move(self, depth):
        # Avoid minmax if possible
        print("Running quick search...", end="", flush=True)
        best_move = self.quick_search()
        if best_move:
            print("quick search successful")
            return best_move

        print("quick search failed, fallback to MinMax")

        best_score = -np.inf
        best_depth = 1
        time_left = 58

        try:
            for d in range(1, depth):
                print(f"Depth: {d} - Time left: {time_left:.3f}...", end="", flush=True)

                before = time()
                with multiprocessing.Pool(processes=1) as pool:
                    res = pool.apply_async(self.run_minmax, (d, self.actions(self.board)))
                    new_move, new_score = res.get(timeout=time_left)
                time_taken = abs(time() - before)

                print(f"Move found in {time_taken:.3f} - Score: {new_score:.3f}")
                time_left -= time_taken

                if new_score >= best_score:
                    best_score = new_score
                    best_move = new_move
                    best_depth = d

                if best_score == np.inf:
                    print(f"Stopped early (winning move)")
                    return best_move
        except IndexError:
            print("ONGA BONGA")
            traceback.print_exc()
        except Exception:
            print(f"Search timed out - Max depth searched: {best_depth}")

        return best_move
