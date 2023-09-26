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
from .main_panel import (STRATUS_PT_main, STRATUS_main_Properties)
from ..operators.render import STRATUS_OT_render_animation
from ..operators.bake import STRATUS_OT_bake_env_img
from ..operators.bake_seq import STRATUS_OT_bake_seq
from ..operators.viewport_editor import STRATUS_OT_viewport_editor, STRATUS_OT_kill_viewport_editor

class STRATUS_RenderProperties(PropertyGroup):

    pixel_size = [
        ('1', "1x", 'Render at full resolution', '', 1),
        ('2', "2x", 'Render at 50%% resolution', '', 2),
        ('4', "4x", 'Render at 25%% resolution', '', 4),
        ('8', "8x", 'Render at 12.5%% resolution', '', 8),
    ]

    color_modes = [
        ('RGB', 'RGB', '', '', 0),
        ('RGBA', 'RGBA', '', '', 1)
    ]

    color_spaces = [
        ('Filmic Log', 'Filmic Log', '', '', 0),
        ('Filmic sRGB', 'Filmic sRGB', '', '', 1),
        ('Linear', 'Linear', '', '', 2),
        ('Linear ACES', 'Linear ACES', '', '', 3),
        ('Linear ACEScg', 'Linear ACEScg', '', '', 4),
        ('Non-Color', 'Non-Color', '', '', 5),
        ('Raw', 'Raw', '', '', 6),
        ('sRGB', 'sRGB', '', '', 7),
        ('XYZ', 'XYZ', '', '', 8),
    ]

    file_formats = [
        ('OPEN_EXR_MULTILAYER', "OpenEXR MultiLayer", 'File format to save baked environment texture as: OpenEXR MultiLayer', 'IMAGE_DATA', 0),
        ('OPEN_EXR', "OpenEXR", 'File format to save baked environment texture as: OpenEXR', 'IMAGE_DATA', 1),
        ('HDR', "Radiance HDR", 'File format to save baked environment texture as: Radiance HDR', 'IMAGE_DATA', 2),
    ]

    exr_codecs = [
        ('DWAB', "DWAB (lossy)", 'Codec settings for OpenEXR: DWAB (lossy)', '', 0),
        ('DWAA', "DWAA (lossy)", 'Codec settings for OpenEXR: DWAA (lossy)', '', 1),
        ('B44A', "B44A (lossy)", 'Codec settings for OpenEXR: B44A (lossy)', '', 2),
        ('B44', "B44 (lossy)", 'Codec settings for OpenEXR: B44 (lossy)', '', 3),
        ('ZIPS', "ZIPS (lossless)", 'Codec settings for OpenEXR: ZIPS (lossless)', '', 4),
        ('RLE', "RLE (lossless)", 'Codec settings for OpenEXR: RLE (lossless)', '', 5),
        ('PIZ', "PIZ (lossless)", 'Codec settings for OpenEXR: PIZ (lossless)', '', 6),
        ('ZIP', "ZIP (lossless)", 'Codec settings for OpenEXR: ZIP (lossless)', '', 7),
        ('PXR24', "Pxr24 (lossy)", 'Codec settings for OpenEXR: Pxr24 (lossy)', '', 8),
        ('NONE', "None", 'Codec settings for OpenEXR: None', '', 9),
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
        default="4",
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
        name = "Steps",
        description="Maximum number of steps before giving up.",
        default=300,
        min= 2,
        max=5000
    )
    cld_0_max_steps_render: IntProperty(
        name = "Cirrius Steps",
        description="Maximum number of steps before giving up.",
        default=300,
        min= 2,
        max=5000
    )
    cld_1_max_steps_render: IntProperty(
        name = "Cumulus Steps",
        description="Maximum number of steps before giving up.",
        default=300,
        min= 2,
        max=5000
    )

    max_light_steps_render: IntProperty(
        name = "Light Steps",
        description="Maximum number of steps before giving up.",
        default=64,
        min= 2,
        max=1000
    )
    cld_0_max_light_steps_render: IntProperty(
        name = "Cirrius Light Steps",
        description="Maximum number of steps before giving up.",
        default=64,
        min= 2,
        max=1000
    )
    cld_1_max_light_steps_render: IntProperty(
        name = "Cumulus Light Steps",
        description="Maximum number of steps before giving up.",
        default=64,
        min= 2,
        max=1000
    ) 

    max_steps_viewport: IntProperty(
        name = "Steps",
        description="Maximum number of steps before giving up.",
        default=150,
        min= 2,
        max=5000
    )
    cld_0_max_steps_viewport: IntProperty(
        name = "Cirrius Steps",
        description="Maximum number of steps before giving up.",
        default=150,
        min= 2,
        max=5000
    )
    cld_1_max_steps_viewport: IntProperty(
        name = "Cumulus Steps",
        description="Maximum number of steps before giving up.",
        default=150,
        min= 2,
        max=5000
    )   
    
    max_light_steps_viewport: IntProperty(
        name = "Light Steps",
        description="Maximum number of steps before giving up.",
        default=16,
        min= 2,
        max=1000
    )
    cld_0_max_light_steps_viewport: IntProperty(
        name = "Cirrius Light Steps",
        description="Maximum number of steps before giving up.",
        default=16,
        min= 2,
        max=1000
    )
    cld_1_max_light_steps_viewport: IntProperty(
        name = "Cumulus Light Steps",
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
        default="3"
    )

    file_path: StringProperty(
        subtype="FILE_PATH",
        default='/tmp\\'
    )

    file_format: EnumProperty(
        name="File Format",
        items=file_formats,
        description="",
        default="OPEN_EXR"
    )

    exr_codec: EnumProperty(
        name="Codec",
        items=exr_codecs,
        description="",
        default="ZIP"
    )

    color_space: EnumProperty(
        name="Color Space",
        items=color_spaces,
        description="",
        default='sRGB'
    )

    color_mode: EnumProperty(
        name="Color",
        items=color_modes,
        description="",
        default="RGBA"
    )

    viewport_pinned: BoolProperty(
        default=False
    )
    render_pinned: BoolProperty(
        default=False
    )

class STRATUS_PT_render_settings(Panel):
    bl_parent_id = "STRATUS_PT_main"
    bl_label = "Render Settings"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        main_prop = scene.main_props
        return main_prop.panels == "REND"

    def draw(self, context):
        layout = self.layout
        prop = context.scene.render_props

        layout.prop(prop, "env_img_strength")

class STRATUS_PT_render(Panel):
    bl_label = "Render"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        main_prop = scene.main_props
        render_prop = scene.render_props
        return (main_prop.panels == "REND" or render_prop.render_pinned)

    def draw_header(self, context):
        scene = context.scene
        render_prop = scene.render_props
        
        the_icon = 'PINNED' if render_prop.render_pinned else 'UNPINNED'
        self.layout.prop(context.scene.render_props, "render_pinned", text="", icon=the_icon)

    def draw(self, context):
        layout = self.layout
        prop = context.scene.render_props

        box = layout.box()
        box.operator(STRATUS_OT_bake_env_img.bl_idname, text="Bake", icon="RENDER_STILL")
        box.operator(STRATUS_OT_bake_seq.bl_idname, text="Bake Sequence", icon="RENDER_ANIMATION")
        box.operator(STRATUS_OT_render_animation.bl_idname, text="Render Animation", icon="RENDER_ANIMATION")

        col_0 = layout.column()
        col_0.label(text="Environment Texture Size")
        col_0.prop(prop, "env_img_render_size", text="")

        layout.separator()

        #layout.prop(prop, "enable_bicubic")
class STRATUS_PT_render_performance(Panel):
    bl_parent_id = "STRATUS_PT_render"
    bl_label = "Performance"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        prop = context.scene.render_props

        layout.prop(prop, "enable_tiling")
        col_1 = layout.column()
        col_1.prop(prop, "render_tile_size", text="Tile Size")
        col_1.enabled = prop.enable_tiling

        layout.label(text="Steps")

        row = layout.row()

        sub_col = row.column()
        sub_col.enabled = not prop.enable_separate_steps_render
        sub_col.prop(prop, "max_steps_render")
        sub_col = row.column()
        sub_col.enabled = not prop.enable_separate_light_steps_render
        sub_col.prop(prop, "max_light_steps_render")

        layout.separator()

        row = layout.row()

        sub_col = row.column()
        sub_col.prop(prop, "enable_separate_steps_render")
        sub_col = row.column()
        sub_col.prop(prop, "enable_separate_light_steps_render")

        row = layout.row()

        sub_col = row.column()
        sub_col.enabled = prop.enable_separate_steps_render
        sub_col.prop(prop, "cld_0_max_steps_render")
        sub_col.prop(prop, "cld_1_max_steps_render")

        sub_col = row.column()
        sub_col.enabled = prop.enable_separate_light_steps_render
        sub_col.prop(prop, "cld_0_max_light_steps_render")
        sub_col.prop(prop, "cld_1_max_light_steps_render")

class STRATUS_PT_render_output(Panel):
    bl_parent_id = "STRATUS_PT_render"
    bl_label = "Sequence Output"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        prop = context.scene.render_props

        layout.prop(prop, "file_path", text="")
        layout.prop(prop, "file_format")

        if (prop.file_format in {'OPEN_EXR', 'OPEN_EXR_MULTILAYER'}):
            if (prop.file_format == 'OPEN_EXR'):
                col_row = layout.row(align=True)
                col_row.label(text="Color")
                col_row.prop(prop, "color_mode", expand=True)
            layout.prop(prop, "exr_codec")

class STRATUS_PT_viewport(Panel):
    bl_label = "Viewport"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        main_prop = scene.main_props
        render_prop = scene.render_props
        return (main_prop.panels == "REND" or render_prop.viewport_pinned)

    def draw_header(self, context):
        scene = context.scene
        render_prop = scene.render_props
        
        the_icon = 'PINNED' if render_prop.viewport_pinned else 'UNPINNED'
        self.layout.prop(context.scene.render_props, "viewport_pinned", text="", icon=the_icon)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.render_props

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
    bl_parent_id = "STRATUS_PT_viewport"
    bl_label = "Steps"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        prop = context.scene.render_props

        row = layout.row()

        sub_col = row.column()
        sub_col.enabled = not prop.enable_separate_steps_viewport
        sub_col.prop(prop, "max_steps_viewport")
        sub_col = row.column()
        sub_col.enabled = not prop.enable_separate_light_steps_viewport
        sub_col.prop(prop, "max_light_steps_viewport")

        layout.separator()

        row = layout.row()

        sub_col = row.column()
        sub_col.prop(prop, "enable_separate_steps_viewport")
        sub_col = row.column()
        sub_col.prop(prop, "enable_separate_light_steps_viewport")

        row = layout.row()

        sub_col = row.column()
        sub_col.enabled = prop.enable_separate_steps_viewport
        sub_col.prop(prop, "cld_0_max_steps_viewport")
        sub_col.prop(prop, "cld_1_max_steps_viewport")

        sub_col = row.column()
        sub_col.enabled = prop.enable_separate_light_steps_viewport
        sub_col.prop(prop, "cld_0_max_light_steps_viewport")
        sub_col.prop(prop, "cld_1_max_light_steps_viewport")
