from board import Board, CheckerType, CellType, Cell
import random as rnd
from abc import ABC, abstractmethod
import numpy as np # forse qui non necessario boooooooh
from icecream import ic


class BasePlayer(ABC):
    """
    Generic player class (abstract). Has functionality to compute the next move based on role
    and to check if a move is valid
    """

    def __init__(self, role, board):
        self.role = role
        self.board = board

        if(self.role == "WHITE"):
            self.role = CheckerType.WHITE
            self.opponent = CheckerType.BLACK # avversario
        else:
            self.role = CheckerType.BLACK
            self.opponent = CheckerType.WHITE

        self.chosen_checker =()
        self.chosen_move = (2,3)

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

        self.board.send_move(move)

        return move

    def check_move(self, move_r, move_c, cell_r, cell_c) -> bool:
        """
        Check if moving a checker from (cell_r,cell_c) to (move_r.move_c) is a valid move

        :param move_r: destination row
        :param move_c: destination column
        :param cell_r: starting row
        :param cell_c: starting column
        :return: True if the move is valid
        """
        dest_cell_checker = self.board.grid[move_r, move_c].checker

        # Innanzitutto, la cella di destinazione deve essere vuota
        if dest_cell_checker != CheckerType.EMPTY:
            return False

        dest_cell_type = self.board.grid[move_r, move_c].type

        if self.role == "WHITE":
            # Deve essere VUOTA
            # Puo' essere una cella NORMAL o una ESCAPE
            return dest_cell_type in [CellType.NORMAL, CellType.ESCAPE]
        elif self.role == "BLACK":
            if self.board.grid[cell_r, cell_c].type == CellType.CAMP:
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

    def self_update(self):
        """
        LAVORA CON UNA COPIA DELLA GRIGLIA, non la griglia originale.
        data la pedina da muovere (self.chosen_checker) e la mossa scelta (self.chosen_move),
        mette la pedina nella nuova posizione, controlla il suo vicinato per vedere se c'è
        da mangiare e nel caso mangia.
        In pratica crea una nuova griglia con lo stato aggiornato.
        In più calcola l'euristica (con una funzione che è ancora da implementare).
        Ritorna la copia della griglia aggiornata e il valore della funzione euristica.

        :param None
        :return: the updated copy of the board
        """
        board_copy = self.board.copy()

        ciao = board_copy.grid[self.chosen_checker].checker
        board_copy.grid[self.chosen_checker].checker = CheckerType.EMPTY #tolgo il checker dalla posizione vecchia
        board_copy.print_grid()
        board_copy.grid[self.chosen_move].checker = ciao #metto il checker nella nuova posizione

        ic(board_copy.grid[self.chosen_move].checker)
        ic(board_copy.grid[(0,0)].checker)
        ic("during function state #2: ")
        board_copy.print_grid()
        # for i in range(9):
        #     for j in range(9):
        #         print(f"{board_copy.grid[i][j].type.value};{board_copy.grid[i][j].checker.value} ", end=" ")
        #     print()

        def Eat(board_copy):
            """
            Funzione per mangiare le pedine. Dato il checker spostato nella nuova posizione
            (indicizzata da chosen_move), controlla il suo vicinato. Se nel vicinato ci sono
            pedine dell'avversario, allora controlla la pedina vicina a tali pedine sulla stessa
            linea. Se c'è una pedina del colore della pedina che ha appena fatto la mossa, OPPURE
            una casella di tipo CAMP OPPURE la casella CASTLE, la pedina avversaria viene rimossa
            perché viene mangiata.
            """

            # aggiungo tipo un bordo esterno alla board perché sennò ci sono tremila robe in
            # più da scrivere insomma vi spiego dopo (il bordo sono celle EMPTY e NORMAL).
            # funzione di numpy così Pivi è contento
            board_copy.grid = np.pad(board_copy.grid, pad_width=1, mode='constant', constant_values=Cell(CellType.NORMAL, CheckerType.EMPTY))

            row = self.chosen_move[0] + 1
            column = self.chosen_move[1] + 1 #creo ste variabili solo per semplicità di notazione

            # controllo se nel vicinato della pedina ci sono pedine avversarie. Se
            # ci sono controllo sulla stessa linea di vista come ho scritto prima.
            # Se vanno mangiate, setto il CheckerType di quella Cell come EMPTY.

            eaten_checkers = list() #lista delle cordinate delle pedine che verranno mangiate muahahah

            if board_copy.grid[row, column - 1].checker == self.opponent:
                if board_copy.grid[row, column - 2].checker == self.role or board_copy.grid[row, column - 2].type == CellType.CAMP or board_copy.grid[row, column - 2].type == CellType.CASTLE:
                    eaten_checkers.append((row, column - 1))

            if board_copy.grid[row, column + 1].checker == self.opponent:
                if board_copy.grid[row, column + 2].checker == self.role or board_copy.grid[row, column + 2].type == CellType.CAMP or board_copy.grid[row, column + 2].type == CellType.CASTLE:
                    eaten_checkers.append((row, column + 1))
                    print("ciao chiaren")

            if board_copy.grid[row - 1, column].checker == self.opponent:
                if board_copy.grid[row - 2, column].checker == self.role or board_copy.grid[row - 2, column].type == CellType.CAMP or board_copy.grid[row - 2, column].type == CellType.CASTLE:
                    eaten_checkers.append((row - 1, column))

            if board_copy.grid[row + 1, column].checker == self.opponent:
                if board_copy.grid[row + 2, column].checker == self.role or board_copy.grid[row + 2, column].type == CellType.CAMP or board_copy.grid[row + 2, column].type == CellType.CASTLE:
                    eaten_checkers.append((row + 1, column))

            print(f"Eaten checkers: {eaten_checkers}")
            # rimuovo le pedine mangiate
            for coordinate in eaten_checkers:
                board_copy.grid[coordinate].checker = CheckerType.EMPTY

            # ritorno la nuova copia della board aggiornata
            return board_copy

        # ritorno la copia della board aggiornata
        return Eat(board_copy)




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
        your_checkers = self.board.whites if self.role == "WHITE" else self.board.blacks
        # shuffle your checkers in a random order
        rnd.shuffle(your_checkers)

        # We loop over the checkers - as soon as we have one
        # with at least one legal move, we return
        for random_checker in your_checkers:
            r = random_checker[0]
            c = random_checker[1]
            self.chosen_checker = (r, c)
            ic(self.chosen_checker)
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
                output = rnd.choice(moves)
                self.chosen_move = output
                return ic(output)
            else:
                ic("NO MOVES FOUND")

        # If we get here, there were no legal moves for any checker
        #FIXME: THE FUCK DO WE DO IN THIS CASE?
        ic("If you see me there's a big problem")

    def play_black(self):
        return self.play_random()

    def play_white(self):
        return self.play_random()