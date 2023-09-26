import bpy
from datetime import datetime

from .. import globals
from .utils.env_img_utils import ENVImage
from .utils.init_utils import init_shaders, init_textures, init_world_node_tree
from .utils.general_utils import new_offscreen_fbo, refresh_viewers
from .utils.draw_utils import draw_env_img, draw_irra_map

from mathutils import Matrix, Vector, Color
from math import radians

class STRATUS_OT_daytime_1(bpy.types.Operator):
    bl_idname = "stratus.preset_daytime_1"
    bl_label = "Daytime 1"
    
    def execute(self, context):
        
        cloud_prop = bpy.context.scene.cloud_props
        atmo_prop = bpy.context.scene.atmo_props
        sun_prop = bpy.context.scene.sun_props
        stars_prop = bpy.context.scene.stars_props
        moon_prop = bpy.context.scene.moon_props

        # ---------------------------------------------------------------------------- #
        #                                 Cloud Layer 0                                #
        # ---------------------------------------------------------------------------- #
        
        cloud_prop.cld_0_show_viewport = True
        cloud_prop.cld_0_show_render = True

        # --------------------------------- Transform -------------------------------- #

        cloud_prop.cld_0_pos_offset = Vector((0.0,0.0))
        cloud_prop.cld_0_height = 10000.0
        cloud_prop.cld_0_rotation = radians(0.0)
        cloud_prop.cld_0_size = 0.274766

        # ----------------------------------- Shape ---------------------------------- #

        cloud_prop.cld_0_top_roundness = 0.5
        cloud_prop.cld_0_bottom_roundness = 0.2
        cloud_prop.cld_0_thickness = 0.546561

        # --------------------------------- Coverage --------------------------------- #
        
        cloud_prop.cld_0_coverage_intsty = 3.73667
        cloud_prop.cld_0_coverage_shape = 0.274286
        cloud_prop.cld_0_curl_octaves = 16

        # ----------------------------------- Shape ---------------------------------- #

        cloud_prop.cld_0_shape_intsty = 1.0
        cloud_prop.cld_0_shape_shape = 1.0
        cloud_prop.cld_0_shape_inverse = 1.0

        # ---------------------------------- Detail ---------------------------------- #
        
        cloud_prop.cld_0_detail_intsty = 0.278804
        cloud_prop.cld_0_detail_shape = 0.0
        cloud_prop.cld_0_detail_inverse = 1.0
        cloud_prop.cld_0_detail_scale = 1.36

        # ---------------------------------- Offsets --------------------------------- #

        cloud_prop.cld_0_detail_offset = Vector((0.0, 0.0))
        cloud_prop.cld_0_shape_offset = Vector((0.0, 0.0))
        cloud_prop.cld_0_coverage_offset = Vector((0.0, 0.0))

        # ---------------------------------- Density --------------------------------- #

        cloud_prop.cld_0_density = 0.081776
        cloud_prop.cld_0_density_height = 0.371495

        # --------------------------------- Lighting --------------------------------- #

        cloud_prop.cld_0_sigma_s = Color((1.0, 1.0, 1.0))
        cloud_prop.cld_0_ambient_intsty = 3.0
        cloud_prop.cld_0_ap_intsty = 0.703738

        cloud_prop.cld_0_atten = .2
        cloud_prop.cld_0_contr = .5
        cloud_prop.cld_0_eccen = .5

        # ---------------------------------------------------------------------------- #
        #                                 Cloud Layer 1                                #
        # ---------------------------------------------------------------------------- #
        
        cloud_prop.cld_1_show_viewport = False
        cloud_prop.cld_1_show_render = False

        # --------------------------------- Transform -------------------------------- #

        cloud_prop.cld_1_pos_offset = Vector((0.0,0.0))
        cloud_prop.cld_1_height = 10000.0
        cloud_prop.cld_1_rotation = radians(0.0)
        cloud_prop.cld_1_size = 0.2

        # ----------------------------------- Shape ---------------------------------- #

        cloud_prop.cld_1_top_roundness = 0.5
        cloud_prop.cld_1_bottom_roundness = 0.2
        cloud_prop.cld_1_thickness = 0.546561

        # --------------------------------- Coverage --------------------------------- #
        
        cloud_prop.cld_1_coverage_intsty = 3.73667
        cloud_prop.cld_1_coverage_shape = 0.274286
        cloud_prop.cld_1_curl_octaves = 16

        # ----------------------------------- Shape ---------------------------------- #

        cloud_prop.cld_1_shape_intsty = 1.0
        cloud_prop.cld_1_shape_shape = 1.0
        cloud_prop.cld_1_shape_inverse = 1.0

        # ---------------------------------- Detail ---------------------------------- #
        
        cloud_prop.cld_1_detail_intsty = 0.278804
        cloud_prop.cld_1_detail_shape = 0.0
        cloud_prop.cld_1_detail_inverse = 1.0
        cloud_prop.cld_1_detail_scale = 1.36

        # ---------------------------------- Offsets --------------------------------- #

        cloud_prop.cld_1_detail_offset = Vector((0.0, 0.0))
        cloud_prop.cld_1_shape_offset = Vector((0.0, 0.0))
        cloud_prop.cld_1_coverage_offset = Vector((0.0, 0.0))

        # ---------------------------------- Density --------------------------------- #

        cloud_prop.cld_1_density = 0.081776
        cloud_prop.cld_1_density_height = 0.371495

        # --------------------------------- Lighting --------------------------------- #

        cloud_prop.cld_1_sigma_s = Color((1.0, 1.0, 1.0))
        cloud_prop.cld_1_ambient_intsty = 3.0
        cloud_prop.cld_1_ap_intsty = 0.703738

        cloud_prop.cld_1_atten = .2
        cloud_prop.cld_1_contr = .5
        cloud_prop.cld_1_eccen = .5

        # ---------------------------------------------------------------------------- #
        #                                  Atmosphere                                  #
        # ---------------------------------------------------------------------------- #

        atmo_prop.atm_show_viewport = True
        atmo_prop.atm_show_render = True

        atmo_prop.prop_sky_altitude = 2000.0

        atmo_prop.prop_air = 1.0
        atmo_prop.prop_dust = 1.0
        atmo_prop.prop_ozone = 1.0

        # ---------------------------------------------------------------------------- #
        #                                      Sun                                     #
        # ---------------------------------------------------------------------------- #

        atmo_prop.atm_show_viewport = True
        atmo_prop.atm_show_render = True

        sun_prop.sun_enable_light = True

        sun_prop.sun_size = radians(0.545)

        sun_prop.sun_intsty = 1.0

        sun_prop.sun_elevation = radians(90.0)
        sun_prop.sun_rotation = radians(0.0)

        # ---------------------------------------------------------------------------- #
        #                                     Moon                                     #
        # ---------------------------------------------------------------------------- #

        moon_prop.moon_show_viewport = False
        moon_prop.moon_show_render = False

        moon_prop.moon_size = radians(6.3)

        moon_prop.moon_enable_light = True

        moon_prop.moon_intsty = 1.0
        moon_prop.moon_ambient_intsty = 0.0

        moon_prop.moon_elevation = radians(13.0)
        moon_prop.moon_rotation = radians(182.0)
        moon_prop.moon_face_rotation = radians(60.0)

        moon_prop.moon_phase_rotation = radians(130.0)
        moon_prop.moon_phase = radians(-125.0)

        # ---------------------------------------------------------------------------- #
        #                                     Stars                                    #
        # ---------------------------------------------------------------------------- #
        
        stars_prop.stars_show_viewport = False
        stars_prop.stars_show_render = False
        stars_prop.stars_intsty = 1.0
        stars_prop.stars_rotation = 0.0

        return {"FINISHED"}

class STRATUS_OT_daytime_2(bpy.types.Operator):
    bl_idname = "stratus.preset_daytime_2"
    bl_label = "Daytime 2"
    
    def execute(self, context):
        print("Daytime_2")
        return {"FINISHED"}

class STRATUS_OT_daytime_3(bpy.types.Operator):
    bl_idname = "stratus.preset_daytime_3"
    bl_label = "Daytime 3"
    
    def execute(self, context):
        print("Daytime_3")
        return {"FINISHED"}

class STRATUS_OT_sunset_1(bpy.types.Operator):
    bl_idname = "stratus.preset_sunset_1"
    bl_label = "Sunset 1"
    
    def execute(self, context):
        print("Sunset 1")
        return {"FINISHED"}

class STRATUS_OT_sunset_2(bpy.types.Operator):
    bl_idname = "stratus.preset_sunset_2"
    bl_label = "Sunset 2"
    
    def execute(self, context):
        print("Sunset 2")
        return {"FINISHED"}

class STRATUS_OT_sunset_3(bpy.types.Operator):
    bl_idname = "stratus.preset_sunset_3"
    bl_label = "Sunset 3"
    
    def execute(self, context):
        print("Sunset 3")
        return {"FINISHED"}

class STRATUS_OT_storm(bpy.types.Operator):
    bl_idname = "stratus.preset_storm"
    bl_label = "Storm"
    
    def execute(self, context):
        print("Storm")
        return {"FINISHED"}

class STRATUS_OT_alien(bpy.types.Operator):
    bl_idname = "stratus.preset_alien"
    bl_label = "Alien"
    
    def execute(self, context):
        print("Alien")
        return {"FINISHED"}

class STRATUS_OT_hell(bpy.types.Operator):
    bl_idname = "stratus.preset_hell"
    bl_label = "Hell"
    
    def execute(self, context):
        print("Hell")
        return {"FINISHED"}

class STRATUS_OT_full_moon(bpy.types.Operator):
    bl_idname = "stratus.preset_full_moon"
    bl_label = "Full Moon"
    
    def execute(self, context):
        print("Full Moon")
        return {"FINISHED"}

class STRATUS_OT_blood_moon(bpy.types.Operator):
    bl_idname = "stratus.preset_blood_moon"
    bl_label = "Blood Moon"
    
    def execute(self, context):
        print("BloodMoon")
        return {"FINISHED"}