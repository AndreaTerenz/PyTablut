from enum import Enum
import numpy as np

class CellType(Enum):
    NORMAL = 0
    CASTLE = 1
    CAMP = 2
    ESCAPE = 3

class CheckerType(Enum):
    EMPTY = 0
    WHITE = 1
    BLACK = 2
    KING = 3

class Cell:
    def __init__(self, _type, _checker):
        self.type = _type
        self.checker = _checker

class Board:
    empty_cell = Cell(CellType.NORMAL, CheckerType.EMPTY)
    def __init__(self):
        self.grid = np.full((9,9), Board.empty_cell)
        self.whites = []
        self.blacks = []
        self.king = (4,4)
        

        self.grid[4,4] = Cell(CellType.CASTLE, CheckerType.KING)

        # Escape cells
        escapes = np.array([(0,1),(0,2),(0,6),(0,7),
                   (1,0),(1,8),
                   (2,0),(2,8),
                   (6,0),(6,8),
                   (7,0),(7,8),
                   (8,1),(8,2),(8,6),(8,7),])

        # Black camps
        self.blacks = np.array([(0,3),(0,4),(0,5),
                 (1,4),
                 (3,0),(3,8),
                 (4,0),(4,1),(4,7),(4,8),
                 (5,0),(5,8),
                 (7,4),
                 (8,3),(8,4),(8,5)])

        self.whites =np.array([(2,4),
                  (3,4),
                  (4,2),(4,3),(4,5),(4,6),
                  (5,4),
                  (6,4)])

        self.grid[escapes[0,:],escapes[1,:]]=Cell(CellType.ESCAPE, CheckerType.EMPTY)
        self.grid[self.blacks[0,:],self.blacks[1:]]=Cell(CellType.CAMP, CheckerType.BLACK)
        self.grid[self.whites[0,:],self.whites[1:]]=Cell(CellType.NORMAL, CheckerType.WHITE)

    def print_grid(self):
        for i in range(9):
            for j in range(9):
                print(f"{self.grid[i][j].type.value};{self.grid[i][j].checker.value} ", end=" ")
            print()

    def update_state(self, server_state):
        """
        Update state grid reading state received from server

        :param server_state: grid state from server
        :return: None
        """
        self.grid[server_state=="EMPTY"].checker=CheckerType.EMPTY
        self.grid[server_state=="WHITE"].checker=CheckerType.WHITE
        i,j=np.where(server_state=="WHITE")
        self.whites=tuple(zip(i,j))
        self.grid[server_state=="BLACK"].checker=CheckerType.BLACK
        i,j=np.where(server_state=="BLACK")
        self.black=tuple(zip(i,j))
        self.grid[server_state=="KING"].checker=CheckerType.KING
        i,j=np.where(server_state=="KING")
        self.king=(int(i),int(j))
        return None

    def send_move(self, move):
        #TODO: Implement sending move to server with UDP
        pass