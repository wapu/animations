import numpy as np
from geometry import get_rotation_matrix
# from scipy.optimize import fsolve


# Equations adapted from https://physics.stackexchange.com/a/466553
def k(m):
    # Smooth approximation of relaxed equation
    return 0.8 + (m-1) * 1.57

    # # Relaxation of discrete equation (has sudden jumps)
    # even = fsolve(lambda x: np.tan(x) + np.tanh(x), (m)*np.pi/2 - np.pi/4)
    # odd  = fsolve(lambda x: np.tan(x) - np.tanh(x), ((m) - 1/2) * np.pi/2)
    # alpha = np.abs(m%2 - 1)
    # return alpha * even + (1 - alpha) * odd

    # # Original discrete equation
    # if m%2==0:
    #     return fsolve(lambda x: np.tan(x) + np.tanh(x), m*np.pi/2 - np.pi/4)
    # else:
    #     return fsolve(lambda x: np.tan(x) - np.tanh(x), (m - 1/2) * np.pi/2)


def u(m,x,p=0):
    if m==0:
        return np.sqrt(3/2) * x

    # Relaxation of discrete equation
    else:
        km = k(m)
        even = (np.cosh(km) * np.cos(km * x + p) + np.cos(km + p) * np.cosh(km * x)) / np.sqrt(np.cosh(km)**2 + np.cos(km + p)**2)
        odd  = (np.sinh(km) * np.sin(km * x + p) + np.sin(km + p) * np.sinh(km * x)) / np.sqrt(np.sinh(km)**2 + np.sin(km + p)**2)
        alpha = np.abs(m%2 - 1)
        return alpha * even + (1 - alpha) * odd

    # # Original discrete equation
    # elif m%2==0:
    #     return (np.cosh(k(m)) * np.cos(k(m) * x) + np.cos(k(m)) * np.cosh(k(m) * x)) / np.sqrt(np.cosh(k(m))**2 + np.cos(k(m))**2)
    # else:
    #     return (np.sinh(k(m)) * np.sin(k(m) * x) + np.sin(k(m)) * np.sinh(k(m) * x)) / np.sqrt(np.sinh(k(m))**2 + np.sin(k(m))**2)


def get_chladni_pattern(m, n, width, height, lim=1, angle=0, xphase=0, yphase=0):
    if angle == 0:
        xx, yy = np.mgrid[-lim:lim:2*lim/width, -lim:lim:2*lim/height]
    else:
        points = np.mgrid[-lim:lim:2*lim/width, -lim:lim:2*lim/height]
        xx, yy = points.transpose(1,2,0).dot(get_rotation_matrix(angle)).transpose(2,0,1)
    return u(m, xx, xphase) * u(n, yy, yphase) + u(n, xx, xphase) * u(m, yy, yphase)


# Equation used in https://demonstrations.wolfram.com/ChladniFigures/
def get_wolfram_chladni_pattern(m, n, width, height, lim=5, xphase=0, yphase=0):
    xx, yy = np.mgrid[-lim:lim:2*lim/width, -lim:lim:2*lim/height]
    return np.cos(n * np.pi * xx + xphase)*np.cos(m * np.pi * yy + yphase) - np.cos(m * np.pi * xx + xphase)*np.cos(n * np.pi * yy + yphase)


if __name__ == '__main__':

    from matplotlib import pyplot as plt
    width, height = 768, 768

    plt.subplot(2,2,1)
    img = np.exp(-np.abs(get_chladni_pattern(3, 4, width, height, lim=1.2)))**6
    plt.imshow(img, vmin=0, vmax=1, cmap='gray')

    plt.subplot(2,2,2)
    img = np.exp(-np.abs(get_chladni_pattern(3, 5, width, height, lim=1.2)))**6
    plt.imshow(img, vmin=0, vmax=1, cmap='gray')

    plt.subplot(2,2,3)
    img = np.exp(-np.abs(get_chladni_pattern(4, 4, width, height, lim=1, angle=np.pi/4)))**6
    plt.imshow(img, vmin=0, vmax=1, cmap='gray')

    plt.subplot(2,2,4)
    img = np.exp(-np.abs(get_chladni_pattern(4, 5, width, height, lim=1, angle=-np.pi/4)))**6
    plt.imshow(img, vmin=0, vmax=1, cmap='gray')

    plt.show()
