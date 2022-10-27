#AbstractBaseClasses
from abc import ABC, abstractmethod
from board import Board, CheckerType, CellType
import random as rnd
from icecream import ic

class BasePlayer(ABC):
    def __init__(self, role, board):
        self.role = role
        self.board = board

    def play(self):
        if self.role == "WHITE":
            self.play_white()
        elif self.role == "BLACK":
            self.play_black()

    @abstractmethod
    def play_black(self):
        pass

    @abstractmethod
    def play_white(self):
        pass

class RandomPlayer(BasePlayer):
    def play_black(self):

        pass

    def play_white(self):
        # Scegli pedina bianca a caso X
        # Prendi lista mosse possibili per X
        # Scegli a caso mossa per X
        def check_cell(_r,_c):
            cell_type = self.board.grid[_r,_c].type
            checker = self.board.grid[_r,_c].checker
            return checker == CheckerType.EMPTY and cell_type in [CellType.NORMAL, CellType.ESCAPE]

        random_checker = (rnd.choice(self.board.whites))
        r = random_checker[0]
        c = random_checker[1]
        ic(r,c)
        moves = []

        # Explore left
        for j in range(c-1,-1,-1):
            if check_cell(r,j):
                moves.append((r,j))
            else:
                break
        # Explore right
        for j in range(c + 1, 9):
            if check_cell(r,j):
                moves.append((r,j))
            else:
                break
        # Explore up
        for i in range(r - 1, -1, -1):
            if check_cell(i,c):
                moves.append((i,c))
            else:
                break
        # Explore down
        for i in range(r + 1, 9):
            if check_cell(i,c):
                moves.append((i,c))
            else:
                break
        ic(moves)
        move = rnd.choice(moves)
        ic(move)