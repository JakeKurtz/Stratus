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
import gpu
import math

from mathutils import Matrix, Vector

from ... import globals
from .general_utils import compute_dir, bgl_uniform_sampler, get_clip_end, look_at

def sun_uniforms(shader):
    prop = bpy.context.scene.sun_props

    shader.uniform_int("enable_sun_as_light", prop.sun_enable_light)

    shader.uniform_float("sun_half_angular", prop.sun_size / 2.0)
    shader.uniform_float("sun.dir", compute_dir(prop.sun_elevation, prop.sun_rotation))
    shader.uniform_float("sun.intsty", prop.sun_disk_intsty)
    shader.uniform_float("sun.silver_intsty", prop.sun_silver_intsty)
    shader.uniform_float("sun.silver_spread", prop.sun_silver_spread)

def moon_uniforms(shader):
    moon_prop = bpy.context.scene.moon_props
    sun_prop = bpy.context.scene.sun_props

    moon_dir = compute_dir(moon_prop.moon_elevation, moon_prop.moon_rotation)

    # Rotate Moon so that it alwasy faces the origin 
    inv_lookat_mat = look_at(moon_dir, Vector((0,0,0)), Vector((0,0,1)))
    inv_lookat_mat.invert()

    # Flip the x,y values when Moon goes over the zenith i.e theta > 90d
    if (math.cos(moon_prop.moon_elevation) < 0.0):
        a = -inv_lookat_mat.row[0]
        b = -inv_lookat_mat.row[1]
        c =  inv_lookat_mat.row[2]
        d =  inv_lookat_mat.row[3]

        inv_lookat_mat = Matrix((a,b,c,d))
        moon_up = Vector((moon_dir[1],-moon_dir[0],0))
    else:
        moon_up = Vector((-moon_dir[1],moon_dir[0],0))

    moon_up.normalize()

    # Offset Moon rotation s.t. it has proper orientation 
    rot_offset_mat = Matrix((
        (0.0000, 0.0000, -1.0000, 0.0000),
        (0.0000, 1.0000,  0.0000, 0.0000),
        (1.0000, 0.0000,  0.0000, 0.0000),
        (0.0000, 0.0000,  0.0000, 1.0000)
    ))

    # Rotate Moon face
    rot_moon_face_mat = Matrix.Rotation(moon_prop.moon_face_rotation, 4, moon_dir)

    # Combine rotations
    rot_mat = rot_offset_mat @ inv_lookat_mat @ rot_moon_face_mat
    shader.uniform_float("moon_rot_mat", rot_mat)  

    if (moon_prop.moon_use_sun_dir):
        moon_phase_dir = compute_dir(sun_prop.sun_elevation, sun_prop.sun_rotation)
    else:
        inv_moon_dir = -moon_dir
        rot_mat = Matrix.Rotation(moon_prop.moon_phase_rotation, 4, inv_moon_dir)

        moon_up = rot_mat @ moon_up
        moon_up.normalize()

        rot_mat = Matrix.Rotation(moon_prop.moon_phase, 4, moon_up)
        moon_phase_dir = rot_mat @ inv_moon_dir
        moon_phase_dir.normalize()

    shader.uniform_int("enable_moon_as_light", moon_prop.moon_enable_light)
    shader.uniform_float("moon_phase_dir", moon_phase_dir)
    shader.uniform_float("moon_half_angular", moon_prop.moon_size/2.0)

    shader.uniform_float("moon_ambient_intsty", moon_prop.moon_ambient_intsty)

    shader.uniform_float("moon.dir", moon_dir)
    shader.uniform_float("moon.intsty", moon_prop.moon_disk_intsty)
    shader.uniform_float("moon.silver_intsty", moon_prop.moon_silver_intsty)
    shader.uniform_float("moon.silver_spread", moon_prop.moon_silver_spread)

def atmo_uniforms(shader):
    prop = bpy.context.scene.atmo_props
    
    shader.uniform_float("rayleigh_density", prop.prop_air)
    shader.uniform_float("mie_density", prop.prop_dust)
    shader.uniform_float("ozone_density", prop.prop_ozone)

def cloud_uniforms(shader):
    prop = bpy.context.scene.cloud_props

    d = prop.cld_horizon_dst
    h = prop.cld_horizon_h
    cld_domain_radius = math.pow((2.0*d),2.0) / (8.0 * h) + h * 0.5
    cld_domain_center = Vector((0.0, 0.0, h-cld_domain_radius))

    # TODO: bake this shit
    shader.uniform_float("cld_top_roundness", prop.cld_top_roundness)
    shader.uniform_float("cld_btm_roundness", prop.cld_btm_roundness)
    shader.uniform_float("cld_top_density", prop.cld_top_density)
    shader.uniform_float("cld_btm_density", prop.cld_btm_density)
    # ---------------------

    shader.uniform_float("cld_ap_intsty", 500000*prop.cld_ap_intsty)
    shader.uniform_float("cld_ambient_intsty", prop.cld_ambient_intsty)

    shader.uniform_float("cld_domain_min_radius", cld_domain_radius)
    shader.uniform_float("cld_domain_max_radius", cld_domain_radius + 15000)
    shader.uniform_float("cld_domain_center", cld_domain_center)

    # ---------------------------------------------------------------------------- #
    shader.uniform_int("enable_cld_0",              prop.cld_0_enable)
    shader.uniform_float("cld_0_density",           prop.cld_0_density)
    shader.uniform_float("cld_0_size",              prop.cld_0_size)
    shader.uniform_float("cld_0_radius",            prop.cld_0_height + cld_domain_radius)
    shader.uniform_float("cld_0_height",            prop.cld_0_thickness)
    shader.uniform_float("cld_0_detail_intsty",     prop.cld_0_detail_intsty)
    shader.uniform_float("cld_0_shape_intsty",      prop.cld_0_shape_intsty)
    shader.uniform_float("cld_0_coverage_intsty",   prop.cld_0_coverage_intsty)

    shader.uniform_float("cld_0_detail_offset",     prop.cld_0_detail_offset)
    shader.uniform_float("cld_0_shape_offset",      prop.cld_0_shape_offset)
    shader.uniform_float("cld_0_coverage_offset",   prop.cld_0_coverage_offset)

    cld_0_trans = Matrix.Translation(cld_domain_center + Vector((0,0,6360e3)))
    cld_0_rot = Matrix.Rotation(prop.cld_0_rotation, 4, 'Z')

    cld_0_transform = cld_0_rot @ cld_0_trans
    cld_0_transform.invert()
    
    shader.uniform_float("cld_0_transform", cld_0_transform)
    # ---------------------------------------------------------------------------- #

    shader.uniform_int("enable_cld_1",              prop.cld_1_enable)

    shader.uniform_float("cld_1_density",           prop.cld_1_density)
    shader.uniform_float("cld_1_size",              prop.cld_1_size)
    shader.uniform_float("cld_1_radius",            prop.cld_1_height + cld_domain_radius)
    shader.uniform_float("cld_1_height",            prop.cld_1_thickness)
    shader.uniform_float("cld_1_detail_intsty",     prop.cld_1_detail_intsty)
    shader.uniform_float("cld_1_shape_intsty",      prop.cld_1_shape_intsty)
    shader.uniform_float("cld_1_coverage_intsty",   prop.cld_1_coverage_intsty)

    shader.uniform_float("cld_1_detail_offset",     prop.cld_1_detail_offset)
    shader.uniform_float("cld_1_shape_offset",      prop.cld_1_shape_offset)
    shader.uniform_float("cld_1_coverage_offset",   prop.cld_1_coverage_offset)

    cld_1_trans = Matrix.Translation(cld_domain_center + Vector((0,0,6360e3)))
    cld_1_rot = Matrix.Rotation(prop.cld_1_rotation, 4, 'Z')

    cld_1_transform = cld_1_rot @ cld_1_trans
    cld_1_transform.invert()
    
    shader.uniform_float("cld_1_transform", cld_1_transform)
    
    # ---------------------------------------------------------------------------- #

    bgl_uniform_sampler(shader, "noise_tex_3D_32", globals.NOISE_TEXTURES[0], 3, 0)
    bgl_uniform_sampler(shader, "noise_tex_3D_128", globals.NOISE_TEXTURES[1], 3, 1)
    bgl_uniform_sampler(shader, "noise_tex_2D_1024", globals.NOISE_TEXTURES[2], 2, 2)
    bgl_uniform_sampler(shader, "blue_noise", globals.NOISE_TEXTURES[3], 2, 3)

    bgl_uniform_sampler(shader, "moon_albedo_tex", globals.MOON_TEXTURES[0], 2, 4)
    bgl_uniform_sampler(shader, "moon_normal_tex", globals.MOON_TEXTURES[1], 2, 5)

def draw_irra_map(fbo_0, fbo_1, render_context):
    sun_prop = bpy.context.scene.sun_props
    moon_prop = bpy.context.scene.moon_props

    irra_dim = (globals.IRRA_WIDTH, globals.IRRA_HEIGHT)

    if render_context == 'VIEWPORT':
        enable_moon = moon_prop.moon_show_viewport
        enable_sun = sun_prop.sun_show_viewport
    elif render_context == 'RENDER':
        enable_moon = moon_prop.moon_show_render
        enable_sun = sun_prop.sun_show_render

    with fbo_0.bind():
        gpu.state.depth_test_set('NONE')

        _shader = globals.SHADER["sky"]

        _shader.bind()
        _shader.uniform_float("img_size", irra_dim)

        atmo_uniforms(_shader)

        _shader.uniform_int("enable_moon", enable_moon)
        _shader.uniform_int("enable_sun", enable_sun)

        _shader.uniform_float("sun.dir", compute_dir(sun_prop.sun_elevation, sun_prop.sun_rotation))
        _shader.uniform_int("enable_sun_as_light", sun_prop.sun_enable_light)

        _shader.uniform_float("moon.dir", compute_dir(moon_prop.moon_elevation, moon_prop.moon_rotation))
        _shader.uniform_int("enable_moon_as_light", moon_prop.moon_enable_light)
        
        globals.BATCH["sky"].draw(_shader)
    
    with fbo_1.bind():
        gpu.state.depth_test_set('NONE')
        _shader = globals.SHADER["sky_irra"]
        _shader.bind()
        _shader.uniform_float("img_size", irra_dim)
        bgl_uniform_sampler(_shader, "env_tex", fbo_0.color_texture, 2, 0)
        globals.BATCH["sky_irra"].draw(_shader)

def draw_env_img(env_img, irra_tex, render_context):
    cloud_prop = bpy.context.scene.cloud_props
    atmo_prop = bpy.context.scene.atmo_props
    sun_prop = bpy.context.scene.sun_props
    moon_prop = bpy.context.scene.moon_props
    render_prop = bpy.context.scene.render_props

    if render_context == 'VIEWPORT':   
        cld_max_steps = render_prop.max_steps_viewport
        cld_max_light_steps = render_prop.max_light_steps_viewport
        enable_atm = atmo_prop.atm_show_viewport
        enable_cld = cloud_prop.cld_show_viewport
        enable_moon = moon_prop.moon_show_viewport
        enable_sun = sun_prop.sun_show_viewport
    elif render_context == 'RENDER':
        cld_max_steps = render_prop.max_steps_render
        cld_max_light_steps = render_prop.max_light_steps_render
        enable_atm = atmo_prop.atm_show_render
        enable_cld = cloud_prop.cld_show_render
        enable_moon = moon_prop.moon_show_render
        enable_sun = sun_prop.sun_show_render

    tile_pos = env_img.get_tile_pos()
    tile_size = env_img.get_tile_size()
    img_size = env_img.get_size()
    offscreen = env_img.get_offscreen()

    with offscreen.bind():

        gpu.state.viewport_set(tile_pos[0]*tile_size, tile_pos[1]*tile_size, tile_size, tile_size)
        gpu.state.depth_test_set('NONE')

        _shader = globals.SHADER["env_img"]

        _shader.bind()

        _shader.uniform_float("img_size", img_size)
        _shader.uniform_int("cld_max_steps", cld_max_steps)
        _shader.uniform_int("cld_max_light_steps", cld_max_light_steps)

        _shader.uniform_float("altitude", atmo_prop.prop_sky_altitude)

        _shader.uniform_int("enable_atm", enable_atm)
        _shader.uniform_int("enable_cld", enable_cld)
        _shader.uniform_int("enable_moon", enable_moon)
        _shader.uniform_int("enable_sun", enable_sun)

        atmo_uniforms(_shader)
        cloud_uniforms(_shader)
        moon_uniforms(_shader)
        sun_uniforms(_shader)

        bgl_uniform_sampler(_shader, "irra_tex", irra_tex, 2, 6)

        globals.BATCH["env_img"].draw(_shader)

    env_img.increment_tile()

def pre_draw_viewport(self, context, irra_tex):

    cloud_prop = context.scene.cloud_props
    atmo_prop = context.scene.atmo_props 
    sun_prop = context.scene.sun_props  
    moon_prop = context.scene.moon_props
    render_prop = context.scene.render_props
    
    scr_width = context.region.width
    scr_height = context.region.height

    tex_width = int(float(scr_width)/float(render_prop.viewport_pixel_size))       
    tex_height = int(float(scr_height)/float(render_prop.viewport_pixel_size))
    
    with self._offscreen_viewport.bind():
        gpu.state.depth_test_set('NONE')
        _shader = globals.SHADER["viewport"]

        _shader.bind()

        proj_mat = context.region_data.perspective_matrix
        
        inv_vp_mat = proj_mat
        inv_vp_mat = inv_vp_mat.inverted()
        
        _shader.uniform_float("img_size", (tex_width, tex_height))
        
        _shader.uniform_float("inv_vp_mat", inv_vp_mat)      
        _shader.uniform_int("cld_max_steps", render_prop.max_steps_viewport)
        _shader.uniform_int("cld_max_light_steps", render_prop.max_light_steps_viewport)

        _shader.uniform_float("altitude", atmo_prop.prop_sky_altitude)

        _shader.uniform_int("enable_atm", atmo_prop.atm_show_viewport)
        _shader.uniform_int("enable_cld", cloud_prop.cld_show_viewport)
        _shader.uniform_int("enable_moon", moon_prop.moon_show_viewport)
        _shader.uniform_int("enable_sun", sun_prop.sun_show_viewport)

        atmo_uniforms(_shader)
        cloud_uniforms(_shader)
        moon_uniforms(_shader)
        sun_uniforms(_shader)

        bgl_uniform_sampler(_shader, "irra_tex", irra_tex, 2, 6)
 
        globals.BATCH["viewport"].draw(_shader)

def post_draw_viewport(self, context):
    scene = context.scene
    prop = scene.render_props

    r3d = context.area.spaces.active.region_3d
    trans_mat = Matrix.Translation(r3d.view_matrix.inverted().translation)
    
    clip_end = get_clip_end(context)
    scale_mat = Matrix.Scale((clip_end*0.9)*.5, 4)
    
    obj_mat = trans_mat @ scale_mat

    proj_view_mat = bpy.context.region_data.perspective_matrix
    
    scr_width = context.region.width
    scr_height = context.region.height

    tex_width = int(float(scr_width)/float(prop.viewport_pixel_size))       
    tex_height = int(float(scr_height)/float(prop.viewport_pixel_size))

    gpu.state.depth_test_set('LESS')

    _shader = globals.SHADER["screen"]
    _shader.bind()

    _shader.uniform_float("projection", proj_view_mat @ obj_mat)

    _shader.uniform_float("monitor_size", (self._monitor_width, self._monitor_height))
    _shader.uniform_float("scr_size", (scr_width, scr_height))
    _shader.uniform_float("tex_size", (tex_width, tex_height))
    _shader.uniform_float("gamma", scene.view_settings.gamma)
    _shader.uniform_float("env_img_strength", prop.env_img_strength)

    bgl_uniform_sampler(_shader, "tex", self._offscreen_viewport.color_texture, 2, 0)

    globals.BATCH["screen"].draw(_shader)

    gpu.state.depth_test_set('NONE')
