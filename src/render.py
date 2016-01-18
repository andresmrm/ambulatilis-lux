#!/usr/bin/env python
# coding: utf-8

import re
import subprocess

from consts import scale, z_scale, dx, dy


# camera distance from center of pos
dcam = scale/4
# how much above the position will be the camera
dz_cam = 1

all_rots = {
    'e': (-dcam, 0),
    's': (0, dcam),
    'w': (dcam, 0),
    'n': (0, -dcam),
}


def expand_pos(pos):
    '''Expands the possible orientations for a position.
    e.g.: ['1','0','0'] becomes:
    [[1,0,0,'e'], [1,0,0,'s'], [1,0,0,'w'], [1,0,0,'n']]
    But ['1','0','0','s'] stays the same.
    Pos should be in game coords, not Blender.'''
    x, y, z = map(int, pos[:3])
    if len(pos) > 3:
        used_rots = pos[3:]
    else:
        used_rots = all_rots.keys()
    return [[x, y, z, orient] for orient in used_rots]


def to_blender_coords(x, y, z):
    '''Convert to blender coords from game coords.'''
    return x * scale + dx, y * scale + dy, z / z_scale + dz_cam


def pos_to_lookats(raw_pos):
    lookats = []
    for pos in expand_pos(raw_pos):
        x, y, z = to_blender_coords(*pos[:3])
        orient = pos[3]
        rot_coord = all_rots[orient]
        x2 = x + rot_coord[0]
        y2 = y + rot_coord[1]
        s = 'LookAt {x2} {y2} {z} {x} {y} {z} 0 0 1'.format(
            x=x, y=y, z=z, x2=x2, y2=y2)
        lookats.append((s, orient))
    return lookats


def load_base(input_file, output_file, luxoutname, render_time,
              write_interval, lookat):
    '''Open a LXS, modify some values and save in another file.'''

    arq = open(input_file, 'r')
    base = arq.read()
    arq.close()

    # set base file name
    base = re.sub('"string filename".+$',
                  '"string filename" ["' + luxoutname + '"]',
                  base, flags=re.M)

    # set render time
    base = re.sub('"integer halttime".+$',
                  '"integer halttime" [%s]' % str(render_time),
                  base, flags=re.M)

    # set write flm
    base = re.sub('"bool write_resume_flm".+$',
                  '"bool write_resume_flm" ["%s"]' % 'true',
                  base, flags=re.M)

    # set restart flm
    base = re.sub('"bool restart_resume_flm".+$',
                  '"bool restart_resume_flm" ["%s"]' % 'false',
                  base, flags=re.M)

    # set write flm interval
    base = re.sub('"integer flmwriteinterval".+$',
                  '"integer flmwriteinterval" [%s]' % str(write_interval),
                  base, flags=re.M)

    # set write image interval
    base = re.sub('"integer writeinterval".+$',
                  '"integer writeinterval" [%s]' % str(write_interval),
                  base, flags=re.M)

    # position camera
    base = re.sub('LookAt.+$', lookat, base, flags=re.M)

    # save file
    arq = open(output_file, 'w')
    arq.write(base)
    arq.close()

    return base


def render_pos(lxs_file, directory, threads=6, gui=False, verbose=False):
    '''Render a LXS file. Change to directory first.'''

    if gui:
        command = 'luxrender'
    else:
        command = 'luxconsole'
    c = 'cd %s; %s -t %s %s' % (directory, command, threads, lxs_file)

    args = {'shell': True}
    if not verbose:
        args['stderr'] = subprocess.STDOUT
    subprocess.check_output(c, **args)


def convert_img(input_file, output_file):
    # convert/resize
    # c = 'convert -resize 800x -quality 90 {on}.png {on}.jpg'.format(
    c = 'convert -quality 90 %s %s' % (input_file, output_file)
    subprocess.check_call(c, shell=True)
