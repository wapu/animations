import numpy as np
import colorsys


def random_rgb():
    color = np.random.random_sample(3)**2
    color = 255 * color / np.max(color)
    return color

def random_hue(start=0, end=1, lightness=0.5, saturation=1.0):
    hue = start + np.random.rand() * (end - start)
    return hls_to_rgb(hue % 1.0, lightness, saturation)

def hls_to_rgb(hue, lightness=0.5, saturation=1.0):
    return np.array(colorsys.hls_to_rgb(hue, lightness, saturation)) * 255

def clamp(color):
    return np.maximum(0, np.minimum(255, color))

# Taken from https://stackoverflow.com/a/74666366
ONE_THIRD = 1/3
TWO_THIRD = 2/3
ONE_SIXTH = 1/6

def _v(m1, m2, h):
    h = h % 1.0
    return np.where(h < ONE_SIXTH, m1 + (m2 - m1) * h * 6,
                    np.where(h < .5, m2,
                             np.where(h < TWO_THIRD, m1 + (m2 - m1) * (TWO_THIRD - h) * 6,
                                      m1)))

def hls_to_rgb_array(h, l=None, s=None):
    if l is None:
        l = np.ones_like(h) * 0.5
    if s is None:
        s = np.ones_like(h)

    m2 = np.where(l < 0.5, l * (1 + s), l + s - (l * s))
    m1 = 2 * l - m2

    r = np.where(s == 0, l, _v(m1, m2, h + ONE_THIRD))
    g = np.where(s == 0, l, _v(m1, m2, h))
    b = np.where(s == 0, l, _v(m1, m2, h - ONE_THIRD))

    return 255 * np.concatenate((r[...,None], g[...,None], b[...,None]), axis=-1)

def hue_to_rgb_array(h):
    h = h[...,None]
    r = (h + 1/3) % 1.0
    g = (h) % 1.0
    b = (h - 1/3) % 1.0
    return 255 * np.concatenate([r,g,b], axis=-1)
