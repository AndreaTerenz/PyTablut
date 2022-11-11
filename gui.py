import sys

import pygame as pg
import pygame.draw as pgdraw
import pygame.math as pgmath

from board import Board, CellType, CheckerType


class GUI:
    SCREEN_SIZE = pgmath.Vector2(540, 540)
    grid_size = pgmath.Vector2(9, 9)
    cell_side = pgmath.Vector2(SCREEN_SIZE.x / grid_size.x,
                               SCREEN_SIZE.y / grid_size.y)

    def __init__(self, b: Board):
        self.board = b

        pg.init()
        self.screen = pg.display.set_mode(GUI.SCREEN_SIZE)
        pg.display.set_caption("PyTablut")

    def on_event(self, event):
        # exit program when quit event is sent
        if event.type == pg.QUIT or (event.type == pg.KEYUP and event.key == pg.K_ESCAPE):
            sys.exit(0)

    def draw(self):
        self.screen.fill(color="black")

        for r in range(9):
            for c in range(9):
                rect = pg.Rect(c * GUI.cell_side.x,
                               r * GUI.cell_side.y,
                               GUI.cell_side.x,
                               GUI.cell_side.y)

                col = "#ddeb5e"
                if self.board.grid[r, c].type == CellType.ESCAPE:
                    col = "#8c4408"
                if self.board.grid[r, c].type == CellType.CASTLE:
                    col = "#ac000e"
                if self.board.grid[r, c].type == CellType.CAMP:
                    col = "#101010"
                pgdraw.rect(self.screen, color=col, rect=rect)

                if self.board.grid[r, c].checker != CheckerType.EMPTY:
                    match self.board.grid[r, c].checker:
                        case CheckerType.BLACK:
                            inner_col = "black"
                            outer_col = "white"
                        case CheckerType.KING:
                            inner_col = "red"
                            outer_col = "black"
                        case _:
                            inner_col = "white"
                            outer_col = "black"

                    radius = 20
                    stroke_w = 2

                    pgdraw.circle(self.screen, color=outer_col,
                                  center=(rect.x + GUI.cell_side.x / 2, rect.y + GUI.cell_side.y / 2),
                                  radius=radius + stroke_w)
                    pgdraw.circle(self.screen, color=inner_col,
                                  center=(rect.x + GUI.cell_side.x / 2, rect.y + GUI.cell_side.y / 2),
                                  radius=radius)

                # pgdraw.rect(screen, color="#cdcdcd",width=1,rect=rect)

        pg.display.flip()

    def run(self, events=False):
        # main loop
        while True:
            # event handling, gets all event from the event queue
            if events:
                for event in pg.event.get():
                    self.on_event(event)

            self.draw()


if __name__ == "__main__":
    gui = GUI(Board())
    gui.run()
