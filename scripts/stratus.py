import bpy
import gpu
import math
import mathutils

from gpu_extras.presets import draw_texture_2d
from gpu_extras.batch import batch_for_shader

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
                       
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )

# ---------------------------------------------------------------------------- #
#                                    GLOBALS                                   #
# ---------------------------------------------------------------------------- #

img_name = "STRATUS_ENV_TEX"

update_hrdi = False
editing_prop = False

state = {"is_rendering": False}

noise_textures = {}
shader = {}
batch = {}

# ---------------------------------------------------------------------------- #
#                                   CALLBACKS                                  #
# ---------------------------------------------------------------------------- #

def update_viewers(context):
    # Flip the shading type, which force Cycles to update its textures.
    if context.scene.render.engine not in ['BLENDER_EEVEE','BLENDER_WORKBENCH']:
        wman = bpy.data.window_managers['WinMan']
        for win in wman.windows :
            for area in win.screen.areas :
                if area.type=='VIEW_3D' :
                    for space in area.spaces :
                        if space.type == 'VIEW_3D' and space.shading.type == 'RENDERED' :
                            space.shading.type = 'SOLID'
                            space.shading.type = 'RENDERED'

    # Flip some scene property to get the Eevee to update its textures in certain circumstances.
    if context.scene.render.engine == 'BLENDER_EEVEE':
        x = context.scene.render.resolution_percentage
        context.scene.render.resolution_percentage = x                          

def update_prop(self, value):
    global editing_prop
    global update_hrdi

    if not editing_prop:
        editing_prop = True
        update_hrdi = True
        bpy.ops.stratus.prop_observer('INVOKE_DEFAULT')

def set_render_state_true(scene):
    state['is_rendering'] = True

def set_render_state_false(scene):
    state['is_rendering'] = False

def render_hrdi(scene):
    if state['is_rendering']:
        print("DAMMIT Bobby!")

# ---------------------------------------------------------------------------- #
#                                    METHODS                                   #
# ---------------------------------------------------------------------------- #

def init_shaders():
        coords = (
            (-1, +1, 0),
            (+1, +1, 0),
            (-1, -1, 0),
            (+1, -1, 0))
            
        indices = ((0,1,2), (1,3,2))

        #with open("C:/Users/jake/source/blender addons/clouds/cloud_exr.vert", 'r') as file:
        with open("C:/Users/alien/OneDrive/Desktop/Blender Addon Dev/Stratus/shaders/cloud_exr.vert", 'r') as file:
            vertex_shader = file.read()
        #with open("C:/Users/jake/source/blender addons/clouds/cloud_exr.frag", 'r') as file:
        with open("C:/Users/alien/OneDrive/Desktop/Blender Addon Dev/Stratus/shaders/cloud_exr.frag", 'r') as file:
            fragment_shader = file.read()

        shader["hrdi"] = gpu.types.GPUShader(vertex_shader, fragment_shader, )
        batch["hrdi"] = batch_for_shader(shader["hrdi"], 'TRIS', {"position": coords}, indices=indices)
        
        coords = (
            (-1, -1, -1), (+1, -1, -1),
            (-1, +1, -1), (+1, +1, -1),
            (-1, -1, +1), (+1, -1, +1),
            (-1, +1, +1), (+1, +1, +1))

        indices = (
            (0, 1, 3), (0, 2, 3), (4,5,7), (4,6,7),
            (0,4,5), (0,1,5), (2,0,4), (2,6,4),
            (1,3,7), (1, 5,7), (3, 2, 6), (3, 6, 7))
        
        #with open("C:/Users/jake/source/blender addons/clouds/cloud.vert", 'r') as file:
        with open("C:/Users/alien/OneDrive/Desktop/Blender Addon Dev/Stratus/shaders/cloud.vert", 'r') as file:
            vertex_shader = file.read()
        #with open("C:/Users/jake/source/blender addons/clouds/cloud.frag", 'r') as file:
        with open("C:/Users/alien/OneDrive/Desktop/Blender Addon Dev/Stratus/shaders/cloud.frag", 'r') as file:
            fragment_shader = file.read()

        shader["viewport"] = gpu.types.GPUShader(vertex_shader, fragment_shader, )
        batch["viewport"] = batch_for_shader(shader["viewport"], 'TRIS', {"position": coords}, indices=indices)

def init_hrdi_image(width, height):
    if img_name not in bpy.data.images:
        bpy.data.images.new(img_name, width, height, alpha=True, float_buffer=True, stereo3d=False)
    bpy.data.images[img_name].scale(width, height)

def init_textures():        
        # Load 32x32x32 Inverse Worly noise tex
        #img = bpy.data.images.load("C:/Users/jake/source/blender addons/clouds/noiseTex32.png", check_existing=True)
        img = bpy.data.images.load("C:/Users/alien/OneDrive/Desktop/Blender Addon Dev/Stratus/textures/noiseTex32.png", check_existing=True)
        img_buff = gpu.types.Buffer('FLOAT', 32**3 * 4, list(img.pixels[:]))
        noise_textures["tex_32_3D"] = gpu.types.GPUTexture((32, 32, 32), layers=0, is_cubemap=False, format='RGBA8', data=img_buff)
        bpy.data.images.remove(img)
        
        # Load 128 Inverse Worly noise tex
        #img = bpy.data.images.load("C:/Users/jake/source/blender addons/clouds/noiseTex128.png", check_existing=True)
        img = bpy.data.images.load("C:/Users/alien/OneDrive/Desktop/Blender Addon Dev/Stratus/textures/noiseTex128.png", check_existing=True)
        img_buff = gpu.types.Buffer('FLOAT', 128**3 * 4, list(img.pixels[:]))
        noise_textures["tex_128_3D"] = gpu.types.GPUTexture((128, 128, 128), layers=0, is_cubemap=False, format='RGBA8', data=img_buff)
        bpy.data.images.remove(img)
        
        # Load 1024 coverage noise tex  
        #img = bpy.data.images.load("C:/Users/jake/source/blender addons/clouds/coverage1024.png", check_existing=True)
        img = bpy.data.images.load("C:/Users/alien/OneDrive/Desktop/Blender Addon Dev/Stratus/textures/coverage1024.png", check_existing=True)
        noise_textures["tex_1024_2D"] = gpu.texture.from_image(img)
        bpy.data.images.remove(img)
        
        # Load blue noise tex
        #img = bpy.data.images.load("C:/Users/jake/source/blender addons/clouds/HDR_L_1.png", check_existing=True)
        img = bpy.data.images.load("C:/Users/alien/OneDrive/Desktop/Blender Addon Dev/Stratus/textures/HDR_L_1.png", check_existing=True)
        noise_textures["blue_2D"] = gpu.texture.from_image(img)
        bpy.data.images.remove(img)

@staticmethod
def cloud_uniforms(self, context, shader):
    scene = context.scene
    mytool = scene.my_tool
    
    shader.uniform_float("time", mytool.prop_cld_center)
    shader.uniform_float("attinuation_clamp", 1)
    
    shader.uniform_float("planet_center", (0,0,-6378150 - mytool.prop_sky_altitude))
    shader.uniform_float("planet_radius", 6378137)
    shader.uniform_float("atmo_radius", 80000 + 6378137)
    shader.uniform_float("altitude", mytool.prop_sky_altitude)
    
    shader.uniform_float("scale_height_rayleigh",7994)
    shader.uniform_float("scale_height_mie",1200)
    shader.uniform_float("scale_height_absorption",8000)
    
    shader.uniform_float("ray_intensity", mytool.prop_air)
    shader.uniform_float("mie_intensity", mytool.prop_dust)
    shader.uniform_float("absorption_intensity", mytool.prop_ozone)
    
    shader.uniform_float("cld_radius", 6000 + 1000000)
    shader.uniform_float("cld_center", (0.0, 0.0, -1002000))
    shader.uniform_float("cld_thickness", mytool.prop_cld_thickness)
    
    shader.uniform_float("cld_top_roundness", mytool.prop_cld_top_roundness)
    shader.uniform_float("cld_btm_roundness", mytool.prop_cld_btm_roundness)
    
    shader.uniform_float("cld_density", mytool.prop_cld_density)
    shader.uniform_float("cld_top_density", mytool.prop_cld_top_density)
    shader.uniform_float("cld_btm_density", mytool.prop_cld_btm_density)

    shader.uniform_float("cld_detail_scale", mytool.prop_detail_scale)
    shader.uniform_float("cld_shape_scale", mytool.prop_shape_scale)
    shader.uniform_float("cld_coverage_scale", mytool.prop_coverage_scale)
    shader.uniform_float("cld_shape_scale2", mytool.prop_shape_scale2)
    
    shader.uniform_float("cld_detail_intsty", mytool.prop_detail_intsty)
    shader.uniform_float("cld_shape_intsty", mytool.prop_shape_intsty)
    shader.uniform_float("cld_coverage_intsty", mytool.prop_coverage_intsty)
    #shader.uniform_float("prop_shape_intsty2", mytool.prop_shape_intsty2)
    
    shader.uniform_float("cld_silver_intsty", mytool.prop_silver_intsty)
    shader.uniform_float("cld_silver_spread", mytool.prop_silver_spread)
    shader.uniform_float("g", mytool.prop_g)
    
    light_dir = mathutils.Vector(
    (math.sin(mytool.prop_sun_rotation) * math.cos(mytool.prop_sun_elevation),
    math.cos(mytool.prop_sun_rotation) * math.cos(mytool.prop_sun_elevation),
    math.sin(mytool.prop_sun_elevation))
    )
    
    light_dir.normalize()
    
    shader.uniform_float("light_dir", light_dir)
    shader.uniform_float("sun_size", mytool.prop_sun_size)

    shader.uniform_sampler("noise_tex_3D_32", noise_textures["tex_32_3D"])
    shader.uniform_sampler("noise_tex_3D_128", noise_textures["tex_128_3D"])
    shader.uniform_sampler("noise_tex_2D_1024", noise_textures["tex_1024_2D"])
    shader.uniform_sampler("blue_noise", noise_textures["blue_2D"])

@staticmethod
def draw_to_viewport(self, context, enable_cld, enable_atmo):
    
    _shader = shader["viewport"]

    width = context.region.width        
    height = context.region.height
    
    gpu.state.depth_test_set('LESS')
    
    _shader.bind()
    
    proj_mat = bpy.context.region_data.perspective_matrix
    
    inv_vp_mat = proj_mat
    inv_vp_mat = inv_vp_mat.inverted()
    
    _shader.uniform_float("projection", context.region_data.window_matrix)
    
    _shader.uniform_float("inv_vp_mat", inv_vp_mat)    
    _shader.uniform_float("img_size", (width, height))
    
    _shader.uniform_int("enable_cld", enable_cld);
    _shader.uniform_int("enable_atmo", enable_atmo);
    
    _shader.uniform_float("light_intsty", context.scene.my_tool.prop_sun_intensity * 10.0)
    
    cloud_uniforms(self, context, _shader)
    
    batch["viewport"].draw(_shader)
    
    gpu.state.depth_test_set('NONE')

@staticmethod
def draw_to_hrdi(self, context, enable_cld, enable_atmo, width, height):
    mytool = context.scene.my_tool

    with self._offscreen_fbo.bind():
        gpu.state.depth_test_set('NONE')

        _shader = shader["hrdi"]

        _shader.bind()
        _shader.uniform_float("img_size", (width, height))
        _shader.uniform_int("enable_cld", enable_cld);
        _shader.uniform_int("enable_atmo", enable_atmo);
        _shader.uniform_float("light_intsty", mytool.prop_sun_intensity * 1000000.0)
        cloud_uniforms(self, context, _shader)
        
        batch["hrdi"].draw(_shader)
        
    buffer = self._offscreen_fbo.texture_color.read()
    buffer.dimensions = width * height * 4
    bpy.data.images[img_name].pixels.foreach_set(buffer)

@staticmethod
def setup_offscreen(width, height):
    _offscreen_fbo = None
    try:
        _offscreen_fbo = gpu.types.GPUOffScreen(width, height, format='RGBA32F')
    except Exception as e:
        print(e)
    return _offscreen_fbo

# ---------------------------------------------------------------------------- #
#                                  PROPERTIES                                  #
# ---------------------------------------------------------------------------- #

class Properties(PropertyGroup):

# ----------------------------- Cloud Properties ----------------------------- #

    object_color: FloatVectorProperty(  
       name="object_color",
       subtype='COLOR',
       default=(1.0, 1.0, 1.0),
       min=0.0, max=1.0,
       description="color picker",
       update = update_prop
       )

    prop_cld_radius: FloatProperty(
        name = "Cloud Radius",
        description = "A float property",
        subtype="DISTANCE",
        default = 6500,
        min = 1.0,
        update=update_prop
        )
        
    prop_cld_center: FloatProperty(
        name = "Cloud Center",
        description = "A float property",
        subtype="DISTANCE",
        default = 1.0,
        min = 0.0,
        update=update_prop
        )
        
    prop_cld_thickness: FloatProperty(
        name = "Thickness",
        description = "A float property",
        subtype="DISTANCE",
        default = 50,
        min = 1.0,
        update=update_prop
        )
        
    prop_cld_top_roundness: FloatProperty(
        name = "Top Roundness",
        description = "A float property",
        default = 0.0,
        min = 0.0,
        max = 1.0,
        update=update_prop
        )
        
    prop_cld_btm_roundness: FloatProperty(
        name = "Bottom Roundness",
        description = "A float property",
        default = 0.2,
        min = 0.0,
        max = 1.0,
        update=update_prop
        )
        
    prop_cld_density: FloatProperty(
        name = "Density",
        description = "A float property",
        default = 2.0,
        min = 0.0,
        update=update_prop
        )

    prop_cld_top_density: FloatProperty(
        name = "Top Density",
        description="Something",
        default=1.0,
        min= 0.0,
        max = 1.0,
        update=update_prop
        ) 
    
    prop_cld_btm_density: FloatProperty(
        name = "Bottom Density",
        description="Something",
        default=1.0,
        min= 0.0,
        max = 1.0,
        update=update_prop
        ) 
    
    prop_detail_scale: FloatProperty(
        name = "Detail Noise Scale",
        description="Something",
        default=0.08,
        min= 0.0,
        max = 1.0,
        update=update_prop
        ) 
    
    prop_shape_scale: FloatProperty(
        name = "Shape Noise Scale",
        description="Something",
        default=0.025,
        min= 0.0,
        max = 1.0,
        update=update_prop
        ) 
    
    prop_coverage_scale: FloatProperty(
        name = "Coverage Noise Scale",
        description="Something",
        default=0.0008,
        min= 0.0,
        max = 1,
        update=update_prop
        ) 
    
    prop_shape_scale2: FloatProperty(
        name = "Shape Noise Scale2",
        description="Something",
        default=0.01,
        min= 0.0,
        max = 1.0,
        update=update_prop
        ) 
    
    prop_detail_intsty: FloatProperty(
        name = "Detail Noise Intensity",
        description="Something",
        default=0.3,
        min= 0.0,
        max = 10.0,
        update=update_prop
        ) 
    
    prop_shape_intsty: FloatProperty(
        name = "Shape Noise Intensity",
        description="Something",
        default=0.25,
        min= 0.0,
        max = 10.0,
        update=update_prop
        ) 

    prop_coverage_intsty: FloatProperty(
        name = "Coverage Noise Intensity",
        description="Something",
        default=1.0,
        min= 0.0,
        max = 10.0,
        update=update_prop
        )
    
    prop_shape_intsty2: FloatProperty(
        name = "Shape Noise Intensity2",
        description="Something",
        default=0.25,
        min= 0.0,
        max = 1.0,
        update=update_prop
        ) 
    
    prop_silver_intsty: FloatProperty(
        name = "Silverline Intensity",
        description="Something",
        default=1.13,
        min= 0.0,
        update=update_prop
        )  
    
    prop_silver_spread: FloatProperty(
        name = "Silverline Spread",
        description="Something",
        default=0.12,
        min= 0.0,
        max = 1.0,
        update=update_prop
        ) 
    
    prop_g: FloatProperty(
        name = "g",
        description="Something",
        default=-0.02,
        min= -1.0,
        max = 1.0,
        update=update_prop
        )  
    
    density_offset: FloatProperty(
        name = "density_offset",
        description="Something",
        default=100,
        update=update_prop
        #min= -1.0,
        #max = 1.0
        )  
         
# ----------------------- Atmosphere and Sun Properties ---------------------- #

    prop_sundisk: BoolProperty(
        name="Sun Disk",
        description="A bool property",
        default = True,
        update=update_prop
        )

    prop_sun_size: FloatProperty(
        name = "Sun Size",
        description = "A float property",
        default = 0.545,
        subtype="ANGLE",
        min = 0.0,
        max = 90.0,
        update=update_prop
        )
        
    prop_sun_intensity: FloatProperty(
        name = "Sun Intensity",
        description = "A float property",
        default = 1.0,
        min = 0.0,
        update=update_prop
        )
        
    prop_sun_elevation: FloatProperty(
        name = "Sun Elevation",
        description = "A float property",
        default = 15.0,
        subtype="ANGLE",
        update=update_prop
        )
        
    prop_sun_rotation: FloatProperty(
        name = "Sun Rotation",
        description = "A float property",
        default = 0.0,
        subtype="ANGLE",
        update=update_prop
        )
        
    prop_sky_altitude: FloatProperty(
        name = "Altitude",
        description = "A float property",
        default = 0.0,
        subtype="DISTANCE",
        min = 0.0,
        update=update_prop
        )

    prop_air: FloatProperty(
        name = "Air",
        description="Something",
        default=1.0,
        min= 0.0,
        max = 10.0,
        update=update_prop
        ) 
    
    prop_dust: FloatProperty(
        name = "Dust",
        description="Something",
        default=1.0,
        min= 0.0,
        max = 10.0,
        update=update_prop
        ) 
    
    prop_ozone: FloatProperty(
        name = "Ozone",
        description="Something",
        default=1.0,
        min= 0.0,
        max = 10.0,
        update=update_prop
        ) 
    
    atm_show_viewport: BoolProperty(
        name="",
        description="A bool property",
        default = True,
        update=update_prop
        )
        
    atm_show_render: BoolProperty(
        name="",
        description="A bool property",
        default = True,
        update=update_prop
        )
    
    cld_show_viewport: BoolProperty(
        name="",
        description="A bool property",
        default = True,
        update=update_prop
        )
        
    cld_show_render: BoolProperty(
        name="",
        description="A bool property",
        default = True,
        update=update_prop
        )

# ---------------------------------------------------------------------------- #
#                                   OPERATORS                                  #
# ---------------------------------------------------------------------------- #

class STRATUS_OT_render(bpy.types.Operator):
    bl_idname = "stratus.render_hrdi"
    bl_label = "Stratus Render HRDI"

    _offscreen_fbo = None

    def invoke(self, context, event):
        width = 1
        height = 1

        init_hrdi_image(width, height)

        self._offscreen_fbo = setup_offscreen(self, context, width, height)
        if not self._offscreen_fbo:
            self.report({'ERROR'}, "Error initializing offscreen buffer. More details in the console")
            return {'CANCELLED'}
        return self.execute(context)

    def execute(self, context):     
        enable_cld = True
        enable_atmo = True

        width = 1
        height = 1

        draw_to_hrdi(self, context, enable_cld, enable_atmo, width, height)

        return {'FINISHED'}

class STRATUS_OT_viewport_editor(bpy.types.Operator):
    bl_idname = "stratus.viewport_editor"
    bl_label = "Stratus Viewport Editor"

    _offscreen_fbo = None
    _handle_draw = None
    _is_enabled = False

    # manage draw handler
    @staticmethod
    def draw_callback(self, context):
        global update_hrdi
        if update_hrdi is True:
            enable_cld = True
            enable_atmo = True

            width = 1
            height = 1

            draw_to_hrdi(self, context, enable_cld, enable_atmo, width, height)
        
        draw_to_viewport(self, context, enable_cld, enable_atmo)

    @staticmethod
    def handle_add(self, context):
        STRATUS_OT_viewport_editor._handle_draw = bpy.types.SpaceView3D.draw_handler_add(
                self.draw_callback, (self, context),
                'WINDOW', 'POST_VIEW',
                )

    @staticmethod
    def handle_remove():
        if STRATUS_OT_viewport_editor._handle_draw is not None:
            bpy.types.SpaceView3D.draw_handler_remove(STRATUS_OT_viewport_editor._handle_draw, 'WINDOW')

        STRATUS_OT_viewport_editor._handle_draw = None

    def init_world_node_tree(self):
        C = bpy.context
        scn = C.scene

        # Get the environment node tree of the current scene
        node_tree = scn.world.node_tree
        tree_nodes = node_tree.nodes

        # Clear all nodes
        tree_nodes.clear()

        # Add Background node
        node_background = tree_nodes.new(type='ShaderNodeBackground')
        node_background.inputs["Strength"].default_value = 0.01

        # Add Environment Texture node
        node_environment = tree_nodes.new('ShaderNodeTexEnvironment')
        # Load and assign the image to the node property
        node_environment.image = bpy.data.images[img_name]
        node_environment.location = -300,0

        # Add Output node
        node_output = tree_nodes.new(type='ShaderNodeOutputWorld')   
        node_output.location = 200,0

        # Link all nodes
        links = node_tree.links
        link = links.new(node_environment.outputs["Color"], node_background.inputs["Color"])
        link = links.new(node_background.outputs["Background"], node_output.inputs["Surface"])
        
    # operator functions
    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if STRATUS_OT_viewport_editor._is_enabled:
            self.cancel(context)
            return {'FINISHED'}
        else:                     
            STRATUS_OT_viewport_editor.init_world_node_tree(self)

            width = 1
            height = 1

            init_hrdi_image(width, height)

            self._offscreen_fbo = setup_offscreen(self, context, width, height)
            
            if not self._offscreen_fbo:
                self.report({'ERROR'}, "Error initializing offscreen buffer. More details in the console")
                return {'CANCELLED'}

            STRATUS_OT_viewport_editor.handle_add(self, context)
            STRATUS_OT_viewport_editor._is_enabled = True

            if context.area:
                context.area.tag_redraw()

            context.window_manager.modal_handler_add(self)
            
            return {'RUNNING_MODAL'}

    def cancel(self, context):
        STRATUS_OT_viewport_editor.handle_remove()
        STRATUS_OT_viewport_editor._is_enabled = False

        if context.area:
            context.area.tag_redraw()

class STRATUS_OT_prop_observer(bpy.types.Operator):
    bl_idname = "stratus.prop_observer"
    bl_label  = ""

    _timer = None
    _stop = False
    def invoke(self, context, event):
            wm = context.window_manager
            self._timer = wm.event_timer_add(0.016, window=context.window)

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}

    def modal(self, context, event):
        global editing_prop
        global update_hrdi

        if self._stop:
            editing_prop = False
            update_hrdi = False
            update_viewers(context)
            return {'FINISHED'}
        
        if event.value == 'RELEASE':
            self._stop = True

        return {'PASS_THROUGH'}

# ---------------------------------------------------------------------------- #
#                                    PANELS                                    #
# ---------------------------------------------------------------------------- #

class STRATUS_PT_cloud_panel(bpy.types.Panel):
    bl_label = "Clouds"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        
        icon_vp = 'RESTRICT_VIEW_OFF' if mytool.cld_show_viewport else "RESTRICT_VIEW_ON"
        icon_r = 'RESTRICT_RENDER_OFF' if mytool.cld_show_render else "RESTRICT_RENDER_ON"

        render_options = layout.row(align=True)
        render_options.label(text="Clouds")
        render_options.prop(mytool, 'cld_show_viewport', icon=icon_vp)
        render_options.prop(mytool, 'cld_show_render', icon=icon_r)

        layout.prop(mytool, "object_color")
        layout.prop(mytool, "prop_cld_radius")
        layout.prop(mytool, "prop_cld_center")
        layout.prop(mytool, "prop_cld_thickness")
        layout.separator()
        layout.prop(mytool, "prop_cld_top_roundness", slider=True)
        layout.prop(mytool, "prop_cld_btm_roundness", slider=True)
        layout.separator()
        layout.prop(mytool, "prop_cld_density")
        layout.prop(mytool, "prop_cld_top_density", slider=True)
        layout.prop(mytool, "prop_cld_btm_density", slider=True)
        layout.separator()
        layout.prop(mytool, "prop_detail_scale")
        layout.prop(mytool, "prop_shape_scale")
        layout.prop(mytool, "prop_coverage_scale")
        layout.prop(mytool, "prop_shape_scale2")
        layout.separator()
        layout.prop(mytool, "prop_detail_intsty")
        layout.prop(mytool, "prop_shape_intsty")
        layout.prop(mytool, "prop_coverage_intsty")
        layout.separator()
        layout.prop(mytool, "prop_silver_intsty")
        layout.prop(mytool, "prop_silver_spread", slider=True)
        layout.prop(mytool, "prop_g", slider=True)
        
class STRATUS_PT_atmo_panel(bpy.types.Panel):
    bl_label = "Atmosphere"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        
        icon_vp = 'RESTRICT_VIEW_OFF' if mytool.atm_show_viewport else "RESTRICT_VIEW_ON"
        icon_r = 'RESTRICT_RENDER_OFF' if mytool.atm_show_render else "RESTRICT_RENDER_ON"

        render_options = layout.row(align=True)
        render_options.label(text="Atmosphere")
        render_options.prop(mytool, 'atm_show_viewport', icon=icon_vp)
        render_options.prop(mytool, 'atm_show_render', icon=icon_r)
        
        layout.prop(mytool, "prop_sundisk")
        layout.separator()
        layout.prop(mytool, "prop_sun_size")
        layout.prop(mytool, "prop_sun_intensity")
        layout.separator()
        layout.prop(mytool, "prop_sun_elevation")
        layout.prop(mytool, "prop_sun_rotation")
        layout.separator()
        layout.prop(mytool, "prop_sky_altitude")
        layout.separator()
        layout.prop(mytool, "prop_air", slider=True)
        layout.prop(mytool, "prop_dust", slider=True)
        layout.prop(mytool, "prop_ozone", slider=True)

classes = (Properties, STRATUS_OT_viewport_editor, STRATUS_OT_prop_observer, STRATUS_PT_cloud_panel, STRATUS_PT_atmo_panel)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.my_tool = PointerProperty(type=Properties)
    
    bpy.context.scene.my_tool.is_dragging = False

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    del bpy.types.Scene.my_tool

if __name__ == "__main__":
    register()
    bpy.app.handlers.frame_change_post.append(render_hrdi)

    bpy.app.handlers.render_init.append(set_render_state_true)
    bpy.app.handlers.render_cancel.append(set_render_state_false)
    bpy.app.handlers.render_complete.append(set_render_state_false)

    init_textures()
    init_shaders()
