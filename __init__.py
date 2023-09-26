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

bl_info = {
    "name": "Stratus",
    "description": "Generates HDRIs with realistic skys.",
    "author": "Jake Kurtz",
    'license': 'GPL-3.0-only',
    "version": (1, 1, 0),
    "blender": (3, 4, 1),
    'location': 'View3D > Sidebar > Stratus Tab',
    "doc_url": "https://jakekurtz.ca",
    "category": "Rendering"
}

import bpy
import os
import bpy.utils.previews

from . import globals

from .operators.render import STRATUS_OT_render_animation
from .operators.bake import STRATUS_OT_bake_env_img
from .operators.bake_seq import STRATUS_OT_bake_seq
from .operators.viewport_editor import STRATUS_OT_viewport_editor, STRATUS_OT_kill_viewport_editor
from .operators.prop_observer import STRATUS_OT_prop_observer

from .panels.main_panel import (
    STRATUS_main_Properties,
    STRATUS_PT_main,
)

from .panels.cloud_panel import (
    STRATUS_CloudProperties, 

    STRATUS_PT_cloud_layer_0,
    STRATUS_PT_cloud_layer_0_transform,
    STRATUS_PT_cloud_layer_0_density,
    STRATUS_PT_cloud_layer_0_light,
    STRATUS_PT_cloud_layer_0_shape,
    STRATUS_PT_cloud_layer_0_shape_coverage_noise,
    STRATUS_PT_cloud_layer_0_shape_shape_noise,
    STRATUS_PT_cloud_layer_0_shape_detail_noise,
    STRATUS_PT_cloud_layer_0_shape_offsets,
    
    STRATUS_PT_cloud_layer_1,
    STRATUS_PT_cloud_layer_1_transform,
    STRATUS_PT_cloud_layer_1_density,
    STRATUS_PT_cloud_layer_1_light,
    STRATUS_PT_cloud_layer_1_shape,
    STRATUS_PT_cloud_layer_1_shape_coverage_noise,
    STRATUS_PT_cloud_layer_1_shape_shape_noise,
    STRATUS_PT_cloud_layer_1_shape_detail_noise,
    STRATUS_PT_cloud_layer_1_shape_offsets,
    )

from .panels.atmo_panel import (
    STRATUS_AtmoProperties,
    STRATUS_PT_atmo_panel)
from .panels.sun_panel import (
    STRATUS_SunProperties,
    STRATUS_PT_sun_panel)
from .panels.stars_panel import (
    STRATUS_StarsProperties,
    STRATUS_PT_stars)
    #STRATUS_PT_stars,
    #STRATUS_PT_stars_pole)
from .panels.moon_panel import (
    STRATUS_MoonProperties,
    STRATUS_PT_moon,
    STRATUS_PT_moon_phase)
from .panels.render_panel import (
    STRATUS_RenderProperties,
    STRATUS_PT_render_settings,
    STRATUS_PT_render,
    STRATUS_PT_render_performance,
    STRATUS_PT_render_output,
    STRATUS_PT_viewport,
    STRATUS_PT_viewport_steps)

classes = (
    STRATUS_main_Properties,
    STRATUS_CloudProperties, 
    STRATUS_AtmoProperties, 
    STRATUS_SunProperties, 
    STRATUS_StarsProperties, 
    STRATUS_MoonProperties, 
    STRATUS_RenderProperties,

    STRATUS_OT_bake_env_img,
    STRATUS_OT_bake_seq,
    STRATUS_OT_render_animation, 
    STRATUS_OT_viewport_editor,
    STRATUS_OT_kill_viewport_editor, 
    STRATUS_OT_prop_observer,

    STRATUS_PT_main,

    STRATUS_PT_cloud_layer_0,
    STRATUS_PT_cloud_layer_0_transform,
    STRATUS_PT_cloud_layer_0_shape,
    STRATUS_PT_cloud_layer_0_density,
    STRATUS_PT_cloud_layer_0_light,
    STRATUS_PT_cloud_layer_0_shape_coverage_noise,
    STRATUS_PT_cloud_layer_0_shape_shape_noise,
    STRATUS_PT_cloud_layer_0_shape_detail_noise,
    STRATUS_PT_cloud_layer_0_shape_offsets,

    STRATUS_PT_cloud_layer_1,
    STRATUS_PT_cloud_layer_1_transform,
    STRATUS_PT_cloud_layer_1_shape,
    STRATUS_PT_cloud_layer_1_density,
    STRATUS_PT_cloud_layer_1_light,
    STRATUS_PT_cloud_layer_1_shape_coverage_noise,
    STRATUS_PT_cloud_layer_1_shape_shape_noise,
    STRATUS_PT_cloud_layer_1_shape_detail_noise,
    STRATUS_PT_cloud_layer_1_shape_offsets,

    STRATUS_PT_atmo_panel,
    STRATUS_PT_sun_panel,
    STRATUS_PT_stars,
    #STRATUS_PT_stars_pole,
    STRATUS_PT_moon,
    STRATUS_PT_moon_phase,

    STRATUS_PT_render_settings,
    STRATUS_PT_viewport,
    STRATUS_PT_viewport_steps,
    STRATUS_PT_render,
    STRATUS_PT_render_performance,
    STRATUS_PT_render_output
    )

def register():
    
    # ------------------------------- Custom Icons ------------------------------- #
    globals.ICONS = bpy.utils.previews.new()
    icons_dir = bpy.utils.user_resource('SCRIPTS', path='addons\Stratus' , create=False)

    globals.ICONS.load("CELE_ICON", os.path.join(icons_dir, "icons\cele_icon.png"), 'IMAGE')
    globals.ICONS.load("CUMU_ICON", os.path.join(icons_dir, "icons\cumu_icon.png"), 'IMAGE')
    globals.ICONS.load("CIRR_ICON", os.path.join(icons_dir, "icons\cirr_icon.png"), 'IMAGE')

    globals.CELE_ICON = globals.ICONS["CELE_ICON"].icon_id
    globals.CUMU_ICON = globals.ICONS["CUMU_ICON"].icon_id
    globals.CIRR_ICON = globals.ICONS["CIRR_ICON"].icon_id
    # ---------------------------------------------------------------------------- #

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.main_props = bpy.props.PointerProperty(type=STRATUS_main_Properties)
    bpy.types.Scene.cloud_props = bpy.props.PointerProperty(type=STRATUS_CloudProperties)
    bpy.types.Scene.atmo_props = bpy.props.PointerProperty(type=STRATUS_AtmoProperties)
    bpy.types.Scene.sun_props = bpy.props.PointerProperty(type=STRATUS_SunProperties)
    bpy.types.Scene.stars_props = bpy.props.PointerProperty(type=STRATUS_StarsProperties)
    bpy.types.Scene.moon_props = bpy.props.PointerProperty(type=STRATUS_MoonProperties)
    bpy.types.Scene.render_props = bpy.props.PointerProperty(type=STRATUS_RenderProperties)

def unregister():
    del bpy.types.Scene.main_props
    del bpy.types.Scene.cloud_props
    del bpy.types.Scene.atmo_props
    del bpy.types.Scene.sun_props
    del bpy.types.Scene.stars_props
    del bpy.types.Scene.moon_props
    del bpy.types.Scene.render_props

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()