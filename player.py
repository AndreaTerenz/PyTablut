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
        move = None
        if self.role == "WHITE":
            move = self.play_white()
        elif self.role == "BLACK":
            move = self.play_black()

        self.board.send_move(move)

    @abstractmethod
    def play_black(self):
        pass

    @abstractmethod
    def play_white(self):
        pass

class RandomPlayer(BasePlayer):
    def play_random(self, check_fn):
        """
        Play a random move given your role

        :param check_fn: returns whether a certain move is valid
        :return: a move
        """

        # Get the list of your checkers
        other_checkers = self.board.whites if self.role == "WHITE" else self.board.blacks
        random_checker = (rnd.choice(other_checkers))
        r = random_checker[0]
        c = random_checker[1]
        ic(r,c)
        moves = []

        # Explore left
        for j in range(c-1,-1,-1):
            if check_fn(r,j,r,c):
                moves.append((r,j))
            else:
                break
        # Explore right
        for j in range(c + 1, 9):
            if check_fn(r,j,r,c):
                moves.append((r,j))
            else:
                break
        # Explore up
        for i in range(r - 1, -1, -1):
            if check_fn(i,c,r,c):
                moves.append((i,c))
            else:
                break
        # Explore down
        for i in range(r + 1, 9):
            if check_fn(i,c,r,c):
                moves.append((i,c))
            else:
                break
        ic(moves)
        return ic(rnd.choice(moves))

    def play_black(self):
        # Scegli pedina bianca a caso X
        # Prendi lista mosse possibili per X
        # Scegli a caso mossa per X
        def check_cell_black(move_r, move_c, cell_r, cell_c):
            cell_type = self.board.grid[move_r, move_c].type
            checker = self.board.grid[move_r, move_c].checker

            if self.board.grid[cell_r, cell_c].type == CellType.CAMP:
                # Deve essere VUOTA
                # Non puo' essere il CASTLE
                return checker == CheckerType.EMPTY and cell_type != CellType.CASTLE
            else:
                return checker == CheckerType.EMPTY and cell_type in [CellType.NORMAL, CellType.ESCAPE]

        return self.play_random(check_cell_black)

    def play_white(self):
        def check_cell_white(move_r, move_c, cell_r, cell_c):
            cell_type = self.board.grid[move_r, move_c].type
            checker = self.board.grid[move_r, move_c].checker
            return checker == CheckerType.EMPTY and cell_type in [CellType.NORMAL, CellType.ESCAPE]

        return self.play_random(check_cell_white)