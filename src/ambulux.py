#!/usr/bin/env python
# coding: utf-8

'''Render map.

Usage:
    ./render.py [options] <store-folder> <final-folder> [<name>...]

Should be run inside Blender. E.g.:
blender myblend.blend -b -P render.py -- /persistent/tmp/folder /final/map

store-folder: Folder to store rendering files.
WARNING! Folders can be created and DELETED inside the store-folder.
So it's strongly recommended to use an empty folder as store-folder.

final-folder: Folder where final images and JSON file will be saved.

name: Names of the zones to be rendered. If not set, render all.

Options:
    -h --help               Show this message.
    -c --config=<config-file>
                            Config file path.
    -T --time=<time>        Render time (s) for each scene [default: 300].
    -w --write-interval=<write-interval>
                            Write interval for image and FML. Defaults to
                            render time.
    -t --threads=<threads>  Number of threads [default: 6].
    -g --gui                Use Luxrender GUI instead of console.
    -j --export-json        Export positions links to JSON.
    -v --verbose            Verbose Luxrender.
    -f --force-export       If should force export of zones. If not try to
                            continue old renders.
'''

import re
import os
import sys
import json
import shutil
import importlib
import subprocess

from docopt import docopt

# Fix to run in Blender...
# sys.path.append('.')
# sys.path.append('../../ambulatilis-lux/src')
# print(sys.argv)
# from consts import scale, z_scale, dx, dy
# from render import (pos_to_lookats, render_pos, load_base,
#                     convert_img, expand_pos)

# ----------------------------------------------------------
#               Default Configuration
# ----------------------------------------------------------

# The ID of the objects that will be used in Blender to mark
# positions where the camera can be should start with this string
position_id = 'position'

# The ID of the objects that will be used in Blender to mark
# the link between the positions should start with this string
path_id = 'path'

# multiplier from positions coords to blender coords
scale = 5

# multiplier for the z coord
z_scale = 2

# X adder from positions coords (scaled) to blender coords
dx = scale/2

# Y adder from positions coords (scaled) to blender coords
dy = scale/2

# Z subtractor when converting from Blender coordinates.
# E.g.: If this value is set to 0.05, all objects with center in z=0.05
# will be converted to z=0.
dz_pos = 0.05

# distance between path center and positions center
pd = scale/2

# camera distance from center of position
dcam = scale/4

# how much above the position will be the camera
dz_cam = 1

all_rots = {
    'e': (-dcam, 0),
    's': (0, dcam),
    'w': (dcam, 0),
    'n': (0, -dcam),
}

# ----------------------------------------------------------


def to_blender_coords(x, y, z):
    '''Convert to blender coords from game coords.'''
    return (x * scale + dx,
            y * scale + dy,
            z / z_scale + dz_cam)


def from_blender_coords(x, y, z):
    '''Convert from blender coords to game coords.'''
    return (int((x-dx)/scale),
            int((y-dy)/scale),
            int(round((z-dz_pos)*z_scale, 0)))


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

    with open(input_file, 'r') as arq:
        base = arq.read()

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
    with open(output_file, 'w') as arq:
        arq.write(base)

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


def pos_to_text(x, y, z):
    return str(x) + '_' + str(y) + '_' + str(z)


def filter_objs_name(name):
    return [obj for obj in bpy.context.visible_objects
            if obj.name[:len(name)] == name]


def round_all(coords):
    return [round(i, 3) for i in coords]


def position_links(obj):
    obj_links = {}
    ox, oy, oz = round_all(obj.location)
    # check in which directions the position is linked
    for path in filter_objs_name(path_id):
        px, py, pz = round_all(path.location)
        if px == ox:
            if py == oy + pd:
                obj_links['n'] = from_blender_coords(ox, oy + scale,
                                                     oz + (pz - oz)*2)
            if py == oy - pd:
                obj_links['s'] = from_blender_coords(ox, oy - scale,
                                                     oz + (pz - oz)*2)
        if py == oy:
            if px == ox + pd:
                obj_links['e'] = from_blender_coords(ox + scale, oy,
                                                     oz + (pz - oz)*2)
            if px == ox - pd:
                obj_links['w'] = from_blender_coords(ox - scale, oy,
                                                     oz + (pz - oz)*2)
    return obj_links


def extract_positions():
    links = {}
    positions = []
    # find positions
    for obj in filter_objs_name(position_id):
        x, y, z = from_blender_coords(*obj.location)
        positions.append([x, y, z])

        # calculate links between positions
        links[pos_to_text(x, y, z)] = position_links(obj)

    return positions, links


def text_pos_to_list(text_pos):
    l = [p.split('_') for p in text_pos.split()]
    # Hack to allow negative X position values.
    # Docopt goes crazzy when a position starts with '-'
    for p in l:
        if (p[0][:2] == 'x-'):
            p[0] = p[0][1:]
    return l


def rest_pos(zones):
    '''Return all positions (with orientations) that are not explicited
    cited by a zone.'''

    if zones:
        # set all layers used in the zones file to visible
        all_used_layers = []
        for zone in zones.values():
            for layer in zone['layers']:
                if layer not in all_used_layers:
                    all_used_layers.append(layer)
        set_visible_layers(all_used_layers)

    all_raw_pos, _ = extract_positions()
    all_expanded_pos = []
    for raw_pos in all_raw_pos:
        all_expanded_pos.extend(expand_pos(raw_pos))

    # print(all_expanded_pos)
    if zones:
        for zone in zones.values():
            zone_pos = zone.get('positions')
            if zone_pos:
                for raw_pos in text_pos_to_list(zone_pos):
                    for exp_pos in expand_pos(raw_pos):
                        # print(exp_pos)
                        all_expanded_pos.remove(exp_pos)

    return all_expanded_pos


def map_to_json(links, outfolder):
    '''Export map position links to a JSON file, so it can be used
    by a JS app.'''
    s = 'var map = %s\nexport default map' % json.dumps(links)
    # s = 'export var map = %s\n' % json.dumps(positions)
    # s += 'export var links = %s\n' % json.dumps(links)
    arq = open('%smap.js' % outfolder, 'w')
    arq.write(s)
    arq.close()


def set_visible_layers(layers):
    for i, _ in enumerate(bpy.data.scenes[0].layers):
        bpy.data.scenes[0].layers[i] = True if i in layers else False


def export_part(zones, name, directory):
    if zones:
        set_visible_layers(zones[name]['layers'])
        bpy.data.scenes[0].luxrender_rendermode.rendermode = (
            zones[name]['mode'])
    bpy.ops.export.luxrender(filename=name+'.lxs', directory=directory)


def load_config(config_file):
    folder, filename = os.path.split(config_file)
    name = os.path.splitext(filename)[0]
    # print(folder, name)
    sys.path.append(folder)
    return importlib.import_module(name).zones
    # module = importlib.import_module(config_file)
    # [i for i in dir(module) if not i.startswith("__")]


def get_pos_list(zones, name):
    if zones and name:
        pos = zones[name].get('positions')
        if pos:
            return text_pos_to_list(pos)
    return rest_pos(zones)


def process(arg_names, zones, force_export):
    for name in arg_names:

        if not name:
            name = 'noname'

        print('ZONE:', name)
        directory = os.path.join(arg_dir, name)
        inputfile = os.path.join(directory, name + '.lxs')

        if force_export:
            shutil.rmtree(directory)

        if not os.path.exists(directory):
            os.makedirs(os.path.join(directory, outdir))
            force_export = True
        elif not os.path.exists(inputfile):
            force_export = True

        if force_export:
            export_part(zones, name, directory)

        pos = get_pos_list(zones, name)

        for p in pos:
            lookats = pos_to_lookats(p)
            for lookat, orient in lookats:
                outname = '_'.join(map(str, p[:3] + [orient]))
                # Luxrender will create <luxoutname>.png and <luxoutname>.flm
                luxoutname = os.path.join(directory, outdir, outname)
                outfile = os.path.join(directory, 'temp.lxs')

                load_base(inputfile, outfile, luxoutname,
                          render_time, write_interval, lookat)
                print('processing: ', p, ':', pos.index(p) + 1, '/', len(pos))
                render_pos(outfile, directory, threads, gui, verbose)
                convert_img(luxoutname + '.png',
                            os.path.join(outfolder, outname + '.jpg'))


if __name__ == '__main__':
    import bpy
    argv = sys.argv
    argv = argv[argv.index("--") + 1:]  # get all args after "--"
    arguments = docopt(__doc__, argv)

    config_file = arguments['--config']
    if config_file:
        zones = load_config(config_file)
    else:
        zones = None

    outdir = 'output'

    threads = int(arguments['--threads'])
    render_time = int(arguments['--time'])

    write_interval = int(arguments['--write-interval'])
    if not write_interval:
        write_interval = render_time

    arg_names = arguments.get('<name>')
    if not arg_names:
        if zones:
            arg_names = zones.keys()
        else:
            arg_names = [None]

    arg_dir = arguments.get('<store-folder>')
    outfolder = arguments.get('<final-folder>')
    force_export = arguments.get('--force-export')
    gui = arguments.get('--gui')
    verbose = arguments.get('--verbose')

    # Export a JSON with positions links to be used by the JS client
    if arguments.get('--export-json'):
        _, links = extract_positions()
        map_to_json(links, outfolder)

    process(arg_names, zones, force_export)
