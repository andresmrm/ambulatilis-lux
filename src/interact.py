#!/usr/bin/env python
# coding: utf-8

'''Render map.

Usage:
    ./render.py [options] <temp-folder> <final-folder> [<name>...]

Should be run inside Blender. E.g.:
blender myblend.blend -b -P render.py -- /persistent/tmp/folder /final/map

temp-folder: Folder to store rendering files.
WARNING! Folders can be created and DELETED inside the temp-folder.
So it's strongly recommended to use an empty folder as temp-folder.

final-folder: Folder where final images and JSON file will be saved.

name: Names of the zones to be rendered. If none is passed, render all zones.

Options:
    -h --help               Show this message.
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

import os
import sys
import json
# import shelve
import shutil

from docopt import docopt

# Fix to run in Blender...
sys.path.append('.')
from consts import scale, z_scale, dx, dy
from render import (pos_to_lookats, render_pos, load_base,
                    convert_img, expand_pos)


base_id = 'position'

dz = 0.05
# distance between path center and positions center
pd = scale/2


def pos_to_text(x, y, z):
    return str(x) + '_' + str(y) + '_' + str(z)


def from_blender_coords(x, y, z):
    '''Convert from blender coords to game coords.'''
    return int((x-dx)/scale), int((y-dy)/scale), int(round((z-dz)*z_scale, 0))


def filter_objs_name(name):
    return [obj for obj in bpy.context.visible_objects
            if obj.name[:len(name)] == name]


def round_all(coords):
    return [round(i, 3) for i in coords]


def position_links(obj):
    obj_links = {}
    ox, oy, oz = round_all(obj.location)
    # check in which directions the position is linked
    for path in filter_objs_name('path'):
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
    for obj in filter_objs_name(base_id):
        x, y, z = from_blender_coords(*obj.location)
        positions.append([x, y, z])

        # calculate links between positions
        links[pos_to_text(x, y, z)] = position_links(obj)

    # with shelve.open('positions.shelve') as db:
    #     db['positions'] = positions
    #     db['links'] = links
    #     db.close()

    return positions, links


def text_pos_to_list(text_pos):
    l = [p.split('_') for p in text_pos.split()]
    # Hack to allow negative X position values.
    # Docopt goes crazzy when a position starts with '-'
    for p in l:
        if (p[0][:2] == 'x-'):
            p[0] = p[0][1:]
    return l


def rest_pos():
    '''Return all positions (with orientations) that are not explicited
    cited by a zone.'''

    all_raw_pos, _ = extract_positions()
    all_expanded_pos = []
    for raw_pos in all_raw_pos:
        all_expanded_pos.extend(expand_pos(raw_pos))

    # print(all_expanded_pos)
    for zone in zones.values():
        zone_pos = zone.get('positions')
        if zone_pos:
            for raw_pos in text_pos_to_list(zone_pos):
                for exp_pos in expand_pos(raw_pos):
                    # print(exp_pos)
                    all_expanded_pos.remove(exp_pos)

    return all_expanded_pos


def map_to_json(links, outfolder):
    # export map to JS
    s = 'var map = %s\nexport default map' % json.dumps(links)
    # s = 'export var map = %s\n' % json.dumps(positions)
    # s += 'export var links = %s\n' % json.dumps(links)
    arq = open('%smap.js' % outfolder, 'w')
    arq.write(s)
    arq.close()


def set_visible_layers(visible):
    for i, _ in enumerate(bpy.data.scenes[0].layers):
        bpy.data.scenes[0].layers[i] = True if i in visible else False


def export_part(name, directory):
    set_visible_layers(zones[name]['visible'])
    bpy.data.scenes[0].luxrender_rendermode.rendermode = zones[name]['mode']
    bpy.ops.export.luxrender(filename=name+'.lxs', directory=directory)


if __name__ == '__main__':
    import bpy
    from zones import zones
    argv = sys.argv
    argv = argv[argv.index("--") + 1:]  # get all args after "--"
    arguments = docopt(__doc__, argv)
    print(arguments)

    outdir = 'output'

    threads = int(arguments['--threads'])
    render_time = int(arguments['--time'])

    write_interval = int(arguments['--write-interval'])
    if not write_interval:
        write_interval = render_time

    arg_names = arguments.get('<name>')
    if not arg_names:
        arg_names = zones.keys()

    arg_dir = arguments.get('<temp-folder>')
    outfolder = arguments.get('<final-folder>')
    force_export = arguments.get('--force-export')
    gui = arguments.get('--gui')
    verbose = arguments.get('--verbose')

    # Export a JSON with positions links to be used by the JS client
    if arguments.get('--export-json'):
        _, links = extract_positions()
        map_to_json(links, outfolder)

    for name in arg_names:
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
            export_part(name, directory)

        pos = zones[name].get('positions')
        if not pos:
            pos = rest_pos()
        else:
            pos = text_pos_to_list(pos)

        for p in pos:
            lookats = pos_to_lookats(p)
            for lookat, orient in lookats:
                outname = '_'.join(map(str, p[:3] + [orient]))
                # Luxrender will create <luxoutname>.png and <luxoutname>.flm
                luxoutname = os.path.join(directory, outdir, outname)
                outfile = os.path.join(directory, 'temp.lxs')

                load_base(inputfile, outfile, luxoutname,
                          render_time, write_interval, lookat)
                print('processing: ', p, ':', pos.index(p), '/', len(pos))
                render_pos(outfile, directory, threads, gui, verbose)
                convert_img(luxoutname + '.png',
                            os.path.join(outfolder, outname + '.jpg'))
