from matplotlib import pyplot as plt
import numpy as np
import gizeh as gz


def get_extinction_symbol_params(radius=None, stroke_width=1):
    # Returns radius, corners and stroke width to draw extinction symbol as thick lines
    radius_ = 6.456
    corners_ = np.array([[ 3.423, -3.937],
                         [-3.423, -3.937],
                         [ 3.423,  3.937],
                         [-3.423,  3.937]])
    stroke_width_ = 1
    # Scale by desired radius if given
    if radius is not None:
        return radius, corners_ * radius/radius_, radius/radius_
    # Otherwise scale by desired stroke width
    return radius_*stroke_width, corners_*stroke_width, stroke_width


if __name__ == '__main__':
    radius, corners, stroke_width = get_extinction_symbol_params(450)
    surface = gz.Surface(1000,1000)
    offset = np.array((500,500))

    gz.circle(r=radius, xy=offset, stroke=(1,1,1), stroke_width=stroke_width).draw(surface)
    gz.polyline(points=corners + offset, close_path=True, fill=None, stroke=(1,1,1), stroke_width=stroke_width).draw(surface)
    img = surface.get_npimage()

    plt.imshow(255 - img, interpolation='bicubic')
    plt.axis('off')
    plt.show()
