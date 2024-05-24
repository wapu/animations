import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    import pygame.draw
import numpy as np

from time import time


from pygame_test import Test
from pygame_swarm import Swarm
from pygame_maze import Maze
from pygame_birds import Bird_1, Bird_2
from pygame_tower import Tower
from pygame_faltr import Faltr
from pygame_matrix import Matrix
from pygame_uebeldumm import UebelDumm
from pygame_spotlights import Spotlights


# Constants
WIDTH = 1920
HEIGHT = 1080
FPS = 30


# Pygame setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()
pygame.font.init()
font = pygame.font.SysFont('CMU Sans Serif', 25)


# Initialize animations
animations = [
        # Test(WIDTH, HEIGHT),
        # Swarm(WIDTH, HEIGHT),
        # Maze(WIDTH, HEIGHT),
        # Bird_1(WIDTH, HEIGHT),
        # Bird_2(WIDTH, HEIGHT),
        # Tower(WIDTH, HEIGHT),
        # Faltr(WIDTH, HEIGHT),
        # Matrix(WIDTH, HEIGHT),
        # UebelDumm(WIDTH, HEIGHT),
        Spotlights(WIDTH, HEIGHT),
    ]
current = -1


# Main loop prep
done = False
bpm = 164
brightness = 1.0
beats = []
last_beat = time()
typed = ''
last_typed = 0
show_fps = True


# Main loop
while not done:
    # Check events
    for e in pygame.event.get():
        if e.type == pygame.KEYDOWN:
            # Quit
            if e.key in [pygame.K_ESCAPE, pygame.K_q]:
                done = True
                break
            # Get BPM from key presses
            elif e.key == pygame.K_b:
                beats.append(time())
                last_beat = beats[-1]
                if len(beats) > 1:
                    if beats[-1] - beats[-2] > 1.5:
                        beats = beats[-1:]
                if len(beats) >= 8:
                    s_per_beat = (beats[-1] - beats[0]) / (len(beats) - 1)
                    bpm = np.round(60/s_per_beat,1)
            # Get BPM as digits
            elif e.key in [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                if time() - last_typed > 1:
                    typed = ''
                last_typed = time()
                typed += e.unicode
                if 48 <= int(typed) <= 300:
                    bpm = int(typed)
                    typed = ''
            # Reset current animation
            elif e.key == pygame.K_r:
                animations[current].reset()
            # Toggle FPS display
            elif e.key == pygame.K_f:
                show_fps = not show_fps
            # BPM +1
            elif e.key == pygame.K_UP:
                if e.mod & pygame.KMOD_SHIFT:
                    bpm += 10
                elif e.mod & pygame.KMOD_CTRL:
                    bpm += 0.1
                elif e.mod & pygame.KMOD_ALT:
                    bpm *= 2
                else:
                    bpm += 1
                last_beat = time()
            # BPM -1
            elif e.key == pygame.K_DOWN:
                if e.mod & pygame.KMOD_SHIFT:
                    bpm -= 10
                elif e.mod & pygame.KMOD_CTRL:
                    bpm -= 0.1
                elif e.mod & pygame.KMOD_ALT:
                    bpm = np.round(bpm/2, 1)
                else:
                    bpm -= 1
                last_beat = time()
            # Next animation
            elif e.key == pygame.K_RIGHT:
                current = (current + 1) % len(animations)
                last_beat = time()
                animations[current].reset()
            # Previous animation
            elif e.key == pygame.K_LEFT:
                current = (current - 1) % len(animations)
                last_beat = time()
                animations[current].reset()
            # Increase brightness
            elif e.key == pygame.K_KP_PLUS:
                if e.mod & pygame.KMOD_SHIFT:
                    brightness = np.minimum(1, brightness + 0.1)
                else:
                    brightness = np.minimum(1, brightness + 0.01)
            # Decrease brightness
            elif e.key == pygame.K_KP_MINUS:
                if e.mod & pygame.KMOD_SHIFT:
                    brightness = np.maximum(0.1, brightness - 0.1)
                else:
                    brightness = np.minimum(0.1, brightness - 0.01)
            # Special event
            elif e.key in [pygame.K_RETURN, pygame.K_SPACE]:
                animations[current].event()


    # Update animation
    delta_t = clock.tick(FPS) / 1000
    t = time()
    animations[current].update(bpm, last_beat, delta_t)

    # Draw
    animations[current].clear_frame(screen)
    screen.blit(font.render(f'{bpm:.1f} bpm', False, (5,5,5)), (10, HEIGHT - 35))
    text_width = font.size(f'{100*brightness:.0f} %')[0]
    screen.blit(font.render(f'{100*brightness:.0f} %', False, (5,5,5)), (WIDTH - 10 - text_width, HEIGHT - 35))
    animations[current].draw(screen, bpm, last_beat, brightness)
    if show_fps:
        pygame.draw.rect(screen, (0,0,0), pygame.Rect(0, 0, 105, 40))
        screen.blit(font.render(f'{1/(time() - t):.1f} fps', False, (5,5,5)), (10, 5))
    pygame.display.update()
