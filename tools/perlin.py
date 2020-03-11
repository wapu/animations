import numpy as np
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from tqdm import tqdm


# Basic 2D Perlin noise taken from https://stackoverflow.com/a/42154921

def lerp(a, b, x): return a + x * (b-a)
def fade(t): return 6 * t**5 - 15 * t**4 + 10 * t**3

def gradient(h, x, y, v):
    g = v[h%4]
    return g[:,:,0] * x + g[:,:,1] * y

def perlin(x, y, t=0, tile_shifts=None):
    # permutation table
    p = np.arange(256, dtype=int)
    np.random.shuffle(p)
    p = np.stack([p,p]).flatten()
    # coordinates of the top-left
    xi = x.astype(int)
    yi = y.astype(int)
    # internal coordinates
    xf = x - xi
    yf = y - yi
    # fade factors
    u = fade(xf)
    v = fade(yf)
    # base vectors (time dependent)
    angle = t * 2*np.pi
    vectors = np.array([[ np.sin(angle),  np.cos(angle)],
                        [ np.sin(angle), -np.cos(angle)],
                        [ np.cos(angle),  np.sin(angle)],
                        [-np.cos(angle),  np.sin(angle)]])
    # noise components
    if tile_shifts is None:
        n00 = gradient(p[p[xi]+yi],     xf,   yf,   vectors)
        n01 = gradient(p[p[xi]+yi+1],   xf,   yf-1, vectors)
        n11 = gradient(p[p[xi+1]+yi+1], xf-1, yf-1, vectors)
        n10 = gradient(p[p[xi+1]+yi],   xf-1, yf,   vectors)
    else:
        # make sure the edges fit together for tiling
        i00 = p[p[xi]+yi]
        i01 = np.roll(i00, tile_shifts[0], axis=0)
        i11 = np.roll(i00, tile_shifts, axis=(0,1))
        i10 = np.roll(i00, tile_shifts[1], axis=1)
        n00 = gradient(i00, xf,   yf,   vectors)
        n01 = gradient(i01, xf,   yf-1, vectors)
        n11 = gradient(i11, xf-1, yf-1, vectors)
        n10 = gradient(i10, xf-1, yf,   vectors)
    # combine noises
    x1 = lerp(n00, n10, u)
    x2 = lerp(n01, n11, u)
    return lerp(x1, x2, v)


def fractal_perlin(shape, t=0, frequency=4, octaves=3, persistence=0.5, tiled=True, coordinate_input=None):
    noise = np.zeros(shape)
    amplitude = persistence

    for octave in range(octaves):
        if coordinate_input is None:
            x, y = np.meshgrid(np.linspace(0, frequency, shape[0], endpoint=False), np.linspace(0, frequency, shape[1], endpoint=False))
        else:
            x, y = coordinate_input, coordinate_input

        if tiled and shape[0]%frequency == 0 and shape[1]%frequency == 0:
            noise += amplitude * perlin(x, y, t, tile_shifts=(-shape[0]//frequency, -shape[1]//frequency))
        else:
            noise += amplitude * perlin(x, y, t)
        frequency *= 2
        amplitude *= persistence

    return noise


def self_referential_perlin(shape, t=0, frequency=4, octaves=3, persistence=0.5, seed=1):
    np.random.seed(seed)
    noise = fractal_perlin(shape, t=t, frequency=frequency, octaves=octaves, persistence=persistence, tiled=False)
    noise = frequency*(2**octaves) * (noise - noise.min()) / (noise.max() - noise.min())
    np.random.seed(seed)
    noise = fractal_perlin(shape, t=t, frequency=frequency, octaves=octaves, persistence=persistence, tiled=False, coordinate_input=noise)
    noise = frequency*(2**octaves) * (noise - noise.min()) / (noise.max() - noise.min())
    return noise


def fractal_perlin_loop(shape, n_frames, octaves=3, persistence=.5, seed=123):
    frames = []
    for t in tqdm(np.linspace(0, 1, n_frames)):
        np.random.seed(seed)
        frames.append(fractal_perlin(shape, t=t, octaves=octaves, persistence=persistence))
    return frames



if __name__ == '__main__':
    pass

    # frames = fractal_perlin_loop((768, 768), 50)
    # fig = plt.figure()
    # images = [[plt.imshow(frame, animated=True)] for frame in frames]
    # animation = animation.ArtistAnimation(fig, images, interval=50, blit=True)
    # plt.show()

    # tiled = fractal_perlin((400, 400))
    # tiled = np.concatenate([tiled, tiled], axis=0)
    # tiled = np.concatenate([tiled, tiled], axis=1)
    # plt.imshow(tiled, cmap='gray')
    # plt.show()

    # plt.imshow(self_referential_perlin((768,768)), cmap='gray', interpolation='bicubic')
    # plt.show()
