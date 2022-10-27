#AbstractBaseClasses
from abc import ABC, abstractmethod
from board import Board
from random import choice

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
        random_checker = choice(self.board.whites)


        pass

