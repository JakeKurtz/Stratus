import bpy
import bgl
import gpu
import math
import mathutils
import ctypes
import addon_utils

import itertools

from mathutils import Matrix, Vector
from datetime import datetime

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
img_name_sky_irra = "STRARUS_SKY_IRRA_TEX"

irradiance_width = 128
irradiance_height = 64

refresh_viewports = False
resize_hrdi = False
reset_hrdi = False
update_hrdi = False
editing_prop = False

state = {"is_rendering": False}

ogl_noise_textures = bgl.Buffer(bgl.GL_INT, [6])
ogl_moon_textures = bgl.Buffer(bgl.GL_INT, [2])
noise_textures = {}
shader = {}
batch = {}

offscreen = None
sky_irradiance_offscreen = None
fbo = None

planet_center = Vector((0,0,-6378150))
planet_radius = 6378137
atmo_radius = planet_radius + 80000

scale_height_rayleigh = 7994
scale_height_mie = 1200
scale_height_absorption = 8000

beta_mie = Vector((21e-6,21e-6,21e-6))
beta_ozone = Vector((2.0556e-6, 4.9788e-6, 2.136e-7))
beta_ray = Vector((5.87901e-6, 13.7369e-6, 33.5374e-6))

sun_lux = 100000
moon_lux = 0.25

zenith_transmittance = 0.0

def setup_offscreen(width, height):
    _offscreen_fbo = None
    try:
        _offscreen_fbo = gpu.types.GPUOffScreen(width, height, format='RGBA32F')
    except Exception as e:
        print(e)
    return _offscreen_fbo

 # ------------------------------------- - ------------------------------------ #

class EXRImage:
    _width = 1024
    _height = 512

    _grid_width = 0
    _grid_height = 0

    _tile_size = 0
    _tile_id = 0
    _nmb_of_tiles = 0

    _offscreen = None
    _name = None

    _img_buff = []

    def __init__(self, name):
        self._name = name
        if self._name not in bpy.data.images:
                bpy.data.images.new(
                    self._name, 
                    self._width, 
                    self._height, 
                    alpha=True, 
                    float_buffer=True)
        
        bpy.data.images[self._name].scale(self._width, self._height)
        self.set_tile_size(512)
        self._offscreen = setup_offscreen(self._width, self._height)
    
    def _init_tile_props(self):
        self._grid_width = int(self._width / self._tile_size)
        self._grid_height = int(self._height / self._tile_size) 
        self._nmb_of_tiles = int(self._grid_width * self._grid_height)

    def set_size(self, size):
        assert type(size) == int or float, "size should be a number, i.e. int or float."
        assert (size >= 0.25 and size <= 24.0), "size should be between the values 0.25 and 24.0"

        self._width = int(1024.0 * float(size))
        self._height = int(512.0 * float(size))

        bpy.data.images[self._name].scale(self._width, self._height)

        if self._offscreen is not None:
            self._offscreen.free()
        self._offscreen = setup_offscreen(self._width, self._height)

        self._init_tile_props()

    def get_size(self):
        return (self._width, self._height)

    def set_tile_size(self, tile_size):
        self._tile_size = tile_size
        self._init_tile_props()

    def get_tile_size(self):
        return self._tile_size

    def get_tile_pos(self):
        tile_x = int(self._tile_id % self._grid_width)
        tile_y = int(self._tile_id / self._grid_width)
        return (tile_x, tile_y)

    def get_offscreen(self):
        return self._offscreen

    def append_tile(self):
        if not self.completed():
            self._tile_id += 1

    def completed(self):
        return (self._tile_id >= self._nmb_of_tiles)
    
    def reset(self):
        self._tile_id = 0

    def save(self):
        self._img_buff = self._offscreen.texture_color.read()
        self._img_buff.dimensions = self._width * self._height * 4
        bpy.data.images[self._name].pixels.foreach_set(self._img_buff)
        print("saved.")

 # ------------------------------------- - ------------------------------------ #

# ---------------------------------------------------------------------------- #
#                                   CALLBACKS                                  #
# ---------------------------------------------------------------------------- #

def update_viewers(context):
    # Flip the shading type, which force Cycles to update its textures.
    if context.scene.render.engine not in ['BLENDER_EEVEE','BLENDER_WORKBENCH']:
        wm = bpy.data.window_managers['WinMan']
        #wm = context.window_manager
        for win in wm.windows :
            for area in win.screen.areas :
                if area.type=='VIEW_3D' :
                    for space in area.spaces :
                        if space.type == 'VIEW_3D' and space.shading.type == 'RENDERED' :
                            #print(space.shading.type)
                            space.shading.type = 'SOLID'
                            space.shading.type = 'RENDERED'

    # Flip some scene property to get the Eevee to update its textures in certain circumstances.
    if context.scene.render.engine == 'BLENDER_EEVEE':
        x = context.scene.render.resolution_percentage
        context.scene.render.resolution_percentage = x                          

def update_prop(self, value):
    global editing_prop
    global reset_hrdi
    #global update_hrdi

    if not editing_prop:
        reset_hrdi = True
        editing_prop = True
        #update_hrdi = True
        bpy.ops.stratus.prop_observer('INVOKE_DEFAULT')

def update_node_tree(self, context):
    init_world_node_tree(self)

def update_env_img_size(self, context):
    global resize_hrdi
    resize_hrdi = True
    '''
    prop = context.scene.my_tool
    size = float(prop.env_img_viewport_size)

    width = int(1024.0 * size)
    height = int(512.0 * size)

    if img_name not in bpy.data.images:
        bpy.data.images.new(img_name, width, height, alpha=True, float_buffer=True, stereo3d=False)
    bpy.data.images[img_name].scale(width, height)

    self._offscreen_fbo = setup_offscreen(width, height)

    print(width,height)

    image = bpy.data.images[img_name]
    image.scale(width, height)
    col_tex = gpu.texture.from_image(image)
    self._fbo = gpu.types.GPUFrameBuffer(depth_slot=None, color_slots=(col_tex))
    '''

def update_cld_coverage_map(self, value):
    mytool = bpy.context.scene.my_tool
    img = mytool.cld_coverage_map

    if img is not None:
        img.gl_load()
        ogl_noise_textures[4] = img.bindcode

        img = bpy.data.images.load("C:/Users/jake/source/blender addons/clouds/Stratus/textures/coverage2048.png", check_existing=True)
        img.gl_load()

        buffer = bgl.Buffer(bgl.GL_FLOAT, (2048**2) * 4)
        
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, ogl_noise_textures[4])

        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_WRAP_S, bgl.GL_CLAMP_TO_EDGE)
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_WRAP_T, bgl.GL_CLAMP_TO_EDGE)
        bgl.glTexParameteri(bgl.GL_TEXTURE_3D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_LINEAR)
        bgl.glTexParameteri(bgl.GL_TEXTURE_3D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_LINEAR)
                
        img.gl_free()
        bpy.data.images.remove(img)

def set_render_state_true(scene):
    state['is_rendering'] = True

def set_render_state_false(scene):
    state['is_rendering'] = False

# ---------------------------------------------------------------------------- #
#                                    METHODS                                   #
# ---------------------------------------------------------------------------- #

def new_shader(name, vert_shader, frag_shader, coords, indices):
    shader[name] = gpu.types.GPUShader(vert_shader, frag_shader, )
    batch[name] = batch_for_shader(shader[name], 'TRIS', {"position": coords}, indices=indices)
    print("built shader "+name)

def get_filepath():
    for mod in addon_utils.modules():
        if mod.bl_info['name'] == "Stratus":
            filepath = mod.__file__
            print(filepath)
        else:
            pass
    return filepath

def init_shaders():
        filepath = "C:/Users/jake/source/blender addons/clouds/Stratus"#get_filepath()

        plane_coords = (
            (-1, +1, 0),
            (+1, +1, 0),
            (-1, -1, 0),
            (+1, -1, 0))        
        plane_indices = ((0,1,2), (1,3,2))

        cube_coords = (
            (-1, -1, -1), (+1, -1, -1),
            (-1, +1, -1), (+1, +1, -1),
            (-1, -1, +1), (+1, -1, +1),
            (-1, +1, +1), (+1, +1, +1))
        cube_indices = (
            (0, 1, 3), (0, 2, 3), (4,5,7), (4,6,7),
            (0,4,5), (0,1,5), (2,0,4), (2,6,4),
            (1,3,7), (1, 5,7), (3, 2, 6), (3, 6, 7))

        # -------------------------------- HRDI Shader ------------------------------- #

        with open(filepath+"/shaders/vertex_shaders/stratus_hrdi.vert", 'r') as file:
            vertex_shader = file.read()
        with open(filepath+"/shaders/fragment_shaders/stratus_hrdi.frag", 'r') as file:
            fragment_shader = file.read()
        new_shader("hrdi", vertex_shader, fragment_shader, plane_coords, plane_indices)

        # -------------------------------- Sky Shader -------------------------------- #

        with open(filepath+"/shaders/vertex_shaders/stratus_sky.vert", 'r') as file:
            vertex_shader = file.read()
        with open(filepath+"/shaders/fragment_shaders/stratus_sky.frag", 'r') as file:
            fragment_shader = file.read()
        new_shader("sky", vertex_shader, fragment_shader, plane_coords, plane_indices)

        # ----------------------------- Irradiance Shader ---------------------------- #

        with open(filepath+"/shaders/vertex_shaders/stratus_irra.vert", 'r') as file:
            vertex_shader = file.read()
        with open(filepath+"/shaders/fragment_shaders/stratus_irra.frag", 'r') as file:
            fragment_shader = file.read()
        new_shader("sky_irra", vertex_shader, fragment_shader, plane_coords, plane_indices)

        # ------------------------------ Viewport Shader ----------------------------- #
        
        with open(filepath+"/shaders/vertex_shaders/stratus_viewport.vert", 'r') as file:
            vertex_shader = file.read()
        with open(filepath+"/shaders/fragment_shaders/stratus_viewport.frag", 'r') as file:
            fragment_shader = file.read()
        new_shader("viewport", vertex_shader, fragment_shader, plane_coords, plane_indices)

        # ------------------------------- Screen Shader ------------------------------ #

        with open(filepath+"/shaders/vertex_shaders/stratus_screen.vert", 'r') as file:
            vertex_shader = file.read()
        with open(filepath+"/shaders/fragment_shaders/stratus_screen.frag", 'r') as file:
            fragment_shader = file.read()
        new_shader("screen", vertex_shader, fragment_shader, cube_coords, cube_indices)

def init_hrdi_image(img_name, width, height):
    if img_name not in bpy.data.images:
        bpy.data.images.new(img_name, width, height, alpha=True, float_buffer=True, stereo3d=False)
    bpy.data.images[img_name].scale(width, height)

    if img_name_sky_irra not in bpy.data.images:
        bpy.data.images.new(img_name_sky_irra, 128, 64, alpha=True, float_buffer=True, stereo3d=False)
    bpy.data.images[img_name_sky_irra].scale(128, 64)

def gen_bgl_buffer(image):
    width = image.size[0]
    height = image.size[1]
    channels = image.channels
    return bgl.Buffer(bgl.GL_FLOAT, (width * height * channels), list(image.pixels[:]))

def bgl_texture_from_image(image, dim, bindcode):

    buffer = gen_bgl_buffer(image)
    
    if len(dim) == 2:
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, bindcode)

        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_WRAP_S, bgl.GL_REPEAT)
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_WRAP_T, bgl.GL_REPEAT)
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_LINEAR)
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_LINEAR)

        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_BASE_LEVEL, 0)
        bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAX_LEVEL, 0)
                
        bgl.glTexImage2D(bgl.GL_TEXTURE_2D, 0, bgl.GL_RGBA, dim[0], dim[1], 0, bgl.GL_RGBA, bgl.GL_FLOAT, buffer)

        bgl.glBindTexture(bgl.GL_TEXTURE_2D, 0)
    elif len(dim) == 3:
        bgl.glBindTexture(bgl.GL_TEXTURE_3D, bindcode)

        bgl.glTexParameteri(bgl.GL_TEXTURE_3D, bgl.GL_TEXTURE_WRAP_S, bgl.GL_REPEAT)
        bgl.glTexParameteri(bgl.GL_TEXTURE_3D, bgl.GL_TEXTURE_WRAP_T, bgl.GL_REPEAT)
        bgl.glTexParameteri(bgl.GL_TEXTURE_3D, bgl.GL_TEXTURE_WRAP_R, bgl.GL_REPEAT)
        bgl.glTexParameteri(bgl.GL_TEXTURE_3D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_LINEAR)
        bgl.glTexParameteri(bgl.GL_TEXTURE_3D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_LINEAR)

        bgl.glTexParameteri(bgl.GL_TEXTURE_3D, bgl.GL_TEXTURE_BASE_LEVEL, 0)
        bgl.glTexParameteri(bgl.GL_TEXTURE_3D, bgl.GL_TEXTURE_MAX_LEVEL, 0)

        bgl.glTexImage3D(bgl.GL_TEXTURE_3D, 0, bgl.GL_RGBA, dim[0], dim[1], dim[2], 0, bgl.GL_RGBA, bgl.GL_FLOAT, buffer)

        bgl.glBindTexture(bgl.GL_TEXTURE_3D, 0)

    bpy.data.images.remove(image)

def init_textures():
        filepath = "C:/Users/jake/source/blender addons/clouds/Stratus"#get_filepath()

        bgl.glGenTextures(6, ogl_noise_textures)
        bgl.glGenTextures(2, ogl_moon_textures)

        img = bpy.data.images.load(filepath+"/textures/noise/noise_32.png", check_existing=True)
        bgl_texture_from_image(img, (32, 32, 32), ogl_noise_textures[0])

        img = bpy.data.images.load(filepath+"/textures/noise/noise_128.png", check_existing=True)
        bgl_texture_from_image(img, (128, 128, 128), ogl_noise_textures[1])
        
        img = bpy.data.images.load(filepath+"/textures/noise/noise_1024.png", check_existing=True)
        bgl_texture_from_image(img, (img.size[0], img.size[1]), ogl_noise_textures[2])

        img = bpy.data.images.load(filepath+"/textures/noise/noise_blue_128.png", check_existing=True)
        bgl_texture_from_image(img, (img.size[0], img.size[1]), ogl_noise_textures[3])
        
        img = bpy.data.images.load(filepath+"/textures/moon/moon_albedo.png", check_existing=True)
        bgl_texture_from_image(img, (img.size[0], img.size[1]), ogl_moon_textures[0])

        img = bpy.data.images.load(filepath+"/textures/moon/moon_normal.png", check_existing=True)
        bgl_texture_from_image(img, (img.size[0], img.size[1]), ogl_moon_textures[1])

def compute_dir(theta, phi):
    dir = Vector(
    (
        math.sin(phi) * math.cos(theta),
        math.cos(phi) * math.cos(theta),
        math.sin(theta)
    ))
    dir.normalize()
    return dir

def sun_uniforms(shader, Ls):
    prop = bpy.context.scene.my_tool

    shader.uniform_int("enable_sun_as_light", prop.sun_enable_light)
    #shader.uniform_float("sun_size", prop.sun_size)

    #sun_solid_angle = prop.sun_size * math.pi / 180.0
    half_angular = prop.sun_size / 2.0
    sun_solid_angle = 2.0*math.pi*(1.0 - math.cos(0.5*half_angular))

    #shader.uniform_float("sun_disk_intsty", prop.sun_disk_intsty * 100000)
    shader.uniform_float("sun_half_angular", half_angular)
    shader.uniform_float("sun.dir", compute_dir(prop.sun_elevation, prop.sun_rotation))
    shader.uniform_float("sun.intsty", prop.sun_disk_intsty)
    shader.uniform_float("sun.silver_intsty", prop.sun_silver_intsty)
    shader.uniform_float("sun.silver_spread", prop.sun_silver_spread)

def moon_uniforms(shader, Ls):
    prop = bpy.context.scene.my_tool

    moon_dir = compute_dir(prop.moon_elevation, prop.moon_rotation)

    # Rotate Moon so that it alwasy faces the origin 
    inv_lookat_mat = look_at(moon_dir, Vector((0,0,0)), Vector((0,0,1)))
    inv_lookat_mat.invert()

    # Flip the x,y values when Moon goes over the zenith i.e theta > 90d
    if (math.cos(prop.moon_elevation) < 0.0):
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
    rot_moon_face_mat = Matrix.Rotation(prop.moon_face_rotation, 4, moon_dir)

    # Combine rotations
    rot_mat = rot_offset_mat @ inv_lookat_mat @ rot_moon_face_mat
    shader.uniform_float("moon_rot_mat", rot_mat)  

    if (prop.moon_use_sun_dir):
        moon_phase_dir = compute_dir(prop.sun_elevation, prop.sun_rotation)
    else:
        inv_moon_dir = -moon_dir
        rot_mat = Matrix.Rotation(prop.moon_phase_rotation, 4, inv_moon_dir)

        moon_up = rot_mat @ moon_up
        moon_up.normalize()

        rot_mat = Matrix.Rotation(prop.moon_phase, 4, moon_up)
        moon_phase_dir = rot_mat @ inv_moon_dir
        moon_phase_dir.normalize()

    shader.uniform_int("enable_moon_as_light", prop.moon_enable_light)
    shader.uniform_float("moon_phase_dir", moon_phase_dir)
    shader.uniform_float("moon_half_angular", prop.moon_size/2.0)

    shader.uniform_float("moon_ambient_intsty", prop.moon_ambient_intsty)

    shader.uniform_float("moon.dir", moon_dir)
    shader.uniform_float("moon.intsty", prop.moon_disk_intsty)
    shader.uniform_float("moon.silver_intsty", prop.moon_silver_intsty)
    shader.uniform_float("moon.silver_spread", prop.moon_silver_spread)

def atmo_uniforms(shader):
    prop = bpy.context.scene.my_tool

    #shader.uniform_float("planet_center", (0,0,-6378150 - prop.prop_sky_altitude))
    #shader.uniform_float("planet_radius", 6378137)
    #shader.uniform_float("atmo_radius", 80000 + 6378137)

    #shader.uniform_float("planet_center", (0,0,-6378150 - prop.prop_sky_altitude))
    #shader.uniform_float("planet_radius", 6360000)
    #shader.uniform_float("atmo_radius", 6420000)
    
    #shader.uniform_float("scale_height_rayleigh",8000)
    #shader.uniform_float("scale_height_mie",1200)
    #shader.uniform_float("scale_height_absorption",8000)
    
    shader.uniform_float("rayleigh_density", prop.prop_air)
    shader.uniform_float("mie_density", prop.prop_dust)
    shader.uniform_float("ozone_density", prop.prop_ozone)

def cloud_uniforms(shader):
    prop = bpy.context.scene.my_tool

    d = prop.cld_horizon_dst
    h = prop.cld_horizon_h
    cld_domain_radius = math.pow((2.0*d),2.0) / (8.0 * h) + h * 0.5
    cld_domain_center = Vector((0.0, 0.0, h-cld_domain_radius))

    shader.uniform_float("cld_domain_min_radius", cld_domain_radius)
    shader.uniform_float("cld_domain_max_radius", cld_domain_radius + 15000)
    shader.uniform_float("cld_domain_center", cld_domain_center)
    
    shader.uniform_float("cld_top_roundness", prop.cld_top_roundness)
    shader.uniform_float("cld_btm_roundness", prop.cld_btm_roundness)
    shader.uniform_float("cld_top_density", prop.cld_top_density)
    shader.uniform_float("cld_btm_density", prop.cld_btm_density)
    shader.uniform_float("cld_ambient_intsty", prop.ambient_intsty)

    # ---------------------------------------------------------------------------- #

    shader.uniform_int("enable_cld_0",              prop.cld_0_enable)
    shader.uniform_float("cld_0_density",           prop.cld_0_density)
    shader.uniform_float("cld_0_size",              prop.cld_0_size)
    shader.uniform_float("cld_0_radius",            prop.cld_0_height + cld_domain_radius)
    shader.uniform_float("cld_0_height",            prop.cld_0_thickness)
    shader.uniform_float("cld_0_detail_intsty",     prop.cld_0_detail_intsty)
    shader.uniform_float("cld_0_shape_intsty",      prop.cld_0_shape_intsty)
    shader.uniform_float("cld_0_coverage_intsty",   prop.cld_0_coverage_intsty)

    shader.uniform_float("cld_0_detail_offset",     prop.cld_0_detail_offset)
    shader.uniform_float("cld_0_shape_offset",      prop.cld_0_shape_offset)
    shader.uniform_float("cld_0_coverage_offset",   prop.cld_0_coverage_offset)

    cld_0_trans = Matrix.Translation(cld_domain_center + Vector((0,0,6360e3)))
    cld_0_rot = Matrix.Rotation(prop.cld_0_rotation, 4, 'Z')

    cld_0_transform = cld_0_rot @ cld_0_trans
    cld_0_transform.invert()
    
    shader.uniform_float("cld_0_transform", cld_0_transform)

    # ---------------------------------------------------------------------------- #

    shader.uniform_int("enable_cld_1",              prop.cld_1_enable)
    shader.uniform_float("cld_1_density",           prop.cld_1_density)
    shader.uniform_float("cld_1_size",              prop.cld_1_size)
    shader.uniform_float("cld_1_radius",            prop.cld_1_height + cld_domain_radius)
    shader.uniform_float("cld_1_height",            prop.cld_1_thickness)
    shader.uniform_float("cld_1_detail_intsty",     prop.cld_1_detail_intsty)
    shader.uniform_float("cld_1_shape_intsty",      prop.cld_1_shape_intsty)
    shader.uniform_float("cld_1_coverage_intsty",   prop.cld_1_coverage_intsty)

    shader.uniform_float("cld_1_detail_offset",     prop.cld_1_detail_offset)
    shader.uniform_float("cld_1_shape_offset",      prop.cld_1_shape_offset)
    shader.uniform_float("cld_1_coverage_offset",   prop.cld_1_coverage_offset)

    cld_1_trans = Matrix.Translation(cld_domain_center + Vector((0,0,6360e3)))
    cld_1_rot = Matrix.Rotation(prop.cld_1_rotation, 4, 'Z')

    cld_1_transform = cld_1_rot @ cld_1_trans
    cld_1_transform.invert()
    
    shader.uniform_float("cld_1_transform", cld_1_transform)
    # ---------------------------------------------------------------------------- #

    shader.uniform_float("cld_ap_intsty", 500000*prop.cld_ap_intsty)
    
    bgl.glActiveTexture(bgl.GL_TEXTURE0);
    bgl.glBindTexture(bgl.GL_TEXTURE_3D, ogl_noise_textures[0]);
    bgl.glUniform1i(bgl.glGetUniformLocation(shader.program, "noise_tex_3D_32"), 0);

    bgl.glActiveTexture(bgl.GL_TEXTURE1);
    bgl.glBindTexture(bgl.GL_TEXTURE_3D, ogl_noise_textures[1]);
    bgl.glUniform1i(bgl.glGetUniformLocation(shader.program, "noise_tex_3D_128"), 1);

    bgl.glActiveTexture(bgl.GL_TEXTURE2);
    bgl.glBindTexture(bgl.GL_TEXTURE_2D, ogl_noise_textures[2]);
    bgl.glUniform1i(bgl.glGetUniformLocation(shader.program, "noise_tex_2D_1024"), 2);
    
    bgl.glActiveTexture(bgl.GL_TEXTURE3);
    bgl.glBindTexture(bgl.GL_TEXTURE_2D, ogl_noise_textures[3]);
    bgl.glUniform1i(bgl.glGetUniformLocation(shader.program, "blue_noise"), 3);
    
    #bgl.glActiveTexture(bgl.GL_TEXTURE4);
    #bgl.glBindTexture(bgl.GL_TEXTURE_2D, ogl_noise_textures[4]);
    #shader.uniform_int("noise_coverage_map", 4);

    bgl.glActiveTexture(bgl.GL_TEXTURE4);
    bgl.glBindTexture(bgl.GL_TEXTURE_2D, ogl_moon_textures[0]);
    bgl.glUniform1i(bgl.glGetUniformLocation(shader.program, "moon_albedo_tex"), 4);

    bgl.glActiveTexture(bgl.GL_TEXTURE5);
    bgl.glBindTexture(bgl.GL_TEXTURE_2D, ogl_moon_textures[1]);
    bgl.glUniform1i(bgl.glGetUniformLocation(shader.program, "moon_normal_tex"), 5);
    
    '''
    shader.uniform_sampler("noise_tex_3D_32", noise_textures["tex_32_3D"])
    shader.uniform_sampler("noise_tex_3D_128", noise_textures["tex_128_3D"])
    shader.uniform_sampler("noise_tex_2D_1024", noise_textures["tex_1024_2D"])
    shader.uniform_sampler("blue_noise", noise_textures["blue_2D"])
    '''

def init_world_node_tree(self):
    scn = bpy.context.scene
    prop = bpy.context.scene.my_tool
    # Get the environment node tree of the current scene
    node_tree = scn.world.node_tree
    tree_nodes = node_tree.nodes

    # Clear all nodes
    tree_nodes.clear()

    # Add Background node
    node_background = tree_nodes.new(type='ShaderNodeBackground')
    node_background.inputs["Strength"].default_value = prop.env_img_strength

    # Add Environment Texture node
    node_environment = tree_nodes.new('ShaderNodeTexEnvironment')
    # Load and assign the image to the node property
    node_environment.image = bpy.data.images[img_name]
    node_environment.interpolation = 'Smart'
    node_environment.location = -300,0

    # Add Output node
    node_output = tree_nodes.new(type='ShaderNodeOutputWorld')   
    node_output.location = 200,0

    # Link all nodes
    links = node_tree.links
    link = links.new(node_environment.outputs["Color"], node_background.inputs["Color"])
    link = links.new(node_background.outputs["Background"], node_output.inputs["Surface"])

def draw_sky_irradiance_map(self, context, fbo_0, fbo_1, viewport):
    prop = bpy.context.scene.my_tool
    
    with fbo_0.bind():
        gpu.state.depth_test_set('NONE')

        _shader = shader["sky"]

        _shader.bind()
        _shader.uniform_float("img_size", (irradiance_width, irradiance_height))
        #_shader.uniform_float("light_intsty", prop.sun_intsty * 50)#* 561.0)

        atmo_uniforms(_shader)

        _shader.uniform_int("enable_moon", prop.moon_show_viewport if viewport else prop.moon_show_render)
        _shader.uniform_int("enable_sun", prop.sun_show_viewport if viewport else prop.sun_show_render)

        #moon_lux = #1.0 if viewport else 0.1
        #sun_lux = #10.0 if viewport else 561.0

        _shader.uniform_float("sun.dir", compute_dir(prop.sun_elevation, prop.sun_rotation))
        #_shader.uniform_float("sun.intsty", 100000)
        _shader.uniform_int("enable_sun_as_light", prop.sun_enable_light)

        _shader.uniform_float("moon.dir", compute_dir(prop.moon_elevation, prop.moon_rotation))
        #_shader.uniform_float("moon.intsty", 0.26)
        _shader.uniform_int("enable_moon_as_light", prop.moon_enable_light)
        
        batch["sky"].draw(_shader)
    
    with fbo_1.bind():
        gpu.state.depth_test_set('NONE')
        _shader = shader["sky_irra"]
        _shader.bind()
        _shader.uniform_float("img_size", (irradiance_width, irradiance_height))

        bgl.glActiveTexture(bgl.GL_TEXTURE0)
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, fbo_0.color_texture)
        bgl.glUniform1i(bgl.glGetUniformLocation(_shader.program, "env_tex"), 0)

        batch["sky_irra"].draw(_shader)
    
def look_at(eye, target, up):

    mz = mathutils.Vector((eye[0]-target[0], eye[1]-target[1], eye[2]-target[2])) # inverse line of sight
    mz.normalize()
    
    mx = up.cross(mz)
    mx.normalize()

    my = mz.cross(mx)
    my.normalize()

    tx =  mx.dot(eye)
    ty =  my.dot(eye)
    tz =  mz.dot(eye)

    return mathutils.Matrix(((mx[0], my[0], mz[0], 0), (mx[1], my[1], mz[1], 0), (mx[2], my[2], mz[2], 0), (tx, ty, tz, 1)))

def pre_draw_viewport(self, context):
    prop = bpy.context.scene.my_tool  
    
    scr_width = context.region.width
    scr_height = context.region.height

    tex_width = int(float(scr_width)/float(prop.viewport_pixel_size))       
    tex_height = int(float(scr_height)/float(prop.viewport_pixel_size))

    with self._offscreen_viewport.bind():
        gpu.state.depth_test_set('NONE')
        _shader = shader["viewport"]

        _shader.bind()

        proj_mat = bpy.context.region_data.perspective_matrix
        
        inv_vp_mat = proj_mat
        inv_vp_mat = inv_vp_mat.inverted()
        
        _shader.uniform_float("img_size", (tex_width, tex_height))
        
        _shader.uniform_float("inv_vp_mat", inv_vp_mat)      
        _shader.uniform_int("cld_max_steps", prop.viewport_max_steps)
        _shader.uniform_int("cld_max_light_steps", prop.viewport_max_light_steps)

        _shader.uniform_float("altitude", prop.prop_sky_altitude)

        #_shader.uniform_float("sun_intsty", context.scene.my_tool.sun_intsty * 10.0)

        _shader.uniform_int("enable_atm", prop.atm_show_viewport)
        _shader.uniform_int("enable_cld", prop.cld_show_viewport)
        _shader.uniform_int("enable_moon", prop.moon_show_viewport)
        _shader.uniform_int("enable_sun", prop.sun_show_viewport)

        atmo_uniforms(_shader)
        cloud_uniforms(_shader)
        moon_uniforms(_shader, 1.0)
        sun_uniforms(_shader, 6005481420.298142)

        bgl.glActiveTexture(bgl.GL_TEXTURE6);
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, self._offscreen_fbo_sky_1.color_texture);
        bgl.glUniform1i(bgl.glGetUniformLocation(_shader.program, "irra_tex"), 6);
        
        batch["viewport"].draw(_shader)

def post_draw_viewport(self, context):
    
    scene = context.scene
    prop = scene.my_tool

    r3d = context.area.spaces.active.region_3d

    if r3d.view_perspective == 'CAMERA':
        obj_camera = bpy.context.scene.camera
        clip_end = obj_camera.data.clip_end
    else:
        clip_end = context.area.spaces.active.clip_end
    
    trans = Matrix.Translation(r3d.view_matrix.inverted().translation)
    scale = Matrix.Scale((clip_end*0.9)*.5, 4)
    
    obj_mat = trans @ scale

    proj_view_mat = bpy.context.region_data.perspective_matrix

    monitor_width = ctypes.windll.user32.GetSystemMetrics(0)
    monitor_height = ctypes.windll.user32.GetSystemMetrics(1)    
    
    scr_width = context.region.width
    scr_height = context.region.height

    tex_width = int(float(scr_width)/float(prop.viewport_pixel_size))       
    tex_height = int(float(scr_height)/float(prop.viewport_pixel_size))

    gpu.state.depth_test_set('LESS')

    _shader = shader["screen"]
    _shader.bind()

    _shader.uniform_float("projection", proj_view_mat @ obj_mat)

    bgl.glActiveTexture(bgl.GL_TEXTURE0)
    bgl.glBindTexture(bgl.GL_TEXTURE_2D, self._offscreen_viewport.color_texture)
    bgl.glUniform1i(bgl.glGetUniformLocation(_shader.program, "tex"), 0)

    _shader.uniform_float("monitor_size", (monitor_width, monitor_height))
    _shader.uniform_float("scr_size", (scr_width, scr_height))
    _shader.uniform_float("tex_size", (tex_width, tex_height))
    _shader.uniform_float("env_img_strength", prop.env_img_strength)
    _shader.uniform_float("gamma", scene.view_settings.gamma)

    batch["screen"].draw(_shader)

    gpu.state.depth_test_set('NONE')

def draw_to_hrdi(self, context, offscreen, max_steps, max_light_steps, width, height, tile_x, tile_y):
    prop = bpy.context.scene.my_tool

    #bpy.data.images[img_name].gl_load()

    with offscreen.bind():
        gpu.state.depth_test_set('NONE')

        _shader = shader["hrdi"]

        _shader.bind()

        _shader.uniform_float("img_size", (width, height))
        
        _shader.uniform_int("tile_x", tile_x)
        _shader.uniform_int("tile_y", tile_y)

        _shader.uniform_int("cld_max_steps", max_steps)
        _shader.uniform_int("cld_max_light_steps", max_light_steps)

        #_shader.uniform_float("sun_intsty", mytool.sun_intsty * 1000000.0)
        
        _shader.uniform_float("altitude", prop.prop_sky_altitude)

        _shader.uniform_int("enable_atm", prop.atm_show_render)
        _shader.uniform_int("enable_cld", prop.cld_show_render)
        _shader.uniform_int("enable_moon", prop.moon_show_render)
        _shader.uniform_int("enable_sun", prop.sun_show_render)

        atmo_uniforms(_shader)
        cloud_uniforms(_shader)
        moon_uniforms(_shader, 0.1)
        sun_uniforms(_shader, 6005481420.298142)

        bgl.glActiveTexture(bgl.GL_TEXTURE6);
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, self._offscreen_fbo_sky_1.color_texture);
        bgl.glUniform1i(bgl.glGetUniformLocation(_shader.program, "irra_tex"), 6);

        #bgl.glActiveTexture(bgl.GL_TEXTURE7);
        #bgl.glBindTexture(bgl.GL_TEXTURE_2D, bpy.data.images[img_name].bindcode);
        #bgl.glUniform1i(bgl.glGetUniformLocation(_shader.program, "test_img"), 7);

        batch["hrdi"].draw(_shader)

    #bpy.data.images[img_name].gl_free()

    #buffer = offscreen.texture_color.read()
    #buffer.dimensions = width * height * 4
    #bpy.data.images[img_name].pixels.foreach_set(buffer) 

    bpy.data.images[img_name].update()

def draw_env_img(exr_image, irra_tex, max_steps, max_light_steps):
    prop = bpy.context.scene.my_tool

    offscreen = exr_image.get_offscreen()
    
    tile_pos = exr_image.get_tile_pos()
    tile_size = exr_image.get_tile_size()
    img_size = exr_image.get_size()
    offscreen = exr_image.get_offscreen()

    with offscreen.bind():

        gpu.state.viewport_set(tile_pos[0]*tile_size, tile_pos[1]*tile_size, tile_size, tile_size)
        gpu.state.depth_test_set('NONE')

        _shader = shader["hrdi"]

        _shader.bind()
        _shader.uniform_float("img_size", img_size)

        _shader.uniform_int("cld_max_steps", max_steps)
        _shader.uniform_int("cld_max_light_steps", max_light_steps)

        _shader.uniform_float("altitude", prop.prop_sky_altitude)

        _shader.uniform_int("enable_atm", prop.atm_show_render)
        _shader.uniform_int("enable_cld", prop.cld_show_render)
        _shader.uniform_int("enable_moon", prop.moon_show_render)
        _shader.uniform_int("enable_sun", prop.sun_show_render)

        atmo_uniforms(_shader)
        cloud_uniforms(_shader)
        moon_uniforms(_shader,0)
        sun_uniforms(_shader,0)

        bgl.glActiveTexture(bgl.GL_TEXTURE6);
        bgl.glBindTexture(bgl.GL_TEXTURE_2D, irra_tex);
        bgl.glUniform1i(bgl.glGetUniformLocation(_shader.program, "irra_tex"), 6);

        batch["hrdi"].draw(_shader)

    exr_image.append_tile()

# ---------------------------------------------------------------------------- #
#                                  PROPERTIES                                  #
# ---------------------------------------------------------------------------- #

class Properties(PropertyGroup):

    env_img_strength: FloatProperty(
        name = "env_img_strength",
        description = "A float property",
        default = 1.0,
        min = 0.0,
        update=update_node_tree
        ) 
# ----------------------------- Cloud Properties ----------------------------- #

# ------------------------- Cloud Layer 0 Properties ------------------------- #

    ambient_intsty: FloatProperty(
        name = "ambient_intsty",
        description = "A float property",
        default = 1.0,
        max = 100.0,
        min = 0.0,
        update=update_prop
        )      
        
    cld_horizon_dst: FloatProperty(
        name = "cld_horizon_dst",
        description = "A float property",
        default = 10000.0,
        max = 1000000.0,
        step = 1000,
        min = 0.0,
        update=update_prop
        )      
        
    cld_horizon_h: FloatProperty(
        name = "cld_horizon_h",
        description = "A float property",
        default = 6500.0,
        max = 1000000.0,
        step = 1000,
        min = 0.0,
        update=update_prop
        )  

    cld_top_roundness: FloatProperty(
        name = "cld_top_roundness",
        description = "A float property",
        default = 0.05,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )
    cld_btm_roundness: FloatProperty(
        name = "cld_btm_roundness",
        description = "A float property",
        default = 0.0,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )    
    cld_top_density: FloatProperty(
        name = "cld_top_density",
        description = "A float property",
        default = 1.0,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )    
    cld_btm_density: FloatProperty(
        name = "cld_btm_density",
        description = "A float property",
        default = 0.5,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )

    cld_0_enable: BoolProperty(
        name="",
        description="A bool property",
        default = True,
        update=update_prop
    )
    cld_0_density: FloatProperty(
        name = "Density",
        description = "A float property",
        default = 0.1,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )
    cld_0_size: FloatProperty(
        name = "Size",
        description="Something",
        default=1.0,
        min= 0.0,
        max = 1,
        update=update_prop
        ) 
    cld_0_height: FloatProperty(
        name = "Height",
        description="Something",
        subtype="DISTANCE",
        default=8000,
        min= 7000,
        max = 10000.0,
        update=update_prop
        )     
    cld_0_thickness: FloatProperty(
        name = "Thickness",
        description = "A float property",
        default = 1.15,
        min = 0.01,
        max = 10.0,
        update=update_prop
        )
    cld_0_detail_intsty: FloatProperty(
        name = "Detail Noise Intensity",
        description="Something",
        default=0.02,
        min= -1.0,
        max = 1.0,
        update=update_prop
        ) 
    cld_0_shape_intsty: FloatProperty(
        name = "Shape Noise Intensity",
        description="Something",
        default=-0.55,
        min= -1.0,
        max = 1.0,
        update=update_prop
        ) 
    cld_0_coverage_intsty: FloatProperty(
        name = "Coverage Noise Intensity",
        description="Something",
        default=1.0,
        min= 0.0,
        max = 1.0,
        update=update_prop
        )
    cld_0_rotation: FloatProperty(
        name = "Rotation",
        description = "",
        default = 0.0,
        subtype="ANGLE",
        update=update_prop
    )
    cld_0_coverage_offset: FloatVectorProperty(
        name = "Coverage Noise Offset",
        description="Something",
        subtype='TRANSLATION',
        size = 2,
        step = 100,
        default=(750,0),
        update=update_prop
        )
    cld_0_shape_offset: FloatVectorProperty(
        name = "Shape Noise Offset",
        description="Something",
        subtype='TRANSLATION',
        size = 2,
        default=(0,0),
        update=update_prop
        )
    cld_0_detail_offset: FloatVectorProperty(
        name = "Detail Noise Offset",
        description="Something",
        subtype='TRANSLATION',
        size = 2,
        default=(0,0),
        update=update_prop
        ) 

# ------------------------- Cloud Layer 1 Properties ------------------------- #
    cld_1_enable: BoolProperty(
        name="",
        description="A bool property",
        default = True,
        update=update_prop
    )
    cld_1_density: FloatProperty(
        name = "Density",
        description = "A float property",
        default = 0.25,
        max = 10.0,
        min = 0.0,
        update=update_prop
        )
    cld_1_size: FloatProperty(
        name = "Size",
        description="Something",
        default=0.5,
        min= 0.0,
        max = 1,
        update=update_prop
        ) 
    cld_1_height: FloatProperty(
        name = "Height",
        description="Something",
        subtype="DISTANCE",
        default=2000,
        min= 500.0,
        max = 2000.0,
        update=update_prop
        )     
    cld_1_thickness: FloatProperty(
        name = "Thickness",
        description = "A float property",
        default = 1.3,
        min = 0.01,
        max = 10.0,
        update=update_prop
        )
    cld_1_detail_intsty: FloatProperty(
        name = "Detail Noise Intensity",
        description="Something",
        default=0.1,
        min= -1.0,
        max = 1.0,
        update=update_prop
        ) 
    cld_1_shape_intsty: FloatProperty(
        name = "Shape Noise Intensity",
        description="Something",
        default=0.3,
        min= -1.0,
        max = 1.0,
        update=update_prop
        ) 
    cld_1_coverage_intsty: FloatProperty(
        name = "Coverage Noise Intensity",
        description="Something",
        default=0.55,
        min= 0.0,
        max = 1.0,
        update=update_prop
        )
    cld_1_rotation: FloatProperty(
        name = "Rotation",
        description = "",
        default = 0.0,
        subtype="ANGLE",
        update=update_prop
    )
    cld_1_coverage_offset: FloatVectorProperty(
        name = "Coverage Noise Offset",
        description="Something",
        subtype='TRANSLATION',
        size = 2,
        step = 100,
        default=(0,0),
        update=update_prop
        )
    cld_1_shape_offset: FloatVectorProperty(
        name = "Shape Noise Offset",
        description="Something",
        subtype='TRANSLATION',
        size = 2,
        default=(0,0),
        update=update_prop
        )
    cld_1_detail_offset: FloatVectorProperty(
        name = "Detail Noise Offset",
        description="Something",
        subtype='TRANSLATION',
        size = 2,
        default=(0,0),
        update=update_prop
        ) 

    cld_silver_intsty: FloatProperty(
        name = "Silverline Intensity",
        description="Intensity of the bright outline along the edge of the clouds.",
        default=1.13,
        min= 0.0,
        update=update_prop
        )  
    cld_silver_spread: FloatProperty(
        name = "Silverline Spread",
        description="The spread of the bright outline along the edge of the clouds.",
        default=0.12,
        min= 0.0,
        max = 1.0,
        update=update_prop
        ) 

    cld_ap_intsty: FloatProperty(
        name = "Atmospheric Perspective Intensity",
        description="The effect the atmosphere has on the appearance of the clouds as viewed from a distance.",
        default=0.2,
        update=update_prop,
        min= 0.0,
        max = 100.0
        )
    cld_coverage_map: PointerProperty(
        name="Image", 
        type=bpy.types.Image,
        update=update_cld_coverage_map
        )

    #bpy.types.WindowManager.image = bpy.props.PointerProperty(name='Image', type=bpy.types.Image)
         
# ------------------------------ Sun Properties ------------------------------ #

    sun_show_viewport: BoolProperty(
        name="",
        description="Display Sun in viewport.",
        default = True,
        update=update_prop
        )
        
    sun_show_render: BoolProperty(
        name="",
        description="Display Sun in render.",
        default = True,
        update=update_prop
        )

    sun_enable_light: BoolProperty(
        name="Light Source",
        description="Enable the Sun as a light source.",
        default = True,
        update=update_prop
        )

    sun_silver_intsty: FloatProperty(
        name = "Silverline Intensity",
        description="Intensity of the bright outline along the edge of the clouds.",
        default=0.6,
        min= 0.0,
        update=update_prop
        ) 

    sun_silver_spread: FloatProperty(
        name = "Silverline Spread",
        description="The spread of the bright outline along the edge of the clouds.",
        default=0.3,
        min= 0.0,
        max = 1.0,
        update=update_prop
        ) 

    sun_size: FloatProperty(
        name = "Size",
        description = "Size of Sun.",
        default = 0.545,
        subtype="ANGLE",
        min = 0.0,
        max = 90.0,
        update=update_prop
        )
        
    sun_disk_intsty: FloatProperty(
        name = "Intensity",
        description = "Strength of Sun disk.",
        default = 10.0,
        min = 0.0,
        update=update_prop
        )

    sun_intsty: FloatProperty(
        name = "Intensity",
        description = "Strength of Sun light.",
        default = 10.0,
        min = 0.0,
        update=update_prop
        )
        
    sun_elevation: FloatProperty(
        name = "Elevation",
        description = "Sun Angle from horizon.",
        default = 5.0,
        subtype="ANGLE",
        update=update_prop
        )
        
    sun_rotation: FloatProperty(
        name = "Rotation",
        description = "Rotation of Sun around zenith.",
        default = 0.0,
        subtype="ANGLE",
        update=update_prop
        )

# --------------------------- Atmosphere Properties -------------------------- #
        
    prop_sky_altitude: FloatProperty(
        name = "Altitude",
        description = "A float property",
        default = 2000.0,
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

# ------------------------------ Moon Properties ----------------------------- #

    moon_show_viewport: BoolProperty(
        name="",
        description="Display Moon in viewport.",
        default = True,
        update=update_prop
        )
        
    moon_show_render: BoolProperty(
        name="",
        description="Display Moon in render.",
        default = True,
        update=update_prop
        )

    moon_enable_light: BoolProperty(
        name="Light Source",
        description="Enable the Moon as a light source.",
        default = True,
        update=update_prop
        )

    moon_silver_intsty: FloatProperty(
        name = "Silverline Intensity",
        description="Intensity of the bright outline along the edge of the clouds.",
        default=1.13,
        min= 0.0,
        update=update_prop
        ) 

    moon_silver_spread: FloatProperty(
        name = "Silverline Spread",
        description="The spread of the bright outline along the edge of the clouds.",
        default=0.12,
        min= 0.0,
        max = 1.0,
        update=update_prop
        ) 

    moon_size: FloatProperty(
        name = "Size",
        description = "Size of Moon.",
        default = 0.545,
        subtype="ANGLE",
        min = 0.0,
        max = 90.0,
        update=update_prop
        )
        
    moon_intsty: FloatProperty(
        name = "Intensity",
        description = "Strength of Moon light.",
        default = 1.0,
        min = 0.0,
        update=update_prop
        )    
        
    moon_disk_intsty: FloatProperty(
        name = "Intensity",
        description = "Strength of Moon Disk.",
        default = 1.0,
        min = 0.0,
        update=update_prop
        )

    moon_ambient_intsty: FloatProperty(
        name = "Ambient Intensity",
        description = "Strength of Moon Face light.",
        default = 1.0,
        min = 0.0,
        max = 0.01,
        update=update_prop
        )
        
    moon_elevation: FloatProperty(
        name = "Elevation",
        description = "Moon Angle from horizon.",
        default = 15.0,
        subtype="ANGLE",
        update=update_prop
        )
        
    moon_rotation: FloatProperty(
        name = "Rotation",
        description = "Rotation of Moon around zenith.",
        default = 0.0,
        subtype="ANGLE",
        update=update_prop
        )

    moon_use_sun_dir: BoolProperty(
        name="Use Sun",
        description="Phase is based on direction of the Sun.",
        default = False,
        update=update_prop
        )

    moon_phase_rotation: FloatProperty(
        name = "Phase Rotation",
        description = "A float property",
        default = 15.0,
        subtype="ANGLE",
        update=update_prop
        )    
        
    moon_face_rotation: FloatProperty(
        name = "Face Rotation",
        description = "A float property",
        default = 15.0,
        subtype="ANGLE",
        update=update_prop
        )
        
    moon_phase: FloatProperty(
        name = "Phase",
        description = "A float property",
        default = 0.0,
        subtype="ANGLE",
        update=update_prop
        )

    env_img_size = [
        ('1', "1K", '1024 x 512', '', 1),
        ('2', "2K", '2048 x 1024', '', 2),
        ('4', "4K", '4096 x 2048', '', 4),
        ('8', "8K", '8192 x 4096', '', 8),
        ('16', "16K", '16384 x 8192', '', 16),
        ('24', "24K", '24576 x 12288', '', 24),
    ]

    env_img_render_size: EnumProperty(
        items=env_img_size,
        description="(1024 x 512) * size",
        default="4"
    )

    env_img_viewport_size: EnumProperty(
        items=env_img_size,
        description="(1024 x 512) * size",
        default="1",
        update=update_env_img_size
    )

    render_step_size: FloatProperty(
        name = "Step Size",
        description="Something",
        default=1.0,
        min= 0.0001,
        max = 1000.0
    )

    viewport_step_size: FloatProperty(
        name = "Step Size",
        description="Something",
        default=1.0,
        min= 0.0001,
        max = 1000.0
    )

    render_max_steps: IntProperty(
        name = "Max Steps",
        description="Maximum number of steps before giving up.",
        default=1024,
        min= 2
    )

    render_max_light_steps: IntProperty(
        name = "Max Light Steps",
        description="Maximum number of steps before giving up.",
        default=128,
        min= 2
    ) 

    viewport_max_steps: IntProperty(
        name = "Max Steps",
        description="Maximum number of steps before giving up.",
        default=300,
        min= 2
    )    
    
    viewport_max_light_steps: IntProperty(
        name = "Max Light Steps",
        description="Maximum number of steps before giving up.",
        default=16,
        min= 2
    )

    pixel_size = [
        ('1', "1x", 'Render at full resolution', '', 1),
        ('2', "2x", 'Render at 50%% resolution', '', 2),
        ('4', "4x", 'Render at 25%% resolution', '', 4),
        ('8', "8x", 'Render at 12.5%% resolution', '', 8),
    ]

    viewport_pixel_size: EnumProperty(
        name = "Pixel Size",
        items=pixel_size,
        description="Pixel size for viewport rendering.",
        default="1"
    )

    enable_previewer: BoolProperty(
        name="enable_previewer",
        description="",
        default = True
    )

# ---------------------------------------------------------------------------- #
#                                   OPERATORS                                  #
# ---------------------------------------------------------------------------- #

class STRATUS_OT_render(bpy.types.Operator):
    bl_idname = "stratus.render_hrdi"
    bl_label = "Stratus Render HRDI"

    _offscreen_fbo = None
    _offscreen_fbo_sky_0 = None
    _offscreen_fbo_sky_1 = None
    _exr_img = None

    def invoke(self, context, event):
        mytool = context.scene.my_tool
        size = int(mytool.env_img_render_size)

        #width = 1024 * size
        #height = 512 * size

        #init_hrdi_image(img_name, width, height)

        self._offscreen_fbo_sky_0 = setup_offscreen(irradiance_width, irradiance_height)
        self._offscreen_fbo_sky_1 = setup_offscreen(irradiance_width, irradiance_height)
        #self._offscreen_fbo = setup_offscreen(width, height)

        self._exr_img = EXRImage(img_name)
        self._exr_img.set_size(size)

        #if not self._offscreen_fbo:
        #    self.report({'ERROR'}, "Error initializing offscreen buffer. More details in the console")
        #    return {'CANCELLED'}

        return self.execute(context)

    def execute(self, context):

        mytool = context.scene.my_tool

        size = int(mytool.env_img_render_size)

        width = 1024 * size
        height = 512 * size

        scene = context.scene
        fp = scene.render.filepath

        for frame in range(scene.frame_start, scene.frame_end + 1):
            scene.frame_set(frame)
            scene.render.filepath = fp + str(frame).zfill(4)

            start_time = datetime.now()
            draw_sky_irradiance_map(self, context, self._offscreen_fbo_sky_0, self._offscreen_fbo_sky_1, False)
            #draw_to_hrdi(self, context, self._offscreen_fbo, mytool.render_max_steps, mytool.render_max_light_steps, width, height, 0, 0)
            while(not self._exr_img.completed()):
                draw_env_img(self._exr_img, self._offscreen_fbo_sky_1.color_texture, mytool.render_max_steps, mytool.render_max_light_steps)
            self._exr_img.save()
            self._exr_img.reset()
            end_time = datetime.now()

            bpy.ops.render.render(write_still=True) 

            duration = end_time - start_time
            s = duration.total_seconds()
            print(" STRATUS Time: "+'{:02.0f}:{:05.2f}'.format(s % 3600 // 60, s % 60)+"\n")

        scene.render.filepath = fp

        return {'FINISHED'}

class STRATUS_OT_viewport_editor(bpy.types.Operator):
    bl_idname = "stratus.viewport_editor"
    bl_label = "Stratus Viewport Editor"

    _offscreen_fbo = None
    _fbo = None
    _offscreen_viewport = None
    _offscreen_fbo_sky_0 = None
    _offscreen_fbo_sky_1 = None
    _handle_draw = None
    _is_enabled = False
    _enable_previewer = True

    _node_environment = None

    _exr_img = None

    # manage draw handler
    @staticmethod
    def post_draw_callback(self, context):
        if context.scene.my_tool.enable_previewer: 
            post_draw_viewport(self, context)
        
    @staticmethod   
    def pre_draw_callback(self, context):
        
        #C = bpy.context
        #scn = C.scene

        # Get the environment node tree of the current scene
        #node_tree = scn.world.node_tree
        #tree_nodes = node_tree.nodes

        prop = context.scene.my_tool
        size = float(prop.env_img_viewport_size)

        draw_sky_irradiance_map(self, context, self._offscreen_fbo_sky_0, self._offscreen_fbo_sky_1, False)

        global resize_hrdi
        if resize_hrdi == True:
            self._exr_img.set_size(size)
            resize_hrdi = False

        global reset_hrdi
        if reset_hrdi:
            self._exr_img.reset()
            reset_hrdi = False

        global update_hrdi
        if update_hrdi is True:

            draw_env_img(self._exr_img, self._offscreen_fbo_sky_1.color_texture, prop.viewport_max_steps, prop.viewport_max_light_steps)

            global refresh_viewports
            if self._exr_img.completed():
                update_hrdi = False
                self._exr_img.save()
                self._exr_img.reset()
                refresh_viewports = True
        
        if context.scene.my_tool.enable_previewer:
            pre_draw_viewport(self, context)

    @staticmethod
    def handle_add(self, context):
        STRATUS_OT_viewport_editor._handle_draw = bpy.types.SpaceView3D.draw_handler_add(
                self.post_draw_callback, (self, context),
                'WINDOW', 'POST_VIEW',
                )

        STRATUS_OT_viewport_editor._handle_draw = bpy.types.SpaceView3D.draw_handler_add(
                self.pre_draw_callback, (self, context),
                'WINDOW', 'PRE_VIEW',
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
        node_background.inputs["Strength"].default_value = 0.1

        # Add Environment Texture node
        node_environment = tree_nodes.new('ShaderNodeTexEnvironment')
        # Load and assign the image to the node property
        node_environment.image = bpy.data.images[img_name]
        node_environment.interpolation = 'Smart'
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

        global refresh_viewports
        if refresh_viewports:
            update_viewers(context)
            refresh_viewports = False

        if event.type in {'ESC'}:
            #bpy.types.SpaceView3D.draw_handler_remove(self._handle_3d, 'WINDOW')
            #context.scene.my_tool.enable_previewer = False 
            #self.tag_redraw()
            return {'CANCELLED'}
        else:
            pass

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if STRATUS_OT_viewport_editor._is_enabled:
            self.cancel(context)
            return {'FINISHED'}
        else:
            wm = context.window_manager
            self._timer = wm.event_timer_add(0.016, window=context.window)
            context.window_manager.modal_handler_add(self)

            width = 256
            height = 128

            init_hrdi_image(img_name, width, height)
            STRATUS_OT_viewport_editor.init_world_node_tree(self)

            self._offscreen_fbo = setup_offscreen(width, height)

            tex =  gpu.types.GPUTexture((256,256), layers=0, is_cubemap=False, format='RGBA32F')
            self._fbo = gpu.types.GPUFrameBuffer(depth_slot=None, color_slots=(tex))

            width = ctypes.windll.user32.GetSystemMetrics(0)
            height = ctypes.windll.user32.GetSystemMetrics(1)

            self._offscreen_viewport = gpu.types.GPUOffScreen(width, height, format='RGBA32F')

            image = bpy.data.images[img_name]
            image.scale(width, height)
            col_tex = gpu.texture.from_image(image)
            self._fbo = gpu.types.GPUFrameBuffer(depth_slot=None, color_slots=(col_tex))

            self._exr_img = EXRImage(img_name)

            bgl.glBindTexture(bgl.GL_TEXTURE_2D, self._offscreen_viewport.color_texture)
            bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_NEAREST)
            bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_NEAREST)
            bgl.glBindTexture(bgl.GL_TEXTURE_2D, 0)

            self._offscreen_fbo_sky_0 = setup_offscreen(irradiance_width, irradiance_height)
            self._offscreen_fbo_sky_1 = setup_offscreen(irradiance_width, irradiance_height)
            
            if not self._offscreen_fbo or not self._offscreen_fbo_sky_0 or not self._offscreen_fbo_sky_1:
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
            update_hrdi = True
            #update_viewers(context)
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

        #layout.template_ID(mytool, 'cld_coverage_map', open='image.open')
        col = layout.column()
        col.label(text="Lighting")
        #col.prop(mytool, "cld_silver_intsty")
        #col.prop(mytool, "cld_silver_spread", slider=True)
        col.prop(mytool, "cld_ap_intsty")
        col.prop(mytool, "cld_top_roundness")
        col.prop(mytool, "cld_btm_roundness")
        col.prop(mytool, "cld_top_density")
        col.prop(mytool, "cld_btm_density")
        col.prop(mytool, "ambient_intsty")
        col.prop(mytool, "cld_horizon_dst")
        col.prop(mytool, "cld_horizon_h")

class STRATUS_PT_sub_cloud_layer_0_panel(bpy.types.Panel):
    bl_parent_id = "STRATUS_PT_cloud_panel"
    bl_label = "Cirro Layer"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        self.layout.prop(context.scene.my_tool, "cld_0_enable")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        layout.enabled = mytool.cld_0_enable

        layout.prop(mytool, "cld_0_rotation")

        grid_0 = layout.grid_flow(columns=1, align=True)
        grid_0.label(text="Basic")

        grid_0.prop(mytool, "cld_0_density", slider=True)
        grid_0.prop(mytool, "cld_0_size", slider=True)
        grid_0.prop(mytool, "cld_0_height", slider=True)
        grid_0.prop(mytool, "cld_0_thickness", slider=True)
        
        grid_1 = layout.grid_flow(columns=1, align=True)
        grid_1.label(text="Noise")

        grid_1.prop(mytool, "cld_0_detail_intsty", slider=True)
        grid_1.prop(mytool, "cld_0_shape_intsty", slider=True)
        grid_1.prop(mytool, "cld_0_coverage_intsty", slider=True)
        
class STRATUS_PT_sub_cloud_layer_1_panel(bpy.types.Panel):
    bl_parent_id = "STRATUS_PT_cloud_panel"
    bl_label = "Cumulus Layer"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        self.layout.prop(context.scene.my_tool, "cld_1_enable")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        layout.enabled = mytool.cld_1_enable

        layout.prop(mytool, "cld_1_rotation")

        grid_0 = layout.grid_flow(columns=1, align=True)
        grid_0.label(text="Basic")

        grid_0.prop(mytool, "cld_1_density", slider=True)
        grid_0.prop(mytool, "cld_1_size", slider=True)
        grid_0.prop(mytool, "cld_1_height", slider=True)
        grid_0.prop(mytool, "cld_1_thickness", slider=True)
        
        grid_1 = layout.grid_flow(columns=1, align=True)
        grid_1.label(text="Noise")

        grid_1.prop(mytool, "cld_1_detail_intsty", slider=True)
        grid_1.prop(mytool, "cld_1_shape_intsty", slider=True)
        grid_1.prop(mytool, "cld_1_coverage_intsty", slider=True)

class STRATUS_PT_sub_cloud_layer_0_noise_offsets_panel(bpy.types.Panel):
    bl_parent_id = "STRATUS_PT_sub_cloud_layer_0_panel"
    bl_label = "Noise Offsets"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        layout.enabled = mytool.cld_0_enable

        grid = layout.grid_flow(columns=1, align=True)
        grid.prop(mytool, "cld_0_coverage_offset")
        grid.prop(mytool, "cld_0_shape_offset")
        grid.prop(mytool, "cld_0_detail_offset")

class STRATUS_PT_sub_cloud_layer_1_noise_offsets_panel(bpy.types.Panel):
    bl_parent_id = "STRATUS_PT_sub_cloud_layer_1_panel"
    bl_label = "Noise Offsets"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        layout.enabled = mytool.cld_1_enable

        grid = layout.grid_flow(columns=1, align=True)
        grid.prop(mytool, "cld_1_coverage_offset")
        grid.prop(mytool, "cld_1_shape_offset")
        grid.prop(mytool, "cld_1_detail_offset")

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
        
        layout.prop(mytool, "prop_sky_altitude")
        layout.separator()
        grid = layout.grid_flow(columns=1, align=True)
        grid.prop(mytool, "prop_air", slider=True)
        grid.prop(mytool, "prop_dust", slider=True)
        grid.prop(mytool, "prop_ozone", slider=True)

class STRATUS_PT_moon_panel(bpy.types.Panel):
    bl_label = "Moon"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.my_tool

        icon_vp = 'RESTRICT_VIEW_OFF' if prop.moon_show_viewport else "RESTRICT_VIEW_ON"
        icon_r = 'RESTRICT_RENDER_OFF' if prop.moon_show_render else "RESTRICT_RENDER_ON"

        render_options = layout.row(align=True)
        render_options.label(text="Moon")
        render_options.prop(prop, 'moon_show_viewport', icon=icon_vp)
        render_options.prop(prop, 'moon_show_render', icon=icon_r)
        
        layout.separator()
        layout.prop(prop, "moon_size")

        layout.separator()
        layout.prop(prop, "moon_enable_light")
        grid_0 = layout.grid_flow(columns=1, align=True)
        grid_0.prop(prop, "moon_disk_intsty")
        grid_0.prop(prop, "moon_ambient_intsty", slider=True)
        grid_0.prop(prop, "moon_silver_intsty")
        grid_0.prop(prop, "moon_silver_spread")

        layout.separator()
        grid_1 = layout.grid_flow(columns=1, align=True)
        grid_1.prop(prop, "moon_elevation")
        grid_1.prop(prop, "moon_rotation")
        
        layout.separator()
        layout.prop(prop, "moon_use_sun_dir")

        grid_2 = layout.grid_flow(columns=1, align=True)
        grid_2.prop(prop, "moon_phase")
        grid_2.prop(prop, "moon_phase_rotation")
        grid_2.prop(prop, "moon_face_rotation")

        #grid_0.enabled = prop.moon_enable_light
        #grid_2.enabled = not prop.moon_use_sun_dir

class STRATUS_PT_sun_panel(bpy.types.Panel):
    bl_label = "Sun"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.my_tool

        icon_vp = 'RESTRICT_VIEW_OFF' if prop.sun_show_viewport else "RESTRICT_VIEW_ON"
        icon_r = 'RESTRICT_RENDER_OFF' if prop.sun_show_render else "RESTRICT_RENDER_ON"

        render_options = layout.row(align=True)
        render_options.label(text="Sun")
        render_options.prop(prop, 'sun_show_viewport', icon=icon_vp)
        render_options.prop(prop, 'sun_show_render', icon=icon_r)
        
        layout.separator()
        layout.prop(prop, "sun_size")

        layout.separator()
        layout.prop(prop, "sun_enable_light")

        grid_0 = layout.grid_flow(columns=1, align=True)
        grid_0.prop(prop, "sun_disk_intsty")
        grid_0.prop(prop, "sun_silver_intsty")
        grid_0.prop(prop, "sun_silver_spread")

        layout.separator()
        grid_1 = layout.grid_flow(columns=1, align=True)
        grid_1.prop(prop, "sun_elevation")
        grid_1.prop(prop, "sun_rotation")

        grid_0.enabled = prop.sun_enable_light

class STRATUS_PT_render_panel(bpy.types.Panel):
    bl_label = "Render Settings"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        layout.operator(STRATUS_OT_render.bl_idname, text="Render", icon="CONSOLE")
        layout.prop(mytool, "enable_previewer")
        layout.prop(mytool, "env_img_strength")

class STRATUS_PT_sub_render_panel(bpy.types.Panel):
    bl_parent_id = "STRATUS_PT_render_panel"
    bl_label = "Render Settings"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        col = layout.column()
        col.label(text="Environment Texture Size")
        col.prop(mytool, "env_img_render_size", text="")

        layout.prop(mytool, "render_max_steps")
        layout.prop(mytool, "render_max_light_steps")

class STRATUS_PT_sub_viewport_panel(bpy.types.Panel):
    bl_parent_id = "STRATUS_PT_render_panel"
    bl_label = "Viewport Settings"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        layout.prop(mytool, "viewport_pixel_size")

        col = layout.column()
        col.label(text="Environment Texture Size")
        col.prop(mytool, "env_img_viewport_size", text="")

        layout.prop(mytool, "viewport_max_steps")
        layout.prop(mytool, "viewport_max_light_steps")

classes = (
    Properties, 
    STRATUS_OT_render, 
    STRATUS_OT_viewport_editor, 
    STRATUS_OT_prop_observer, 
    STRATUS_PT_cloud_panel,
    STRATUS_PT_sub_cloud_layer_0_panel,
    STRATUS_PT_sub_cloud_layer_1_panel,
    STRATUS_PT_sub_cloud_layer_0_noise_offsets_panel,
    STRATUS_PT_sub_cloud_layer_1_noise_offsets_panel,
    STRATUS_PT_atmo_panel,
    STRATUS_PT_sun_panel,
    STRATUS_PT_moon_panel,
    STRATUS_PT_render_panel, 
    STRATUS_PT_sub_viewport_panel, 
    STRATUS_PT_sub_render_panel)

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

    init_textures()
    init_shaders()