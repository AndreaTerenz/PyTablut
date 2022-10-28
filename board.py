from enum import Enum
import numpy as np

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

class Board:
    """
    Represents the global state of the game
    """

    empty_cell = Cell(CellType.NORMAL, CheckerType.EMPTY)
    def __init__(self):
        self.grid = np.full((9,9), Board.empty_cell)
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
                    if cell_type == CellType.ESCAPE:
                        char_to_print = "-"

                    if checker_type == CheckerType.KING:
                        char_to_print = "K"
                    elif checker_type == CheckerType.BLACK:
                        char_to_print = "B"
                    elif checker_type == CheckerType.WHITE:
                        char_to_print = "W"

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

    def send_move(self, move):
        #TODO: Actually send move to server
        #NOTE: Maybe don't do this in the Board object and leave it to the main script?
        # This way it doesn't need a reference to the Connection object. Idk seems cleaner
        pass