import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    import pygame.draw
import numpy as np
import json

from time import time


from pygame_swarm import Swarm
from pygame_maze import Maze
from pygame_birds import Bird_1, Bird_2
from pygame_tower import Tower
from pygame_faltr import Faltr
from pygame_matrix import Matrix
from pygame_uebeldumm import UebelDumm
from pygame_spotlights import Spotlights
# from pygame_explosion import Explosion
# from pygame_lo import LO
from pygame_lines import Lines
from pygame_welde import Welde
from pygame_zweizwei import ZweiZwei
from pygame_fireworks import Fireworks
from pygame_snowflakes import Snowflakes
from metaballs import Metaballs
from weave import Weave
from fourier_curves import FourierCurves
from test import Test


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
font = pygame.font.SysFont('Free Mono', 20)


# Load key bindings
with open('keybindings.json') as f:
    keys = json.load(f)
for k in keys.keys():
    keys[k] = pygame.key.key_code(keys[k])


# Initialize animations
animations = [anim(WIDTH, HEIGHT - 30) for anim in [Swarm, Maze, Bird_1, Bird_2, Tower, Faltr, Matrix, UebelDumm, Spotlights, Lines, Welde, ZweiZwei, Fireworks, Snowflakes, Metaballs, Weave, FourierCurves, Test]]
animations = [anim(WIDTH, HEIGHT - 30) for anim in [Swarm, Maze, Bird_1, Bird_2, Tower, Matrix, UebelDumm, Spotlights, Lines, Welde, Metaballs, FourierCurves, Test]]
current = len(animations) - 1


# Main loop prep
done = False
pause = False
status_bar = True
help = False
bpm = 160
t_prev = time()
internal_time = 0
last_beat = 0
last_measure = 0
beats = []
brightness = 1.0
typed = ''
last_typed = 0

# Help panel prep
help_bg = pygame.Surface((800,800))
help_bg.set_alpha(230)
help_bg.fill((0,0,0))
pygame.draw.rect(help_bg, [255]*3, (0,0,800,800), width=1)
text_width = font.size('-- key bindings --')[0]
help_bg.blit(font.render('-- key bindings --', True, [255]*3), (400 - text_width/2, 30))
i = 0
for function, hotkey in keys.items():
    if len(function) > 1:
        text_width = font.size(f'{function}:')[0]
        help_bg.blit(font.render(f'{function}:', True, [255]*3), (400 - text_width - 15, 80 + 28 * i))
        name = pygame.key.name(hotkey)
        if name[0] == '[':
            name = f'numpad {name[1]}'
        help_bg.blit(font.render(name, True, [255]*3), (415, 80 + 28 * i))
        i += 1
help_bg.blit(font.render('to set a specific BPM value, type it out like 1 - 2 - 8', True, [255]*3), (60, 750))


# Main loop
while not done:

    # Handle keyboard inputs
    for e in pygame.event.get():
        if e.type == pygame.KEYDOWN:
            # Get BPM as digits
            if e.key in [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                if time() - last_typed > 1:
                    typed = ''
                last_typed = time()
                typed += e.unicode
                if 48 <= int(typed) <= 300:
                    bpm = float(typed)
                    typed = ''
            # Special effects 0 - 9.fill((0,0,0))
            elif e.key in [pygame.K_KP0, pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4, pygame.K_KP5, pygame.K_KP6, pygame.K_KP7, pygame.K_KP8, pygame.K_KP9]:
                animations[current].event(int(pygame.key.name(e.key)[1:2]))
            # Quit
            elif e.key == keys['exit']:
                if help == True:
                    help = False
                else:
                    done = True
                    break
            # Get BPM from key presses
            elif e.key == keys['synch beat']:
                beats.append(internal_time)
                if len(beats) > 1:
                    if beats[-1] - beats[-2] > 1.5:
                        beats = beats[-1:]
                last_beat = beats[0]
                last_measure = beats[0]
                if len(beats) >= 8:
                    s_per_beat = (beats[-1] - beats[0]) / (len(beats) - 1)
                    bpm = np.round(60/s_per_beat,1)
            # Pause animation
            elif e.key == keys['toggle pause']:
                pause = not pause
            # Toggle status bar
            elif e.key == keys['toggle info']:
                status_bar = not status_bar
            # Toggle help screen
            elif e.key == keys['toggle help']:
                help = not help
            # Reset current animation
            elif e.key == keys['reset animation']:
                animations[current].reset()
                # last_beat = internal_time
            # Increase intensity of current animation
            elif e.key == keys['increase intensity']:
                animations[current].intensity = (animations[current].intensity + 1) % 4
            # Decrease intensity of current animation
            elif e.key == keys['decrease intensity']:
                animations[current].intensity = (animations[current].intensity - 1) % 4
            # BPM increase
            elif e.key == keys['increase bpm']:
                if e.mod & pygame.KMOD_SHIFT:
                    bpm += 10
                elif e.mod & pygame.KMOD_CTRL:
                    bpm += 0.1
                elif e.mod & pygame.KMOD_ALT:
                    bpm *= 2
                else:
                    bpm += 1
                last_beat = internal_time
                last_measure = internal_time
            # BPM decrease
            elif e.key == keys['decrease bpm']:
                if e.mod & pygame.KMOD_SHIFT:
                    bpm -= 10
                elif e.mod & pygame.KMOD_CTRL:
                    bpm -= 0.1
                elif e.mod & pygame.KMOD_ALT:
                    bpm = np.round(bpm/2, 1)
                else:
                    bpm -= 1
                last_beat = internal_time
                last_measure = internal_time
            # Next animation
            elif e.key == keys['next animation']:
                current = (current + 1) % len(animations)
                screen.fill((0,0,0))
                # last_beat = internal_time
                animations[current].reset()
            # Previous animation
            elif e.key == keys['previous animation']:
                current = (current - 1) % len(animations)
                screen.fill((0,0,0))
                # last_beat = internal_time
                animations[current].reset()
            # Increase brightness
            elif e.key == keys['increase brightness']:
                if e.mod & pygame.KMOD_CTRL:
                    brightness = np.minimum(1, brightness + 0.01)
                else:
                    brightness = np.minimum(1, brightness + 0.1)
            # Decrease brightness
            elif e.key == keys['decrease brightness']:
                if e.mod & pygame.KMOD_CTRL:
                    brightness = np.maximum(0, brightness - 0.01)
                else:
                    brightness = np.maximum(0, brightness - 0.1)

    # Bookkeeping
    clock.tick(FPS) / 1000
    t = time()
    t_diff = t - t_prev
    t_prev = t
    if not pause:
        internal_time += t_diff
        beat_interval = 60/bpm
        beat_progress = ((internal_time - last_beat) % beat_interval) / beat_interval
        measure_interval = 4*beat_interval
        measure_progress = ((internal_time - last_measure) % measure_interval) / measure_interval

        # Trigger beat event
        if internal_time - last_beat > beat_interval:
            while internal_time - last_beat > beat_interval:
                last_beat += beat_interval
            animations[current].beat(internal_time)

        # Trigger measure event
        if internal_time - last_measure > measure_interval:
            while internal_time - last_measure > measure_interval:
                last_measure += measure_interval
            animations[current].measure(internal_time)

        # Update animation
        animations[current].update(internal_time, beat_progress, measure_progress, bpm)

        # Draw frame
        animations[current].clear_frame(screen)
        animations[current].draw(screen, brightness, internal_time, beat_progress, measure_progress)

    # Help screen
    if help:
        screen.blit(help_bg, (WIDTH/2 - 400, (HEIGHT - 30)/2 - 400))

    # Status bar
    if status_bar:
        fps = min(999.9, 1/(time() - t))
        pixels = pygame.surfarray.pixels3d(screen)
        light = np.mean(pixels) / 255
        del pixels
        screen.unlock()
        intensity = ['○']*4
        intensity[animations[current].intensity] = '●'
        internal_time_str = f'{int(internal_time)//3600:01d}:{(int(internal_time)//60)%60:02d}:{internal_time%60:05.2f}'

        sep = ' | '
        text = f'bpm {bpm:5.1f} {sep} fps {fps:5.1f} {sep} '
        text += f'anim {current+1:2d}/{len(animations):d} {sep} lvl {"".join(intensity)} {sep} '
        text += f'time {internal_time_str} {sep} '
        text += f'brightness {100*brightness:3.0f} {sep} screen {100*light:4.1f}% {sep} '
        text += f'{animations[current].__class__.__name__[:15]} {sep} '
        text += f'[h] for help'

        pygame.draw.rect(screen, (0,0,0), pygame.Rect(0, HEIGHT - 30, WIDTH, 30))
        screen.blit(font.render(text, False, [15]*3), (15, HEIGHT - 25))

    # Show updates
    pygame.display.update()
