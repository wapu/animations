from matplotlib import pyplot as plt
import numpy as np
import gizeh as gz
from shapely import geometry as geo


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


def get_extinction_symbol_contours(radius=None, stroke_width=1):
    # Get scaled patameters
    radius, corners, stroke_width = get_extinction_symbol_params(radius, stroke_width)
    corners = np.concatenate([np.zeros((1,2)), corners, np.zeros((1,2))])
    # Construct outer circle and inner lines
    circle = geo.Point((0,0)).buffer(radius).boundary.buffer(stroke_width/2)
    lines = geo.LineString(corners).buffer(stroke_width/2, join_style=2, cap_style=3)
    # Take union over areas
    all = circle.union(lines)
    return [all.exterior, *all.interiors]


if __name__ == '__main__':
    surface = gz.Surface(1000,1000)
    offset = np.array((500,500))

    radius, corners, stroke_width = get_extinction_symbol_params(450)
    gz.circle(r=radius, xy=offset, stroke=(1,0,1), stroke_width=stroke_width).draw(surface)
    gz.polyline(points=corners + offset, close_path=True, fill=None, stroke=(1,0,1), stroke_width=stroke_width).draw(surface)

    for poly in get_extinction_symbol_contours(450):
        gz.polyline(points=np.array(poly.coords) + offset, close_path=True, fill=None, stroke=(1,1,1), stroke_width=2).draw(surface)

    img = surface.get_npimage()
    plt.imshow(255 - img, interpolation='bicubic')
    plt.axis('off')
    plt.show()
