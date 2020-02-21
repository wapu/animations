import numpy as np
from scipy.optimize import fsolve
from matplotlib import pyplot as plt


# Equations taken from https://physics.stackexchange.com/a/466553
def k(m):
    if m%2==0:
        return fsolve(lambda x: np.tan(x) + np.tanh(x), m*np.pi/2 - np.pi/4)
    else:
        return fsolve(lambda x: np.tan(x) - np.tanh(x), (m - 1/2) * np.pi/2)

def u(m,x):
    if m==0:
        return np.sqrt(3/2) * x
    elif m%2==0:
        return (np.cosh(k(m)) * np.cos(k(m) * x) + np.cos(k(m)) * np.cosh(k(m) * x)) / np.sqrt(np.cosh(k(m))**2 + np.cos(k(m))**2)
    else:
        return (np.sinh(k(m)) * np.sin(k(m) * x) + np.sin(k(m)) * np.sinh(k(m) * x)) / np.sqrt(np.sinh(k(m))**2 + np.sin(k(m))**2)


width, height = 768, 768
lim = 1.2
coords = np.mgrid[-lim:lim:2*lim/width, -lim:lim:2*lim/height].transpose(1,2,0)

m, n = 6, 7
w = u(m, coords[:,:,0]) * u(n, coords[:,:,1]) + u(n, coords[:,:,0]) * u(m, coords[:,:,1])
img = np.exp(-np.abs(w))**6

plt.imshow(img, cmap='gray')
plt.show()
