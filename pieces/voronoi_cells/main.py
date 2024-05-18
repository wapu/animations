import numpy as np
from shapely import geometry as geo

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from stippling import *
from tsp import *


name = 'voronoi_cells_tsp_eye'
width, height = 768, 768
duration = 1.5

webm_params = {
    '-b:v': '2500k',
    '-minrate': '50k',
    '-maxrate': '5000k',
    '-crf': '0',
}

mp4_params = {
    '-b:v': '2500k',
    '-minrate': '50k',
    '-maxrate': '5000k',
}


c1 = geo.point.Point(0.5 * width, 0.35 * height).buffer(0.5 * height)
c2 = geo.point.Point(0.5 * width, 0.65 * height).buffer(0.5 * height)
eye = c1.intersection(c2).buffer(-20)
iris = geo.point.Point(0.5 * width, 0.5 * height).buffer(0.25 * height)
pupil = geo.point.Point(0.5 * width, 0.5 * height).buffer(0.13 * height)
left = geo.point.Point(0.96 * width, 0.5 * height).buffer(20)
right = geo.point.Point(0.04 * width, 0.5 * height).buffer(20)
top = geo.point.Point(0.5 * width, 0.24 * height).buffer(10)
bottom = geo.point.Point(0.5 * width, 0.76 * height).buffer(10)


# Prepare input for Voronoi stippling
def prepare_eye_shape():
    surface = gz.Surface(width=width, height=height)
    gz.rectangle(lx=width, ly=height, xy=(width/2, height/2), fill=(0,0,0)).draw(surface)

    gz.polyline(points=eye.buffer(20).exterior.coords, stroke_width=0, fill=(.4,.4,.4)).draw(surface)

    gz.polyline(points=eye.exterior.coords,   stroke_width=0, fill=(.1,.1,.1)).draw(surface)
    gz.polyline(points=iris.exterior.coords,  stroke_width=0, fill=(1,1,1)).draw(surface)
    gz.polyline(points=pupil.exterior.coords, stroke_width=0, fill=(0,0,0)).draw(surface)

    gz.polyline(points=left.exterior.coords,   stroke_width=0, fill=(.0,.0,.0)).draw(surface)
    gz.polyline(points=right.exterior.coords,  stroke_width=0, fill=(.0,.0,.0)).draw(surface)
    gz.polyline(points=top.exterior.coords,    stroke_width=0, fill=(1,1,1)).draw(surface)
    gz.polyline(points=bottom.exterior.coords, stroke_width=0, fill=(1,1,1)).draw(surface)

    surface.write_to_png('eye_shape.png')


# Stipple image and create TSP problem
def stipple_image():
    points = stipple_image_points('eye_shape.png', n_points=1000, scale_factor=2, max_iterations=250)
    np.save('eye_stippled.npy', points)


# Solve TSP problem
def solve_tsp():
    points = np.load('eye_stippled.npy')
    route = solve_tsp_ortools(points)
    write_cyc(route, 'eye_path.cyc')
    postprocess_cyc('eye_stippled.npy', 'eye_path.cyc', 'eye_processed.npy', (256, 256), segment_length=15, degree=3, radius=110./128.)


# Prepare keyframes
def prepare_keyframes(n_keyframes=30, n_vertices=24):
    base_points = np.load('eye_processed.npy')[::1]
    center_and_scale(base_points, (height/2, width/2), width/2 * (110./128.))

    clip_poly_outer = eye.buffer(0, join_style=2, mitre_limit=20)
    clip_poly_inner = pupil.buffer(-10)

    keyframes = np.zeros((n_keyframes + 1, len(base_points), n_vertices + 2), dtype=np.float32)

    for n in range(n_keyframes):
        progress = float(n) / n_keyframes

        points = [(1 - progress) * base_points[i,:] + progress * base_points[(i+1) % len(base_points),:]
                  for i in range(len(base_points))]
        points.extend([(-height, -width), (-height, 2*width), (2*height, -width), (2*height, 2*width)])

        v = Voronoi(points)

        for i in range(len(points) - 4):
            region = v.regions[v.point_region[i]]
            region = [(v.vertices[region[j]][0], v.vertices[region[j]][1]) for j in range(len(region))]

            region = geo.polygon.Polygon(region)
            region = region.intersection(clip_poly_outer).difference(clip_poly_inner)
            if region.is_empty:
                continue
            if isinstance(region, geo.multipolygon.MultiPolygon):
                continue
            region = region.exterior.coords

            center = np.mean(region, axis=0)
            keyframes[n, i, :2] = center
        
            for j in range(n_vertices):
                theta = (2 * np.pi * j) / float(n_vertices)
                r_dir = np.sin(theta), np.cos(theta)
                for k in range(len(region)):
                    res = line_ray_intersection(center, r_dir, region[k], region[(k+1) % len(region)], norm=False)
                    if res is not None:
                        break
                keyframes[n, i, j+2] = res[1] if res is not None else 0

    for i in range(len(base_points)):
        keyframes[-1, i, :] = keyframes[0, (i+1) % len(base_points), :]

    np.save('eye_keyframes.npy', keyframes)


# Render frame at time t
def make_frame(t):
    color_bg = np.array([0.,0.,0.])
    color = np.array([1.,1.,1.])
    surface = gz.Surface(width, height)

    keyframes = np.load('eye_keyframes.npy')
    progress = t / duration
    weights = equidistant_weight_functions(progress, len(keyframes))

    n_points = keyframes.shape[1]
    n_vertices = keyframes.shape[2] - 2
    for i in range(n_points):
        center = sum([weights[j] * keyframes[j,i,:2] for j in range(len(keyframes))])

        vertices = []
        for v in range(n_vertices):
            theta = (2 * np.pi * v) / float(n_vertices)
            r_dir = np.array([np.sin(theta), np.cos(theta)])
            dist = sum([weights[j] * keyframes[j,i,v+2] for j in range(len(keyframes))])
            vertices.append(center + dist * r_dir)

        vertices_geo = geo.polygon.Polygon(vertices)
        inside = vertices_geo.intersection(iris).area / vertices_geo.area

        vertices_bz = []
        vertices_np = np.array(vertices)
        degree = 5
        for r in range(len(vertices)):
            n_subdivs = int(np.linalg.norm(vertices_np[r,:] - vertices_np[(r+1) % len(vertices),:]))
            n_subdivs = max(1, n_subdivs)
            for s in range(n_subdivs):
                t = r + float(s) / n_subdivs
                bz = de_boor(t, vertices_np, degree)
                vertices_bz.append((bz[0], bz[1]))

        color_factor = (1-progress) * float(i**10 % n_points) / n_points + \
            progress * float((i+1)**10 % n_points) / n_points
        gz.polyline(points=vertices_bz, close_path=True, stroke_width=1, stroke=(0,0,0),
                    fill=color * (0.2 + 0.4 * (1 - inside) + 0.5 * color_factor)).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    prepare_eye_shape()
    stipple_image()
    solve_tsp()
    prepare_keyframes()

    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
