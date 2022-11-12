import sys

import pygame as pg
import pygame.draw as pgdraw
import pygame.math as pgmath

from board import Board, CellType, CheckerType


class GUI:
    SCREEN_SIZE = pgmath.Vector2(7) * 9 * 10
    GRID_SIZE = pgmath.Vector2(9)
    CELL_SIZE = pgmath.Vector2(SCREEN_SIZE.x / GRID_SIZE.x,
                               SCREEN_SIZE.y / GRID_SIZE.y)

    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(GUI.SCREEN_SIZE)
        pg.display.set_caption("StreetKing")

    def on_event(self, event):
        # exit program when quit event is sent
        if event.type == pg.QUIT or GUI.check_key(event, pg.K_ESCAPE):
            sys.exit(0)

    @staticmethod
    def check_key(event, key, state=pg.KEYUP):
        return event.type == state and event.key == key

    def draw(self, board):
        self.screen.fill(color="black")

        for r in range(9):
            for c in range(9):
                rect = pg.Rect(c * GUI.CELL_SIZE.x,
                               r * GUI.CELL_SIZE.y,
                               GUI.CELL_SIZE.x,
                               GUI.CELL_SIZE.y)

                match board.grid[r, c].type:
                    case CellType.ESCAPE:
                        col = "#8c4408"
                    case CellType.CASTLE:
                        col = "#ac000e"
                    case CellType.CAMP:
                        col = "#101010"
                    case _:
                        col = "#ddeb5e"

                pgdraw.rect(self.screen, color=col, rect=rect)

                if board.grid[r, c].checker != CheckerType.EMPTY:
                    match board.grid[r, c].checker:
                        case CheckerType.BLACK:
                            inner_col = "black"
                            outer_col = "white"
                        case CheckerType.KING:
                            inner_col = "red"
                            outer_col = "black"
                        case _:
                            inner_col = "white"
                            outer_col = "black"

                    radius = 0.6 * GUI.CELL_SIZE.x / 2
                    stroke_ratio = 0.1

                    pgdraw.circle(self.screen, color=outer_col,
                                  center=(rect.x + GUI.CELL_SIZE.x / 2, rect.y + GUI.CELL_SIZE.y / 2),
                                  radius=radius * (1 + stroke_ratio))
                    pgdraw.circle(self.screen, color=inner_col,
                                  center=(rect.x + GUI.CELL_SIZE.x / 2, rect.y + GUI.CELL_SIZE.y / 2),
                                  radius=radius)

        pg.display.flip()

    def run(self, board, events=False):
        # main loop
        while True:
            # event handling, gets all event from the event queue
            if events:
                for event in pg.event.get():
                    self.on_event(event)

            self.draw(board)


if __name__ == "__main__":
    gui = GUI()
    gui.run(Board())
