#!/usr/bin/env python
# coding: utf-8

# '''Render map.

# Usage:
#     ./render.py [options] [<pos>...]

# pos: a position to be rendered. eg: 2_3_0_l
# When the first number of a position is negative, add an 'x'
# before it. eg: x-2_3_9

# Options:
#     -h --help          Show this message.
#     -t --time=<time>   Render time (s) for each scene [default: 300].
#     -g --gui           Use Luxrender GUI instead of console.
# '''


# import os
import re
# import shelve
import subprocess

# from docopt import docopt

from consts import scale, z_scale, dx, dy


# camera distance from center of pos
m = scale/4
# how much above the position will be the camera
dz = 1

all_rots = {
    'e': (-m, 0),
    's': (0, m),
    'w': (m, 0),
    'n': (0, -m),
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
    return x * scale + dx, y * scale + dy, z / z_scale + dz


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
    if verbose:
        subprocess.check_output(c, shell=True)
    else:
        subprocess.check_output(c, stderr=subprocess.STDOUT, shell=True)


def convert_img(input_file, output_file):
    # convert/resize
    # c = 'convert -resize 800x -quality 90 {on}.png {on}.jpg'.format(
    c = 'convert -quality 90 %s %s' % (input_file, output_file)
    subprocess.check_call(c, shell=True)


# if __name__ == '__main__':
#     arguments = docopt(__doc__)
#     print(arguments)

#     # render_time = int(arguments['--time'])

#     # filename = 'aberto.Scene.00003.lxs'
#     # outfile = 'temp'

#     arg_pos = arguments.get('<pos>')
#     if arg_pos:
#         pos = [p.split('_') for p in arg_pos]
#     else:
#         with shelve.open('positions.shelve') as db:
#             pos = db['positions']

#     # print('minutos: ' + str(len(pos) * 4 * render_time / 60))

#     for p in pos:
#         # Hack to allow negative X position values.
#         # Docopt goes crazzy when a position starts with '-'
#         if (p[0][:2] == 'x-'):
#             p[0] = p[0][1:]

#         print('processing: ', p, ':', pos.index(p), '/', len(pos))
#         outname = '_'.join(map(str, p[:3] + [orient]))
#         lookats = pos_to_lookats(p)
#         text_base = load_base(
#             inputfile, outfile, render_time, write_interval)
#         for lookat, orient in lookats:
#             render_pos(text_base, lookat, orient, directory, outname)
#             convert_img(iinn, outt)
#             print('processed: ' + outname)




# import os
# fs = os.listdir('.')
# for f in fs:
#   if f.find('_o') > -1:
#     os.rename(f, f.replace('_o', '_w'))
#   if f.find('_l') > -1:
#     os.rename(f, f.replace('_l', '_e'))
