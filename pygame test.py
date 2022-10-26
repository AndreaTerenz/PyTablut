import sys
import pygame as pg
import pygame.math as pgmath
import pygame.draw as pgdraw

def on_event(event):
    # exit program when quit event is sent
    if event.type == pg.QUIT:
        sys.exit(0)

def draw(screen):
    screen.fill(color="black")

    pgdraw.rect(screen,
                color="red",
                rect=pg.Rect(10, 10, 100, 100))
    pgdraw.circle(screen,
                  color="white",
                  center=pgmath.Vector2(200, 200),
                  radius=20)

    pg.display.flip()

def main():
    pg.init()
    screen = pg.display.set_mode((800, 800))
    pg.display.set_caption("PyTablut")

    # main loop
    while True:
        # event handling, gets all event from the event queue
        for event in pg.event.get():
            on_event(event)

        draw(screen)

if __name__ == "__main__":
    main()
