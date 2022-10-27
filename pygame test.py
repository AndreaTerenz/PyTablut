import sys
import pygame as pg
import pygame.math as pgmath
import pygame.draw as pgdraw
import pygame.mouse as pgmouse
from icecream import ic

from board import Board, CellType

SCREEN_SIZE = pgmath.Vector2(540,540)
grid_size = pgmath.Vector2(9,9)
cell_side = pgmath.Vector2(SCREEN_SIZE.x/grid_size.x,
                           SCREEN_SIZE.y/grid_size.y)

b = Board()

def on_event(event):
    # exit program when quit event is sent
    if event.type == pg.QUIT:
        sys.exit(0)

def draw(screen):
    screen.fill(color="black")

    for r in range(9):
        for c in range(9):
            rect = pg.Rect(r*cell_side.x,
                         c*cell_side.y,
                         cell_side.x,
                         cell_side.y)

            col = "#d8eb34"
            if b.grid[r,c].type == CellType.ESCAPE:
                col = "#8c4408"
            if b.grid[r,c].type == CellType.CASTLE:
                col = "#EE0000"
            if b.grid[r,c].type == CellType.CAMP:
                col = "#101010"
            pgdraw.rect(screen, color=col,rect=rect)

            pgdraw.rect(screen, color="#EEEEEE",width=1,rect=rect)

    mouse_pos = list(pgmouse.get_pos())

    def round_to_multiple(n,m):
        return m*round(n/m)

    mouse_pos[0] = (round_to_multiple(mouse_pos[0], cell_side.x/2))
    mouse_pos[1] = (round_to_multiple(mouse_pos[1], cell_side.y/2))
    ic(mouse_pos)

    pgdraw.circle(screen,
                  color="white",
                  center=mouse_pos,
                  radius=20)

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
