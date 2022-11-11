import sys

import pygame as pg
import pygame.draw as pgdraw
import pygame.math as pgmath

from board import Board, CellType, CheckerType

SCREEN_SIZE = pgmath.Vector2(540,540)
grid_size = pgmath.Vector2(9,9)
cell_side = pgmath.Vector2(SCREEN_SIZE.x/grid_size.x,
                           SCREEN_SIZE.y/grid_size.y)

b = Board()

def on_event(event):
    # exit program when quit event is sent
    if event.type == pg.QUIT or (event.type == pg.KEYUP and event.key == pg.K_ESCAPE):
        sys.exit(0)

def draw(screen):
    screen.fill(color="black")

    for r in range(9):
        for c in range(9):
            rect = pg.Rect(r*cell_side.x,
                         c*cell_side.y,
                         cell_side.x,
                         cell_side.y)

            col = "#ddeb5e"
            if b.grid[r, c].type == CellType.ESCAPE:
                col = "#8c4408"
            if b.grid[r, c].type == CellType.CASTLE:
                col = "#ac000e"
            if b.grid[r, c].type == CellType.CAMP:
                col = "#101010"
            pgdraw.rect(screen, color=col, rect=rect)

            if b.grid[r, c].checker != CheckerType.EMPTY:
                match b.grid[r, c].checker:
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

                pgdraw.circle(screen, color=outer_col, center=(rect.x + cell_side.x / 2, rect.y + cell_side.y / 2),
                              radius=radius + stroke_w)
                pgdraw.circle(screen, color=inner_col, center=(rect.x + cell_side.x / 2, rect.y + cell_side.y / 2),
                              radius=radius)

            # pgdraw.rect(screen, color="#cdcdcd",width=1,rect=rect)

    pg.display.flip()

def main():
    pg.init()
    screen = pg.display.set_mode((SCREEN_SIZE.x, SCREEN_SIZE.y))
    pg.display.set_caption("PyTablut")

    # main loop
    while True:
        # event handling, gets all event from the event queue
        for event in pg.event.get():
            on_event(event)

        draw(screen)

if __name__ == "__main__":
    main()
