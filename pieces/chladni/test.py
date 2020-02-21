import numpy as np
from scipy.optimize import fsolve
from matplotlib import pyplot as plt


# Equations adapted from https://physics.stackexchange.com/a/466553
def k(m):
    # Smooth approximation of interpolated equation
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


def u(m,x):
    if m==0:
        return np.sqrt(3/2) * x

    # Relaxation of discrete equation
    else:
        km = k(m)
        even = (np.cosh(km) * np.cos(km * x) + np.cos(km) * np.cosh(km * x)) / np.sqrt(np.cosh(km)**2 + np.cos(km)**2)
        odd  = (np.sinh(km) * np.sin(km * x) + np.sin(km) * np.sinh(km * x)) / np.sqrt(np.sinh(km)**2 + np.sin(km)**2)
        alpha = np.abs(m%2 - 1)
        return alpha * even + (1 - alpha) * odd

    # # Original discrete equation
    # elif m%2==0:
    #     return (np.cosh(k(m)) * np.cos(k(m) * x) + np.cos(k(m)) * np.cosh(k(m) * x)) / np.sqrt(np.cosh(k(m))**2 + np.cos(k(m))**2)
    # else:
    #     return (np.sinh(k(m)) * np.sin(k(m) * x) + np.sin(k(m)) * np.sinh(k(m) * x)) / np.sqrt(np.sinh(k(m))**2 + np.sin(k(m))**2)


def get_chladni_pattern(m, n, width, height, lim=1):
    xx, yy = np.mgrid[-lim:lim:2*lim/width, -lim:lim:2*lim/height]
    return u(m, xx) * u(n, yy) + u(n, xx) * u(m, yy)


if __name__ == '__main__':
    width, height = 768, 768

    import matplotlib.animation as animation
    t = np.linspace(0,2*np.pi,100)
    frames = [np.exp(-np.abs(get_chladni_pattern(n, m, width, height)))**8 for n, m in zip(4 + np.sin(t), 5 + np.cos(t))]
    for i in range(len(frames)):
        frames[i] = np.mean([frames[i], frames[i][:,::-1], frames[i][::-1,::-1], frames[i][::-1,:]], axis=0)
    fig = plt.figure()
    images = [[plt.imshow(frame, vmin=0, vmax=1, cmap='gray', animated=True)] for frame in frames]
    animation = animation.ArtistAnimation(fig, images, interval=100, blit=True)
    plt.show()

    # plt.subplot(2,2,1)
    # img = np.exp(-np.abs(get_chladni_pattern(3, 4, width, height, lim=1.2)))**6
    # plt.imshow(img, vmin=0, vmax=1, cmap='gray')
    # plt.subplot(2,2,2)
    # img = np.exp(-np.abs(get_chladni_pattern(3, 5, width, height, lim=1.2)))**6
    # plt.imshow(img, vmin=0, vmax=1, cmap='gray')
    # plt.subplot(2,2,3)
    # img = np.exp(-np.abs(get_chladni_pattern(4, 4, width, height, lim=1.2)))**6
    # plt.imshow(img, vmin=0, vmax=1, cmap='gray')
    # plt.subplot(2,2,4)
    # img = np.exp(-np.abs(get_chladni_pattern(4, 5, width, height, lim=1.2)))**6
    # plt.imshow(img, vmin=0, vmax=1, cmap='gray')
    # plt.show()
