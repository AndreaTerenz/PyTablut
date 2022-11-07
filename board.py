from enum import Enum

import numpy as np
from icecream import ic



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

                    if checker_type == CheckerType.KING:
                        char_to_print = "K"
                    elif checker_type == CheckerType.BLACK:
                        char_to_print = "B"
                    elif checker_type == CheckerType.WHITE:
                        char_to_print = "W"
                    else:
                        # Everything here applies only to EMPTY cells
                        char_to_print = " "
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

                #FIXME: PIVI AGGIORNA PYTHON
                if server_cell == "EMPTY":
                    self.grid[i][j].checker = CheckerType.EMPTY
                elif server_cell == "WHITE":
                    self.grid[i][j].checker = CheckerType.WHITE
                    self.whites.append((i,j))
                elif server_cell == "BLACK":
                    self.grid[i][j].checker = CheckerType.BLACK
                    self.blacks.append((i, j))
                elif server_cell == "KING":
                    self.grid[i][j].checker = CheckerType.KING
                    self.king = (i,j)

    def apply_move(self, from_cell, to_cell, role):
        """
        Returns a COPY of the board in which a checker has been moved from
        'from_cell' to 'to_cell', checking also if any enemy checkers are taken
        in the process

        :param from_cell:
        :param to_cell:
        :param role:
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

        opponent = (CheckerType.BLACK if role == CheckerType.WHITE else CheckerType.WHITE)

        # riga/colonna devono essere piu' di 1 e meno di 7, perche' ci vogliono
        # due celle di spazio per poter mangiare in ogni direzione (una per la pedina
        # avversaria da mangiare e un altro per la seconda pedina propria da usare per mangiare)

        # caso del re
        row_k, column_k = output.king
        king_neighbors = list()
        king_neighbors.append([output.grid[row_k,column_k - 1], output.grid[row_k - 1,column_k], \
                output.grid[row_k,column_k + 1], output.grid[row_k + 1,column_k]])

        blacks = king_neighbors.count(Cell(CellType.NORMAL, CheckerType.BLACK))
        castles = king_neighbors.count(Cell(CellType.CASTLE, CheckerType.EMPTY))

        if blacks == 4:
            output.king(100,100)
        elif blacks == 3 and castles == 1:
            output.king(100,100)

        if column > 1:
            if output.grid[row, column - 1].checker == opponent:
                if output.grid[row, column - 2].checker == role or output.grid[row, column - 2].type in [CellType.CAMP, CellType.CASTLE]:
                    eaten_checkers.append((row, column - 1))
            if role == CheckerType.BLACK and output.grid[row, column - 1].checker == CheckerType.KING:
                if output.grid[row, column - 2].checker == role or output.grid[row, column - 2].type in [CellType.CAMP, CellType.CASTLE]:
                    self.king = (100,100)


        if column < 7 and output.grid[row, column + 1].checker == opponent:
            if output.grid[row, column + 2].checker == role or output.grid[row, column + 2].type in [CellType.CAMP, CellType.CASTLE]:
                eaten_checkers.append((row, column + 1))
            if role == CheckerType.BLACK and output.grid[row, column - 1].checker == CheckerType.KING:
                if output.grid[row, column + 2].checker == role or output.grid[row, column + 2].type in [CellType.CAMP,CellType.CASTLE]:
                    self.king = (100, 100)

        if row > 1 and output.grid[row - 1, column].checker == opponent:
            if output.grid[row - 2, column].checker == role or output.grid[row - 2, column].type in [CellType.CAMP, CellType.CASTLE]:
                eaten_checkers.append((row - 1, column))
            if role == CheckerType.BLACK and output.grid[row - 1, column].checker == CheckerType.KING:
                if output.grid[row - 2, column].checker == role or output.grid[row - 2, column].type in [CellType.CAMP,CellType.CASTLE]:
                    self.king = (100, 100)

        if row < 7 and output.grid[row + 1, column].checker == opponent:
            if output.grid[row + 2, column].checker == role or output.grid[row + 2, column].type in [CellType.CAMP, CellType.CASTLE]:
                eaten_checkers.append((row + 1, column))
            if role == CheckerType.BLACK and output.grid[row + 1, column].checker == CheckerType.KING:
                if output.grid[row + 2, column].checker == role or output.grid[row + 2, column].type in [CellType.CAMP,CellType.CASTLE]:
                    self.king = (100, 100)

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

    def copy(self):
        board_copy = Board()

        for i in range(9):
            for j in range(9):
                board_copy.grid[i,j] = self.grid[i,j].copy()

        board_copy.whites = self.whites.copy()
        board_copy.blacks = self.blacks.copy()
        board_copy.king = self.king

        return board_copy