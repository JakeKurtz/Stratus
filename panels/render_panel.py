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

from .. import globals
from .panel_utils import update_env_img_size, update_env_img_strength
from ..operators.render import STRATUS_OT_render_animation
from ..operators.bake import STRATUS_OT_bake_env_img
from ..operators.viewport_editor import STRATUS_OT_viewport_editor, STRATUS_OT_kill_viewport_editor

class STRATUS_RenderProperties(PropertyGroup):

    pixel_size = [
        ('1', "1x", 'Render at full resolution', '', 1),
        ('2', "2x", 'Render at 50%% resolution', '', 2),
        ('4', "4x", 'Render at 25%% resolution', '', 4),
        ('8', "8x", 'Render at 12.5%% resolution', '', 8),
    ]

    env_img_strength: FloatProperty(
        name = "Environment Image Strength",
        description = "Strength of background node in World shader.",
        default = 0.1,
        min = 0.0,
        update=update_env_img_strength
    ) 

    env_img_render_size: EnumProperty(
        items=globals.ENV_IMG_SIZE,
        description="(1024 x 512) * size",
        default="1",
        update=update_env_img_size
    )

    env_img_viewport_size: EnumProperty(
        items=globals.ENV_IMG_SIZE,
        description="(1024 x 512) * size",
        default="1",
        update=update_env_img_size
    )

    enable_separate_steps_viewport: BoolProperty(
        name = "Use Separate Steps",
        description="",
        default = False,
    )
    enable_separate_light_steps_viewport: BoolProperty(
        name = "Use Separate Light Steps",
        description="",
        default = False,
    )
    enable_separate_steps_render: BoolProperty(
        name = "Use Separate Steps",
        description="",
        default = False,
    )
    enable_separate_light_steps_render: BoolProperty(
        name = "Use Separate Light Steps",
        description="",
        default = False,
    )

    max_steps_render: IntProperty(
        name = "Max Steps",
        description="Maximum number of steps before giving up.",
        default=300,
        min= 2,
        max=5000
    )
    cld_0_max_steps_render: IntProperty(
        name = "Max Cirrius Steps",
        description="Maximum number of steps before giving up.",
        default=300,
        min= 2,
        max=5000
    )
    cld_1_max_steps_render: IntProperty(
        name = "Max Cumulus Steps",
        description="Maximum number of steps before giving up.",
        default=300,
        min= 2,
        max=5000
    )

    max_light_steps_render: IntProperty(
        name = "Max Light Steps",
        description="Maximum number of steps before giving up.",
        default=64,
        min= 2,
        max=1000
    )
    cld_0_max_light_steps_render: IntProperty(
        name = "Max Cirrius Light Steps",
        description="Maximum number of steps before giving up.",
        default=64,
        min= 2,
        max=1000
    )
    cld_1_max_light_steps_render: IntProperty(
        name = "Max Cumulus Light Steps",
        description="Maximum number of steps before giving up.",
        default=64,
        min= 2,
        max=1000
    ) 

    max_steps_viewport: IntProperty(
        name = "Max Steps",
        description="Maximum number of steps before giving up.",
        default=150,
        min= 2,
        max=5000
    )
    cld_0_max_steps_viewport: IntProperty(
        name = "Max Cirrius Steps",
        description="Maximum number of steps before giving up.",
        default=150,
        min= 2,
        max=5000
    )
    cld_1_max_steps_viewport: IntProperty(
        name = "Max Cumulus Steps",
        description="Maximum number of steps before giving up.",
        default=150,
        min= 2,
        max=5000
    )   
    
    max_light_steps_viewport: IntProperty(
        name = "Max Light Steps",
        description="Maximum number of steps before giving up.",
        default=16,
        min= 2,
        max=1000
    )
    cld_0_max_light_steps_viewport: IntProperty(
        name = "Max Cirrius Light Steps",
        description="Maximum number of steps before giving up.",
        default=16,
        min= 2,
        max=1000
    )
    cld_1_max_light_steps_viewport: IntProperty(
        name = "Max Cumulus Light Steps",
        description="Maximum number of steps before giving up.",
        default=16,
        min= 2,
        max=1000
    )

    viewport_pixel_size: EnumProperty(
        name = "Pixel Size",
        items=pixel_size,
        description="Pixel size for viewport rendering.",
        default="4"
    )

    enable_bicubic: BoolProperty(
        name = "Use Bicubic Sampling",
        description="Preserves fine details when magnifying textures. Requires 8x more samples than bilinear sampling.",
        default = False,
    )

    enable_tiling: BoolProperty(
        name = "Use Tiling",
        description="Render high resolution images in tiles to reduce memory usage, using the specified tile size.",
        default = True,
    )

    render_tile_size: EnumProperty(
        name = "Tile Size",
        items=globals.TILE_SIZE,
        description="Tile Size",
        default="2"
    )

class STRATUS_PT_render_panel(Panel):
    bl_label = "Rendering"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        prop = context.scene.render_props

        layout.prop(prop, "env_img_strength")
class STRATUS_PT_sub_render_panel(Panel):
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
        col_0.prop(prop, "env_img_render_size", text="")

        layout.separator()

        layout.prop(prop, "enable_tiling")
        col_1 = layout.column()
        col_1.prop(prop, "render_tile_size", text="Tile Size")
        col_1.enabled = prop.enable_tiling

        layout.prop(prop, "enable_bicubic")
    
class STRATUS_PT_sub_viewport_panel(Panel):
    bl_parent_id = "STRATUS_PT_render_panel"
    bl_label = "Viewport"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        prop = context.scene.render_props

        if globals.VIEWPORT_RUNNING:
            layout.operator(STRATUS_OT_kill_viewport_editor.bl_idname, text="Stop Viewport Editor", icon="CANCEL")
        else:
            layout.operator(STRATUS_OT_viewport_editor.bl_idname, text="Start Viewport Editor", icon="RESTRICT_VIEW_OFF")

        layout.separator()

        layout.prop(prop, "viewport_pixel_size")

        layout.separator()

        col = layout.column()
        col.label(text="Environment Texture Size")
        col.prop(prop, "env_img_viewport_size", text="")

class STRATUS_PT_viewport_steps(Panel):
    bl_parent_id = "STRATUS_PT_sub_viewport_panel"
    bl_label = "Steps"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        prop = context.scene.render_props

        col = layout.column()
        sub = col.row()
        sub.enabled = not prop.enable_separate_steps_viewport
        sub.prop(prop, "max_steps_viewport")
        
        col = layout.column()
        sub = col.row()
        sub.enabled = not prop.enable_separate_light_steps_viewport
        sub.prop(prop, "max_light_steps_viewport")

        layout.separator()
        layout.prop(prop, "enable_separate_steps_viewport")

        grid_0 = layout.grid_flow(columns=1, align=True)
        grid_0.prop(prop, "cld_0_max_steps_viewport")
        grid_0.prop(prop, "cld_1_max_steps_viewport")

        layout.separator()
        layout.prop(prop, "enable_separate_light_steps_viewport")

        grid_1 = layout.grid_flow(columns=1, align=True)
        grid_1.prop(prop, "cld_0_max_light_steps_viewport")
        grid_1.prop(prop, "cld_1_max_light_steps_viewport")

        grid_0.enabled = prop.enable_separate_steps_viewport
        grid_1.enabled = prop.enable_separate_light_steps_viewport
class STRATUS_PT_render_steps(Panel):
    bl_parent_id = "STRATUS_PT_sub_render_panel"
    bl_label = "Steps"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        prop = context.scene.render_props


        col = layout.column()
        sub = col.row()
        sub.enabled = not prop.enable_separate_steps_render
        sub.prop(prop, "max_steps_render")

        col = layout.column()
        sub = col.row()
        sub.enabled = not prop.enable_separate_light_steps_render
        sub.prop(prop, "max_light_steps_render")

        layout.separator()
        layout.prop(prop, "enable_separate_steps_render")

        grid_0 = layout.grid_flow(columns=1, align=True)
        grid_0.prop(prop, "cld_0_max_steps_render")
        grid_0.prop(prop, "cld_1_max_steps_render")

        layout.separator()
        layout.prop(prop, "enable_separate_light_steps_render")

        grid_1 = layout.grid_flow(columns=1, align=True)
        grid_1.prop(prop, "cld_0_max_light_steps_render")
        grid_1.prop(prop, "cld_1_max_light_steps_render")

        grid_0.enabled = prop.enable_separate_steps_render
        grid_1.enabled = prop.enable_separate_light_steps_render
