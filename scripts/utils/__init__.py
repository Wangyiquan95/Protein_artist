import bpy
from math import sin, cos, pi
TAU = 2*pi
import colorsys
import os


# set material parameters
# ['Alpha'][Anisotropic'][Anisotropic Rotation'][Base Color'][Clearcoat'][Clearcoat Normal'][Clearcoat Roughness'][Emission'][Emission Strength'][IOR'][Metallic'][Normal'][Roughness'][Sheen'][Sheen Tint'][Specular'][Specular Tint'][Subsurface'][Subsurface Anisotropy'][Subsurface Color'][Subsurface IOR'][Subsurface Radius'][Tangent'][Transmission'][Transmission Roughness'][Weight']

def material_list(name, color):
    # transparent materials
    mat1 = bpy.data.materials.new(name+'_1')
    mat1.use_nodes = True
    # remove default nodes tree
    if mat1.node_tree:
        mat1.node_tree.links.clear()
        mat1.node_tree.nodes.clear()
    # set the name
    nodes1 = mat1.node_tree.nodes
    links1 = mat1.node_tree.links

    # create shader
    shader1 = nodes1.new(type='ShaderNodeBsdfPrincipled')
    output1 = nodes1.new(type='ShaderNodeOutputMaterial')
    nodes1["Principled BSDF"].inputs['Base Color'].default_value = color
    nodes1["Principled BSDF"].inputs['Alpha'].default_value = 0.5
    nodes1["Principled BSDF"].inputs['Metallic'].default_value = 0.46
    nodes1["Principled BSDF"].inputs['Roughness'].default_value = 0.1

    # link the shader
    links1.new(shader1.outputs[0], output1.inputs[0])
    # create normal Principled BSDF material
    mat2 = create_material(name+'_2', (0.3, 0.1, 0.06), alpha=1)

    # create glowing materials
    mat3 = bpy.data.materials.new(name+'_3')
    mat3.use_nodes = True
    # remove default nodes tree
    if mat3.node_tree:
        mat3.node_tree.links.clear()
        mat3.node_tree.nodes.clear()
    # set the name
    nodes3 = mat3.node_tree.nodes
    links3 = mat3.node_tree.links

    # create shader
    shader3a = nodes3.new(type='ShaderNodeBsdfGlass')
    shader3b = nodes3.new(type='ShaderNodeEmission')
    output3 = nodes3.new(type='ShaderNodeOutputMaterial')

    nodes3["Glass BSDF"].inputs['Color'].default_value = (0.3, 0.1, 0.06, 1)
    nodes3["Glass BSDF"].inputs['Roughness'].default_value = 0
    nodes3["Emission"].inputs['Color'].default_value = color
    nodes3["Emission"].inputs['Strength'].default_value = 2
    # link the shader
    links3.new(shader3a.outputs[0], output3.inputs['Surface'])
    links3.new(shader3b.outputs[0], output3.inputs['Volume'])

    # create emission materials
    mat4 = create_material(name+'_4',(0.3, 0.1, 0.06), alpha=1)
    newShader(name+'_4', 'emission', 0.3, 0.1, 0.06, intensity=10)

    # create subsurface materials
    mat5 = bpy.data.materials.new(name + '_5')
    mat5.use_nodes = True
    # remove default nodes tree
    if mat5.node_tree:
        mat5.node_tree.links.clear()
        mat5.node_tree.nodes.clear()
    # set the name
    nodes5 = mat5.node_tree.nodes
    links5 = mat5.node_tree.links

    # create shader
    shader5 = nodes5.new(type='ShaderNodeBsdfPrincipled')
    output5 = nodes5.new(type='ShaderNodeOutputMaterial')

    nodes5["Principled BSDF"].inputs['Base Color'].default_value = color
    nodes5["Principled BSDF"].inputs['Subsurface'].default_value = 0.5

    # link the shader
    links5.new(shader5.outputs[0], output5.inputs['Surface'])
    return {'transparent':mat1,'BSDF':mat2,'glass glowing':mat3,'emission':mat4,'subsurface':mat5}

def remove_object(obj):
    if obj.type == 'MESH':
        if obj.data.name in bpy.data.meshes:
            bpy.data.meshes.remove(obj.data)
        if obj.name in bpy.context.scene.objects:
            bpy.context.scene.objects.unlink(obj)
        bpy.data.objects.remove(obj)
    else:
        raise NotImplementedError('Other types not implemented yet besides \'MESH\'')


def track_to_constraint(obj, target):
    constraint = obj.constraints.new('TRACK_TO')
    constraint.target = target
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    #constraint.track_axis = 'TRACK_Z'
    constraint.up_axis = 'UP_Y'
    #constraint.owner_space = 'LOCAL'
    #constraint.target_space = 'LOCAL'

    return constraint


def create_target(origin=(0,0,0)):
    target = bpy.data.objects.new('Target', None)
    bpy.context.collection.objects.link(target)
    target.location = origin
    return target


def create_camera(origin, target=None, lens=35, clip_start=0.1, clip_end=200, type='PERSP', ortho_scale=6):
    # Create object and camera
    camera = bpy.data.cameras.new("Camera")
    camera.lens = lens
    camera.clip_start = clip_start
    camera.clip_end = clip_end
    camera.type = type # 'PERSP', 'ORTHO', 'PANO'
    if type == 'ORTHO':
        camera.ortho_scale = ortho_scale

    # Link object to scene
    obj = bpy.data.objects.new("CameraObj", camera)
    obj.location = origin
    bpy.context.collection.objects.link(obj)
    bpy.context.scene.camera = obj # Make this the current camera

    if target: 
        track_to_constraint(obj, target)
    return obj


def create_light(origin, type='POINT', energy=1, color=(1,1,1), target=None):
    # Light types: 'POINT', 'SUN', 'SPOT', 'HEMI', 'AREA'
    bpy.ops.object.add(type='LIGHT', location=origin)
    obj = bpy.context.object
    obj.data.type = type
    obj.data.energy = energy
    obj.data.color = color

    if target: 
        track_to_constraint(obj, target)
    return obj


def simple_scene(target_coords, camera_coords, sun_coords, lens=35):
    target = create_target(target_coords)
    camera = create_camera(camera_coords, target, lens)
    sun = create_light(sun_coords, 'SUN', target=target)

    return target, camera, sun


def set_smooth(obj, level=None, smooth=True):
    if level:
        # Add subsurf modifier
        modifier = obj.modifiers.new('Subsurf', 'SUBSURF')
        modifier.levels = level
        modifier.render_levels = level

    # Smooth surface
    mesh = obj.data
    for p in mesh.polygons:
        p.use_smooth = smooth


def rainbow_lights(r=5, n=100, freq=2, energy=0.1):
    for i in range(n):
        t = float(i)/float(n)
        pos = (r*sin(TAU*t), r*cos(TAU*t), r*sin(freq*TAU*t))

        # Create lamp
        bpy.ops.object.add(type='LIGHT', location=pos)
        obj = bpy.context.object
        obj.data.type = 'POINT'

        # Apply gamma correction for Blender
        color = tuple(pow(c, 2.2) for c in colorsys.hsv_to_rgb(t, 0.6, 1))

        # Set HSV color and lamp energy
        obj.data.color = color
        obj.data.energy = energy


def remove_all(type=None):
    # Possible type:
    # "MESH", "CURVE", "SURFACE", "META", "FONT", "ARMATURE",
    # "LATTICE", "EMPTY", "CAMERA", "LIGHT"
    if type:
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_by_type(type=type)
        bpy.ops.object.delete()
    else:
        # Remove all elements in scene
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)


def create_material(name,base_color=(1, 1, 1, 1), alpha=1, metalic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name)

    if len(base_color) == 3:
        base_color = list(base_color)
        base_color.append(1)

    mat.use_nodes = True
    node = mat.node_tree.nodes['Principled BSDF']
    node.inputs['Alpha'].default_value = alpha
    node.inputs['Base Color'].default_value = base_color
    node.inputs['Metallic'].default_value = metalic
    node.inputs['Roughness'].default_value = roughness

    return mat 


def colorRGB_256(color):
    return tuple(pow(float(c)/255.0, 2.2) for c in color)


def render(
    render_folder='rendering',
    render_name='render',
    resolution_x=800,
    resolution_y=800,
    resolution_percentage=100,
    animation=False,
    frame_end=None,
    render_engine='CYCLES'
):
    scene = bpy.context.scene
    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    scene.render.resolution_percentage = resolution_percentage
    scene.render.engine = render_engine
    if frame_end:
        scene.frame_end = frame_end

    # Check if script is executed inside Blender
    if bpy.context.space_data is None:
        # Specify folder to save rendering and check if it exists
        render_folder = os.path.join(os.getcwd(), render_folder)
        if(not os.path.exists(render_folder)):
            os.mkdir(render_folder)

        if animation:
            # Render animation
            scene.render.filepath = os.path.join(
                render_folder,
                render_name)
            bpy.ops.render.render(animation=True)
        else:
            # Render still frame
            scene.render.filepath = os.path.join(
                render_folder,
                render_name + '.png')
            bpy.ops.render.render(write_still=True)


def bmesh_to_object(bm, name='Object'):
    mesh = bpy.data.meshes.new(name + 'Mesh')
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)

    return obj


def newMaterial(id):

    mat = bpy.data.materials.get(id)

    if mat is None:
        mat = bpy.data.materials.new(name=id)

    mat.use_nodes = True

    if mat.node_tree:
        mat.node_tree.links.clear()
        mat.node_tree.nodes.clear()

    return mat

def newShader(id, type, r, g, b,intensity=1):

    mat = newMaterial(id)

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    output = nodes.new(type='ShaderNodeOutputMaterial')

    if type == "diffuse":
        shader = nodes.new(type='ShaderNodeBsdfDiffuse')
        nodes["Diffuse BSDF"].inputs[0].default_value = (r, g, b, 1)

    elif type == "emission":
        shader = nodes.new(type='ShaderNodeEmission')
        nodes["Emission"].inputs[0].default_value = (r, g, b, 1)
        nodes["Emission"].inputs[1].default_value = intensity

    elif type == "glossy":
        shader = nodes.new(type='ShaderNodeBsdfGlossy')
        nodes["Glossy BSDF"].inputs[0].default_value = (r, g, b, 1)
        nodes["Glossy BSDF"].inputs[1].default_value = 0

    links.new(shader.outputs[0], output.inputs[0])

    return mat