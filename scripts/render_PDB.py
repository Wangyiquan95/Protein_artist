#!/usr/bin/env python3
import bpy
import time
import colorsys
from math import sin, cos, pi
import shutil
from mathutils import Euler,Vector
import argparse
import pymol
import sys
import os

import utils
TAU = 2*pi
def fetch_PDB(id,output,mode='cartoon'):
    pymol.cmd.bg_color('white')
    pymol.cmd.viewport('2000', '2000')
    pymol.cmd.fetch(id)
    pymol.cmd.remove('solvent')
    time.sleep(1)
    if mode=='new surface':
        pymol.cmd.hide('all')
        pymol.cmd.set('gaussian_resolution', '5.6')
        pymol.cmd.map_new('map', 'gaussian', '1', 'n. C+O+N+CA', '5')
        pymol.cmd.isosurface('surf', 'map', '0.8')
    elif mode == 'cartoon':
        pymol.cmd.show(mode)
    else:
        pymol.cmd.hide('all')
        pymol.cmd.show(mode)
    pymol.cmd.orient()
    pymol.cmd.save(output)
    pymol.cmd.delete('all')

def render_PDB(paths,camera_coordinates,camera_lens,materials,output_dir,output_name,quality='medium'):
    # Remove all elements
    utils.remove_all()

    # Create camera and lamp
    target = utils.create_target((0, 0, 0))
    camera = utils.create_camera(camera_coordinates, target, lens=camera_lens)
    # utils.simple_scene((0, 0, 0), (60, 150, 0), (-100, 100, 100), lens=22)

    # Create object
    bpy.ops.import_scene.x3d(filepath=paths[0])

    # Make this the current camera
    # bpy.context.scene.camera = bpy.data.objects['Viewpoint']
    # rename object
    bpy.data.objects['Shape_IndexedFaceSet'].name = 'Surface'
    # add color palette for background
    palette = [(255, 255, 255),(99, 80, 100), (80, 81, 82), (0, 0, 0), (184, 253, 153), (20, 195, 162), (13, 229, 168),
               (124, 244, 154), (184, 253, 153)]
    palette = [utils.colorRGB_256(color) for color in palette]
    obj = bpy.data.objects['Surface']

    # Apply materials to object
    obj.data.materials[0] = materials['subsurface']

    # Create object
    bpy.ops.import_scene.x3d(filepath=paths[1])
    if bpy.data.objects.get('Shape_IndexedFaceSet') != None:
        bpy.data.objects['Shape_IndexedFaceSet'].name = 'Core'
        obj2 = bpy.data.objects['Core']


        # Apply materials to object2
        obj2.data.materials[0] = materials['BSDF']
    # Deselect all
    bpy.ops.object.select_all(action='DESELECT')
    # select objects
    for o in bpy.context.scene.objects:
        if o.type == 'LIGHT':
            o.select_set(True)
        else:
            o.select_set(False)
    # delete selected objects
    bpy.ops.object.delete()

    for id in bpy.data.objects.keys():
        if "Shape_Cylinder" in id or "Shape_Sphere" in id:
            bpy.data.objects[id].select_set(True)
            bpy.data.objects[id].data.materials[0] = materials['emission']

    # Set background color of scene
    bpy.context.scene.world.use_nodes = False
    bpy.context.scene.world.color = palette[0]
    if quality=='high':
        resolution_x = 2550
        resolution_y = 3300
    elif quality=='medium':
        resolution_x = 1275
        resolution_y = 1650
    elif quality=='low':
        resolution_x = 510
        resolution_y = 660
    else:
        resolution_x = 1275
        resolution_y = 1650
    # Render scene
    utils.render(
        output_dir, output_name, resolution_x, resolution_y,
        render_engine='CYCLES')

if __name__ == '__main__':
    'usage: render_PDB -i 1IGT'
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--id', '-i', type=str, default='1IGT',
                        help='PDB ID or PDB_chain')
    parser.add_argument('--camera_lens', '-lens', type=int, default=18,
                        help='Camera lens. Default 22.')
    parser.add_argument('--camera_pos', '-pos', type=int, default=40,
                        help='Camera position. Default 140.')
    parser.add_argument('--core_style', '-cs', type=str, default='cartoon',
                        help='Core structure style.')
    parser.add_argument('--shell_style', '-ss', type=str, default='surface',
                        help='Shell structure style.')
    parser.add_argument('--temporary_path', '-tmp', type=str, default='data',
                        help="output file folder name")
    parser.add_argument('--output_path', '-o', type=str, default='../img',
                        help="output file folder name")
    parser.add_argument('--output_quality', '-q', type=str, default='low',
                        help="output image quality")
    args = parser.parse_args()

    # create a tmp dir to download the structure file
    os.makedirs(args.temporary_path, exist_ok=True)
    os.makedirs(args.output_path, exist_ok=True)
    core = f"{args.temporary_path}/{args.id}_core.wrl"
    surface = f"{args.temporary_path}/{args.id}_surface.wrl"
    if not os.path.isfile(core):
        fetch_PDB(args.id,core, args.core_style)
    if not os.path.isfile(surface):
        fetch_PDB(args.id, surface, args.shell_style)
    paths = [surface,core] # first one is the surface, second is the core
    # create material for model
    mats=utils.material_list('material',(0.47,0.33,1,1))
    render_PDB(paths,(0,args.camera_pos,0),args.camera_lens,mats,args.output_path,args.id,args.output_quality)
    # remove tmp dir
    shutil.rmtree(args.temporary_path)
