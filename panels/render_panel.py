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
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )                
from bpy.types import (Panel,
                       PropertyGroup,
                       )
                       
from .panel_utils import update_env_img_size, update_env_img_strength
from ..operators.render import STRATUS_OT_render_animation
from ..operators.bake import STRATUS_OT_bake_env_img
from ..operators.viewport_editor import STRATUS_OT_viewport_editor

class STRATUS_RenderProperties(PropertyGroup):
    env_img_size = [
        ('1', "1K", '1024 x 512', '', 1),
        ('2', "2K", '2048 x 1024', '', 2),
        ('4', "4K", '4096 x 2048', '', 4),
        ('8', "8K", '8192 x 4096', '', 8),
        ('16', "16K", '16384 x 8192', '', 16),
        ('24', "24K", '24576 x 12288', '', 24),
    ]

    tile_size = [
        ('0', "256", '256 x 256', '', 256),
        ('1', "512", '512 x 512', '', 512),
        ('2', "1024", '1024 x 1024', '', 1024),
        ('3', "2048", '2048 x 2048', '', 2048),
        ('4', "4096", '4096 x 4096', '', 4096),
    ]
    
    pixel_size = [
        ('1', "1x", 'Render at full resolution', '', 1),
        ('2', "2x", 'Render at 50%% resolution', '', 2),
        ('4', "4x", 'Render at 25%% resolution', '', 4),
        ('8', "8x", 'Render at 12.5%% resolution', '', 8),
    ]

    env_img_strength: FloatProperty(
        name = "env_img_strength",
        description = "A float property",
        default = 0.1,
        min = 0.0,
        update=update_env_img_strength
    ) 

    env_img_render_size: EnumProperty(
        items=env_img_size,
        description="(1024 x 512) * size",
        default="4",
        update=update_env_img_size
    )

    env_img_viewport_size: EnumProperty(
        items=env_img_size,
        description="(1024 x 512) * size",
        default="1",
        update=update_env_img_size
    )

    max_steps_render: IntProperty(
        name = "Max Steps",
        description="Maximum number of steps before giving up.",
        default=1024,
        min= 2
    )

    max_light_steps_render: IntProperty(
        name = "Max Light Steps",
        description="Maximum number of steps before giving up.",
        default=128,
        min= 2
    ) 

    max_steps_viewport: IntProperty(
        name = "Max Steps",
        description="Maximum number of steps before giving up.",
        default=300,
        min= 2
    )    
    
    max_light_steps_viewport: IntProperty(
        name = "Max Light Steps",
        description="Maximum number of steps before giving up.",
        default=16,
        min= 2
    )

    viewport_pixel_size: EnumProperty(
        name = "Pixel Size",
        items=pixel_size,
        description="Pixel size for viewport rendering.",
        default="1"
    )

    enable_tiling: BoolProperty(
        name = "Use Tiling",
        description="Render high resolution images in tiles to reduce memory usage, using the specified tile size.",
        default = True,
    )

    render_tile_size: EnumProperty(
        name = "Tile Size",
        items=tile_size,
        description="Tile Size",
        default="2"
    )

class STRATUS_PT_render_panel(bpy.types.Panel):
    bl_label = "Render Settings"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        prop = context.scene.render_props

        layout.prop(prop, "env_img_strength")

class STRATUS_PT_sub_render_panel(bpy.types.Panel):
    bl_parent_id = "STRATUS_PT_render_panel"
    bl_label = "Render"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        prop = context.scene.render_props

        layout.operator(STRATUS_OT_bake_env_img.bl_idname, text="Bake", icon="RENDER_STILL")
        layout.operator(STRATUS_OT_render_animation.bl_idname, text="Render Animation", icon="RENDER_ANIMATION")

        layout.separator()

        col_0 = layout.column()
        col_0.label(text="Environment Texture Size")
        col_0.prop(prop, "env_img_render_size")

        layout.separator()

        layout.prop(prop, "enable_tiling")
        col_1 = layout.column()
        col_1.prop(prop, "render_tile_size", text="Tile Size")
        col_1.enabled = prop.enable_tiling
        
        layout.separator()

        layout.prop(prop, "max_steps_render")
        layout.prop(prop, "max_light_steps_render")

class STRATUS_PT_sub_viewport_panel(bpy.types.Panel):
    bl_parent_id = "STRATUS_PT_render_panel"
    bl_label = "Viewport"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        prop = context.scene.render_props

        layout.operator(STRATUS_OT_viewport_editor.bl_idname, text="Start Viewport Editor", icon="RESTRICT_VIEW_OFF")

        layout.separator()

        layout.prop(prop, "viewport_pixel_size")

        layout.separator()

        col = layout.column()
        col.label(text="Environment Texture Size")
        col.prop(prop, "env_img_viewport_size", text="")

        layout.separator()

        layout.prop(prop, "max_steps_viewport")
        layout.prop(prop, "max_light_steps_viewport")
