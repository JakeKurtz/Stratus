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

from .panel_utils import update_prop

class STRATUS_CloudProperties(PropertyGroup):

    cld_show_viewport: BoolProperty(
        name="",
        description="Display clouds in viewport.",
        default = True,
        update=update_prop
        )
        
    cld_show_render: BoolProperty(
        name="",
        description="Display clouds in render.",
        default = True,
        update=update_prop
        )

    cld_ap_intsty: FloatProperty(
        name = "Atmospheric Perspective Intensity",
        description="The effect the atmosphere has on the appearance of the clouds as viewed from a distance.",
        default=0.5,
        min= 0.0,
        max = 1.0,
        update=update_prop
        )

    cld_ambient_intsty: FloatProperty(
        name = "Ambient Intensity",
        description = "The intensity of ambient light coming from the atmosphere.",
        default = 3.0,
        max = 100.0,
        min = 0.0,
        update=update_prop
        )    
        
    cld_G: FloatProperty(
        name = "G",
        description = "A float property",
        default = 0.0,
        max = 1.0,
        min = -1.0,
        update=update_prop
        )           

# ------------------------- Cloud Layer 0 Properties ------------------------- #

    cld_0_noise_sizes: FloatVectorProperty(
        name = "cld_0_noise_scale",
        description="",
        size = 3,
        step = 0.01,
        default=(1,1,1),
        update=update_prop
        )

    cld_0_top_roundness: FloatProperty(
        name = "cld_0_top_roundness",
        description = "",
        default = 0.2,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )      

    cld_0_bottom_roundness: FloatProperty(
        name = "cld_1_bottom_roundness",
        description = "",
        default = 0.2,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )    

    cld_0_enable: BoolProperty(
        name="",
        description="Enable cirro cloud layer.",
        default = True,
        update=update_prop
    )

    cld_0_density: FloatProperty(
        name = "Density",
        description = "Cloud layer density.",
        default = 0.25,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )

    cld_0_density_height: FloatProperty(
        name = "Density Height",
        description = "Cloud layer density height.",
        default = 0.45,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )

    cld_0_size: FloatProperty(
        name = "Size",
        description="Cloud layer size.",
        default=1.0,
        min= 0.0,
        max = 1,
        update=update_prop
        ) 

    cld_0_height: FloatProperty(
        name = "Height",
        description="Height from sea level.",
        subtype="DISTANCE",
        default=8000,
        min= 7000,
        max = 10000.0,
        update=update_prop
        )  

    cld_0_thickness: FloatProperty(
        name = "Thickness",
        description = "Cloud layer thickness.",
        default = 0.9,
        min = 0.01,
        max = 1.0,
        update=update_prop
        )    
        
    cld_0_powder_intsty: FloatProperty(
        name = "Powder Intensity",
        description = "Intensity of the powder effect.",
        default = 0.5,
        min = 0.0,
        max = 1.0,
        update=update_prop
        )

    cld_0_sigma_s: FloatVectorProperty(
        name = "Absorption",
        description="",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0),
        min=0.0, max=1.0,
        update=update_prop
        )

    cld_0_ap_intsty: FloatProperty(
        name = "Atmospheric Perspective Intensity",
        description="The effect the atmosphere has on the appearance of the clouds as viewed from a distance.",
        default=0.5,
        min= 0.0,
        max = 1.0,
        update=update_prop
        )

    cld_0_ambient_intsty: FloatProperty(
        name = "Ambient Intensity",
        description = "The intensity of ambient light coming from the atmosphere.",
        default = 3.0,
        max = 100.0,
        min = 0.0,
        update=update_prop
        )    
        
    cld_0_atten: FloatProperty(
        name = "Attenuation",
        description = "",
        default = 0.2,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )    
        
    cld_0_contr: FloatProperty(
        name = "Contribution",
        description = "",
        default = 0.5,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )

    cld_0_eccen: FloatProperty(
        name = "Eccentricity Attenuation",
        description = "",
        default = 0.5,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )

    cld_0_detail_intsty: FloatProperty(
        name = "Detail Noise Intensity",
        description="Intensity of detail noise applied to cloud layer.",
        default=-0.024,
        min= 0.0,
        max = 1.0,
        update=update_prop
        ) 

    cld_0_shape_intsty: FloatProperty(
        name = "Shape Noise Intensity",
        description="Intensity of shape noise applied to cloud layer.",
        default=-0.17,
        min= 0.0,
        max = 1.0,
        update=update_prop
        ) 

    cld_0_coverage_intsty: FloatProperty(
        name = "Coverage Noise Intensity",
        description="Intensity of coverage noise applied to cloud layer.",
        default=0.87,
        min= 0.0,
        max = 5.0,
        update=update_prop
        )

    cld_0_curl_octaves: IntProperty(
        name = "Curl Octaves",
        description="Intensity of Curl noise applied to cloud layer.",
        default=0,
        min= 0,
        max = 16,
        update=update_prop
        )
    
    cld_0_coverage_shape: FloatProperty(
        name = "Coverage Shape",
        description = "Interpolates between coverage noise maps.",
        default = 0.36,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )     
        
    cld_0_shape_shape: FloatProperty(
        name = "Shape",
        description = "Interpolates between noise maps.",
        default = 0.0,
        max = 1.0,
        min = 0.0,
        update=update_prop
        ) 
    
    cld_0_detail_shape: FloatProperty(
        name = "Shape",
        description = "Interpolates between noise maps.",
        default = 0.0,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )     
        
    cld_0_shape_inverse: FloatProperty(
        name = "Inverse",
        description = "Interpolates between noise maps.",
        default = 0.0,
        max = 1.0,
        min = 0.0,
        update=update_prop
        ) 

    cld_0_detail_inverse: FloatProperty(
        name = "Inverse",
        description = "Interpolates between noise maps.",
        default = 0.0,
        max = 1.0,
        min = 0.0,
        update=update_prop
        ) 
        
    cld_0_rotation: FloatProperty(
        name = "Rotation",
        description = "Cloud layer rotation.",
        default = 0.0,
        subtype="ANGLE",
        update=update_prop
        )

    cld_0_pos_offset: FloatVectorProperty(
        name = "Position Offset",
        description="Position offset.",
        subtype='TRANSLATION',
        size = 2,
        step = 1,
        default=(0,0),
        update=update_prop
        )

    cld_0_coverage_offset: FloatVectorProperty(
        name = "Coverage Noise Offset",
        description="Coverage noise texture offset.",
        subtype='TRANSLATION',
        size = 2,
        step = 1,
        default=(936,0),
        update=update_prop
        )

    cld_0_shape_offset: FloatVectorProperty(
        name = "Shape Noise Offset",
        description="Shape noise texture offset.",
        subtype='TRANSLATION',
        size = 2,
        step = 1,
        default=(0,0),
        update=update_prop
        )

    cld_0_detail_offset: FloatVectorProperty(
        name = "Detail Noise Offset",
        description="Detail noise texture offset.",
        subtype='TRANSLATION',
        size = 2,
        default=(0,0),
        step = 1,
        update=update_prop
        ) 

# ------------------------- Cloud Layer 1 Properties ------------------------- #

    cld_1_noise_sizes: FloatVectorProperty(
        name = "cld_1_noise_scale",
        description="",
        size = 3,
        step = 0.01,
        default=(1,1,1),
        update=update_prop
        )

    
    cld_1_top_roundness: FloatProperty(
        name = "cld_1_top_roundness",
        description = "",
        default = 0.2,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )        
        
    cld_1_bottom_roundness: FloatProperty(
        name = "cld_1_bottom_roundness",
        description = "",
        default = 0.2,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )    

    cld_1_enable: BoolProperty(
        name="",
        description="Enable cumulus cloud layer.",
        default = True,
        update=update_prop
    )

    cld_1_density: FloatProperty(
        name = "Density",
        description = "Cloud layer density.",
        default = 0.2,
        max = 5.0,
        min = 0.0,
        update=update_prop
        )

    cld_1_density_height: FloatProperty(
        name = "Density Height",
        description = "Cloud layer density height.",
        default = 0.45,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )

    cld_1_size: FloatProperty(
        name = "Size",
        description="Cloud layer size.",
        default=0.45,
        min= 0.0,
        max = 1,
        update=update_prop
        ) 

    cld_1_height: FloatProperty(
        name = "Height",
        description="Height from sea level.",
        subtype="DISTANCE",
        default=2000,
        min= 500.0,
        max = 6000.0,
        update=update_prop
        )  
          
    cld_1_thickness: FloatProperty(
        name = "Thickness",
        description = "Cloud layer thickness.",
        default = 2.5,
        min = 0.01,
        max = 2.5,
        update=update_prop
        )

    cld_1_powder_intsty: FloatProperty(
        name = "Powder Intensity",
        description = "Intensity of the powder effect.",
        default = 1.0,
        min = 0.0,
        max = 1.0,
        update=update_prop
        )

    cld_1_sigma_s: FloatVectorProperty(
        name = "Absorption",
        description="",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0),
        min=0.0, max=1.0,
        update=update_prop
        )

    cld_1_ap_intsty: FloatProperty(
        name = "Atmospheric Perspective Intensity",
        description="The effect the atmosphere has on the appearance of the clouds as viewed from a distance.",
        default=0.5,
        min= 0.0,
        max = 1.0,
        update=update_prop
        )

    cld_1_ambient_intsty: FloatProperty(
        name = "Ambient Intensity",
        description = "The intensity of ambient light coming from the atmosphere.",
        default = 3.0,
        max = 100.0,
        min = 0.0,
        update=update_prop
        )    
        
    cld_1_atten: FloatProperty(
        name = "Attenuation",
        description = "",
        default = 0.2,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )    
        
    cld_1_contr: FloatProperty(
        name = "Contribution",
        description = "",
        default = 0.5,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )

    cld_1_eccen: FloatProperty(
        name = "Eccentricity Attenuation",
        description = "",
        default = 0.5,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )

    cld_1_detail_intsty: FloatProperty(
        name = "Detail Noise Intensity",
        description="Intensity of detail noise applied to cloud layer.",
        default=0.05,
        min = 0.0,
        max = 1.0,
        update=update_prop
        ) 

    cld_1_shape_intsty: FloatProperty(
        name = "Shape Noise Intensity",
        description="Intensity of shape noise applied to cloud layer.",
        default=0.23,
        min = 0.0,
        max = 1.0,
        update=update_prop
        ) 

    cld_1_coverage_intsty: FloatProperty(
        name = "Coverage Noise Intensity",
        description="Intensity of coverage noise applied to cloud layer.",
        default=0.62,
        min= 0.0,
        max = 5.0,
        update=update_prop
        )

    cld_1_curl_octaves: IntProperty(
        name = "Curl Octaves",
        description="Intensity of Curl noise applied to cloud layer.",
        default=0,
        min= 0,
        max = 16,
        update=update_prop
        )

    cld_1_coverage_shape: FloatProperty(
        name = "Coverage Shape",
        description = "Interpolates between coverage noise maps.",
        default = 0.1,
        max = 1.0,
        min = 0.0,
        update=update_prop
        ) 

    cld_1_rotation: FloatProperty(
        name = "Rotation",
        description = "Cloud layer rotation.",
        default = 0.0,
        subtype="ANGLE",
        update=update_prop
        )

    cld_1_pos_offset: FloatVectorProperty(
        name = "Position Offset",
        description="Position offset.",
        subtype='TRANSLATION',
        size = 2,
        step = 1,
        default=(0,0),
        update=update_prop
        )

    cld_1_coverage_offset: FloatVectorProperty(
        name = "Coverage Noise Offset",
        description="Coverage noise texture offset.",
        subtype='TRANSLATION',
        size = 2,
        step = 1,
        default=(3671,9425),
        update=update_prop
        )

    cld_1_shape_offset: FloatVectorProperty(
        name = "Shape Noise Offset",
        description="Shape noise texture offset.",
        subtype='TRANSLATION',
        size = 2,
        step = 1,
        default=(0,0),
        update=update_prop
        )

    cld_1_detail_offset: FloatVectorProperty(
        name = "Detail Noise Offset",
        description="Detail noise texture offset.",
        subtype='TRANSLATION',
        size = 2,
        step = 1,
        default=(0,0),
        update=update_prop
        ) 

    scale_0: FloatProperty(
        name = "scale_0",
        description = "",
        default = 0.35,
        update=update_prop
        )

    scale_1: FloatProperty(
        name = "scale_1",
        description = "",
        default = 0.35,
        update=update_prop
        )
    '''
    scale_1: IntProperty(
        name = "scale_1",
        description = "",
        default = 1,
        min = 1,
        max = 16,
        update=update_prop
        )
    '''
    scale_2: FloatProperty(
        name = "scale_2",
        description = "",
        default = 0.8,
        min = 0.0,
        max = 1000000.0,
        update=update_prop
        )      
        
    scale_3: FloatProperty(
        name = "scale_3",
        description = "",
        default = 0.0,
        min = 0.0,
        update=update_prop
        )  

    sigma_s: FloatVectorProperty(
        name = "sigma_s",
        description="",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0),
        min=0.0, max=1.0,
        update=update_prop
        ) 

class STRATUS_PT_cloud_panel(Panel):
    bl_label = "Clouds"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.cloud_props
        
        icon_vp = 'RESTRICT_VIEW_OFF' if prop.cld_show_viewport else "RESTRICT_VIEW_ON"
        icon_r = 'RESTRICT_RENDER_OFF' if prop.cld_show_render else "RESTRICT_RENDER_ON"

        render_options = layout.row(align=True)
        render_options.label(text="Clouds")
        render_options.prop(prop, 'cld_show_viewport', icon=icon_vp)
        render_options.prop(prop, 'cld_show_render', icon=icon_r)

class STRATUS_PT_cloud_layer_0(Panel):
    bl_parent_id = "STRATUS_PT_cloud_panel"
    bl_label = "Cirro Layer"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        self.layout.prop(context.scene.cloud_props, "cld_0_enable")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.cloud_props
        layout.enabled = prop.cld_0_enable

        layout.prop(prop, "cld_1_noise_sizes")

        layout.prop(prop, "scale_0")
        layout.prop(prop, "scale_1")
        layout.prop(prop, "scale_2")
        layout.prop(prop, "scale_3")       
class STRATUS_PT_cloud_layer_0_transform(Panel):
    bl_parent_id = "STRATUS_PT_cloud_layer_0"
    bl_label = "Transform"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.cloud_props
        layout.enabled = prop.cld_0_enable

        grid_0 = layout.grid_flow(columns=1, align=True)
        grid_0.label(text="Location")
        grid_0.prop(prop, "cld_0_pos_offset", text="")
        grid_0.prop(prop, "cld_0_height", slider=True, text="Z")

        grid_1 = layout.grid_flow(columns=1, align=True)
        grid_1.label(text="Rotation")
        grid_1.prop(prop, "cld_0_rotation", text="")

        grid_2 = layout.grid_flow(columns=1, align=True)
        grid_2.label(text="Scale")
        grid_2.prop(prop, "cld_0_size", slider=True, text="")
class STRATUS_PT_cloud_layer_0_density(Panel):
    bl_parent_id = "STRATUS_PT_cloud_layer_0"
    bl_label = "Density"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.cloud_props
        layout.enabled = prop.cld_0_enable

        layout.prop(prop, "cld_0_density", slider=True)
        layout.prop(prop, "cld_0_density_height", slider=True)
class STRATUS_PT_cloud_layer_0_light(Panel):
    bl_parent_id = "STRATUS_PT_cloud_layer_0"
    bl_label = "Lighting"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.cloud_props
        layout.enabled = prop.cld_0_enable

        layout.prop(prop, "cld_0_sigma_s")
        layout.prop(prop, "cld_0_ap_intsty", slider=True)
        layout.prop(prop, "cld_0_ambient_intsty")

        grid = layout.grid_flow(columns=1, align=True)
        grid.label(text="Scattering")
        grid.prop(prop, "cld_0_atten")
        grid.prop(prop, "cld_0_contr")
        grid.prop(prop, "cld_0_eccen")
class STRATUS_PT_cloud_layer_0_shape(Panel):
    bl_parent_id = "STRATUS_PT_cloud_layer_0"
    bl_label = "Shaping"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.cloud_props
        layout.enabled = prop.cld_0_enable

        layout.prop(prop, "cld_0_bottom_roundness", slider=True)
        layout.prop(prop, "cld_0_top_roundness", slider=True)
        layout.prop(prop, "cld_0_thickness", slider=True)   
        layout.prop(prop, "cld_0_curl_octaves", slider=True)  
class STRATUS_PT_cloud_layer_0_shape_coverage_noise(Panel):
    bl_parent_id = "STRATUS_PT_cloud_layer_0_shape"
    bl_label = "Coverage"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.cloud_props
        layout.enabled = prop.cld_0_enable

        layout.prop(prop, "cld_0_coverage_intsty", slider=True, text="Intensity")
        layout.prop(prop, "cld_0_coverage_shape", slider=True, text="Shape")

        grid = layout.grid_flow(columns=1, align=True)
        grid.label(text="Offset")
        grid.prop(prop, "cld_0_coverage_offset", text="")
class STRATUS_PT_cloud_layer_0_shape_shape_noise(Panel):
    bl_parent_id = "STRATUS_PT_cloud_layer_0_shape"
    bl_label = "Shape"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.cloud_props
        layout.enabled = prop.cld_0_enable

        layout.prop(prop, "cld_0_shape_intsty", slider=True, text="Intensity")
        layout.prop(prop, "cld_0_shape_shape", slider=True, text="Shape")
        layout.prop(prop, "cld_0_shape_inverse", slider=True, text="Inflate")

        grid = layout.grid_flow(columns=1, align=True)
        grid.label(text="Offset")
        grid.prop(prop, "cld_0_shape_offset", text="")
class STRATUS_PT_cloud_layer_0_shape_detail_noise(Panel):
    bl_parent_id = "STRATUS_PT_cloud_layer_0_shape"
    bl_label = "Detail"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.cloud_props
        layout.enabled = prop.cld_0_enable

        layout.prop(prop, "cld_0_detail_intsty", slider=True, text="Intensity")
        layout.prop(prop, "cld_0_detail_shape", slider=True, text="Shape")
        layout.prop(prop, "cld_0_detail_inverse", slider=True, text="Inflate")

        grid = layout.grid_flow(columns=1, align=True)
        grid.label(text="Offset")
        grid.prop(prop, "cld_0_detail_offset", text="")

class STRATUS_PT_cloud_layer_1(Panel):
    bl_parent_id = "STRATUS_PT_cloud_panel"
    bl_label = "Cumulus Layer"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        self.layout.prop(context.scene.cloud_props, "cld_1_enable")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.cloud_props

        layout.enabled = prop.cld_1_enable
        layout.prop(prop, "scale_2")
        layout.prop(prop, "scale_3")
class STRATUS_PT_cloud_layer_1_transform(Panel):
    bl_parent_id = "STRATUS_PT_cloud_layer_1"
    bl_label = "Transform"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.cloud_props
        layout.enabled = prop.cld_1_enable

        grid_0 = layout.grid_flow(columns=1, align=True)
        grid_0.label(text="Location")
        grid_0.prop(prop, "cld_1_pos_offset", text="")
        grid_0.prop(prop, "cld_1_height", slider=True, text="Z")

        grid_1 = layout.grid_flow(columns=1, align=True)
        grid_1.label(text="Rotation")
        grid_1.prop(prop, "cld_1_rotation", text="")

        grid_2 = layout.grid_flow(columns=1, align=True)
        grid_2.label(text="Scale")
        grid_2.prop(prop, "cld_1_size", slider=True, text="")
class STRATUS_PT_cloud_layer_1_density(Panel):
    bl_parent_id = "STRATUS_PT_cloud_layer_1"
    bl_label = "Density"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.cloud_props
        layout.enabled = prop.cld_1_enable

        layout.prop(prop, "cld_1_density", slider=True)
        layout.prop(prop, "cld_1_density_height", slider=True)
class STRATUS_PT_cloud_layer_1_light(Panel):
    bl_parent_id = "STRATUS_PT_cloud_layer_1"
    bl_label = "Lighting"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.cloud_props
        layout.enabled = prop.cld_1_enable

        layout.prop(prop, "cld_1_sigma_s")
        layout.prop(prop, "cld_1_ap_intsty", slider=True)
        layout.prop(prop, "cld_1_ambient_intsty")

        grid = layout.grid_flow(columns=1, align=True)
        grid.label(text="Scattering")
        grid.prop(prop, "cld_1_atten")
        grid.prop(prop, "cld_1_contr")
        grid.prop(prop, "cld_1_eccen")
class STRATUS_PT_cloud_layer_1_shape(Panel):
    bl_parent_id = "STRATUS_PT_cloud_layer_1"
    bl_label = "Shaping"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.cloud_props
        layout.enabled = prop.cld_1_enable

        layout.prop(prop, "cld_1_bottom_roundness", slider=True)
        layout.prop(prop, "cld_1_top_roundness", slider=True)
        layout.prop(prop, "cld_1_thickness", slider=True)
        layout.prop(prop, "cld_1_curl_octaves", slider=True)
        
class STRATUS_PT_cloud_layer_1_shape_coverage_noise(Panel):
    bl_parent_id = "STRATUS_PT_cloud_layer_1_shape"
    bl_label = "Coverage"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.cloud_props
        layout.enabled = prop.cld_1_enable
        
        layout.prop(prop, "cld_1_coverage_intsty", slider=True, text="Intensity")
        layout.prop(prop, "cld_1_coverage_shape", slider=True, text="Shape")

        grid = layout.grid_flow(columns=1, align=True)
        grid.label(text="Offset")
        grid.prop(prop, "cld_1_coverage_offset", text="")
class STRATUS_PT_cloud_layer_1_shape_shape_noise(Panel):
    bl_parent_id = "STRATUS_PT_cloud_layer_1_shape"
    bl_label = "Shape"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.cloud_props
        layout.enabled = prop.cld_1_enable
        
        layout.prop(prop, "cld_1_shape_intsty", slider=True, text="Intensity")

        grid = layout.grid_flow(columns=1, align=True)
        grid.label(text="Offset")
        grid.prop(prop, "cld_1_shape_offset", text="")
class STRATUS_PT_cloud_layer_1_shape_detail_noise(Panel):
    bl_parent_id = "STRATUS_PT_cloud_layer_1_shape"
    bl_label = "Detail"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.cloud_props
        layout.enabled = prop.cld_1_enable

        layout.prop(prop, "cld_1_detail_intsty", slider=True, text="Intensity")

        grid = layout.grid_flow(columns=1, align=True)
        grid.label(text="Offset")
        grid.prop(prop, "cld_1_detail_offset", text="")