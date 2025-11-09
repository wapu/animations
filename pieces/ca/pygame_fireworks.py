import contextlib
with contextlib.redirect_stdout(None):
    import pygame.draw
import numpy as np

from shapely import geometry as geo
from shapely import intersection, difference

from colors import *



def unit_circle(n_points):
    angles = np.linspace(0, 2*np.pi, n_points, endpoint=False)
    x = np.cos(angles)
    y = np.sin(angles)
    return np.stack([x,y], axis=-1)

def rotate(points, angle):
    c = np.cos(angle)
    s = np.sin(angle)
    r = np.array([[c, -s], [s, c]])
    return np.matmul(points, r)



class Firework():

    def __init__(self, center, hues, t_start):
        # General parameters
        self.center = np.array(center)
        self.hues = hues
        self.t_start = t_start
        self.decay = 1.0
        self.decay_per_s = 0.15 + 0.1 * np.random.rand()
        self.trail_length = np.random.randint(5,15)

        # Initiate particles
        self.n_particles = 30 + np.random.randint(30)
        self.coords = np.tile(self.center, (self.n_particles, 1))
        self.trail = [np.array(self.coords)]
        self.vs = unit_circle(self.n_particles)
        self.vs *= 5 + 20 * np.random.rand(self.n_particles, 1)
        self.vs += np.random.randn(*self.vs.shape)
        self.sizes = 2 + 4 * np.random.rand(self.n_particles)

    def update(self, t, gravity):
        self.vs += np.array([0, gravity])
        self.vs *= 0.9
        self.coords += self.vs
        self.trail.append(np.array(self.coords))
        if len(self.trail) > self.trail_length:
            self.trail = self.trail[-self.trail_length:]

        self.decay = self.decay_per_s**(t - self.t_start)


class Rocket():

    def __init__(self, width, height):
        # Position and velocity
        x = (-0.1 + 1.2 * np.random.rand()) * width
        y = height + 10
        self.coord = np.array([x, y])
        vx = -5 + 10*np.random.rand() - 0.01 * (x - width/2)
        vy = -25 - 12 * np.random.rand()
        self.v = np.array([vx, vy])

        # Color and trail
        self.hue = np.random.rand()
        self.trail = [self.coord]
        self.trail_length = np.random.randint(10,20)

        self.exploded = False

    def update(self, gravity):
        self.v += np.array([0, gravity])
        self.coord += self.v

        # Keep track of trail and cut if too long
        self.trail.append(np.array(self.coord))
        if len(self.trail) > self.trail_length:
            self.trail = self.trail[-self.trail_length:]



class Fireworks():

    def __init__(self, width, height):
        self.W = width
        self.H = height
        self.pole = np.array([self.W/2, 0.9 * self.H])

        # Prepare Mietshäuser-Syndikat skyline polygon
        self.skyline = np.array([[0.0, 14.43], [0.90319951, 14.43], [1.0505995, 10.054], [1.1905995, 4.101], [4.6962995, 4.027], [8.2019995, 3.953], [8.2019995, 16.033], [8.5194995, 16.351], [8.8369995, 16.668], [10.3428, 16.668], [10.9848, 16.026], [11.6269, 15.384], [12.3942, 13.844], [13.7637, 11.191], [14.4252, 10.314], [14.8166, 9.989], [14.8166, 10.308], [15.6893, 11.729], [17.0699, 13.819], [17.5777, 14.807], [17.8092, 14.575], [18.0407, 14.344], [18.1238, 12.397], [18.2315, 9.326], [18.2562, 8.202], [19.05, 8.202], [19.0539, 12.369], [19.0578, 16.536], [19.3912, 17.198], [19.7247, 17.859], [20.3145, 17.944], [20.9044, 18.028], [21.0866, 17.547], [22.2757, 15.61], [23.2826, 14.155], [23.2829, 13.427], [23.2833, 12.7], [30.9562, 12.7], [30.9562, 11.278], [31.11194, 9.077], [31.26769, 8.298], [34.08851, 8.399], [37.21041, 8.596], [37.51149, 8.692], [37.44963, 12.532], [37.38778, 16.372], [37.58199, 16.687], [37.77621, 17.001], [38.031127, 16.843], [38.743676, 15.42], [39.483684, 13.41], [39.766061, 12.665], [40.09227, 13.013], [41.15911, 15.081], [42.09157, 17.014], [42.40629, 17.368], [42.71606, 17.462], [43.03403, 17.462], [44.07272, 16.378], [45.59562, 14.857], [46.70989, 13.846], [47.33994, 13.273], [47.91651, 13.424], [50.2418, 14.724], [52.189, 15.874], [52.3875, 15.875], [52.4212, 10.252], [52.4998, 4.629], [52.5934, 3.654], [52.7557, 3.221], [52.9351, 2.931], [56.0347, 2.987], [59.1343, 3.042], [59.2666, 8.728], [59.3989, 14.413], [59.8964, 14.508], [60.3938, 14.604], [60.5716, 14.316], [60.7493, 14.029], [60.8178, 8.673], [60.8863, 3.318], [61.1649, 3.146], [61.4434, 2.974], [65.2279, 3.008], [69.0124, 3.042], [69.2162, 3.246], [69.4201, 3.45], [69.4366, 10.258], [69.4531, 17.065], [71.3052, 17.065], [71.3478, 15.61], [71.5743, 10.632], [71.7581, 7.109], [72.4577, 7.154], [74.6786, 7.171], [76.2, 7.143], [76.2, 4.057], [76.3737, 3.883], [76.5475, 3.709], [78.8211, 5.919], [83.2776, 10.195], [85.4604, 12.261], [85.4604, 13.229], [84.402, 13.229], [84.402, 18.256], [85.3281, 18.256], [86.3512, 15.676], [87.7402, 12.263], [88.1062, 11.047], [88.1062, 10.665], [88.5692, 10.252], [89.0322, 9.839], [94.6546, 9.719], [100.277, 9.598], [100.277, 13.008], [100.6078, 12.899], [101.2653, 12.15], [101.5922, 11.509], [101.5961, 9.459], [101.6, 7.408], [102.1291, 7.408], [102.1291, 11.417], [102.8141, 10.603], [103.4991, 9.789], [104.2458, 9.789], [104.2458, 10.094], [105.449, 12.872], [106.6523, 15.346], [107.6854, 15.346], [107.6854, 7.422], [108.8098, 7.454], [110.6524, 7.447], [111.3704, 7.408], [111.4461, 4.828], [111.5218, 2.249], [116.8135, 2.249], [116.8901, 4.576], [116.9667, 6.903], [117.37, 7.058], [117.7733, 7.213], [118.3517, 6.944], [118.9302, 6.675], [119.4593, 5.653], [120.4289, 4.141], [120.8693, 3.653], [121.4872, 4.735], [122.1052, 5.816], [126.8015, 5.818], [131.4979, 5.82], [131.494, 6.813], [131.4901, 7.805], [131.1632, 8.37], [130.0686, 10.181], [129.3008, 11.428], [129.6717, 11.663], [130.0427, 11.898], [131.6963, 11.902], [133.35, 11.906], [133.35, 17.198], [133.593, 17.198], [134.3702, 16.333], [135.5824, 14.832], [136.2604, 13.959], [137.4927, 12.295], [138.725, 10.868], [138.9477, 11.006], [139.1707, 11.541], [139.9947, 13.64], [140.5947, 14.81], [140.9367, 15.255], [141.1497, 13.952], [141.2607, 10.939], [141.2877, 8.78], [141.8167, 8.919], [142.3457, 9.057], [142.3457, 19.579], [143.8297, 19.579], [144.6877, 18.19], [148.1907, 12.232], [149.3087, 10.308], [149.6797, 9.778], [149.9627, 10.118], [151.3127, 12.287], [152.3817, 14.115], [152.5187, 13.738], [152.7267, 10.873], [152.7967, 8.386], [153.3267, 8.305], [153.8557, 8.225], [153.7897, 12.381], [153.8637, 17.142], [154.0027, 17.748], [154.2687, 17.584], [156.1017, 15.258], [157.9137, 12.811], [158.8537, 11.422], [159.4807, 10.564], [159.7377, 10.383], [159.9827, 10.378], [160.5147, 10.921], [161.2347, 12.246], [161.9997, 13.777], [162.2927, 13.68], [162.5867, 13.583], [162.6627, 11.138], [162.7387, 8.694], [163.0597, 8.8], [163.3797, 8.906], [163.5217, 13.395], [163.6637, 17.883], [164.3057, 18.797], [165.3207, 19.987], [165.7527, 20.269], [166.1637, 20.364], [166.5667, 20.373], [168.2227, 18.388], [169.8787, 16.404], [175.9167, 16.404], [176.1267, 16.073], [176.3497, 15.291], [176.4367, 12.634], [176.4767, 10.583], [178.8747, 10.583], [179.0137, 10.945], [179.2037, 13.922], [179.2547, 16.536], [180.8747, 16.614], [182.4947, 16.692], [182.6567, 16.085], [182.8197, 15.478], [182.8237, 10.44], [182.8267, 5.402], [183.6867, 5.451], [186.7187, 5.528], [188.8897, 5.556], [188.9677, 7.604], [189.0447, 9.651], [189.5357, 9.745], [190.0267, 9.839], [190.3147, 9.551], [190.6017, 9.264], [190.8817, 5.359], [191.1617, 1.455], [199.8927, 1.455], [199.9477, 5.953], [200.0137, 13.03], [200.0247, 15.61], [201.0837, 15.61], [201.1147, 13.956], [201.1147, 12.104], [201.0837, 11.906], [203.4647, 11.906], [203.4677, 10.781], [203.6327, 9.055], [203.7947, 8.453], [207.0687, 8.484], [210.3437, 8.515], [210.3437, 17.236], [210.7557, 17.151], [211.1677, 17.065], [211.7537, 15.61], [212.7097, 13.022], [213.0797, 11.889], [213.3017, 12.228], [214.2137, 14.75], [215.0717, 16.932], [216.1437, 16.337], [217.4787, 15.478], [220.3977, 13.236], [220.9027, 13.016], [221.2757, 12.936], [221.4317, 13.15], [223.5247, 14.91], [225.4607, 16.456], [225.6327, 16.284], [225.8047, 16.112], [225.8617, 9.842], [225.9177, 3.572], [229.7677, 3.498], [233.6177, 3.425], [233.6887, 10.113], [233.7597, 16.801], [234.3507, 16.885], [234.9417, 16.969], [235.0117, 9.212], [235.0827, 1.455], [238.8577, 1.381], [242.6337, 1.308], [242.7387, 1.646], [243.0147, 8.599], [243.2347, 15.875], [243.2847, 16.536], [244.1447, 16.619], [245.0037, 16.702], [245.0367, 12.584], [245.0937, 8.603], [245.1567, 8.04], [245.2687, 7.859], [247.6077, 7.573], [250.0557, 7.261], [250.2957, 7.112], [250.2957, 3.735], [250.5467, 3.58], [250.7987, 3.424], [251.1177, 4.027], [252.8227, 6.536], [255.3887, 9.804], [256.9107, 11.796], [257.3737, 12.331], [257.8367, 12.683], [257.3737, 12.691], [256.9107, 12.7], [256.9107, 17.198], [258.5017, 17.198], [260.4177, 13.295], [262.3347, 9.392], [269.9587, 9.392], [270.5787, 11.232], [271.4567, 13.329], [271.7147, 13.587], [272.2477, 13.104], [273.4897, 11.411], [274.1997, 10.201], [274.3827, 8.606], [274.5647, 7.011], [274.6017, 8.252], [274.6377, 9.493], [274.8787, 9.643], [275.1207, 9.792], [275.6357, 9.085], [276.1507, 8.378], [277.2987, 10.341], [278.9427, 13.321], [279.5177, 14.247], [279.9227, 6.529], [279.9287, 5.253], [280.5247, 5.302], [282.3297, 5.321], [283.5397, 5.291], [283.5017, 2.646], [283.4647, 0.0], [287.8477, 0.0], [287.9227, 2.579], [287.9987, 5.159], [289.7787, 5.237], [291.5587, 5.315], [291.6307, 10.0], [291.7027, 14.684], [292.9907, 14.684], [293.4277, 13.493], [294.1717, 11.559], [294.4807, 10.816], [294.7457, 10.98], [295.0107, 11.515], [295.3747, 13.021], [296.2297, 16.475], [296.7187, 18.794], [302.9417, 18.724], [309.1647, 18.653], [309.6187, 17.727], [310.8097, 15.243], [311.5467, 13.685], [311.8117, 13.662], [312.0757, 13.638], [312.8497, 15.689], [313.6237, 17.74], [313.8897, 17.651], [314.1557, 17.563], [316.0267, 13.811], [318.0287, 10.059], [318.4477, 10.651], [321.0317, 15.346], [322.0287, 17.065], [322.4567, 17.859], [325.4017, 17.934], [328.3477, 18.009], [328.3927, 14.627], [328.4977, 10.848], [328.5847, 8.4], [328.6127, 6.35], [339.7247, 6.35], [339.7247, 22.489], [342.2477, 22.489], [342.2427, 16.923], [342.2387, 11.357], [342.5437, 11.169], [342.8497, 10.98], [347.2407, 10.89], [351.6317, 10.8], [351.6317, 17.991], [351.7747, 17.991], [352.4977, 17.378], [353.3607, 16.014], [354.3537, 14.432], [354.9707, 13.329], [355.1137, 12.757], [356.8117, 12.575], [358.5107, 12.393], [358.5107, 6.879], [357.5137, 6.879], [357.3747, 6.152], [357.2357, 5.425], [357.5427, 5.223], [357.8487, 5.021], [359.1717, 5.09], [360.4947, 5.159], [360.5777, 6.019], [360.6607, 6.879], [359.8337, 6.879], [359.7917, 8.003], [359.8247, 10.614], [360.0147, 12.171], [361.8717, 12.435], [363.6027, 12.567], [364.3267, 14.622], [365.0507, 16.677], [365.5367, 17.214], [366.0217, 17.75], [366.5657, 17.672], [367.1097, 17.594], [367.1807, 11.575], [367.2517, 5.556], [367.9737, 5.536], [369.2257, 5.383], [373.0627, 5.262], [376.3697, 5.272], [377.2837, 5.488], [378.1967, 5.705], [378.2337, 10.062], [378.3117, 14.72], [378.3537, 15.021], [379.1477, 15.137], [379.9417, 15.254], [379.9677, 11.662], [380.0507, 7.54], [380.1577, 6.255], [380.2057, 5.499], [380.5817, 5.643], [384.4847, 5.85], [389.1357, 6.026], [390.2607, 6.141], [390.2607, 14.816], [392.7077, 14.854], [395.8167, 14.908], [396.4777, 14.924], [396.5547, 12.621], [396.6307, 10.318], [397.0837, 10.285], [398.4267, 10.281], [399.3167, 10.311], [399.7347, 10.077], [400.1527, 9.843], [400.1997, 8.195], [400.2477, 6.547], [399.7377, 6.414], [399.2287, 6.281], [399.3087, 5.323], [399.3887, 4.365], [401.6957, 4.289], [404.0027, 4.213], [404.0987, 6.789], [404.2257, 22.952], [404.2837, 48.418], [0.0, 48.418]])
        self.skyline *= self.W / np.max(self.skyline[:,0])
        self.skyline = 1.1 * self.skyline - 0.05 * self.W
        self.skyline[:,1] += 100 + self.H - np.max(self.skyline[:,1])

        # Prepare moon phases
        r = 0.08 * self.H
        full_moon = geo.Point([0,0]).buffer(r)
        waning_gibbous = intersection(full_moon, geo.Point([0, r/3]).buffer(r))
        third_quarter = intersection(full_moon, geo.box(-2*r, 0, 2*r, 2*r))
        waning_crescent = difference(full_moon, geo.Point([0, -r/3]).buffer(r))
        new_moon = geo.box(5*self.W - 1, 5*self.H - 1, 5*self.W + 1, 5*self.H + 1)
        waxing_crescent = difference(full_moon, geo.Point([0, r/3]).buffer(r))
        first_quarter = intersection(full_moon, geo.box(-2*r, 0, 2*r, -2*r))
        waxing_gibbous = intersection(full_moon, geo.Point([0, -r/3]).buffer(r))
        self.moons = [full_moon, waning_gibbous, third_quarter, waning_crescent, new_moon, waxing_crescent, first_quarter, waxing_gibbous]
        self.moons = [m.exterior.coords for m in self.moons]

        self.n_rocket_target = 8

        self.n_stars = 200
        self.sky_rotation = -0.1

        self.reset()


    def reset(self):
        self.intensity = 0
        self.g = 0.55

        self.rockets = []
        self.fireworks = []
        self.skyline_hue = 0
        self.bg_light = 1

        self.star_coords = np.random.rand(self.n_stars, 2) * 2 * ((self.W/2)**2 + self.H**2)**0.5 - self.pole
        self.stars_offset = np.zeros_like(self.star_coords)
        self.star_sizes = 1 + 2 * np.random.rand(self.n_stars)**4
        self.star_colors = [hls_to_rgb(np.random.rand(), 0.7, 0.3) for i in range(self.n_stars)]

        self.moon_coord = np.array([-0.8*self.H, 0])
        self.moon_offset = np.zeros(2)
        self.moon_size = 0.08 * self.H
        self.moon_phase = 0


    def event(self, num):
        match num:
            case 0:
                pass


    def clear_frame(self, screen):
        # screen.fill((0,0,0))
        gradient = pygame.Surface((1,self.H))
        for i in range(self.H//3):
            fade = np.exp(-((i/self.H - 0.01)**2) * 200 * self.bg_light)
            pygame.draw.line(gradient, hls_to_rgb(self.skyline_hue, 0.02 * fade, 0.25), (0, self.H - i), (1, self.H - i))
        screen.blit(pygame.transform.smoothscale(gradient, (self.W, self.H)), (0,0))


    def beat(self, t):
        # Start new fireworks
        eligible = [r for r in self.rockets if (0.05 * self.H < r.coord[1] < 0.6 * self.H)]
        n_explode = np.random.randint(2,5)
        if len(eligible) > n_explode + 1:
            explode = np.random.choice(eligible, n_explode, replace=False)
        elif len(eligible) > 1:
            explode = eligible[:-1]
        else:
            explode = eligible
        for r in explode:
            hues = [(r.hue + 0.1*np.random.randn())%1 for i in range(np.random.randint(2,5))]
            self.fireworks.append(Firework(r.coord, hues, t))
            r.exploded = True

        # Clean up old rockets
        self.rockets = [r for r in self.rockets if (-self.H * 0.2 < r.coord[1] < self.H * 1.2) and not r.exploded]

        # Clean up old fireworks
        self.fireworks = [f for f in self.fireworks if f.decay > 0.1]

        # Shake up the stars :)
        self.stars_offset = 5 * np.random.randn(self.n_stars, 2)
        self.moon_offset = 5 * np.random.randn(2)

        # Progress moon phase
        self.moon_phase = (self.moon_phase + 1) % len(self.moons)


    def measure(self, t):
        pass


    def update(self, t, beat_progress, measure_progress, bpm):
        # Add new rockets, probability depending on how many there are already
        if np.random.rand() < 0.75 * (1 - len(self.rockets) / self.n_rocket_target):
            self.rockets.append(Rocket(self.W, self.H))

        # Move all objects
        for r in self.rockets:
            r.update(self.g)
        for f in self.fireworks:
            f.update(t, self.g)


    def draw(self, screen, brightness, t, beat_progress, measure_progress):
        beat_cos = 0.5 - 0.5*np.cos(2*np.pi * beat_progress + np.pi)
        beat_exp = np.exp(-(beat_progress**2)*6)
        beat_scale = (1 - 0.05 * beat_cos)

        self.skyline_hue = (t/4) % 1
        self.bg_light = 0.5 + 0.5 * beat_cos

        screen.lock()

        # Draw stars
        star_coords = rotate((self.star_coords + self.stars_offset) * beat_scale, self.sky_rotation * t) + self.pole
        for i in range(self.n_stars):
            pygame.draw.circle(screen, self.star_colors[i] * (1 - 0.8 * beat_exp) * brightness, star_coords[i], self.star_sizes[i])

        # Draw moon
        moon_coord = rotate((self.moon_coord + self.moon_offset) * beat_scale, self.sky_rotation * t) + self.pole
        color = hls_to_rgb(0.21, 0.1 * brightness, 0.2)
        pygame.draw.circle(screen, [0,0,0], moon_coord, self.moon_size)
        pygame.draw.circle(screen, 0.5 * color, moon_coord, self.moon_size, width=1)
        pygame.draw.polygon(screen, color, rotate(self.moons[self.moon_phase], self.sky_rotation * t) + moon_coord)

        # Draw rocket trajectories
        for r in self.rockets:
            for i in range(len(r.trail) - 1):
                color = hls_to_rgb(r.hue, 0.1 * (i/r.trail_length) * brightness, 0.5 * (i/r.trail_length))
                pygame.draw.line(screen, color, r.trail[i], r.trail[i+1], width=1 + i//3)
            color = hls_to_rgb(r.hue, 0.2 * brightness, 1.0)
            pygame.draw.circle(screen, color, r.coord, 2)

        # Draw skyline
        skyline = (self.skyline - self.pole) * beat_scale + self.pole
        pygame.draw.polygon(screen, hls_to_rgb(self.skyline_hue, (0.003 - 0.002 * beat_exp) * brightness, 0.3), skyline)
        pygame.draw.aalines(screen, hls_to_rgb(self.skyline_hue, (0.05 - 0.025 * beat_exp) * brightness, 0.3), True, skyline)

        # Draw fireworks particles
        for f in self.fireworks:
            for p in range(f.n_particles):
                hue = f.hues[p % len(f.hues)]
                for i in range(len(f.trail) - 1):
                    color = hls_to_rgb(hue, 0.7 * f.decay * (i/f.trail_length) * (0.1 + 0.9 * np.random.rand()) * brightness, f.decay)
                    pygame.draw.circle(screen, color, f.trail[i][p], f.sizes[p] * f.decay)
                color = hls_to_rgb(hue, 0.9 * f.decay * (0.1 + 0.9 * np.random.rand()) * brightness, f.decay)
                pygame.draw.circle(screen, color, f.coords[p,:], f.sizes[p] * f.decay)

        screen.unlock()
