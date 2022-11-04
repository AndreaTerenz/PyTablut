import random as rnd
from abc import ABC, abstractmethod

from icecream import ic

from board import CheckerType, CellType


class BasePlayer(ABC):
    """
    Generic player class (abstract). Has functionality to compute the next move based on role
    and to check if a move is valid
    """

    def __init__(self, role, board):
        self.role = role
        self.board = board

        #FIXME: Chiama l'800 6969 per donare un euro alla lotta contro
        # l'uso di CheckerType per indicare il ruolo del player...
        if self.role == "WHITE":
            self.role = CheckerType.WHITE
            self.opponent = CheckerType.BLACK # avversario
        else:
            self.role = CheckerType.BLACK
            self.opponent = CheckerType.WHITE

        self.old_pos = (0, 3)
        self.new_pos = (2, 3)

    def play(self):
        """
        Compute next move based on role

        :return: The computed move
        """

        move = None
        if self.role == CheckerType.WHITE:
            move = self.play_white()
        elif self.role == CheckerType.BLACK:
            move = self.play_black()

        return move

    def check_move(self, destination_r, destination_c, start_r, start_c) -> bool:
        """
        Check if moving a checker from (cell_r,cell_c) to (move_r.move_c) is a valid move

        :param destination_r: destination row
        :param destination_c: destination column
        :param start_r: starting row
        :param start_c: starting column
        :return: True if the move is valid
        """
        dest_cell_checker = self.board.grid[destination_r, destination_c].checker

        # Innanzitutto, la cella di destinazione deve essere vuota
        if dest_cell_checker != CheckerType.EMPTY:
            return False

        dest_cell_type = self.board.grid[destination_r, destination_c].type

        if self.role == CheckerType.WHITE:
            # Deve essere VUOTA
            # Puo' essere una cella NORMAL o una ESCAPE
            return dest_cell_type in [CellType.NORMAL, CellType.ESCAPE]
        elif self.role == CheckerType.BLACK:
            if self.board.grid[start_r, start_c].type == CellType.CAMP:
                # Deve essere VUOTA
                # Non puo' essere il CASTLE
                return dest_cell_type != CellType.CASTLE
            else:
                # Deve essere VUOTA
                # Puo' essere una cella NORMAL o una ESCAPE
                return dest_cell_type in [CellType.NORMAL, CellType.ESCAPE]

    @abstractmethod
    def play_black(self):
        """
        Play black move

        :return: Black's move
        """
        pass

    @abstractmethod
    def play_white(self):
        """
        Play white move

        :return: White's move
        """
        pass

class RandomPlayer(BasePlayer):
    """
    Random player - at every turn, picks a random checker and returns a random move for it
    """

    def play_random(self):
        """
        Play a random move given your role

        :return: a move
        """

        # Get the list of your checkers
        your_checkers = self.board.whites if self.role == CheckerType.WHITE else self.board.blacks
        # shuffle your checkers in a random order
        rnd.shuffle(your_checkers)

        # We loop over the checkers - as soon as we have one
        # with at least one legal move, we return
        for random_checker in your_checkers:
            r = random_checker[0]
            c = random_checker[1]

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
                if self.check_move(r,j,r,c):
                    moves.append((r,j))
                else:
                    break
            # Explore up
            for i in range(r - 1, -1, -1):
                if self.check_move(i,c,r,c):
                    moves.append((i,c))
                else:
                    break
            # Explore down
            for i in range(r + 1, 9):
                if self.check_move(i,c,r,c):
                    moves.append((i,c))
                else:
                    break

            ic(moves)

            if len(moves) > 0:
                output_move = ic(rnd.choice(moves))
                output_start = ic(random_checker)

                self.old_pos = output_start
                self.new_pos = output_move

                return output_start, output_move
            else:
                ic("NO MOVES FOUND")

        # If we get here, there were no legal moves for any checker
        #FIXME: THE FUCK DO WE DO IN THIS CASE?
        ic("If you see me there's a big problem")

    def play_black(self):
        return self.play_random()

    def play_white(self):
        return self.play_random()