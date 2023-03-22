# ------------------------------------------------------------------------- #
#
#    Copyright (C) 2023 Jake Kurtz
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# ------------------------------------------------------------------------- #

import bpy
import bgl
import gpu
import math
import addon_utils

from mathutils import Vector, Matrix          

def refresh_viewers(context):
    # Flip the shading type, which force Cycles to update its textures.
    if context.scene.render.engine not in ['BLENDER_EEVEE','BLENDER_WORKBENCH']:
        wm = bpy.data.window_managers['WinMan']
        for win in wm.windows :
            for area in win.screen.areas :
                if area.type=='VIEW_3D' :
                    for space in area.spaces :
                        if space.type == 'VIEW_3D' and space.shading.type == 'RENDERED' :
                            space.shading.type = 'SOLID'
                            space.shading.type = 'RENDERED'

    # Flip some scene property to get the Eevee to update its textures in certain circumstances.
    if context.scene.render.engine == 'BLENDER_EEVEE':
        x = context.scene.render.resolution_percentage
        context.scene.render.resolution_percentage = x   

def get_dir():
    for mod in addon_utils.modules():
        if mod.bl_info['name'] == "Stratus":
            filepath = mod.__file__
            break
    dir = str(filepath.rsplit('\\', 1)[0])
    return dir

def get_clip_end(context):
    r3d = context.area.spaces.active.region_3d
    if r3d.view_perspective == 'CAMERA':
        obj_camera = bpy.context.scene.camera
        clip_end = obj_camera.data.clip_end
    else:
        clip_end = context.area.spaces.active.clip_end
    return clip_end


def compute_dir(theta, phi):
    dir = Vector(
    (
        math.sin(phi) * math.cos(theta),
        math.cos(phi) * math.cos(theta),
        math.sin(theta)
    ))
    dir.normalize()
    return dir

def look_at(eye, target, up):

    mz = Vector((eye[0]-target[0], eye[1]-target[1], eye[2]-target[2])) # inverse line of sight
    mz.normalize()
    
    mx = up.cross(mz)
    mx.normalize()

    my = mz.cross(mx)
    my.normalize()

    tx =  mx.dot(eye)
    ty =  my.dot(eye)
    tz =  mz.dot(eye)

    return Matrix((
        (mx[0], my[0], mz[0], 0), 
        (mx[1], my[1], mz[1], 0), 
        (mx[2], my[2], mz[2], 0), 
        (tx,    ty,    tz,    1)))


def new_env_img_image(img_name, width, height):
    if img_name not in bpy.data.images:
        bpy.data.images.new(img_name, width, height, alpha=True, float_buffer=True, stereo3d=False)
    bpy.data.images[img_name].scale(width, height)
    return bpy.data.images[img_name]

def new_bgl_buffer(image):
    width = image.size[0]
    height = image.size[1]
    channels = image.channels
    return bgl.Buffer(bgl.GL_FLOAT, (width * height * channels), list(image.pixels[:]))

def new_offscreen_fbo(width, height):
    _offscreen_fbo = None
    try:
        _offscreen_fbo = gpu.types.GPUOffScreen(width, height, format='RGBA32F')
    except Exception as e:
        print(e)
    return _offscreen_fbo

def bgl_texture_from_image(image, dim, bindcode):
    buffer = new_bgl_buffer(image)
    if len(dim) == 2:
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, bindcode)

        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_WRAP_S, bgl.GL_REPEAT)
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_WRAP_T, bgl.GL_REPEAT)

        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_LINEAR)
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_LINEAR)
        
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_BASE_LEVEL, 0)
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAX_LEVEL, 0)
            
        bgl.glTexImage2D(bgl.GL_TEXTURE_2D, 0, bgl.GL_RGBA16F, dim[0], dim[1], 0, bgl.GL_RGBA, bgl.GL_FLOAT, buffer)

        bgl.glBindTexture(bgl.GL_TEXTURE_2D, 0)
    elif len(dim) == 3:
        bgl.glBindTexture(bgl.GL_TEXTURE_3D, bindcode)
        
        bgl.glTexParameteri(bgl.GL_TEXTURE_3D, bgl.GL_TEXTURE_WRAP_S, bgl.GL_REPEAT)
        bgl.glTexParameteri(bgl.GL_TEXTURE_3D, bgl.GL_TEXTURE_WRAP_T, bgl.GL_REPEAT)
        bgl.glTexParameteri(bgl.GL_TEXTURE_3D, bgl.GL_TEXTURE_WRAP_R, bgl.GL_REPEAT)

        bgl.glTexParameteri(bgl.GL_TEXTURE_3D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_LINEAR)
        bgl.glTexParameteri(bgl.GL_TEXTURE_3D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_LINEAR)

        bgl.glTexParameteri(bgl.GL_TEXTURE_3D, bgl.GL_TEXTURE_BASE_LEVEL, 0)
        bgl.glTexParameteri(bgl.GL_TEXTURE_3D, bgl.GL_TEXTURE_MAX_LEVEL, 0)
    
        bgl.glTexImage3D(bgl.GL_TEXTURE_3D, 0, bgl.GL_RGBA16F, dim[0], dim[1], dim[2], 0, bgl.GL_RGBA, bgl.GL_FLOAT, buffer)

        bgl.glBindTexture(bgl.GL_TEXTURE_3D, 0)
    bpy.data.images.remove(image)

def bgl_uniform_sampler(shader, name, texture, dim, slot):

    if dim == 1:
        target = bgl.GL_TEXTURE_1D
    elif dim == 2:
        target = bgl.GL_TEXTURE_2D
    elif dim == 3:
        target = bgl.GL_TEXTURE_3D

    bgl.glActiveTexture(bgl.GL_TEXTURE0 + slot)
    bgl.glBindTexture(target, texture)
    bgl.glUniform1i(bgl.glGetUniformLocation(shader.program, name), slot)