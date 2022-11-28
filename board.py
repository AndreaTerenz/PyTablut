import math
from enum import Enum

import numpy as np
from icecream import ic
from numpy import sign


# ic.disable()


class CellType(Enum):
    """
    Possible board cell types
    """

    NORMAL = 0
    CASTLE = 1
    CAMP = 2
    ESCAPE = 3

class CheckerType(Enum):
    """
    Possible checker types
    """

    EMPTY = 0
    WHITE = 1
    BLACK = 2
    KING = 3

    def __str__(self):
        match self:
            case CheckerType.EMPTY:
                return "EMPTY"
            case CheckerType.WHITE:
                return "WHITE"
            case CheckerType.BLACK:
                return "BLACK"
            case CheckerType.KING:
                return "KING"

class Cell:
    """
    Represents a cell in the board grid
    """

    def __init__(self, _type, _checker):
        """
        Create a new Cell object

        :param _type: cell type
        :param _checker: type of the checker currently on this cell
        """

        self.type = _type
        self.checker = _checker

    def copy(self):
        return Cell(self.type, self.checker)

class Board:
    """
    Represents the global state of the game
    """

    KING_FUCCED = (69, 69)

    empty_cell = Cell(CellType.NORMAL, CheckerType.EMPTY)

    # FIXME: This keep_empty thing is beyond ugly
    def __init__(self, keep_empty=False):
        self.grid = np.zeros((9, 9), dtype=np.dtype(Cell))
        self.whites = []
        self.blacks = []
        self.king = (4, 4)

        self.grid[:, :] = Cell(CellType.NORMAL, CheckerType.EMPTY)

        self.grid[self.king] = Cell(CellType.CASTLE, CheckerType.KING)

        # Escape cells
        escapes = [(0, 1), (0, 2), (0, 6), (0, 7),
                   (1, 0), (1, 8),
                   (2, 0), (2, 8),
                   (6, 0), (6, 8),
                   (7, 0), (7, 8),
                   (8, 1), (8, 2), (8, 6), (8, 7), ]

        # Black camps
        self.blacks = [(0, 3), (0, 4), (0, 5),
                       (1, 4),
                       (3, 0), (3, 8),
                       (4, 0), (4, 1), (4, 7), (4, 8),
                       (5, 0), (5, 8),
                       (7, 4),
                       (8, 3), (8, 4), (8, 5)]

        self.whites = [(2, 4),
                       (3, 4),
                       (4, 2), (4, 3), (4, 5), (4, 6),
                       (5, 4),
                       (6, 4)]

        for e in escapes:
            self.grid[e[0], e[1]] = Cell(CellType.ESCAPE, CheckerType.EMPTY)
        for c in self.blacks:
            self.grid[c[0], c[1]] = Cell(CellType.CAMP, CheckerType.BLACK)
        for w in self.whites:
            self.grid[w[0], w[1]] = Cell(CellType.NORMAL, CheckerType.WHITE)

    def print_grid(self, ascii_art=True, title=""):
        """
        Print current grid state

        :param ascii_art: If True, print the grid in ASCII art (default True)
        :param title: If a non-empty string, will be printed before the board
        """
        if title != "":
            print(title)

        for i in range(9):
            for j in range(9):
                cell_type = self.grid[i][j].type
                checker_type = self.grid[i][j].checker

                if not ascii_art:
                    print(f"{cell_type.value};{checker_type.value} ", end=" ")
                else:
                    char_to_print = " "
                    match checker_type:
                        case CheckerType.KING:
                            char_to_print = "K"
                        case CheckerType.BLACK:
                            char_to_print = "B"
                        case CheckerType.WHITE:
                            char_to_print = "W"
                        # default case
                        case _:
                            # Everything here applies only to EMPTY cells
                            if cell_type == CellType.ESCAPE:
                                char_to_print = "-"
                            elif cell_type == CellType.CASTLE:
                                char_to_print = "#"

                    print(char_to_print, end=" ")
            print()

    def update_state(self, server_state):
        """
        Update state grid reading state received from server

        :param server_state: grid state from server
        :return: None
        """
        self.blacks = []
        self.whites = []
        for i in range(9):
            for j in range(9):
                # Cella di turno da leggere
                server_cell = server_state[i][j]

                match server_cell:
                    case "EMPTY":
                        self.grid[i][j].checker = CheckerType.EMPTY
                    case "WHITE":
                        self.grid[i][j].checker = CheckerType.WHITE
                        self.whites.append((i,j))
                    case "BLACK":
                        self.grid[i][j].checker = CheckerType.BLACK
                        self.blacks.append((i, j))
                    case "KING":
                        self.grid[i][j].checker = CheckerType.KING
                        self.king = (i, j)

    def apply_move(self, from_cell, to_cell, _role):
        """
        Returns a COPY of the board in which a checker has been moved from
        'from_cell' to 'to_cell', checking also if any enemy checkers are taken
        in the process

        :param from_cell:
        :param to_cell:
        :param _role:
        :return:
        """

        output = self.copy()
        checker_to_move = output.grid[from_cell].checker

        output.set_checker_at_pos(to_cell, checker_to_move)
        output.set_checker_at_pos(from_cell, CheckerType.EMPTY)

        row, column = to_cell #creo ste variabili solo per semplicità di notazione

        # controllo se nel vicinato della pedina ci sono pedine avversarie. Se
        # ci sono controllo sulla stessa linea di vista come ho scritto prima.
        # Se vanno mangiate, setto il CheckerType di quella Cell come EMPTY.

        eaten_checkers = [] #lista delle cordinate delle pedine che verranno mangiate muahahah

        role = (CheckerType.WHITE if _role == "WHITE" else CheckerType.BLACK)
        opponent = (CheckerType.BLACK if _role == "WHITE" else CheckerType.WHITE)

        # riga/colonna devono essere piu' di 1 e meno di 7, perche' ci vogliono
        # due celle di spazio per poter mangiare in ogni direzione (una per la pedina
        # avversaria da mangiare e un altro per la seconda pedina propria da usare per mangiare)

        # caso del re
        row_k, column_k = output.king
        # can't check outside the board

        if output.king_trapped():
            output.king = Board.KING_FUCCED

        others = []

        if column > 1:
            others.append([(row, column - 1), (row, column - 2)])
        if column < 7:
            others.append([(row, column + 1), (row, column + 2)])
        if row > 1:
            others.append([(row - 1, column), (row - 2, column)])
        if row < 7:
            others.append([(row + 1, column), (row + 2, column)])

        for o in others:
            near, far = o
            if output.grid[near].checker == opponent and output.grid[near].type != CellType.CAMP:
                if output.grid[far].checker == role or \
                        output.grid[far].type in [CellType.CAMP, CellType.CASTLE]:
                    eaten_checkers.append(near)

        if output.king_trapped():
            pass  # output.king = (100,100)

        if len(eaten_checkers) > 0:
            pass #ic(f"Eaten checkers: {eaten_checkers}")
        # rimuovo le pedine mangiate
        for coordinate in eaten_checkers:
            output.set_checker_at_pos(coordinate, CheckerType.EMPTY)

        return output

    # These two methods overload the subscript operator ("[]")
    # to allow a Board object to be indexed like a 2D array,
    # using simply "obj[r,c]" instead of "obj.grid[r,c]"

    def __getitem__(self, item):
        r, c = item
        return self.grid[r, c] if (0 <= r <= 9 and 0 <= c <= 9) else None

    def __setitem__(self, key, value):
        r, c = key
        if type(value) == Cell and 0 <= r <= 9 and 0 <= c <= 9:
            self.grid[r, c] = value

    def set_checker_at_pos(self, position, new_checker: CheckerType) -> bool:
        """
        Puts a checker of a certain type into a certain position, updating the self.whites
        or self.blacks list (depending on the 'checker' argument).

        :param position: (row,column) destination position
        :param new_checker: type of the checker being moved
        """
        old_check = self.grid[position].checker
        if old_check != CheckerType.EMPTY and new_checker != CheckerType.EMPTY:
            ic("CAN'T PUT A CHECKER IN A NON EMPTY CELL")
            return False

        self.grid[position].checker = new_checker

        if new_checker == CheckerType.EMPTY:
            match old_check:
                case CheckerType.WHITE:
                    self.whites.remove(position)
                case CheckerType.BLACK:
                    self.blacks.remove(position)
                case CheckerType.KING:
                    #ic("....what do you mean you want to DELETE the king? Are you gay")
                    return False
        else:
            match new_checker:
                case CheckerType.WHITE:
                    self.whites += [position]
                case CheckerType.BLACK:
                    self.blacks += [position]
                case CheckerType.KING:
                    self.king = position

        return True

    def is_game_over(self):
        """
        Checks if the current state of the grid is terminal (the game is over)

        :return: True if the game is over
        """
        if self.king == Board.KING_FUCCED:
            return True

        # King in an escape tile?
        if self.grid[self.king].type == CellType.ESCAPE:
            return True

        return self.king_trapped()

    def king_trapped(self):
        if self.king == Board.KING_FUCCED:
            return True

        king_r, king_c = self.king
        black_king_neighbors = 0
        borders_castle = 0

        # Count how many blacks borders the kings
        # and "how many castles" (either 0 or 1, obv)
        for n in get_cell_neighbors(king_r, king_c):
            r, c = n
            is_black = self.grid[r, c].checker == CheckerType.BLACK
            is_castle = self.grid[r, c].type == CellType.CASTLE
            black_king_neighbors += int(is_black)
            borders_castle += int(is_castle)

        if self.grid[self.king].type == CellType.CASTLE and black_king_neighbors == 4:
            # 4 blacks have surrounded the king in the castle
            return True
        elif borders_castle > 0 and black_king_neighbors == 3:
            # 3 blacks have surrounded the king near the castle
            return True
        elif black_king_neighbors >= 2:
            # 2 blacks have surrounded the king
            return True

    def copy(self):
        """
        Create a DEEP copy of the board

        :return: a Board object with the same state as self
        """

        board_copy = Board(keep_empty=True)

        for i in range(9):
            for j in range(9):
                board_copy.grid[i, j] = self.grid[i, j].copy()

        board_copy.whites = self.whites.copy()
        board_copy.blacks = self.blacks.copy()
        board_copy.king = self.king

        return board_copy

    def to_string_grid(self):
        """
        Converts the board's grid to a 2D matrix of strings representing the
        checker in each cell (EMPTY, WHITE, KING or BLACK)

        :return: a 2D matrix of strings
        """

        output = [[""] * 9] * 9

        for i in range(9):
            for j in range(9):
                output[i][j] = str(self.grid[i, j].checker)

        return output

    def get_checkers_for_role(self, role: str, include_king=True) -> list:
        """
        Return checkers that can belong to the player of the given role

        :param role: player role (either "WHITE" or "BLACK")
        :param include_king: if False, don't count the king as a white checker
        :return: list of checkers or empty list if role is invalid
        """
        match (role):
            case "WHITE":
                return self.whites + ([self.king] if include_king else [])
            case "BLACK":
                return self.blacks
            case _:
                return []

    def check_move(self, destination_r, destination_c, start_r, start_c) -> bool:
        """
        Check if moving a checker from (cell_r,cell_c) to (move_r.move_c) is a valid move

        :param destination_r: destination row
        :param destination_c: destination column
        :param start_r: starting row
        :param start_c: starting column
        :return: True if the move is valid
        """
        # Forbid diagonal moves
        if start_r != destination_r and start_c != destination_c:
            return False

        # Moving the checker to the same position it's already in is trivially always possible
        if start_r == destination_r and start_c == destination_c:
            return True

        checker_to_move = self.grid[start_r, start_c].checker
        dest_cell_checker = self.grid[destination_r, destination_c].checker

        # Innanzitutto, la cella di destinazione deve essere vuota
        if dest_cell_checker != CheckerType.EMPTY:
            return False

        dest_cell_type = self.grid[destination_r, destination_c].type

        if checker_to_move in [CheckerType.WHITE, CheckerType.KING]:
            # Deve essere VUOTA
            # Puo' essere una cella NORMAL o una ESCAPE
            return dest_cell_type in [CellType.NORMAL, CellType.ESCAPE]
        elif checker_to_move == CheckerType.BLACK:
            if self.grid[start_r, start_c].type == CellType.CAMP:
                # Deve essere VUOTA
                # Non puo' essere il CASTLE
                return dest_cell_type != CellType.CASTLE
            else:
                # Deve essere VUOTA
                # Puo' essere una cella NORMAL o una ESCAPE
                return dest_cell_type in [CellType.NORMAL, CellType.ESCAPE]

    def moves_for_cell(self, r, c):
        """
        Compute list of all possible legal moves for a checker in (r,c)

        :param r: checker row
        :param c: checker column
        :return: List of legal moves
        """
        moves = []

        """
        moves += [(r,j) for j in takewhile(lambda j: self.check_move(r, j, r, c), range(c-1,-1,-1))]
        moves += [(r,j) for j in takewhile(lambda j: self.check_move(r, j, r, c), range(c + 1, 9))]
        moves += [(i,c) for i in takewhile(lambda i: self.check_move(i,c,r,c), range(r - 1, -1, -1))]
        moves += [(i,c) for i in takewhile(lambda i: self.check_move(i,c,r,c), range(r + 1, 9))]
        """

        # Explore left
        for j in range(c - 1, -1, -1):
            if self.check_move(r, j, r, c):
                moves.append((r, j))
            else:
                break
        # Explore right
        for j in range(c + 1, 9):
            if self.check_move(r, j, r, c):
                moves.append((r, j))
            else:
                break
        # Explore up
        for i in range(r - 1, -1, -1):
            if self.check_move(i, c, r, c):
                moves.append((i, c))
            else:
                break
        # Explore down
        for i in range(r + 1, 9):
            if self.check_move(i, c, r, c):
                moves.append((i, c))
            else:
                break

        return moves

    def available_escapes(self):
        """
        Find all Escape cells visible from the king's position (if any exist)

        :return: the list of (r,c) positions of the visible escapes (empty list if none are found)
        """
        r, c = self.king

        if 3 <= r <= 5 and 3 <= c <= 5:
            # Around the center of the board there are definitely no visible escapes
            return []

        escapes = []

        # Explore left
        if self.path_between_cells(self.king, (r, 0)):
            escapes.append((r, 0))
        # Explore right
        if self.path_between_cells(self.king, (r, 8)):
            escapes.append((r, 8))
        # Explore up
        if self.path_between_cells(self.king, (0, c)):
            escapes.append((0, c))
        # Explore down
        if self.path_between_cells(self.king, (8, c)):
            escapes.append((8, c))

        return escapes

    def path_between_cells(self, start, end):
        sr, sc = start
        er, ec = end

        if sr != er and sc != ec:
            return False

        if sr == er and sc == ec:
            return True

        if sr == er:
            direction = -sign(sc - ec)
            cells = [self[sr, j] for j in range(sc + direction, ec + direction, direction)]
        else:
            direction = -sign(sr - er)
            cells = [self[i, sc] for i in range(sr + direction, er + direction, direction)]

        for cell in cells:
            if cell.checker != CheckerType.EMPTY or cell.type in [CellType.CAMP, CellType.CASTLE]:
                return False
        return True


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


def get_cell_neighbors(r, c):
    """
    Returns neighboring positions for position [r,c]

    """

    output = []

    if r >= 1:
        output.append((r - 1, c))
    if r <= 7:
        output.append((r + 1, c))
    if c >= 1:
        output.append((r, c - 1))
    if c <= 7:
        output.append((r, c + 1))

    return output


def get_mirror_position(r, c, center_r, center_c):
    """
    Utility function to return the mirror of position [r,c] with respect to
    position [center_r, center_c]

    :param r: Row of position to be mirrorred
    :param c: Column of position to be mirrorred
    :param center_r: Row of center of symmetry
    :param center_c: Column of center of symmetry
    :return: Mirrored position
    """

    delta_r = r - center_r
    delta_c = c - center_c

    return center_r - delta_r, center_c - delta_c


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
