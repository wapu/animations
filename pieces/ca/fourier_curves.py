import contextlib
with contextlib.redirect_stdout(None):
    import pygame.draw
import numpy as np

from colors import *



def generate_harmonics(symmetry, n_harmonics):
    fibonacci = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]

    harmonics = []
    even = True
    m = 1

    for i in range(n_harmonics):
        k = 1

        if i != 0:
            k = m * symmetry
            if even:
                k += 1
                m += 1
            else:
                k -= 1
        even = not even

        a_x = fibonacci[n_harmonics - i] / fibonacci[n_harmonics]
        p_x = 2*np.pi * fibonacci[np.random.randint(n_harmonics)] / fibonacci[n_harmonics]

        a_y = a_x
        if (k-1) % symmetry == 0:
            p_y = p_x - np.pi/2
        else:
            p_y = p_x + np.pi/2

        harmonics.append([k, a_x, p_x, a_y, p_y])

    return np.array(harmonics)


def get_shape_from_harmonics(harmonics, n_points=1000):
    # "Lopez"
    points = []
    t_delta = 2*np.pi / n_points

    for t in np.linspace(0, 2*np.pi, n_points, endpoint=True):
        x, y = 0, 0

        for k, a_x, p_x, a_y, p_y in harmonics:
            x += a_x * np.cos(t * k + p_x)
            y += a_y * np.cos(t * k + p_y)

        points.append(np.array([x, y]))

    return np.array(points) * 180


def hermite(x):
    return 3*x**2 - 2*x**3



class FourierCurves():

    def __init__(self, width, height):
        self.center = np.array([width/2, height/2])
        self.WH = np.array([width, height])

        # Animation parameters
        self.n_points = 1000
        self.symmetries = [9,12,15,25]
        self.n_harmonics = 9
        self.zoom = 1.06

        # Extra surface for darkening background layers
        self.darkener = pygame.Surface((width, height + 30))

        self.reset()


    def reset(self):
        # Init variables
        self.intensity = 0
        self.beats = 0
        self.beats_per_harmonic = 8
        self.flash = 0
        self.clear = False
        self.waterfall_target = 0
        self.waterfall = 0

        # Fourier series coefficients
        self.old_symmetry = np.random.choice(self.symmetries)
        self.old_harmonics = generate_harmonics(self.old_symmetry, self.n_harmonics)
        self.new_symmetry = np.random.choice(self.symmetries)
        self.new_harmonics = generate_harmonics(self.new_symmetry, self.n_harmonics)

        # Initial Fourier curve
        self.curve = get_shape_from_harmonics(self.old_harmonics)
        self.curve = self.center + self.curve


    def event(self, num):
        match num:
            case 0:
                self.symmetries = [9,12,15,25]
            case 1:
                self.flash = 1
            case 2:
                self.clear = True
            case 3:
                self.symmetries = [3]
            case 4:
                self.waterfall_target = 1 - self.waterfall_target
            case 5:
                self.symmetries = [5]
            case 6:
                self.symmetries = [6]
            case 7:
                self.symmetries = [7]
            case 8:
                self.symmetries = [8]
            case 9:
                self.symmetries = [9]


    def clear_frame(self, screen):
        # Fully clear screen if clear event has been triggered
        if self.clear:
            screen.fill((0,0,0))
            self.clear = False

        # Apply some percentage of darkening to previous frame
        # alpha goes from 0 to 255
        self.darkener.set_alpha(32 - 8 * self.intensity)
        screen.blit(self.darkener, (0,0))

        # Zoom in on previous frame
        # Stretch horizontally if in waterfall mode
        prev_frame = pygame.transform.smoothscale_by(screen, (self.zoom + 0.05 * self.waterfall, self.zoom))
        W, H = prev_frame.get_size()

        # Use darkened and zoomed previous frame as background for new frame
        # In waterfall mode, paste somewhat lower and fill top of screen black
        # Careful, HARDCODED 30 pixels at the bottom (see stage/info area)
        screen.blit(prev_frame, (0, int(50*self.waterfall)), area=pygame.Rect((W - self.WH[0])//2, (H - self.WH[1] - 30)//2, self.WH[0], self.WH[1] + 30))
        if int(50*self.waterfall) > 0:
            screen.fill((0,0,0), rect=pygame.Rect(0, 0, W, int(50*self.waterfall)))


    def beat(self, t):
        self.beats += 1
        if self.beats == self.beats_per_harmonic//2:
            self.old_symmetry = self.new_symmetry
            self.new_symmetry = np.random.choice(self.symmetries)
        # Generate new harmonics and start transition after fixed number of beats
        if self.beats >= self.beats_per_harmonic:
            self.beats = 0
            self.old_harmonics = self.new_harmonics
            self.new_harmonics = generate_harmonics(self.new_symmetry, self.n_harmonics)


    def measure(self, t):
        pass


    def update(self, t, beat_progress, measure_progress, bpm):
        beat_cos = 0.5 - 0.5*np.cos(2*np.pi * beat_progress)

        # Interpolate between previous and next set of harmonics
        p = hermite(hermite((self.beats + beat_progress) / self.beats_per_harmonic))
        harmonics = (1 - p) * self.old_harmonics + p * self.new_harmonics

        # Compute coordinates of Fourier curve
        curve = get_shape_from_harmonics(harmonics, self.n_points)
        curve = curve * (0.9 + (0.3 - 0.2*self.waterfall) * beat_cos * (0.25 + 0.25 * self.intensity))

        # Compute coordinates of projected curve in waterfall mode
        falling_curve = np.array(curve)
        falling_curve[:,0] = falling_curve[:,0] * (1 + 0.6 * falling_curve[:,1]/self.WH[1])
        falling_curve[:,1] = falling_curve[:,1] * (0.4 + 0.3 * falling_curve[:,1]/self.WH[1])
        falling_curve[:,1] = falling_curve[:,1] - (0.2 + 0.05 * beat_cos * (1 + self.intensity)/3) * self.WH[1]

        # Interpolate between normal and waterfall mode coordinates
        self.curve = self.center + self.waterfall * falling_curve + (1 - self.waterfall) * curve

        # Decay flash event and anneal to waterfall mode target
        self.flash *= 0.9
        self.waterfall = 0.95 * self.waterfall + 0.05 * self.waterfall_target


    def draw(self, screen, brightness, t, beat_progress, measure_progress):
        beat_cos = 0.5 - 0.5*np.cos(2*np.pi * beat_progress + np.pi)

        # Area within
        if self.intensity <= 1:
            fill = np.zeros(3)
        elif self.intensity == 2:
            fill = hls_to_rgb(0.25 * t - 0.2, 0.003 * beat_cos + 0.02 * self.flash)
        else:
            fill = hls_to_rgb(0.25 * t - 0.2, 0.005 * beat_cos + 0.03 * self.flash)
        pygame.draw.polygon(screen, fill * brightness, self.curve)

        # Fourier curve
        if self.intensity == 0:
            color = hls_to_rgb(0.25 * t, 0.2 - 0.1 * beat_cos + 0.4 * self.flash)
            pygame.draw.lines(screen, color * brightness, False, self.curve, width=2)
        else:
            if self.intensity == 1:
                color = hls_to_rgb(0.25 * t, 0.5 - 0.2 * beat_cos + (0.5 + 0.2 * beat_cos) * self.flash)
            elif self.intensity == 2:
                color = hls_to_rgb(0.25 * t, 0.5 - 0.4 * beat_cos + (0.5 + 0.4 * beat_cos) * self.flash)
            elif self.intensity == 3:
                color = hls_to_rgb(0.25 * t, 0.4 - 0.3 * beat_cos + (0.5 + 0.4 * beat_cos) * self.flash)
            pygame.draw.lines(screen, color * brightness, False, self.curve, width=int(1 + 1.5 * self.flash))

        # Pearls
        d = np.sqrt(np.sum(np.square(self.curve - self.center), axis=1))
        d_max = d.max()
        for i in np.linspace(0, self.n_points, 3*self.old_symmetry, endpoint=False).round().astype(int):
        # for point in self.curve[::self.n_points//(self.old_symmetry)]:
            color = hls_to_rgb(0.25 * t, (0.2 + 0.6 * beat_cos) * (0.4 + 0.6 * d[i]/d_max), 0.6)
            pygame.draw.circle(screen, color * brightness, self.curve[i], radius=1 + self.intensity/3 + 2*self.flash)
