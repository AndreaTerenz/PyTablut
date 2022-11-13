from enum import Enum

import numpy as np
from icecream import ic

ic.disable()


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

    empty_cell = Cell(CellType.NORMAL, CheckerType.EMPTY)
    def __init__(self):
        self.grid = np.zeros((9,9), dtype=np.dtype(Cell))

        for i in range(9):
            for j in range(9):
                self.grid[i,j] = Cell(CellType.NORMAL, CheckerType.EMPTY)

        self.whites = []
        self.blacks = []
        self.king = (4,4)

        self.grid[4,4] = Cell(CellType.CASTLE, CheckerType.KING)

        # Escape cells
        escapes = [(0,1),(0,2),(0,6),(0,7),
                   (1,0),(1,8),
                   (2,0),(2,8),
                   (6,0),(6,8),
                   (7,0),(7,8),
                   (8,1),(8,2),(8,6),(8,7),]

        # Black camps
        self.blacks = [(0,3),(0,4),(0,5),
                 (1,4),
                 (3,0),(3,8),
                 (4,0),(4,1),(4,7),(4,8),
                 (5,0),(5,8),
                 (7,4),
                 (8,3),(8,4),(8,5)]

        self.whites = [(2,4),
                  (3,4),
                  (4,2),(4,3),(4,5),(4,6),
                  (5,4),
                  (6,4)]

        for e in escapes:
            self.grid[e[0], e[1]] = Cell(CellType.ESCAPE, CheckerType.EMPTY)
        for c in self.blacks:
            self.grid[c[0], c[1]] = Cell(CellType.CAMP, CheckerType.BLACK)
        for w in self.whites:
            self.grid[w[0], w[1]] = Cell(CellType.NORMAL, CheckerType.WHITE)

    def print_grid(self, ascii_art = True):
        """
        Print current grid state

        :param ascii_art: If True, print the grid in ASCII art (default True)
        """
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
                        self.king = (i,j)

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

        """
        Funzione per mangiare le pedine. Dato il checker spostato nella nuova posizione
        (indicizzata da new_pos), controlla il suo vicinato. Se nel vicinato ci sono
        pedine dell'avversario, allora controlla la pedina vicina a tali pedine sulla stessa
        linea. Se c'è una pedina del colore della pedina che ha appena fatto la mossa, OPPURE
        una casella di tipo CAMP OPPURE la casella CASTLE, la pedina avversaria viene rimossa
        perché viene mangiata.
        """

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
        if output.king != (100, 100):
            pass
            """
            king_neighbors = [output.grid[row_k,column_k - 1], output.grid[row_k - 1,column_k],
                              output.grid[row_k,column_k + 1], output.grid[row_k + 1,column_k]]

            blacks = king_neighbors.count(Cell(CellType.NORMAL, CheckerType.BLACK))
            castles = king_neighbors.count(Cell(CellType.CASTLE, CheckerType.EMPTY))

            if blacks == 4:
                output.king = (100,100)
            elif blacks == 3 and castles == 1:
                output.king = (100,100)
            """

        if column > 1:
            if output.grid[row, column - 1].checker == opponent:
                if output.grid[row, column - 2].checker == role or output.grid[row, column - 2].type in [CellType.CAMP, CellType.CASTLE]:
                    eaten_checkers.append((row, column - 1))
            if role == CheckerType.BLACK and output.grid[row, column - 1].checker == CheckerType.KING:
                if output.grid[row, column - 2].checker == role or output.grid[row, column - 2].type in [CellType.CAMP,
                                                                                                         CellType.CASTLE]:
                    pass
                    # self.king = (100,100)


        if column < 7 and output.grid[row, column + 1].checker == opponent:
            if output.grid[row, column + 2].checker == role or output.grid[row, column + 2].type in [CellType.CAMP, CellType.CASTLE]:
                eaten_checkers.append((row, column + 1))
            if role == CheckerType.BLACK and output.grid[row, column - 1].checker == CheckerType.KING:
                if output.grid[row, column + 2].checker == role or output.grid[row, column + 2].type in [CellType.CAMP,
                                                                                                         CellType.CASTLE]:
                    pass
                    #self.king = (100, 100)

        if row > 1 and output.grid[row - 1, column].checker == opponent:
            if output.grid[row - 2, column].checker == role or output.grid[row - 2, column].type in [CellType.CAMP, CellType.CASTLE]:
                eaten_checkers.append((row - 1, column))
            if role == CheckerType.BLACK and output.grid[row - 1, column].checker == CheckerType.KING:
                if output.grid[row - 2, column].checker == role or output.grid[row - 2, column].type in [CellType.CAMP,
                                                                                                         CellType.CASTLE]:
                    pass
                    #self.king = (100, 100)

        if row < 7 and output.grid[row + 1, column].checker == opponent:
            if output.grid[row + 2, column].checker == role or output.grid[row + 2, column].type in [CellType.CAMP, CellType.CASTLE]:
                eaten_checkers.append((row + 1, column))
            if role == CheckerType.BLACK and output.grid[row + 1, column].checker == CheckerType.KING:
                if output.grid[row + 2, column].checker == role or output.grid[row + 2, column].type in [CellType.CAMP,
                                                                                                         CellType.CASTLE]:
                    pass
                    #self.king = (100, 100)

        if len(eaten_checkers) > 0:
            ic(f"Eaten checkers: {eaten_checkers}")
        # rimuovo le pedine mangiate
        for coordinate in eaten_checkers:
            output.set_checker_at_pos(coordinate, CheckerType.EMPTY)

        return output

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
                    ic("....what do you mean you want to DELETE the king? Are you gay")
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
        if self.king == (100, 100):
            return True

        # King in an escape tile?
        if self.grid[self.king].type == CellType.ESCAPE:
            return True

        king_r, king_c = self.king
        black_king_neighbors = 0
        borders_castle = 0

        # Count how many blacks borders the kings
        # and "how many castles" (either 0 or 1, obv)
        neighbors = [(king_r-1,king_c),(king_r+1,king_c),(king_r,king_c-1),(king_r,king_c+1)]
        for n in neighbors:
            r,c = n
            if 0 <= r <= 8 and 0 <= c <= 8:
                is_black = self.grid[r,c].checker == CheckerType.BLACK
                is_castle = self.grid[r,c].type == CellType.CASTLE
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

        return False

    def copy(self):
        """
        Create a DEEP copy of the board

        :return: a Board object with the same state as self
        """

        board_copy = Board()

        for i in range(9):
            for j in range(9):
                board_copy.grid[i,j] = self.grid[i,j].copy()

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
        checker_to_move = self.grid[start_r, start_c].checker
        dest_cell_checker = self.grid[destination_r, destination_c].checker

        # Innanzitutto, la cella di destinazione deve essere vuota
        if dest_cell_checker != CheckerType.EMPTY:
            return False

        dest_cell_type = self.grid[destination_r, destination_c].type

        if checker_to_move == CheckerType.WHITE:
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
