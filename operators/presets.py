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
    bl_label = "Whispy"
    
    def execute(self, context):
        
        cloud_prop = bpy.context.scene.cloud_props
        atmo_prop = bpy.context.scene.atmo_props
        sun_prop = bpy.context.scene.sun_props
        stars_prop = bpy.context.scene.stars_props
        moon_prop = bpy.context.scene.moon_props
        render_prop = bpy.context.scene.render_props

        # ---------------------------------------------------------------------------- #
        #                                    Render                                    #
        # ---------------------------------------------------------------------------- #A

        render_prop.env_img_strength = .1

        # ---------------------------------- Render ---------------------------------- #

        render_prop.enable_separate_steps_render = False
        render_prop.enable_separate_light_steps_render = False

        render_prop.max_steps_render = 64
        render_prop.max_light_steps_render = 32

        render_prop.cld_0_max_steps_render = 64
        render_prop.cld_1_max_steps_render = 300

        render_prop.cld_0_max_light_steps_render = 32
        render_prop.cld_1_max_light_steps_render = 64

        # --------------------------------- Viewport --------------------------------- #

        render_prop.enable_separate_steps_viewport = False
        render_prop.enable_separate_light_steps_viewport = False

        render_prop.max_steps_viewport = 24
        render_prop.max_light_steps_viewport = 16

        render_prop.cld_0_max_steps_viewport = 25
        render_prop.cld_1_max_steps_viewport = 150

        render_prop.cld_0_max_light_steps_viewport = 16
        render_prop.cld_1_max_light_steps_viewport = 32

        # ---------------------------------------------------------------------------- #
        #                                 Cloud Layer 0                                #
        # ---------------------------------------------------------------------------- #
        
        cloud_prop.cld_0_show_viewport = True
        cloud_prop.cld_0_show_render = True

        # --------------------------------- Transform -------------------------------- #

        cloud_prop.cld_0_pos_offset = Vector((0.0,0.0))
        cloud_prop.cld_0_height = 10000.0
        cloud_prop.cld_0_rotation = radians(300.0)
        cloud_prop.cld_0_size = 0.15

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

        sun_prop.sun_show_viewport = True
        sun_prop.sun_show_render = True

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

        # ---------------------------------------------------------------------------- #
        #                                     Stars                                    #
        # ---------------------------------------------------------------------------- #
        
        stars_prop.stars_show_viewport = False
        stars_prop.stars_show_render = False

        return {"FINISHED"}

class STRATUS_OT_daytime_2(bpy.types.Operator):
    bl_idname = "stratus.preset_daytime_2"
    bl_label = "Fluffy"
    
    def execute(self, context):
                
        cloud_prop = bpy.context.scene.cloud_props
        atmo_prop = bpy.context.scene.atmo_props
        sun_prop = bpy.context.scene.sun_props
        stars_prop = bpy.context.scene.stars_props
        moon_prop = bpy.context.scene.moon_props
        render_prop = bpy.context.scene.render_props

        # ---------------------------------------------------------------------------- #
        #                                    Render                                    #
        # ---------------------------------------------------------------------------- #A

        render_prop.env_img_strength = .1

        # ---------------------------------- Render ---------------------------------- #

        render_prop.enable_separate_steps_render = False
        render_prop.enable_separate_light_steps_render = False

        render_prop.max_steps_render = 300
        render_prop.max_light_steps_render = 64

        render_prop.cld_0_max_steps_render = 64
        render_prop.cld_1_max_steps_render = 300

        render_prop.cld_0_max_light_steps_render = 32
        render_prop.cld_1_max_light_steps_render = 64

        # --------------------------------- Viewport --------------------------------- #

        render_prop.enable_separate_steps_viewport = False
        render_prop.enable_separate_light_steps_viewport = False

        render_prop.max_steps_viewport = 150
        render_prop.max_light_steps_viewport = 64

        render_prop.cld_0_max_steps_viewport = 25
        render_prop.cld_1_max_steps_viewport = 150

        render_prop.cld_0_max_light_steps_viewport = 16
        render_prop.cld_1_max_light_steps_viewport = 32

        # ---------------------------------------------------------------------------- #
        #                                 Cloud Layer 0                                #
        # ---------------------------------------------------------------------------- #
        
        cloud_prop.cld_0_show_viewport = False
        cloud_prop.cld_0_show_render = False

        # ---------------------------------------------------------------------------- #
        #                                 Cloud Layer 1                                #
        # ---------------------------------------------------------------------------- #
        
        cloud_prop.cld_1_show_viewport = True
        cloud_prop.cld_1_show_render = True

        # --------------------------------- Transform -------------------------------- #

        cloud_prop.cld_1_pos_offset = Vector((0.0,0.0))
        cloud_prop.cld_1_height = 6000.0
        cloud_prop.cld_1_rotation = radians(300.0)
        cloud_prop.cld_1_size = 0.6

        # ----------------------------------- Shape ---------------------------------- #

        cloud_prop.cld_1_bottom_roundness = 0.041667
        cloud_prop.cld_1_thickness = 2.5

        # --------------------------------- Coverage --------------------------------- #
        
        cloud_prop.cld_1_coverage_intsty = 1.88609
        cloud_prop.cld_1_coverage_shape = 1.0
        cloud_prop.cld_1_curl_octaves = 0

        # ----------------------------------- Shape ---------------------------------- #

        cloud_prop.cld_1_shape_intsty = 0.625

        # ---------------------------------- Detail ---------------------------------- #
        
        cloud_prop.cld_1_detail_intsty = 0.10119
        cloud_prop.cld_1_detail_scale = 1.0

        # ---------------------------------- Offsets --------------------------------- #

        cloud_prop.cld_1_detail_offset = Vector((0.0, 0.0))
        cloud_prop.cld_1_shape_offset = Vector((0.0, 0.0))
        cloud_prop.cld_1_coverage_offset = Vector((0.0, 0.0))

        # ---------------------------------- Density --------------------------------- #

        cloud_prop.cld_1_density = 1.0
        cloud_prop.cld_1_density_height = 0.601191

        # --------------------------------- Lighting --------------------------------- #

        cloud_prop.cld_1_sigma_s = Color((1.0, 1.0, 1.0))
        cloud_prop.cld_1_ambient_intsty = 1.5
        cloud_prop.cld_1_ap_intsty = 0.75

        cloud_prop.cld_1_atten = .35
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

        sun_prop.sun_show_viewport = True
        sun_prop.sun_show_render = True

        sun_prop.sun_enable_light = True

        sun_prop.sun_size = radians(0.545)

        sun_prop.sun_intsty = 1.0

        sun_prop.sun_elevation = radians(157.38)
        sun_prop.sun_rotation = radians(12.63)

        # ---------------------------------------------------------------------------- #
        #                                     Moon                                     #
        # ---------------------------------------------------------------------------- #

        moon_prop.moon_show_viewport = False
        moon_prop.moon_show_render = False

        # ---------------------------------------------------------------------------- #
        #                                     Stars                                    #
        # ---------------------------------------------------------------------------- #
        
        stars_prop.stars_show_viewport = False
        stars_prop.stars_show_render = False

        return {"FINISHED"}

class STRATUS_OT_daytime_3(bpy.types.Operator):
    bl_idname = "stratus.preset_daytime_3"
    bl_label = "Daytime 3"
    
    def execute(self, context):
        print("Daytime_3")
        return {"FINISHED"}

class STRATUS_OT_sunset_1(bpy.types.Operator):
    bl_idname = "stratus.preset_sunset_1"
    bl_label = "Fluffy Sunset"
    
    def execute(self, context):
                
        cloud_prop = bpy.context.scene.cloud_props
        atmo_prop = bpy.context.scene.atmo_props
        sun_prop = bpy.context.scene.sun_props
        stars_prop = bpy.context.scene.stars_props
        moon_prop = bpy.context.scene.moon_props
        render_prop = bpy.context.scene.render_props

        # ---------------------------------------------------------------------------- #
        #                                    Render                                    #
        # ---------------------------------------------------------------------------- #A

        render_prop.env_img_strength = .1

        # ---------------------------------- Render ---------------------------------- #

        render_prop.enable_separate_steps_render = True
        render_prop.enable_separate_light_steps_render = True

        render_prop.max_steps_render = 300
        render_prop.max_light_steps_render = 64

        render_prop.cld_0_max_steps_render = 64
        render_prop.cld_1_max_steps_render = 300

        render_prop.cld_0_max_light_steps_render = 32
        render_prop.cld_1_max_light_steps_render = 64

        # --------------------------------- Viewport --------------------------------- #

        render_prop.enable_separate_steps_viewport = True
        render_prop.enable_separate_light_steps_viewport = True

        render_prop.max_steps_viewport = 150
        render_prop.max_light_steps_viewport = 64

        render_prop.cld_0_max_steps_viewport = 25
        render_prop.cld_1_max_steps_viewport = 150

        render_prop.cld_0_max_light_steps_viewport = 16
        render_prop.cld_1_max_light_steps_viewport = 32

        # ---------------------------------------------------------------------------- #
        #                                 Cloud Layer 0                                #
        # ---------------------------------------------------------------------------- #
        
        cloud_prop.cld_0_show_viewport = False
        cloud_prop.cld_0_show_render = False

        # ---------------------------------------------------------------------------- #
        #                                 Cloud Layer 1                                #
        # ---------------------------------------------------------------------------- #
        
        cloud_prop.cld_1_show_viewport = True
        cloud_prop.cld_1_show_render = True

        # --------------------------------- Transform -------------------------------- #

        cloud_prop.cld_1_pos_offset = Vector((24.0,146.0))
        cloud_prop.cld_1_height = 500.0
        cloud_prop.cld_1_rotation = radians(184.53)
        cloud_prop.cld_1_size = 1.0

        # ----------------------------------- Shape ---------------------------------- #

        cloud_prop.cld_1_top_roundness = 0.5
        cloud_prop.cld_1_bottom_roundness = 0.0
        cloud_prop.cld_1_thickness = 2.5

        # --------------------------------- Coverage --------------------------------- #
        
        cloud_prop.cld_1_coverage_intsty = 2.0
        cloud_prop.cld_1_coverage_shape = 1.0
        cloud_prop.cld_1_curl_octaves = 0

        # ----------------------------------- Shape ---------------------------------- #

        cloud_prop.cld_1_shape_intsty = 1.0

        # ---------------------------------- Detail ---------------------------------- #
        
        cloud_prop.cld_1_detail_intsty = 0.071429
        cloud_prop.cld_1_detail_scale = 1.0

        # ---------------------------------- Offsets --------------------------------- #

        cloud_prop.cld_1_detail_offset = Vector((0.0, 0.0))
        cloud_prop.cld_1_shape_offset = Vector((0.0, 0.0))
        cloud_prop.cld_1_coverage_offset = Vector((0.0, 0.0))

        # ---------------------------------- Density --------------------------------- #

        cloud_prop.cld_1_density = 0.56
        cloud_prop.cld_1_density_height = 0.35

        # --------------------------------- Lighting --------------------------------- #

        cloud_prop.cld_1_sigma_s = Color((1.0, 1.0, 1.0))
        cloud_prop.cld_1_ambient_intsty = 1.6
        cloud_prop.cld_1_ap_intsty = 1.0

        cloud_prop.cld_1_atten = .38
        cloud_prop.cld_1_contr = .5
        cloud_prop.cld_1_eccen = .5

        # ---------------------------------------------------------------------------- #
        #                                  Atmosphere                                  #
        # ---------------------------------------------------------------------------- #

        atmo_prop.atm_show_viewport = True
        atmo_prop.atm_show_render = True

        atmo_prop.prop_sky_altitude = 2000.0

        atmo_prop.prop_air = 1.12
        atmo_prop.prop_dust = 1.0
        atmo_prop.prop_ozone = 1.4

        # ---------------------------------------------------------------------------- #
        #                                      Sun                                     #
        # ---------------------------------------------------------------------------- #

        sun_prop.sun_show_viewport = True
        sun_prop.sun_show_render = True

        sun_prop.sun_enable_light = True

        sun_prop.sun_size = radians(0.545)

        sun_prop.sun_intsty = 1.0

        sun_prop.sun_elevation = radians(181.59)
        sun_prop.sun_rotation = radians(-195.06)

        # ---------------------------------------------------------------------------- #
        #                                     Moon                                     #
        # ---------------------------------------------------------------------------- #

        moon_prop.moon_show_viewport = True
        moon_prop.moon_show_render = True

        moon_prop.moon_size = radians(6.3)

        moon_prop.moon_enable_light = True

        moon_prop.moon_intsty = 35.0
        moon_prop.moon_ambient_intsty = 0.0

        moon_prop.moon_elevation = radians(24.4)
        moon_prop.moon_rotation = radians(11.96)
        moon_prop.moon_face_rotation = radians(60.0)

        moon_prop.moon_phase = radians(140.0)
        moon_prop.moon_phase_rotation = radians(45.0)

        # ---------------------------------------------------------------------------- #
        #                                     Stars                                    #
        # ---------------------------------------------------------------------------- #
        
        stars_prop.stars_show_viewport = True
        stars_prop.stars_show_render = True
        stars_prop.stars_intsty = 15.0
        stars_prop.stars_rotation = 0.0

        return {"FINISHED"}

class STRATUS_OT_sunset_2(bpy.types.Operator):
    bl_idname = "stratus.preset_sunset_2"
    bl_label = "Dynamic Sunset"
    
    def execute(self, context):
                
        cloud_prop = bpy.context.scene.cloud_props
        atmo_prop = bpy.context.scene.atmo_props
        sun_prop = bpy.context.scene.sun_props
        stars_prop = bpy.context.scene.stars_props
        moon_prop = bpy.context.scene.moon_props
        render_prop = bpy.context.scene.render_props

        # ---------------------------------------------------------------------------- #
        #                                    Render                                    #
        # ---------------------------------------------------------------------------- #A

        render_prop.env_img_strength = .1

        # ---------------------------------- Render ---------------------------------- #

        render_prop.enable_separate_steps_render = True
        render_prop.enable_separate_light_steps_render = True

        render_prop.max_steps_render = 300
        render_prop.max_light_steps_render = 64

        render_prop.cld_0_max_steps_render = 64
        render_prop.cld_1_max_steps_render = 300

        render_prop.cld_0_max_light_steps_render = 32
        render_prop.cld_1_max_light_steps_render = 64

        # --------------------------------- Viewport --------------------------------- #

        render_prop.enable_separate_steps_viewport = True
        render_prop.enable_separate_light_steps_viewport = True

        render_prop.max_steps_viewport = 150
        render_prop.max_light_steps_viewport = 64

        render_prop.cld_0_max_steps_viewport = 25
        render_prop.cld_1_max_steps_viewport = 150

        render_prop.cld_0_max_light_steps_viewport = 16
        render_prop.cld_1_max_light_steps_viewport = 32

        # ---------------------------------------------------------------------------- #
        #                                 Cloud Layer 0                                #
        # ---------------------------------------------------------------------------- #
        
        cloud_prop.cld_0_show_viewport = True
        cloud_prop.cld_0_show_render = True

        # --------------------------------- Transform -------------------------------- #

        cloud_prop.cld_0_pos_offset = Vector((0.0,0.0))
        cloud_prop.cld_0_height = 6000.0
        cloud_prop.cld_0_rotation = radians(0.0)
        cloud_prop.cld_0_size = 0.161905

        # ----------------------------------- Shape ---------------------------------- #

        cloud_prop.cld_0_bottom_roundness = 0.15
        cloud_prop.cld_0_thickness = 1.0

        # --------------------------------- Coverage --------------------------------- #
        
        cloud_prop.cld_0_coverage_intsty = 3.76832
        cloud_prop.cld_0_coverage_shape = 1.0
        cloud_prop.cld_0_curl_octaves = 16

        # ----------------------------------- Shape ---------------------------------- #

        cloud_prop.cld_0_shape_intsty = 1.0
        cloud_prop.cld_0_shape_shape = 1.0
        cloud_prop.cld_0_shape_inverse = 0.0

        # ---------------------------------- Detail ---------------------------------- #
        
        cloud_prop.cld_0_detail_intsty = 0.25
        cloud_prop.cld_0_detail_shape = 1.0
        cloud_prop.cld_0_detail_inverse = 0.0
        cloud_prop.cld_0_detail_scale = 4.279

        # ---------------------------------- Offsets --------------------------------- #

        cloud_prop.cld_0_detail_offset = Vector((0.0, 0.0))
        cloud_prop.cld_0_shape_offset = Vector((0.0, 0.0))
        cloud_prop.cld_0_coverage_offset = Vector((0.0, 0.0))

        # ---------------------------------- Density --------------------------------- #

        cloud_prop.cld_0_density = 0.153205
        cloud_prop.cld_0_density_height = 0.621495

        # --------------------------------- Lighting --------------------------------- #

        cloud_prop.cld_0_sigma_s = Color((1.0, 1.0, 1.0))
        cloud_prop.cld_0_ambient_intsty = 3.0
        cloud_prop.cld_0_ap_intsty = 0.876357

        cloud_prop.cld_0_atten = .2
        cloud_prop.cld_0_contr = .2
        cloud_prop.cld_0_eccen = .2

        # ---------------------------------------------------------------------------- #
        #                                 Cloud Layer 1                                #
        # ---------------------------------------------------------------------------- #
        
        cloud_prop.cld_1_show_viewport = True
        cloud_prop.cld_1_show_render = True

        # --------------------------------- Transform -------------------------------- #

        cloud_prop.cld_1_pos_offset = Vector((100.0,100.0))
        cloud_prop.cld_1_height = 3479.17
        cloud_prop.cld_1_rotation = radians(-60.0)
        cloud_prop.cld_1_size = 0.428571

        # ----------------------------------- Shape ---------------------------------- #

        cloud_prop.cld_1_bottom_roundness = 0.22
        cloud_prop.cld_1_thickness = 2.5

        # --------------------------------- Coverage --------------------------------- #
        
        cloud_prop.cld_1_coverage_intsty = 2.42
        cloud_prop.cld_1_coverage_shape = 0.4
        cloud_prop.cld_1_curl_octaves = 6

        # ----------------------------------- Shape ---------------------------------- #

        cloud_prop.cld_1_shape_intsty = 0.45

        # ---------------------------------- Detail ---------------------------------- #
        
        cloud_prop.cld_1_detail_intsty = 0.16
        cloud_prop.cld_1_detail_scale = 0.40

        # ---------------------------------- Offsets --------------------------------- #

        cloud_prop.cld_1_detail_offset = Vector((0.0, 0.0))
        cloud_prop.cld_1_shape_offset = Vector((0.0, 0.0))
        cloud_prop.cld_1_coverage_offset = Vector((0.0, 0.0))

        # ---------------------------------- Density --------------------------------- #

        cloud_prop.cld_1_density = 0.56
        cloud_prop.cld_1_density_height = 0.35

        # --------------------------------- Lighting --------------------------------- #

        cloud_prop.cld_1_sigma_s = Color((1.0, 1.0, 1.0))
        cloud_prop.cld_1_ambient_intsty = 1.6
        cloud_prop.cld_1_ap_intsty = 1.0

        cloud_prop.cld_1_atten = .5
        cloud_prop.cld_1_contr = .5
        cloud_prop.cld_1_eccen = .5

        # ---------------------------------------------------------------------------- #
        #                                  Atmosphere                                  #
        # ---------------------------------------------------------------------------- #

        atmo_prop.atm_show_viewport = True
        atmo_prop.atm_show_render = True

        atmo_prop.prop_sky_altitude = 2000.0

        atmo_prop.prop_air = 1.45
        atmo_prop.prop_dust = 1.0
        atmo_prop.prop_ozone = 1.5

        # ---------------------------------------------------------------------------- #
        #                                      Sun                                     #
        # ---------------------------------------------------------------------------- #

        sun_prop.sun_show_viewport = True
        sun_prop.sun_show_render = True

        sun_prop.sun_enable_light = True

        sun_prop.sun_size = radians(0.545)

        sun_prop.sun_intsty = 1.0

        sun_prop.sun_elevation = radians(182.16)
        sun_prop.sun_rotation = radians(-195.06)

        # ---------------------------------------------------------------------------- #
        #                                     Moon                                     #
        # ---------------------------------------------------------------------------- #

        moon_prop.moon_show_viewport = False
        moon_prop.moon_show_render = False

        # ---------------------------------------------------------------------------- #
        #                                     Stars                                    #
        # ---------------------------------------------------------------------------- #
        
        stars_prop.stars_show_viewport = True
        stars_prop.stars_show_render = True
        stars_prop.stars_intsty = 15.0
        stars_prop.stars_rotation = 0.0

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
                
        cloud_prop = bpy.context.scene.cloud_props
        atmo_prop = bpy.context.scene.atmo_props
        sun_prop = bpy.context.scene.sun_props
        stars_prop = bpy.context.scene.stars_props
        moon_prop = bpy.context.scene.moon_props
        render_prop = bpy.context.scene.render_props

        # ---------------------------------------------------------------------------- #
        #                                    Render                                    #
        # ---------------------------------------------------------------------------- #A

        render_prop.env_img_strength = .1

        # ---------------------------------- Render ---------------------------------- #

        render_prop.enable_separate_steps_render = False
        render_prop.enable_separate_light_steps_render = False

        render_prop.max_steps_render = 600
        render_prop.max_light_steps_render = 200

        render_prop.cld_0_max_steps_render = 64
        render_prop.cld_1_max_steps_render = 300

        render_prop.cld_0_max_light_steps_render = 32
        render_prop.cld_1_max_light_steps_render = 64

        # --------------------------------- Viewport --------------------------------- #

        render_prop.enable_separate_steps_viewport = False
        render_prop.enable_separate_light_steps_viewport = False

        render_prop.max_steps_viewport = 200
        render_prop.max_light_steps_viewport = 120

        render_prop.cld_0_max_steps_viewport = 25
        render_prop.cld_1_max_steps_viewport = 150

        render_prop.cld_0_max_light_steps_viewport = 16
        render_prop.cld_1_max_light_steps_viewport = 32

        # ---------------------------------------------------------------------------- #
        #                                 Cloud Layer 0                                #
        # ---------------------------------------------------------------------------- #
        
        cloud_prop.cld_0_show_viewport = False
        cloud_prop.cld_0_show_render = False

        # ---------------------------------------------------------------------------- #
        #                                 Cloud Layer 1                                #
        # ---------------------------------------------------------------------------- #
        
        cloud_prop.cld_1_show_viewport = True
        cloud_prop.cld_1_show_render = True

        # --------------------------------- Transform -------------------------------- #

        cloud_prop.cld_1_pos_offset = Vector((10.0,21.0))
        cloud_prop.cld_1_height = 1449.4
        cloud_prop.cld_1_rotation = radians(259.53)
        cloud_prop.cld_1_size = 0.6

        # ----------------------------------- Shape ---------------------------------- #

        cloud_prop.cld_1_bottom_roundness = 0.0
        cloud_prop.cld_1_thickness = 2.5

        # --------------------------------- Coverage --------------------------------- #
        
        cloud_prop.cld_1_coverage_intsty = 2.98728
        cloud_prop.cld_1_coverage_shape = 0.553571
        cloud_prop.cld_1_curl_octaves = 0

        # ----------------------------------- Shape ---------------------------------- #

        cloud_prop.cld_1_shape_intsty = 0.672619

        # ---------------------------------- Detail ---------------------------------- #
        
        cloud_prop.cld_1_detail_intsty = 0.053571
        cloud_prop.cld_1_detail_scale = 1.195

        # ---------------------------------- Offsets --------------------------------- #

        cloud_prop.cld_1_detail_offset = Vector((0.0, 0.0))
        cloud_prop.cld_1_shape_offset = Vector((0.0, 0.0))
        cloud_prop.cld_1_coverage_offset = Vector((0.0, 0.0))

        # ---------------------------------- Density --------------------------------- #

        cloud_prop.cld_1_density = 1.8631
        cloud_prop.cld_1_density_height = 0.428571

        # --------------------------------- Lighting --------------------------------- #

        cloud_prop.cld_1_sigma_s = Color((1.0, 1.0, 1.0))
        cloud_prop.cld_1_ambient_intsty = 0.552
        cloud_prop.cld_1_ap_intsty = 0.892857

        cloud_prop.cld_1_atten = 1.0
        cloud_prop.cld_1_contr = 0.5
        cloud_prop.cld_1_eccen = 0.5

        # ---------------------------------------------------------------------------- #
        #                                  Atmosphere                                  #
        # ---------------------------------------------------------------------------- #

        atmo_prop.atm_show_viewport = True
        atmo_prop.atm_show_render = True

        atmo_prop.prop_sky_altitude = 2000.0

        atmo_prop.prop_air = 1.0
        atmo_prop.prop_dust = 2.0
        atmo_prop.prop_ozone = 0.75

        # ---------------------------------------------------------------------------- #
        #                                      Sun                                     #
        # ---------------------------------------------------------------------------- #

        sun_prop.sun_show_viewport = True
        sun_prop.sun_show_render = True

        sun_prop.sun_enable_light = True

        sun_prop.sun_size = radians(0.545)

        sun_prop.sun_intsty = 1.0

        sun_prop.sun_elevation = radians(174.15)
        sun_prop.sun_rotation = radians(12.63)

        # ---------------------------------------------------------------------------- #
        #                                     Moon                                     #
        # ---------------------------------------------------------------------------- #

        moon_prop.moon_show_viewport = False
        moon_prop.moon_show_render = False

        # ---------------------------------------------------------------------------- #
        #                                     Stars                                    #
        # ---------------------------------------------------------------------------- #
        
        stars_prop.stars_show_viewport = False
        stars_prop.stars_show_render = False

        return {"FINISHED"}

class STRATUS_OT_alien(bpy.types.Operator):
    bl_idname = "stratus.preset_alien"
    bl_label = "Alien"
    
    def execute(self, context):
                
        cloud_prop = bpy.context.scene.cloud_props
        atmo_prop = bpy.context.scene.atmo_props
        sun_prop = bpy.context.scene.sun_props
        stars_prop = bpy.context.scene.stars_props
        moon_prop = bpy.context.scene.moon_props
        render_prop = bpy.context.scene.render_props

        # ---------------------------------------------------------------------------- #
        #                                    Render                                    #
        # ---------------------------------------------------------------------------- #A

        render_prop.env_img_strength = .1

        # ---------------------------------- Render ---------------------------------- #

        render_prop.enable_separate_steps_render = True
        render_prop.enable_separate_light_steps_render = True

        render_prop.max_steps_render = 300
        render_prop.max_light_steps_render = 64

        render_prop.cld_0_max_steps_render = 64
        render_prop.cld_1_max_steps_render = 300

        render_prop.cld_0_max_light_steps_render = 32
        render_prop.cld_1_max_light_steps_render = 64

        # --------------------------------- Viewport --------------------------------- #

        render_prop.enable_separate_steps_viewport = True
        render_prop.enable_separate_light_steps_viewport = True

        render_prop.max_steps_viewport = 150
        render_prop.max_light_steps_viewport = 64

        render_prop.cld_0_max_steps_viewport = 25
        render_prop.cld_1_max_steps_viewport = 150

        render_prop.cld_0_max_light_steps_viewport = 16
        render_prop.cld_1_max_light_steps_viewport = 32

        # ---------------------------------------------------------------------------- #
        #                                 Cloud Layer 0                                #
        # ---------------------------------------------------------------------------- #
        
        cloud_prop.cld_0_show_viewport = True
        cloud_prop.cld_0_show_render = True

        # --------------------------------- Transform -------------------------------- #

        cloud_prop.cld_0_pos_offset = Vector((0.0,0.0))
        cloud_prop.cld_0_height = 10000.0
        cloud_prop.cld_0_rotation = radians(38.43)
        cloud_prop.cld_0_size = 0.074048

        # ----------------------------------- Shape ---------------------------------- #

        cloud_prop.cld_0_bottom_roundness = 0.110714
        cloud_prop.cld_0_thickness = 0.546561

        # --------------------------------- Coverage --------------------------------- #
        
        cloud_prop.cld_0_coverage_intsty = 4.33544
        cloud_prop.cld_0_coverage_shape = 0.0
        cloud_prop.cld_0_curl_octaves = 0

        # ----------------------------------- Shape ---------------------------------- #

        cloud_prop.cld_0_shape_intsty = 0.52381
        cloud_prop.cld_0_shape_shape = 1.0
        cloud_prop.cld_0_shape_inverse = 1.0

        # ---------------------------------- Detail ---------------------------------- #
        
        cloud_prop.cld_0_detail_intsty = 0.190476
        cloud_prop.cld_0_detail_shape = 0.0
        cloud_prop.cld_0_detail_inverse = 1.0
        cloud_prop.cld_0_detail_scale = 0.82

        # ---------------------------------- Offsets --------------------------------- #

        cloud_prop.cld_0_detail_offset = Vector((0.0, 0.0))
        cloud_prop.cld_0_shape_offset = Vector((0.0, 0.0))
        cloud_prop.cld_0_coverage_offset = Vector((0.0, 0.0))

        # ---------------------------------- Density --------------------------------- #

        cloud_prop.cld_0_density = 0.047619
        cloud_prop.cld_0_density_height = 0.514352

        # --------------------------------- Lighting --------------------------------- #

        cloud_prop.cld_0_sigma_s = Color((0.2148, 0.014073, 1.0))
        cloud_prop.cld_0_ambient_intsty = 3.0
        cloud_prop.cld_0_ap_intsty = 1.0

        cloud_prop.cld_0_atten = 0.2
        cloud_prop.cld_0_contr = 1.0
        cloud_prop.cld_0_eccen = .11

        # ---------------------------------------------------------------------------- #
        #                                 Cloud Layer 1                                #
        # ---------------------------------------------------------------------------- #
        
        cloud_prop.cld_1_show_viewport = True
        cloud_prop.cld_1_show_render = True

        # --------------------------------- Transform -------------------------------- #

        cloud_prop.cld_1_pos_offset = Vector((0.0,0.0))
        cloud_prop.cld_1_height = 6000
        cloud_prop.cld_1_rotation = radians(278.76)
        cloud_prop.cld_1_size = 1.0

        # ----------------------------------- Shape ---------------------------------- #

        cloud_prop.cld_1_bottom_roundness = 0.0
        cloud_prop.cld_1_thickness = 0.336072

        # --------------------------------- Coverage --------------------------------- #
        
        cloud_prop.cld_1_coverage_intsty = 2.24323
        cloud_prop.cld_1_coverage_shape = 0.64881
        cloud_prop.cld_1_curl_octaves = 0

        # ----------------------------------- Shape ---------------------------------- #

        cloud_prop.cld_1_shape_intsty = 1.0

        # ---------------------------------- Detail ---------------------------------- #
        
        cloud_prop.cld_1_detail_intsty = 0.27381
        cloud_prop.cld_1_detail_scale = 0.28

        # ---------------------------------- Offsets --------------------------------- #

        cloud_prop.cld_1_detail_offset = Vector((0.0, 0.0))
        cloud_prop.cld_1_shape_offset = Vector((0.0, 0.0))
        cloud_prop.cld_1_coverage_offset = Vector((0.0, 0.0))

        # ---------------------------------- Density --------------------------------- #

        cloud_prop.cld_1_density = 3.1131
        cloud_prop.cld_1_density_height = 0.625001

        # --------------------------------- Lighting --------------------------------- #

        cloud_prop.cld_1_sigma_s = Color((0.240201, 0.050251, 1.0))
        cloud_prop.cld_1_ambient_intsty = 3.0
        cloud_prop.cld_1_ap_intsty = 0.863095

        cloud_prop.cld_1_atten = 0.35
        cloud_prop.cld_1_contr = .5
        cloud_prop.cld_1_eccen = .5

        # ---------------------------------------------------------------------------- #
        #                                  Atmosphere                                  #
        # ---------------------------------------------------------------------------- #

        atmo_prop.atm_show_viewport = True
        atmo_prop.atm_show_render = True

        atmo_prop.prop_sky_altitude = 2000.0

        atmo_prop.prop_air = 0.1
        atmo_prop.prop_dust = 0.0
        atmo_prop.prop_ozone = 10.0

        # ---------------------------------------------------------------------------- #
        #                                      Sun                                     #
        # ---------------------------------------------------------------------------- #

        sun_prop.sun_show_viewport = True
        sun_prop.sun_show_render = True

        sun_prop.sun_enable_light = True

        sun_prop.sun_size = radians(0.545)

        sun_prop.sun_intsty = 1.0

        sun_prop.sun_elevation = radians(148.5)
        sun_prop.sun_rotation = radians(193.56)

        # ---------------------------------------------------------------------------- #
        #                                     Moon                                     #
        # ---------------------------------------------------------------------------- #

        moon_prop.moon_show_viewport = False
        moon_prop.moon_show_render = False

        # ---------------------------------------------------------------------------- #
        #                                     Stars                                    #
        # ---------------------------------------------------------------------------- #
        
        stars_prop.stars_show_viewport = True
        stars_prop.stars_show_render = True
        stars_prop.stars_intsty = 500.0
        stars_prop.stars_rotation = 0.0

        return {"FINISHED"}

class STRATUS_OT_hell(bpy.types.Operator):
    bl_idname = "stratus.preset_hell"
    bl_label = "Hell"
    
    def execute(self, context):
        
        cloud_prop = bpy.context.scene.cloud_props
        atmo_prop = bpy.context.scene.atmo_props
        sun_prop = bpy.context.scene.sun_props
        stars_prop = bpy.context.scene.stars_props
        moon_prop = bpy.context.scene.moon_props
        render_prop = bpy.context.scene.render_props

        # ---------------------------------------------------------------------------- #
        #                                    Render                                    #
        # ---------------------------------------------------------------------------- #

        render_prop.env_img_strength = .1

        # ---------------------------------- Render ---------------------------------- #

        render_prop.enable_separate_steps_render = False
        render_prop.enable_separate_light_steps_render = False

        render_prop.max_steps_render = 600
        render_prop.max_light_steps_render = 64

        render_prop.cld_0_max_steps_render = 64
        render_prop.cld_1_max_steps_render = 300

        render_prop.cld_0_max_light_steps_render = 32
        render_prop.cld_1_max_light_steps_render = 64

        # --------------------------------- Viewport --------------------------------- #

        render_prop.enable_separate_steps_viewport = False
        render_prop.enable_separate_light_steps_viewport = False

        render_prop.max_steps_viewport = 300
        render_prop.max_light_steps_viewport = 32

        render_prop.cld_0_max_steps_viewport = 25
        render_prop.cld_1_max_steps_viewport = 150

        render_prop.cld_0_max_light_steps_viewport = 16
        render_prop.cld_1_max_light_steps_viewport = 32

        # ---------------------------------------------------------------------------- #
        #                                 Cloud Layer 0                                #
        # ---------------------------------------------------------------------------- #
        
        cloud_prop.cld_0_show_viewport = False
        cloud_prop.cld_0_show_render = False

        # ---------------------------------------------------------------------------- #
        #                                 Cloud Layer 1                                #
        # ---------------------------------------------------------------------------- #
        
        cloud_prop.cld_1_show_viewport = True
        cloud_prop.cld_1_show_render = True

        # --------------------------------- Transform -------------------------------- #

        cloud_prop.cld_1_pos_offset = Vector((0.0,0.0))
        cloud_prop.cld_1_height = 1456.52
        cloud_prop.cld_1_rotation = radians(0.0)
        cloud_prop.cld_1_size = 0.5

        # ----------------------------------- Shape ---------------------------------- #

        cloud_prop.cld_1_bottom_roundness = 0.10559
        cloud_prop.cld_1_thickness = 2.5

        # --------------------------------- Coverage --------------------------------- #
        
        cloud_prop.cld_1_coverage_intsty = 3.48822
        cloud_prop.cld_1_coverage_shape = 0.63354
        cloud_prop.cld_1_curl_octaves = 0

        # ----------------------------------- Shape ---------------------------------- #

        cloud_prop.cld_1_shape_intsty = 1.0

        # ---------------------------------- Detail ---------------------------------- #
        
        cloud_prop.cld_1_detail_intsty = 0.31677
        cloud_prop.cld_1_detail_scale = 0.43

        # ---------------------------------- Offsets --------------------------------- #

        cloud_prop.cld_1_detail_offset = Vector((0.0, 0.0))
        cloud_prop.cld_1_shape_offset = Vector((0.0, 0.0))
        cloud_prop.cld_1_coverage_offset = Vector((0.0, 0.0))

        # ---------------------------------- Density --------------------------------- #

        cloud_prop.cld_1_density = 0.440994
        cloud_prop.cld_1_density_height = 0.0

        # --------------------------------- Lighting --------------------------------- #

        cloud_prop.cld_1_sigma_s = Color((0.763364, 1.0, 0.279802))
        cloud_prop.cld_1_ambient_intsty = 1.1
        cloud_prop.cld_1_ap_intsty = 1.0

        cloud_prop.cld_1_atten = 0.845963
        cloud_prop.cld_1_contr = 0.307453
        cloud_prop.cld_1_eccen = 0.493789

        # ---------------------------------------------------------------------------- #
        #                                  Atmosphere                                  #
        # ---------------------------------------------------------------------------- #

        atmo_prop.atm_show_viewport = True
        atmo_prop.atm_show_render = True

        atmo_prop.prop_sky_altitude = 0.0

        atmo_prop.prop_air = 10.0
        atmo_prop.prop_dust = 10.0
        atmo_prop.prop_ozone = 0.0

        # ---------------------------------------------------------------------------- #
        #                                      Sun                                     #
        # ---------------------------------------------------------------------------- #

        sun_prop.sun_show_viewport = True
        sun_prop.sun_show_render = True

        sun_prop.sun_enable_light = True

        sun_prop.sun_size = radians(5.0)

        sun_prop.sun_intsty = 1.0

        sun_prop.sun_elevation = radians(6.57)
        sun_prop.sun_rotation = radians(-12.78)

        # ---------------------------------------------------------------------------- #
        #                                     Moon                                     #
        # ---------------------------------------------------------------------------- #

        moon_prop.moon_show_viewport = False
        moon_prop.moon_show_render = False

        # ---------------------------------------------------------------------------- #
        #                                     Stars                                    #
        # ---------------------------------------------------------------------------- #
        
        stars_prop.stars_show_viewport = False
        stars_prop.stars_show_render = False

        return {"FINISHED"}

class STRATUS_OT_full_moon(bpy.types.Operator):
    bl_idname = "stratus.preset_full_moon"
    bl_label = "Full Moon"
    
    def execute(self, context):
                
        cloud_prop = bpy.context.scene.cloud_props
        atmo_prop = bpy.context.scene.atmo_props
        sun_prop = bpy.context.scene.sun_props
        stars_prop = bpy.context.scene.stars_props
        moon_prop = bpy.context.scene.moon_props
        render_prop = bpy.context.scene.render_props

        # ---------------------------------------------------------------------------- #
        #                                    Render                                    #
        # ---------------------------------------------------------------------------- #

        render_prop.env_img_strength = 25.0

        # ---------------------------------- Render ---------------------------------- #

        render_prop.enable_separate_steps_render = True
        render_prop.enable_separate_light_steps_render = True

        render_prop.max_steps_render = 300
        render_prop.max_light_steps_render = 64

        render_prop.cld_0_max_steps_render = 64
        render_prop.cld_1_max_steps_render = 300

        render_prop.cld_0_max_light_steps_render = 32
        render_prop.cld_1_max_light_steps_render = 64

        # --------------------------------- Viewport --------------------------------- #

        render_prop.enable_separate_steps_viewport = True
        render_prop.enable_separate_light_steps_viewport = True

        render_prop.max_steps_viewport = 150
        render_prop.max_light_steps_viewport = 64

        render_prop.cld_0_max_steps_viewport = 25
        render_prop.cld_1_max_steps_viewport = 150

        render_prop.cld_0_max_light_steps_viewport = 16
        render_prop.cld_1_max_light_steps_viewport = 32

        # ---------------------------------------------------------------------------- #
        #                                 Cloud Layer 0                                #
        # ---------------------------------------------------------------------------- #
        
        cloud_prop.cld_0_show_viewport = False
        cloud_prop.cld_0_show_render = False

        # ---------------------------------------------------------------------------- #
        #                                 Cloud Layer 1                                #
        # ---------------------------------------------------------------------------- #
        
        cloud_prop.cld_1_show_viewport = True
        cloud_prop.cld_1_show_render = True

        # --------------------------------- Transform -------------------------------- #

        cloud_prop.cld_1_pos_offset = Vector((100.0,100.0))
        cloud_prop.cld_1_height = 6000.0
        cloud_prop.cld_1_rotation = radians(505.38)
        cloud_prop.cld_1_size = 0.25

        # ----------------------------------- Shape ---------------------------------- #

        cloud_prop.cld_1_bottom_roundness = 0.041667
        cloud_prop.cld_1_thickness = 2.5

        # --------------------------------- Coverage --------------------------------- #
        
        cloud_prop.cld_1_coverage_intsty = 2.0331
        cloud_prop.cld_1_coverage_shape = 0.626191
        cloud_prop.cld_1_curl_octaves = 0

        # ----------------------------------- Shape ---------------------------------- #

        cloud_prop.cld_1_shape_intsty = 0.45

        # ---------------------------------- Detail ---------------------------------- #
        
        cloud_prop.cld_1_detail_intsty = 0.16
        cloud_prop.cld_1_detail_scale = 0.40

        # ---------------------------------- Offsets --------------------------------- #

        cloud_prop.cld_1_detail_offset = Vector((0.0, 0.0))
        cloud_prop.cld_1_shape_offset = Vector((0.0, 0.0))
        cloud_prop.cld_1_coverage_offset = Vector((0.0, 0.0))

        # ---------------------------------- Density --------------------------------- #

        cloud_prop.cld_1_density = 0.679048
        cloud_prop.cld_1_density_height = 0.433334

        # --------------------------------- Lighting --------------------------------- #

        cloud_prop.cld_1_sigma_s = Color((1.0, 1.0, 1.0))
        cloud_prop.cld_1_ambient_intsty = 3.0
        cloud_prop.cld_1_ap_intsty = 0.934524

        cloud_prop.cld_1_atten = .5
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

        sun_prop.sun_show_viewport = False
        sun_prop.sun_show_render = False

        # ---------------------------------------------------------------------------- #
        #                                     Moon                                     #
        # ---------------------------------------------------------------------------- #

        moon_prop.moon_show_viewport = True
        moon_prop.moon_show_render = True

        moon_prop.moon_size = radians(4.17)

        moon_prop.moon_enable_light = True

        moon_prop.moon_intsty = 1.0
        moon_prop.moon_ambient_intsty = 0.00125

        moon_prop.moon_elevation = radians(31.96)
        moon_prop.moon_rotation = radians(-10.68)
        moon_prop.moon_face_rotation = radians(0.0)

        moon_prop.moon_phase = radians(68.37)
        moon_prop.moon_phase_rotation = radians(45.0)

        # ---------------------------------------------------------------------------- #
        #                                     Stars                                    #
        # ---------------------------------------------------------------------------- #
        
        stars_prop.stars_show_viewport = True
        stars_prop.stars_show_render = True
        stars_prop.stars_intsty = 0.1
        stars_prop.stars_rotation = 0.0

        return {"FINISHED"}

class STRATUS_OT_blood_moon(bpy.types.Operator):
    bl_idname = "stratus.preset_blood_moon"
    bl_label = "Blood Moon"
    
    def execute(self, context):
                
        cloud_prop = bpy.context.scene.cloud_props
        atmo_prop = bpy.context.scene.atmo_props
        sun_prop = bpy.context.scene.sun_props
        stars_prop = bpy.context.scene.stars_props
        moon_prop = bpy.context.scene.moon_props
        render_prop = bpy.context.scene.render_props

        # ---------------------------------------------------------------------------- #
        #                                    Render                                    #
        # ---------------------------------------------------------------------------- #

        render_prop.env_img_strength = 30.0

        # ---------------------------------- Render ---------------------------------- #

        render_prop.enable_separate_steps_render = True
        render_prop.enable_separate_light_steps_render = True

        render_prop.max_steps_render = 300
        render_prop.max_light_steps_render = 64

        render_prop.cld_0_max_steps_render = 64
        render_prop.cld_1_max_steps_render = 300

        render_prop.cld_0_max_light_steps_render = 32
        render_prop.cld_1_max_light_steps_render = 64

        # --------------------------------- Viewport --------------------------------- #

        render_prop.enable_separate_steps_viewport = True
        render_prop.enable_separate_light_steps_viewport = True

        render_prop.max_steps_viewport = 150
        render_prop.max_light_steps_viewport = 64

        render_prop.cld_0_max_steps_viewport = 25
        render_prop.cld_1_max_steps_viewport = 150

        render_prop.cld_0_max_light_steps_viewport = 16
        render_prop.cld_1_max_light_steps_viewport = 32

        # ---------------------------------------------------------------------------- #
        #                                 Cloud Layer 0                                #
        # ---------------------------------------------------------------------------- #
        
        cloud_prop.cld_0_show_viewport = False
        cloud_prop.cld_0_show_render = False

        # ---------------------------------------------------------------------------- #
        #                                 Cloud Layer 1                                #
        # ---------------------------------------------------------------------------- #
        
        cloud_prop.cld_1_show_viewport = True
        cloud_prop.cld_1_show_render = True

        # --------------------------------- Transform -------------------------------- #

        cloud_prop.cld_1_pos_offset = Vector((100.0,100.0))
        cloud_prop.cld_1_height = 3413.69
        cloud_prop.cld_1_rotation = radians(292.47)
        cloud_prop.cld_1_size = 0.25

        # ----------------------------------- Shape ---------------------------------- #

        cloud_prop.cld_1_bottom_roundness = 0.041667
        cloud_prop.cld_1_thickness = 2.5

        # --------------------------------- Coverage --------------------------------- #
        
        cloud_prop.cld_1_coverage_intsty = 1.76524
        cloud_prop.cld_1_coverage_shape = 0.346429
        cloud_prop.cld_1_curl_octaves = 0

        # ----------------------------------- Shape ---------------------------------- #

        cloud_prop.cld_1_shape_intsty = 0.45

        # ---------------------------------- Detail ---------------------------------- #
        
        cloud_prop.cld_1_detail_intsty = 0.16
        cloud_prop.cld_1_detail_scale = 0.40

        # ---------------------------------- Offsets --------------------------------- #

        cloud_prop.cld_1_detail_offset = Vector((0.0, 0.0))
        cloud_prop.cld_1_shape_offset = Vector((0.0, 0.0))
        cloud_prop.cld_1_coverage_offset = Vector((0.0, 0.0))

        # ---------------------------------- Density --------------------------------- #

        cloud_prop.cld_1_density = 0.679048
        cloud_prop.cld_1_density_height = 0.12381

        # --------------------------------- Lighting --------------------------------- #

        cloud_prop.cld_1_sigma_s = Color((1.0, 1.0, 1.0))
        cloud_prop.cld_1_ambient_intsty = 3.0
        cloud_prop.cld_1_ap_intsty = 0.5

        cloud_prop.cld_1_atten = .5
        cloud_prop.cld_1_contr = .5
        cloud_prop.cld_1_eccen = .5

        # ---------------------------------------------------------------------------- #
        #                                  Atmosphere                                  #
        # ---------------------------------------------------------------------------- #

        atmo_prop.atm_show_viewport = True
        atmo_prop.atm_show_render = True

        atmo_prop.prop_sky_altitude = 2000.0

        atmo_prop.prop_air = 6.0
        atmo_prop.prop_dust = 1.0
        atmo_prop.prop_ozone = 1.0

        # ---------------------------------------------------------------------------- #
        #                                      Sun                                     #
        # ---------------------------------------------------------------------------- #

        sun_prop.sun_show_viewport = False
        sun_prop.sun_show_render = False

        # ---------------------------------------------------------------------------- #
        #                                     Moon                                     #
        # ---------------------------------------------------------------------------- #

        moon_prop.moon_show_viewport = True
        moon_prop.moon_show_render = True

        moon_prop.moon_size = radians(6.3)

        moon_prop.moon_enable_light = True

        moon_prop.moon_intsty = 1.5
        moon_prop.moon_ambient_intsty = 0.0

        moon_prop.moon_elevation = radians(3.43)
        moon_prop.moon_rotation = radians(-11.86)
        moon_prop.moon_face_rotation = radians(-71.79)

        moon_prop.moon_phase = radians(31.2)
        moon_prop.moon_phase_rotation = radians(-14.07)

        # ---------------------------------------------------------------------------- #
        #                                     Stars                                    #
        # ---------------------------------------------------------------------------- #
        
        stars_prop.stars_show_viewport = True
        stars_prop.stars_show_render = True
        stars_prop.stars_intsty = 0.1
        stars_prop.stars_rotation = 0.0

        return {"FINISHED"}