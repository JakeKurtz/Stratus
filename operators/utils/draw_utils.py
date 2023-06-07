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

from mathutils import Matrix, Vector, Color
from bl_math import lerp

from ... import globals
from .general_utils import compute_dir, bgl_uniform_sampler, get_clip_end, look_at, new_offscreen_fbo

def stars_uniforms(shader):
    prop = bpy.context.scene.stars_props

    shader.uniform_float("stars_intsty", prop.stars_intsty)

    pole_dir = compute_dir(prop.stars_pole_elevation, prop.stars_pole_rotation)
    rot_mat = Matrix.Rotation(prop.stars_rotation, 4, pole_dir)
    shader.uniform_float("stars_rot_mat", rot_mat)

def sun_uniforms(shader):
    prop = bpy.context.scene.sun_props

    shader.uniform_bool("enable_sun_as_light", prop.sun_enable_light)

    shader.uniform_float("sun_half_angular", prop.sun_size / 2.0)
    shader.uniform_float("sun.dir", compute_dir(prop.sun_elevation, prop.sun_rotation))
    shader.uniform_float("sun.intsty", prop.sun_intsty)
    #shader.uniform_float("sun.silver_intsty", prop.sun_silver_intsty)
    #shader.uniform_float("sun.silver_spread", prop.sun_silver_spread)

def moon_uniforms(shader):
    moon_prop = bpy.context.scene.moon_props
    sun_prop = bpy.context.scene.sun_props

    moon_dir = compute_dir(moon_prop.moon_elevation, moon_prop.moon_rotation)

    # Rotate Moon so that it always faces the origin 
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

    shader.uniform_bool("enable_moon_as_light", moon_prop.moon_enable_light)
    shader.uniform_float("moon_phase_dir", moon_phase_dir)
    shader.uniform_float("moon_half_angular", moon_prop.moon_size/2.0)

    shader.uniform_float("moon_ambient_intsty", moon_prop.moon_ambient_intsty)

    shader.uniform_float("moon.dir", moon_dir)
    shader.uniform_float("moon.intsty", moon_prop.moon_intsty)
    #shader.uniform_float("moon.silver_intsty", moon_prop.moon_silver_intsty)
    #shader.uniform_float("moon.silver_spread", moon_prop.moon_silver_spread)

def atmo_uniforms(shader):
    prop = bpy.context.scene.atmo_props
    
    shader.uniform_float("rayleigh_density", prop.prop_air)
    shader.uniform_float("mie_density", prop.prop_dust)
    shader.uniform_float("ozone_density", prop.prop_ozone)

def cloud_uniforms(shader):
    prop = bpy.context.scene.cloud_props
    render_prop = bpy.context.scene.render_props

    d = 60000.0#prop.scale_0#60000.0 # (m) # 10000.0
    h = 1000.0#prop.scale_1#1000.0 # (m)  # 100.0
    cld_domain_radius = math.pow((2.0*d),2.0) / (8.0 * h) + h * 0.5
    cld_domain_center = Vector((0.0, 0.0, h-cld_domain_radius))
    cld_domain_thickness = 15000.0 # (m)

    #shader.uniform_float("cld_G", prop.cld_G)

    cld_0_ap_intsty = 500000.0 * lerp(0.5, 0.04175, prop.cld_0_ap_intsty)
    cld_1_ap_intsty = 500000.0 * lerp(0.5, 0.04175, prop.cld_1_ap_intsty)

    cld_0_powder_intsty = lerp(3.0, 0.5, prop.cld_0_powder_intsty)
    cld_1_powder_intsty = lerp(3.0, 0.5, prop.cld_1_powder_intsty)

    shader.uniform_float("cld_domain_center", cld_domain_center)

    # ---------------------------------------------------------------------------- #

    scale = lerp(0.1, 7.5, prop.cld_0_size);
    detail_scale = prop.cld_1_noise_sizes[0]
    shape_scale = prop.cld_1_noise_sizes[1] / scale;
    coverage_scale = prop.cld_1_noise_sizes[2] / scale;
    #detail_scale = 0.002 / scale;
    #shape_scale = (0.0015 / scale) * 0.3;
    #coverage_scale = 0.00003 / scale;

    shell_thickness = 500.0 * scale;

    sigma_a = Vector((0.0, 0.0, 0.0))
    cld_0_sigma_t = max(Vector(prop.cld_0_sigma_s) + sigma_a, Vector((0.000000001,0.000000001,0.000000001)))

    shader.uniform_bool("enable_cld_0",                 prop.cld_0_enable)

    shader.uniform_int("cloud_0.layer",                 0)

    shader.uniform_float("cloud_0.btm_roundness",       prop.cld_0_bottom_roundness)
    shader.uniform_float("cloud_0.top_roundness",       prop.cld_0_top_roundness)

    shader.uniform_float("cloud_0.radius",              prop.cld_0_height + cld_domain_radius)
    shader.uniform_float("cloud_0.density",             prop.cld_0_density)
    shader.uniform_float("cloud_0.density_height",      prop.cld_0_density_height)
    shader.uniform_float("cloud_0.thickness",           prop.cld_0_thickness)
    shader.uniform_float("cloud_0.shell_thickness",     shell_thickness)

    shader.uniform_float("cloud_0.sigma_s",             prop.cld_0_sigma_s)
    shader.uniform_float("cloud_0.sigma_t",             cld_0_sigma_t)

    shader.uniform_float("cloud_0.ap_intsty",           cld_0_ap_intsty)
    shader.uniform_float("cloud_0.ambient_intsty",      prop.cld_0_ambient_intsty)

    shader.uniform_float("cloud_0.coverage_shape",      prop.cld_0_coverage_shape)
    shader.uniform_float("cloud_0.shape_shape",         prop.cld_0_shape_shape)
    shader.uniform_float("cloud_0.detail_shape",        prop.cld_0_detail_shape)

    shader.uniform_float("cloud_0.shape_inverse",       prop.cld_0_shape_inverse)
    shader.uniform_float("cloud_0.detail_inverse",      prop.cld_0_detail_inverse)

    shader.uniform_float("cloud_0.atten",               prop.cld_0_atten)
    shader.uniform_float("cloud_0.contr",               prop.cld_0_contr)
    shader.uniform_float("cloud_0.eccen",               prop.cld_0_eccen)

    shader.uniform_float("cloud_0.coverage_scale",      coverage_scale)
    shader.uniform_float("cloud_0.shape_scale",         shape_scale)
    shader.uniform_float("cloud_0.detail_scale",        detail_scale)

    shader.uniform_int("cloud_0.curl_octaves",          prop.cld_0_curl_octaves)

    shader.uniform_float("cloud_0.coverage_intsty",     prop.cld_0_coverage_intsty)
    shader.uniform_float("cloud_0.shape_intsty",        0.6 * prop.cld_0_shape_intsty)
    shader.uniform_float("cloud_0.detail_intsty",       0.6 * prop.cld_0_detail_intsty)

    shader.uniform_float("cloud_0.pos_offset",          prop.cld_0_pos_offset * 100.0)
    shader.uniform_float("cloud_0.coverage_offset",     prop.cld_0_coverage_offset * 100.0)
    shader.uniform_float("cloud_0.shape_offset",        prop.cld_0_shape_offset * 100.0)
    shader.uniform_float("cloud_0.detail_offset",       prop.cld_0_detail_offset * 100.0)

    cld_0_trans = Matrix.Translation(cld_domain_center + Vector((0,0,6360e3)))
    cld_0_rot = Matrix.Rotation(prop.cld_0_rotation, 4, 'Z')

    cld_0_transform = cld_0_rot @ cld_0_trans
    cld_0_transform.invert()
    
    shader.uniform_float("cloud_0.transform", cld_0_transform)
    # ---------------------------------------------------------------------------- #

    scale = lerp(0.1, 7.5, prop.cld_1_size);

    detail_scale = 0.0019#prop.cld_1_noise_sizes[0]                # 0.0019
    shape_scale = 0.0015 / scale #prop.cld_1_noise_sizes[1] / scale;        # 0.0015
    coverage_scale = 0.000035 / scale #prop.cld_1_noise_sizes[2] / scale;     # 0.000035
    #coverage_scale = 0.000003 / scale;

    shell_thickness = 1000 * scale;

    sigma_a = Vector((0.0, 0.0, 0.0))
    cld_1_sigma_t = max(Vector(prop.cld_1_sigma_s) + sigma_a, Vector((0.000000001,0.000000001,0.000000001)))

    shader.uniform_bool("enable_cld_1",                 prop.cld_1_enable)

    shader.uniform_int("cloud_1.layer",                 1)

    shader.uniform_float("cloud_1.btm_roundness",       prop.cld_1_bottom_roundness)
    shader.uniform_float("cloud_1.top_roundness",       prop.cld_1_top_roundness)

    shader.uniform_float("cloud_1.radius",              prop.cld_1_height + cld_domain_radius)
    shader.uniform_float("cloud_1.density",             prop.cld_1_density)
    shader.uniform_float("cloud_1.density_height",      prop.cld_1_density_height)
    shader.uniform_float("cloud_1.thickness",           prop.cld_1_thickness)
    shader.uniform_float("cloud_1.shell_thickness",     shell_thickness)

    shader.uniform_float("cloud_1.sigma_s",             prop.cld_1_sigma_s)
    shader.uniform_float("cloud_1.sigma_t",             cld_1_sigma_t)

    shader.uniform_float("cloud_1.ap_intsty",           cld_1_ap_intsty)
    shader.uniform_float("cloud_1.ambient_intsty",      prop.cld_1_ambient_intsty)

    shader.uniform_float("cloud_1.coverage_shape",      prop.cld_1_coverage_shape)

    shader.uniform_float("cloud_1.atten",               prop.cld_1_atten)
    shader.uniform_float("cloud_1.contr",               prop.cld_1_contr)
    shader.uniform_float("cloud_1.eccen",               prop.cld_1_eccen)

    shader.uniform_float("cloud_1.coverage_scale",      coverage_scale)
    shader.uniform_float("cloud_1.shape_scale",         shape_scale)
    shader.uniform_float("cloud_1.detail_scale",        detail_scale)

    shader.uniform_int("cloud_1.curl_octaves",          prop.cld_1_curl_octaves)

    shader.uniform_float("cloud_1.coverage_intsty",     prop.cld_1_coverage_intsty)
    shader.uniform_float("cloud_1.shape_intsty",        0.6 * prop.cld_1_shape_intsty)
    shader.uniform_float("cloud_1.detail_intsty",       prop.cld_1_detail_intsty)

    shader.uniform_float("cloud_1.pos_offset",          prop.cld_1_pos_offset * 100.0)
    shader.uniform_float("cloud_1.coverage_offset",     prop.cld_1_coverage_offset * 100.0)
    shader.uniform_float("cloud_1.shape_offset",        prop.cld_1_shape_offset * 100.0)
    shader.uniform_float("cloud_1.detail_offset",       prop.cld_1_detail_offset * 100.0)

    #shader.uniform_float("scale_0",                     prop.scale_0)
    #shader.uniform_float("scale_1",                     prop.scale_1)
    #shader.uniform_int("scale_1",                       prop.scale_1)
    #shader.uniform_float("scale_2",                     prop.scale_2)
    shader.uniform_float("scale_3",                     prop.scale_3)

    cld_1_trans = Matrix.Translation(cld_domain_center + Vector((0,0,6360e3)))
    cld_1_rot = Matrix.Rotation(prop.cld_1_rotation, 4, 'Z')

    cld_1_transform = cld_1_rot @ cld_1_trans
    cld_1_transform.invert()
    
    shader.uniform_float("cloud_1.transform", cld_1_transform)

    # ---------------------------------------------------------------------------- #

    bgl_uniform_sampler(shader,     "noise_tex_3D_64",      globals.NOISE_TEXTURES[0],  dim=3, wrap='REPEAT', filter='LINEAR', slot=0)
    bgl_uniform_sampler(shader,     "noise_tex_3D_128",     globals.NOISE_TEXTURES[1],  dim=3, wrap='REPEAT', filter='LINEAR', slot=1)
    bgl_uniform_sampler(shader,     "noise_tex_2D_2048",    globals.NOISE_TEXTURES[2],  dim=2, wrap='REPEAT', filter='LINEAR', slot=2)
    bgl_uniform_sampler(shader,     "blue_noise",           globals.NOISE_TEXTURES[3],  dim=2, wrap='REPEAT', filter='LINEAR', slot=3)

    bgl_uniform_sampler(shader,     "moon_albedo_tex",      globals.MOON_TEXTURES[0],   dim=2, wrap='REPEAT', filter='LINEAR', slot=4)
    bgl_uniform_sampler(shader,     "moon_normal_tex",      globals.MOON_TEXTURES[1],   dim=2, wrap='REPEAT', filter='LINEAR', slot=5)

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

        _shader.uniform_bool("enable_moon", enable_moon)
        _shader.uniform_bool("enable_sun", enable_sun)

        _shader.uniform_float("sun.dir", compute_dir(sun_prop.sun_elevation, sun_prop.sun_rotation))
        _shader.uniform_bool("enable_sun_as_light", sun_prop.sun_enable_light)

        _shader.uniform_float("moon.dir", compute_dir(moon_prop.moon_elevation, moon_prop.moon_rotation))
        _shader.uniform_bool("enable_moon_as_light", moon_prop.moon_enable_light)
        
        globals.BATCH["sky"].draw(_shader)
    
    with fbo_1.bind():
        gpu.state.depth_test_set('NONE')
        _shader = globals.SHADER["sky_irra"]
        _shader.bind()
        _shader.uniform_float("img_size", irra_dim)
        bgl_uniform_sampler(_shader, "env_tex", fbo_0.color_texture, dim=2, wrap='REPEAT', filter='LINEAR', slot=0)
        globals.BATCH["sky_irra"].draw(_shader)

def draw_env_img(env_img, irra_tex, render_context):
    cloud_prop = bpy.context.scene.cloud_props
    atmo_prop = bpy.context.scene.atmo_props
    sun_prop = bpy.context.scene.sun_props
    stars_prop = bpy.context.scene.stars_props
    moon_prop = bpy.context.scene.moon_props
    render_prop = bpy.context.scene.render_props

    if render_context == 'VIEWPORT':   
        if (render_prop.enable_separate_steps_viewport):
            cld_0_max_steps = render_prop.cld_0_max_steps_viewport
            cld_1_max_steps = render_prop.cld_1_max_steps_viewport
        else:
            cld_0_max_steps = render_prop.max_steps_viewport
            cld_1_max_steps = render_prop.max_steps_viewport

        if (render_prop.enable_separate_light_steps_viewport):
            cld_0_max_light_steps = render_prop.cld_0_max_light_steps_viewport
            cld_1_max_light_steps = render_prop.cld_1_max_light_steps_viewport
        else:
            cld_0_max_light_steps = render_prop.max_light_steps_viewport
            cld_1_max_light_steps = render_prop.max_light_steps_viewport

        enable_atm = atmo_prop.atm_show_viewport
        enable_cld = cloud_prop.cld_show_viewport
        enable_moon = moon_prop.moon_show_viewport
        enable_sun = sun_prop.sun_show_viewport
        enable_stars = stars_prop.stars_show_viewport
        enable_bicubic = False
        
    elif render_context == 'RENDER':
        if (render_prop.enable_separate_steps_render):
            cld_0_max_steps = render_prop.cld_0_max_steps_render
            cld_1_max_steps = render_prop.cld_1_max_steps_render
        else:
            cld_0_max_steps = render_prop.max_steps_render
            cld_1_max_steps = render_prop.max_steps_render

        if (render_prop.enable_separate_light_steps_render):
            cld_0_max_light_steps = render_prop.cld_0_max_light_steps_render
            cld_1_max_light_steps = render_prop.cld_1_max_light_steps_render
        else:
            cld_0_max_light_steps = render_prop.max_light_steps_render
            cld_1_max_light_steps = render_prop.max_light_steps_render

        enable_atm = atmo_prop.atm_show_render
        enable_cld = cloud_prop.cld_show_render
        enable_moon = moon_prop.moon_show_render
        enable_sun = sun_prop.sun_show_render
        enable_stars = stars_prop.stars_show_render
        enable_bicubic = render_prop.enable_bicubic

    tile_pos = env_img.get_tile_pos()
    tile_size = env_img.get_tile_size()
    img_size = env_img.get_size()
    offscreen = env_img.get_offscreen()

    with offscreen.bind():
        if env_img.use_tiling():
            gpu.state.viewport_set(tile_pos[0]*tile_size, tile_pos[1]*tile_size, tile_size, tile_size)

        gpu.state.depth_test_set('NONE')

        _shader = globals.SHADER["env_img"]

        _shader.bind()
        
        _shader.uniform_float("img_size", img_size)

        _shader.uniform_int("cloud_0.max_steps", cld_0_max_steps)
        _shader.uniform_int("cloud_1.max_steps", cld_1_max_steps)

        _shader.uniform_int("cloud_0.max_light_steps", cld_0_max_light_steps)
        _shader.uniform_int("cloud_1.max_light_steps", cld_1_max_light_steps)

        _shader.uniform_float("altitude", atmo_prop.prop_sky_altitude)

        #_shader.uniform_bool("enable_bicubic", enable_bicubic)

        _shader.uniform_bool("enable_atm", enable_atm)
        _shader.uniform_bool("enable_cld", enable_cld)
        _shader.uniform_bool("enable_moon", enable_moon)
        _shader.uniform_bool("enable_sun", enable_sun)
        _shader.uniform_bool("enable_stars", enable_stars)

        atmo_uniforms(_shader)
        cloud_uniforms(_shader)
        moon_uniforms(_shader)
        sun_uniforms(_shader)
        stars_uniforms(_shader)

        bgl_uniform_sampler(_shader, "irra_tex", irra_tex, dim=2, wrap='REPEAT', filter='LINEAR', slot=6)

        globals.BATCH["env_img"].draw(_shader)

    env_img.increment_tile()

def update_viewport_offscreen(self, context):
    scr_width = context.region.width
    scr_height = context.region.height

    if (self._scr_width != scr_width) or (self._scr_height != scr_height):
        self._scr_width = scr_width
        self._scr_height = scr_height

        if self._offscreen_viewport != None:
            self._offscreen_viewport.free()
        self._offscreen_viewport = new_offscreen_fbo(self._scr_width, self._scr_height)

def pre_draw_viewport(self, context, irra_tex):
    cloud_prop = context.scene.cloud_props
    atmo_prop = context.scene.atmo_props 
    sun_prop = context.scene.sun_props  
    stars_prop = context.scene.stars_props  
    moon_prop = context.scene.moon_props
    render_prop = context.scene.render_props
    
    update_viewport_offscreen(self, context)

    tex_width = int(float(self._scr_width)/float(render_prop.viewport_pixel_size))       
    tex_height = int(float(self._scr_height)/float(render_prop.viewport_pixel_size))

    if (render_prop.enable_separate_steps_viewport):
        cld_0_max_steps = render_prop.cld_0_max_steps_viewport
        cld_1_max_steps = render_prop.cld_1_max_steps_viewport
    else:
        cld_0_max_steps = render_prop.max_steps_viewport
        cld_1_max_steps = render_prop.max_steps_viewport

    if (render_prop.enable_separate_light_steps_viewport):
        cld_0_max_light_steps = render_prop.cld_0_max_light_steps_viewport
        cld_1_max_light_steps = render_prop.cld_1_max_light_steps_viewport
    else:
        cld_0_max_light_steps = render_prop.max_light_steps_viewport
        cld_1_max_light_steps = render_prop.max_light_steps_viewport
    
    with self._offscreen_viewport.bind():
        gpu.state.depth_test_set('NONE')
        _shader = globals.SHADER["viewport"]

        _shader.bind()

        proj_mat = context.region_data.perspective_matrix
        
        inv_vp_mat = proj_mat
        inv_vp_mat = inv_vp_mat.inverted()
        
        _shader.uniform_float("img_size", (tex_width, tex_height))
        
        _shader.uniform_float("inv_vp_mat", inv_vp_mat)

        _shader.uniform_int("cloud_0.max_steps", cld_0_max_steps)
        _shader.uniform_int("cloud_1.max_steps", cld_1_max_steps)

        _shader.uniform_int("cloud_0.max_light_steps", cld_0_max_light_steps)
        _shader.uniform_int("cloud_1.max_light_steps", cld_1_max_light_steps)

        _shader.uniform_float("altitude", atmo_prop.prop_sky_altitude)

        #_shader.uniform_bool("enable_bicubic", False)

        _shader.uniform_bool("enable_atm", atmo_prop.atm_show_viewport)
        _shader.uniform_bool("enable_cld", cloud_prop.cld_show_viewport)
        _shader.uniform_bool("enable_moon", moon_prop.moon_show_viewport)
        _shader.uniform_bool("enable_sun", sun_prop.sun_show_viewport)
        _shader.uniform_bool("enable_stars", stars_prop.stars_show_viewport)
        _shader.uniform_bool("enable_pole_visualizer", stars_prop.stars_show_pole)
        
        _shader.uniform_float("pole_dir", compute_dir(stars_prop.stars_pole_elevation, stars_prop.stars_pole_rotation))

        atmo_uniforms(_shader)
        cloud_uniforms(_shader)
        moon_uniforms(_shader)
        sun_uniforms(_shader)
        stars_uniforms(_shader)

        bgl_uniform_sampler(_shader, "irra_tex", irra_tex, dim=2, wrap='REPEAT', filter='LINEAR', slot=6)
 
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

    tex_width = int(float(self._scr_width)/float(prop.viewport_pixel_size))       
    tex_height = int(float(self._scr_height)/float(prop.viewport_pixel_size))

    gpu.state.depth_test_set('LESS')

    _shader = globals.SHADER["screen"]
    _shader.bind()

    _shader.uniform_float("projection", proj_view_mat @ obj_mat)

    _shader.uniform_float("scr_size", (self._scr_width, self._scr_height))
    _shader.uniform_float("tex_size", (tex_width, tex_height))
    _shader.uniform_float("gamma", scene.view_settings.gamma)
    _shader.uniform_float("env_img_strength", prop.env_img_strength)

    bgl_uniform_sampler(_shader, "tex", self._offscreen_viewport.color_texture, dim=2, wrap='REPEAT', filter='NEAREST', slot=0)

    globals.BATCH["screen"].draw(_shader)

    gpu.state.depth_test_set('NONE')
