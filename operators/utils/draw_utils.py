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

from ... import globals
from .general_utils import compute_dir, bgl_uniform_sampler
from .shader_utils import atmo_uniforms, cloud_uniforms, sun_uniforms, moon_uniforms

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