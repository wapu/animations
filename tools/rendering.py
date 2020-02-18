import os, shutil, time
import subprocess
from multiprocessing import Pool
from PIL import Image
import numpy as np
basestring = str


# Render videos

import gizeh as gz
import moviepy.editor as mpy

webm_params = {
    '-y': None,
    '-an': None,
    '-framerate': '50',
    '-c:v': 'libvpx-vp9',
    '-speed': '1',
    '-b:v': '2000k',
    '-minrate': '50k',
    '-maxrate': '5000k',
    '-crf': '1',
}

def render_webm(filename, make_frame, duration, extra_params={}):
    c = mpy.VideoClip(make_frame, duration=duration)
    params = [str(p) for p in sum(dict(webm_params, **extra_params).items(), ()) if p is not None]
    c.write_videofile(f'{filename}.webm',
                      fps=int(dict(webm_params, **extra_params)['-framerate']),
                      ffmpeg_params=params)

def save_poster(filename, make_frame, t=0):
    c = mpy.VideoClip(make_frame, duration=1)
    c.save_frame(f'{filename}.jpg', t=t)

mp4_params = {
    '-y': None,
    '-an': None,
    '-vcodec': 'libx264',
    '-pix_fmt': 'yuv420p',
    '-preset': 'veryslow',
    '-b:v': '2000k',
    '-minrate': '50k',
    '-maxrate': '5000k',
}

def convert_to_mp4(filename, extra_params={}):
    print(f'Creating .mp4 version of "{filename}.webm"')
    params = [str(p) for p in sum(dict(mp4_params, **extra_params).items(), ()) if p is not None]
    subprocess.call(['ffmpeg', '-i', f'{filename}.webm'] + params + [f'{filename}.mp4',])


# Interpolation functions

def hermite(val):
    return 3*val*val - 2*val*val*val

def ease_in(val):
    return val*val*val

def ease_out(val):
    val -= 1
    return 1 + val*val*val

def ease_mid(val, m0=2, m1=2):
    val2 = val*val
    val3 = val*val2
    return (val3 - 2*val2 + val) * m0 + (-2*val3 + 3*val2) + (val3 - val2) * m1

def inverse_hermite(val):
    return 0.5 + 0.5 * (2*val - 1)**3

def interpolate(val, interpolation):
    if interpolation in [False, None, 'none', 'None']:
        return val
    elif interpolation == 'hermite' or interpolation == True:
        return hermite(val)
    elif interpolation == 'inverse_hermite':
        return inverse_hermite(val)
    elif interpolation == 'ease_out':
        return ease_out(val)
    elif interpolation == 'ease_in':
        return ease_in(val)
    elif interpolation == 'ease_mid':
        return ease_mid(val)

def interval_progress(progress, interval, interpolation=None):
    (start, stop) = interval
    p = np.minimum(1.0, np.maximum(0.0, (progress - start) / (stop - start)))
    return interpolate(p, interpolation)

def interval_progresses(progress, n_intervals, interpolation=None):
    if isinstance(interpolation, str):
        interpolation = [interpolation] * n_intervals
    if len(interpolation) < n_intervals:
        interpolation.extend([interpolation[-1]] * (n_intervals - len(interpolation)))

    p = []
    for i in range(n_intervals):
        p.append(interval_progress(progress, (float(i) / n_intervals, float(i+1) / n_intervals), interpolation=interpolation[i]))
    return p

def weight_function(progress, peak, radius, interpolation=None):
    d = min(1.0, max(0.0, float(abs(peak - progress)) / radius))
    return 1.0 - interpolate(d, interpolation)


def equidistant_weight_functions(progress, n_points, interpolation=None):
    if isinstance(interpolation, str) or interpolation is None:
        interpolation = [interpolation] * n_points
    if len(interpolation) < n_points:
        interpolation.extend([interpolation[-1]] * (n_points - len(interpolation)))

    p = []
    for i in range(n_points):
        p.append(weight_function(progress, float(i) / (n_points - 1), 1.0 / (n_points - 1), interpolation=interpolation[i]))
    return p


# def render_one_frame(args):
#   n, total_frames, render_frame, output_path = args

#   print('Rendering frame %05d/%05d' % (n+1, total_frames))
#   I = render_frame(n, total_frames)
#   I = Image.fromarray(I)
#   I.save(output_path + '/%05d.png' % (n,))

# def render_animation(name, total_frames, render_frame, f_start=0, f_end=0, multiprocessing=True):
#   if f_end <= f_start: f_end = total_frames

#   output_path = 'output/' + name
#   if os.path.exists(output_path) and f_start == 0 and f_end == total_frames:
#       shutil.rmtree(output_path)
#       time.sleep(0.5)
#   if not os.path.exists(output_path):
#       os.makedirs(output_path)

#   if multiprocessing:
#       pool = Pool()
#       pool.map(render_one_frame, [(n, total_frames, render_frame, output_path) for n in range(f_start, f_end)])
#   else:
#       for n in range(f_start, f_end):
#           render_one_frame((n, total_frames, render_frame, output_path))


# def convert_to_webm(name, fps=50, qmin=10, qmax=42):
#   output_path = 'output/' + name

#   subprocess.call(['ffmpeg.exe', '-y',
#       '-r', str(fps),
#       '-i', output_path + '/%05d.png',
#       '-c:v', 'libvpx',
#       '-qmin', str(qmin),
#       '-qmax', str(qmax),
#       # '-crf', '4',
#       # '-b:v', '1500k',
#       'webm/%s-%dfps.webm' % (name, fps)])
