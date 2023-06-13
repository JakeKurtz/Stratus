/* ------------------------------------------------------------------------- *
*
*    Copyright (C) 2023 Jake Kurtz
*
*    This program is free software: you can redistribute it and/or modify
*    it under the terms of the GNU General Public License as published by
*    the Free Software Foundation, either version 3 of the License, or
*    (at your option) any later version.
*
*    This program is distributed in the hope that it will be useful,
*    but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
*    GNU General Public License for more details.
*
*    You should have received a copy of the GNU General Public License
*    along with this program. If not, see <https://www.gnu.org/licenses/>.
*
* ------------------------------------------------------------------------- */

/* -------------------------------- Textures -------------------------------- */

uniform sampler3D noise_tex_3D_64;
uniform sampler3D noise_tex_3D_128;
uniform sampler2D noise_tex_2D_2048;
uniform sampler2D blue_noise;
uniform sampler2D moon_albedo_tex;
uniform sampler2D moon_normal_tex;
uniform sampler2D irra_tex;
/* -------------------------------------------------------------------------- */
/*                                   UTILITY                                  */
/* -------------------------------------------------------------------------- */

uniform vec2 img_size;

#define M_PI        3.1415926535897932
#define M_3_16PI    0.0596831036594607 // 3 / (16pi)
#define M_1_PI      0.3183098861837906 // 1 / pi
#define M_1_2PI     0.1591549430918953 // 1 / (2pi)
#define M_1_4PI     0.0795774715459476 // 1 / (4pi)
#define M_PI_180    0.0174532925199432 // pi / 180
#define M_180_PI    57.295779513082320 // 180 / pi
#define M_2PI       6.2831853071795864 // 2pi

struct Ray
{
    vec3 pos;
    vec3 dir;
};

struct Light
{
    vec3 dir;
    float intsty;
    float silver_intsty;
    float silver_spread;
};

float saturate(float x)
{
    return clamp(x, 0.0, 1.0);
}

float remap(float v, float l1, float h1, float l2, float h2)
{
    return l2 + (v - l1) * (h2 - l2) / (h1 - l1);
}

/* Using big numbers causes weird issues with normal mix for some reason.*/
vec3 _mix(vec3 a, vec3 b, float t) {
    return saturate(1.0 - t) * a + saturate(t) * b;
}

vec4 _mix(vec4 a, vec4 b, float t) {
    return saturate(1.0 - t) * a + saturate(t) * b;
}

vec4 tex_sample(sampler2D tex, vec2 uv)
{
    return texture(tex, mod(uv, vec2(1.0)));
}

vec4 bicubic_sample(sampler2D tex, vec2 uv, vec2 size) 
{
    vec2 tex_size = size;
    vec2 inv_tex_size = 1.0 / tex_size;

    vec2 tc = uv * tex_size - 0.5;
    vec2 f = fract(tc);
    tc -= f;
 
    // we'll need the second and third powers
    // of f to compute our filter weights
    vec2 f2 = f * f;
    vec2 f3 = f2 * f;
 
    //compute the filter weights
    vec2 w0 = f2 - 0.5 * (f3 + f);
    vec2 w1 = 1.5 * f3 - 2.5 * f2 + 1.0;
    vec2 w3 = 0.5 * (f3 - f2);
    vec2 w2 = 1.0 - w0 - w1 - w3;

    vec2 s0 = w0 + w1;
    vec2 s1 = w2 + w3;
 
    vec2 f0 = w1 / (w0 + w1);
    vec2 f1 = w3 / (w2 + w3);
 
    vec2 t0 = tc - 1.0 + f0;
    vec2 t1 = tc + 1.0 + f1;

    t0 *= inv_tex_size;
    t1 *= inv_tex_size;

    return
        (texture( tex, vec2( t0.x, t0.y ) ) * s0.x
      +  texture( tex, vec2( t1.x, t0.y ) ) * s1.x) * s0.y
      + (texture( tex, vec2( t0.x, t1.y ) ) * s0.x
      +  texture( tex, vec2( t1.x, t1.y ) ) * s1.x) * s1.y;
}

vec4 bicubic_sample(sampler3D tex, vec3 uvw, vec3 size) 
{
    vec3 tex_size = size;
    vec3 inv_tex_size = 1.0 / tex_size;

    vec3 tc = mod(uvw, vec3(1.0)) * tex_size - 0.5;
    vec3 f = fract(tc);
    tc -= f;
 
    // we'll need the second and third powers
    // of f to compute our filter weights
    vec3 f2 = f * f;
    vec3 f3 = f2 * f;
 
    //compute the filter weights
    vec3 w0 = f2 - 0.5 * (f3 + f);
    vec3 w1 = 1.5 * f3 - 2.5 * f2 + 1.0;
    vec3 w3 = 0.5 * (f3 - f2);
    vec3 w2 = 1.0 - w0 - w1 - w3;

    vec3 s0 = w0 + w1;
    vec3 s1 = w2 + w3;
 
    vec3 f0 = w1 / (w0 + w1);
    vec3 f1 = w3 / (w2 + w3);
 
    vec3 t0 = tc - 1.0 + f0;
    vec3 t1 = tc + 1.0 + f1;

    t0 *= inv_tex_size;
    t1 *= inv_tex_size;

    return
        texture( tex, vec3( t0.x, t0.y, t0.z ) ) * s0.x * s0.y * s0.z
      + texture( tex, vec3( t1.x, t0.y, t0.z ) ) * s1.x * s0.y * s0.z
      + texture( tex, vec3( t0.x, t1.y, t0.z ) ) * s0.x * s1.y * s0.z
      + texture( tex, vec3( t1.x, t1.y, t0.z ) ) * s1.x * s1.y * s0.z
      + texture( tex, vec3( t0.x, t0.y, t1.z ) ) * s0.x * s0.y * s1.z
      + texture( tex, vec3( t1.x, t0.y, t1.z ) ) * s1.x * s0.y * s1.z
      + texture( tex, vec3( t0.x, t1.y, t1.z ) ) * s0.x * s1.y * s1.z
      + texture( tex, vec3( t1.x, t1.y, t1.z ) ) * s1.x * s1.y * s1.z;
}

float reduce_add(vec3 f)
{
  return f.x + f.y + f.z;
}

vec3 sample_spherical_direction(vec2 uv)
{
    float phi = M_2PI * (uv.x - 0.5);
    float theta = M_PI * uv.y;

    vec3 n;
    n.x = cos(phi) * sin(theta);
    n.y = -sin(phi) * sin(theta);
    n.z = -cos(theta);

    return n;
}

vec2 sample_spherical_map(vec3 d)
{
    vec2 uv = vec2(0.5 - atan(d.z, d.x) * M_1_2PI, 0.5 + asin(d.y) * M_1_PI);
    return uv;
}

vec2 sample_spherical_map2(const vec3 d)
{
    vec2 uv = vec2(0.5 - atan(d.y, d.x) * M_1_2PI, 0.5 + asin(d.z) * M_1_PI);
    return uv;
}

vec3 orthogonal(vec3 v)
{
    return abs(v.x) > abs(v.z) ? vec3(-v.y, v.x, 0.0) : vec3(0.0, -v.z, v.y);
}

vec3 tangent(vec3 N) 
{
  vec3 T, B;
  if(N.x == .0 && N.z == .0) T = vec3(0.,0.,.1);
  if(N.z == .0) T = vec3(0.,0.,-1.);
  else 
  {
    float l = sqrt(N.x*N.x+N.z*N.z);
    T.x = N.z/l;
    T.y = .0;
    T.z = -N.x/l;
  }
  return T;
}

/* ------------------------------ SDF Functions ----------------------------- */

float sdf_sphere( vec3 p, float s ) 
{
  return length(p)-s;
}

float sdf_op_sub(float d1, float d2) 
{ 
    return max(-d1,d2); 
}

float sdf_op_smooth_sub( float d1, float d2, float k ) 
{
    float h = clamp( 0.5 - 0.5*(d2+d1)/k, 0.0, 1.0 );
    return mix( d2, -d1, h ) + k*h*(1.0-h); 
}

/* ------------------------- Intersection Functions ------------------------- */

bool sphere_intersect(Ray ray, vec3 center, float radius, out float t0, out float t1)
{
    precise vec3 l = (ray.pos - center);
    precise float b = dot(ray.dir, l);
    precise vec3 qc = l - b*ray.dir;
    precise float h = radius*radius - dot(qc,qc);

    if (h < 0.0) {
        t0 = -1.0;
        t1 = -1.0;
        return false;
    }

    h = sqrt(h);

    t0 = -b-h;
    t1 = -b+h;

    bool behind = (t0 < 0.0 && t1 < 0.0);

    return !behind;
}

/* ---------------------------------- Hash ---------------------------------- */

#define UI0 1597334673U
#define UI1 3812015801U
#define UI2 uvec2(UI0, UI1)
#define UI3 uvec3(UI0, UI1, 2798796415U)
#define UIF (1.0 / float(0xffffffffU))

float hash11(float n) 
{ 
    return fract(sin(n)*43758.5453); 
}

vec2 hash22(vec2 p) 
{ 
    p = vec2( dot(p,vec2(127.1,311.7)), dot(p,vec2(269.5,183.3)) ); 
    return -1. + 2. * fract(sin(p)*43758.5453); 
}

float hash12(vec2 p)
{
	vec3 p3  = fract(vec3(p.xyx) * .1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

vec3 hash33(vec3 p)
{
    uvec3 q = uvec3(ivec3(p)) * UI3;
    q = (q.x ^ q.y ^ q.z)*UI3;
    return vec3(q) * UIF;
}

/* ---------------------------------- Noise --------------------------------- */

vec4 worley(vec3 uv)
{    
    vec3 id = floor(uv);
    vec3 p = fract(uv);
    vec4 v = vec4(10000.0, 0.0, 0.0, 0.0);

    for (float x = -1.; x <= 1.; ++x)
    {
        for(float y = -1.; y <= 1.; ++y)
        {
            for(float z = -1.; z <= 1.; ++z)
            {
              vec3 offset = vec3(x, y, z);
              vec3 h = hash33((id + offset));
              vec3 d = p - (h + offset);

              float s = smoothstep(-1.0, 1.0, (v.x-length(d))/0.3);
              v.yzw = mix(v.yzw, h, s);
              v.x = min(v.x, length(d));
            }
        }
    }
    return v;
}

float gradientNoise(vec3 x, float freq)
{
    // grid
    vec3 p = floor(x);
    vec3 w = fract(x);
    
    // quintic interpolant
    vec3 u = w * w * w * (w * (w * 6. - 15.) + 10.);
    
    // gradients
    vec3 ga = hash33(mod(p + vec3(0., 0., 0.), freq));
    vec3 gb = hash33(mod(p + vec3(1., 0., 0.), freq));
    vec3 gc = hash33(mod(p + vec3(0., 1., 0.), freq));
    vec3 gd = hash33(mod(p + vec3(1., 1., 0.), freq));
    vec3 ge = hash33(mod(p + vec3(0., 0., 1.), freq));
    vec3 gf = hash33(mod(p + vec3(1., 0., 1.), freq));
    vec3 gg = hash33(mod(p + vec3(0., 1., 1.), freq));
    vec3 gh = hash33(mod(p + vec3(1., 1., 1.), freq));
    
    // projections
    float va = dot(ga, w - vec3(0., 0., 0.));
    float vb = dot(gb, w - vec3(1., 0., 0.));
    float vc = dot(gc, w - vec3(0., 1., 0.));
    float vd = dot(gd, w - vec3(1., 1., 0.));
    float ve = dot(ge, w - vec3(0., 0., 1.));
    float vf = dot(gf, w - vec3(1., 0., 1.));
    float vg = dot(gg, w - vec3(0., 1., 1.));
    float vh = dot(gh, w - vec3(1., 1., 1.));
	
    // interpolation
    return va + 
           u.x * (vb - va) + 
           u.y * (vc - va) + 
           u.z * (ve - va) + 
           u.x * u.y * (va - vb - vc + vd) + 
           u.y * u.z * (va - vc - ve + vg) + 
           u.z * u.x * (va - vb - ve + vf) + 
           u.x * u.y * u.z * (-va + vb + vc - vd + ve - vf - vg + vh);
}

float gradientNoise(vec2 x, float freq)
{
    // grid
    vec2 p = floor(x);
    vec2 w = fract(x);
    
    vec2 u = w*w*(3.0-2.0*w);

    // gradients
    vec2 ga = hash22(mod(p + vec2(0., 0.), freq));
    vec2 gb = hash22(mod(p + vec2(1., 0.), freq));
    vec2 gc = hash22(mod(p + vec2(0., 1.), freq));
    vec2 gd = hash22(mod(p + vec2(1., 1.), freq));

    // projections
    float va = dot(ga, w - vec2(0., 0.));
    float vb = dot(gb, w - vec2(1., 0.));
    float vc = dot(gc, w - vec2(0., 1.));
    float vd = dot(gd, w - vec2(1., 1.));
	
    // interpolation
    
    float a = mix( va, vb, u.x);
    float b = mix( vc, vd, u.x);
    return mix( a, b, u.y);
    
    return va + 
           u.x * (vb - va) + 
           u.y * (vc - va) + 
           u.x * u.y * (va - vb - vc + vd);
}

float perlinfbm(vec3 p, float freq, int octaves)
{
    float G = exp2(-.85);
    float amp = 1.;
    float noise = 0.;
    for (int i = 0; i < octaves; ++i)
    {
        noise += amp * gradientNoise(p.xy * freq, freq);
        freq *= 2.;
        amp *= G;
    }
    
    return noise;
}
/* ------------------------------- Atmosphere ------------------------------- */

uniform bool enable_atm;
uniform bool enable_moon;
uniform bool enable_sun;

uniform bool enable_moon_as_light;
uniform bool enable_sun_as_light;

uniform Light sun;
uniform Light moon;

uniform float altitude;

uniform float rayleigh_density;
uniform float mie_density;
uniform float ozone_density;

const float earth_radius = 6360e3;
const float atmosphere_radius = 6420e3;
const float mie_coeff = 21e-6;

const float rayleigh_scale_height = 8.0e3;
const float mie_scale_height = 1.2e3;

const float atmo_camera_offset = 1000.0;

const float mie_G = 0.75;

const int num_wavelengths = 21;          
const int min_wavelength = 380;
const int max_wavelength = 780;

const float step_lambda = (max_wavelength - min_wavelength) / (num_wavelengths - 1);

// Sun irradiance on top of the atmosphere (W*m^-2*nm^-1)
uniform float irradiance[21] = float[] (
    1.45756829855592995315f, 1.56596305559738380175f, 1.65148449067670455293f,
    1.71496242737209314555f, 1.75797983805020541226f, 1.78256407885924539336f,
    1.79095108475838560302f, 1.78541550133410664714f, 1.76815554864306845317f,
    1.74122069647250410362f, 1.70647127164943679389f, 1.66556087452739887134f,
    1.61993437242451854274f, 1.57083597368892080581f, 1.51932335059305478886f,
    1.46628494965214395407f, 1.41245852740172450623f, 1.35844961970384092709f,
    1.30474913844739281998f, 1.25174963272610817455f, 1.19975998755420620867f);

// Rayleigh scattering coefficient (m^-1) 
uniform float rayleigh_coeff[21] = float[] (
    0.00005424820087636473f, 0.00004418549866505454f, 0.00003635151910165377f,
    0.00003017929012024763f, 0.00002526320226989157f, 0.00002130859310621843f,
    0.00001809838025320633f, 0.00001547057129129042f, 0.00001330284977336850f,
    0.00001150184784075764f, 0.00000999557429990163f, 0.00000872799973630707f,
    0.00000765513700977967f, 0.00000674217203751443f, 0.00000596134125832052f,
    0.00000529034598065810f, 0.00000471115687557433f, 0.00000420910481110487f,
    0.00000377218381260133f, 0.00000339051255477280f, 0.00000305591531679811f);

// Ozone absorption coefficient (m^-1) 
uniform float ozone_coeff[21] = float[] (
    0.00000000325126849861f, 0.00000000585395365047f, 0.00000001977191155085f,
    0.00000007309568762914f, 0.00000020084561514287f, 0.00000040383958096161f,
    0.00000063551335912363f, 0.00000096707041180970f, 0.00000154797400424410f,
    0.00000209038647223331f, 0.00000246128056164565f, 0.00000273551299461512f,
    0.00000215125863128643f, 0.00000159051840791988f, 0.00000112356197979857f,
    0.00000073527551487574f, 0.00000046450130357806f, 0.00000033096079921048f,
    0.00000022512612292678f, 0.00000014879129266490f, 0.00000016828623364192f);

// CIE XYZ color matching functions
uniform vec3 cmf_xyz[21] = vec3[](
        vec3(0.00136800000f, 0.00003900000f, 0.00645000100f),
        vec3(0.01431000000f, 0.00039600000f, 0.06785001000f),
        vec3(0.13438000000f, 0.00400000000f, 0.64560000000f),
        vec3(0.34828000000f, 0.02300000000f, 1.74706000000f),
        vec3(0.29080000000f, 0.06000000000f, 1.66920000000f),
        vec3(0.09564000000f, 0.13902000000f, 0.81295010000f),
        vec3(0.00490000000f, 0.32300000000f, 0.27200000000f),
        vec3(0.06327000000f, 0.71000000000f, 0.07824999000f),
        vec3(0.29040000000f, 0.95400000000f, 0.02030000000f),
        vec3(0.59450000000f, 0.99500000000f, 0.00390000000f),
        vec3(0.91630000000f, 0.87000000000f, 0.00165000100f),
        vec3(1.06220000000f, 0.63100000000f, 0.00080000000f),
        vec3(0.85444990000f, 0.38100000000f, 0.00019000000f),
        vec3(0.44790000000f, 0.17500000000f, 0.00002000000f),
        vec3(0.16490000000f, 0.06100000000f, 0.00000000000f),
        vec3(0.04677000000f, 0.01700000000f, 0.00000000000f),
        vec3(0.01135916000f, 0.00410200000f, 0.00000000000f),
        vec3(0.00289932700f, 0.00104700000f, 0.00000000000f),
        vec3(0.00069007860f, 0.00024920000f, 0.00000000000f),
        vec3(0.00016615050f, 0.00006000000f, 0.00000000000f),
        vec3(0.00004150994f, 0.00001499000f, 0.00000000000f));

const int quadrature_steps = 8;

uniform float quadrature_nodes[8] = float[8] (
    0.006811185292,
    0.03614807107,
    0.09004346519,
    0.1706680068,
    0.2818362161,
    0.4303406404,
    0.6296271457,
    0.9145252695);

uniform float quadrature_weights[8] = float[8] (
    0.01750893642,
    0.04135477391,
    0.06678839063,
    0.09507698807,
    0.1283416365,
    0.1707430204,
    0.2327233347,
    0.3562490486);

const mat3 xyz_to_rgb = mat3(
     3.2404542, -0.9692660,  0.0556434,
    -1.5371385,  1.8760108, -0.2040259,
    -0.4985314,  0.0415560,  1.0572252
);
uniform float sun_half_angular;
uniform float moon_half_angular;

uniform vec3 moon_phase_dir;
uniform float moon_ambient_intsty;

uniform mat4 moon_rot_mat;
uniform mat4 moon_face_rot_mat;

uniform bool enable_stars;
uniform bool enable_pole_visualizer;
uniform mat4 stars_rot_mat;
uniform float stars_intsty = 1.0;

uniform vec3 pole_dir;

#define MAX_RADIATION 2e31

#define LIGHT_YEAR 9.4607e+15 // One light year in meters.
#define STELLAR_RADIUS 6.957e+8 // Radius of the sun in meters.
#define SIGMA 5.670367e-8 // Stefan-Boltzmann constant.

#define RATIO 3.066257e-22       // (STELLAR_RADIUS^2 * SIGMA) / LIGHT_YEAR^2
/* --------------------------------- Clouds --------------------------------- */

uniform bool enable_cld;
uniform bool enable_cld_0;
uniform bool enable_cld_1;

/*
*   cloud domain height at zenith (m): h
*   cloud domain horizon view distance (m): d
*   cloud domain radius (m): r
*   cloud domain center (m): c
*
*   r = (2d)^2 / (8h) + h/2
*   c = <0, 0, h - r>
*/

uniform vec3 cld_domain_center;

uniform int cld_max_steps;
uniform int cld_max_light_steps;

uniform float cld_G;

//const float cld_top_roundness = 0.05;
//const float cld_btm_roundness = 0.40;

const float cld_top_density = 1.0;
//const float cld_btm_density = 0.45;

uniform bool enable_bicubic;

struct Cloud {
    float   top_roundness;
    float   btm_roundness;

    float   radius;
    float   density;
    float   density_height;
    float   thickness;
    float   shell_thickness;

    vec3    sigma_s;
    vec3    sigma_t;

    float   ap_intsty;
    float   ambient_intsty;

    float   atten;
    float   contr;
    float   eccen;

    float   coverage_shape;
    float   shape_shape;
    float   detail_shape;

    float   shape_inverse;
    float   detail_inverse;

    float   coverage_scale;
    float   shape_scale;
    float   detail_scale;

    int     curl_octaves;

    float   coverage_intsty;
    float   shape_intsty;
    float   detail_intsty;

    vec2    pos_offset;

    vec2    coverage_offset;
    vec2    shape_offset;
    vec2    detail_offset;

    mat4    transform;

    int     max_steps;
    int     max_light_steps;

    int     layer; // 0: Cirrus     1: Cumulus 
};

uniform Cloud cloud_0;
uniform Cloud cloud_1;

uniform float scale_0;
uniform float scale_1;
uniform float scale_2;
uniform float scale_3;

//uniform vec3 sigma_s;
//const vec3 sigma_a = vec3(0.0);
//const vec3 sigma_t = max(sigma_s + sigma_a, vec3(0.000000001));
/* -------------------------------------------------------------------------- */
/*                                 ATMOSPHERE                                 */
/* -------------------------------------------------------------------------- */

vec3 spec_to_rgb(float spec[num_wavelengths])
{
    vec3 xyz = vec3(0.0, 0.0, 0.0);
    for (int i = 0; i < num_wavelengths; i++) {
        xyz.x += cmf_xyz[i].x * spec[i];
        xyz.y += cmf_xyz[i].y * spec[i];
        xyz.z += cmf_xyz[i].z * spec[i];
    }
    vec3 rgb = xyz_to_rgb * (xyz * step_lambda);
    return rgb;
}

float get_height(vec3 p)
{
    float min_altitude = 0.0;
    float max_altitude = atmosphere_radius-earth_radius;
    return clamp((length(p) - atmo_camera_offset + altitude) - earth_radius, min_altitude, max_altitude);
}

/* ----------------------------- Phase Functions ---------------------------- */

float phase_rayleigh(float mu)
{
    return M_3_16PI * (1.0 + (mu*mu));
}

float phase_mie(float mu, float G)
{
    float sqr_G = G*G;
    return (3.0 * (1.0 - sqr_G) * (1.0 + (mu*mu))) / (8.0 * M_PI * (2.0 + sqr_G) * pow((1.0 + sqr_G - 2.0 * G * mu), 1.5));
}

float phase_hg(float mu, float G)
{
    float sqr_G = G*G;
    return M_1_4PI  * ((1.0 - sqr_G) / pow(1.0 + sqr_G - 2.0 * G * mu, 1.5));
}

/* https://www.shadertoy.com/view/4sjBDG */
float phase_mie_numerical(float mu)
{
    // This function was optimized to minimize (delta*delta)/reference in order to capture
    // the low intensity behavior.
    float bestParams[10];
    bestParams[0]=9.805233e-06;
    bestParams[1]=-6.500000e+01;
    bestParams[2]=-5.500000e+01;
    bestParams[3]=8.194068e-01;
    bestParams[4]=1.388198e-01;
    bestParams[5]=-8.370334e+01;
    bestParams[6]=7.810083e+00;
    bestParams[7]=2.054747e-03;
    bestParams[8]=2.600563e-02;
    bestParams[9]=-4.552125e-12;
    
    float p1 = mu + bestParams[3];
    vec4 expValues = exp(vec4(bestParams[1] *mu+bestParams[2], bestParams[5] *p1*p1, bestParams[6] *mu, bestParams[9] *mu));
    vec4 expValWeight= vec4(bestParams[0], bestParams[4], bestParams[7], bestParams[8]);
    return dot(expValues, expValWeight) * 0.25;
}

/* ------------------------ Atmosphere volume models ------------------------ */

float density_rayleigh(float height)
{
  return exp(-height / rayleigh_scale_height);
}

float density_mie(float height)
{
  return exp(-height / mie_scale_height);
}

float density_ozone(float height)
{
  float den = 0.0;
  if (height >= 10000.0 && height < 25000.0) {
    den = 1.0 / 15000.0 * height - 2.0 / 3.0;
  }
  else if (height >= 25000 && height < 40000) {
    den = -(1.0 / 15000.0 * height - 8.0 / 3.0);
  }
  return den;
}

/* ------------------------- Atmosphere Intersection ------------------------ */

bool surface_intersection(Ray ray)
{
    float t0, t1;

    bool hit = sphere_intersect(ray, vec3(0.0), earth_radius, t0, t1);
    bool front = (t0 >= 0 && t1 >= 0);

    return (hit && front);
}

vec3 atmosphere_intersection(Ray ray, bool ignore_earth = false)
{
    
    float t0, t1;
	bool hit_atmosphere = sphere_intersect(ray, vec3(0.0), atmosphere_radius, t0, t1);

    if (!ignore_earth) {
        float s0, s1;
        bool hit_earth = sphere_intersect(ray, vec3(0.0), earth_radius, s0, s1);

        bool earth_front = (s0 > 0 && s1 > 0);

        float t = 0.0;
        if (hit_earth && earth_front) {
            t = s0; 
        } else {
            t = t1;
        }
        return ray.pos + ray.dir * t;
    } else {
        return ray.pos + ray.dir * t1;
    }
}

/* ----------------------------- Atmosphere Main ---------------------------- */

vec3 ray_optical_depth(Ray ray, bool ignore_earth = false)
{
    vec3 ray_end = atmosphere_intersection(ray, ignore_earth);
    float ray_length = distance(ray.pos, ray_end);

    vec3 segment = ray_length * ray.dir;

    vec3 optical_depth = vec3(0.0, 0.0, 0.0);

    for (int i = 0; i < quadrature_steps; i++) {
        vec3 pos = ray.pos + quadrature_nodes[i] * segment;

        float height = get_height(pos);
        vec3 density = vec3(density_rayleigh(height), density_mie(height), density_ozone(height));

        optical_depth += density * quadrature_weights[i];
    }
    return optical_depth * ray_length;
}

vec4 atmo_raymarch(Ray ray, Light light) 
{
    /* this code computes single-inscattering along a ray through the atmosphere */
    vec3 ray_end = atmosphere_intersection(ray);
    float ray_length = distance(ray.pos, ray_end);

    float segment_length = ray_length / 64.0;
    vec3 segment = segment_length * ray.dir;

    vec3 optical_depth = vec3(0.0, 0.0, 0.0);

    /* zero out light accumulation */
    float r_spectrum[num_wavelengths];
    for (int wl = 0; wl < num_wavelengths; wl++) {
        r_spectrum[wl] = 0.0;
    }

    /* phase function for scattering and the density scale factor */
    float mu = dot(ray.dir, light.dir);
    vec3 phase_function = vec3(phase_rayleigh(mu), phase_mie(mu, mie_G), 0.0);
    vec3 density_scale = vec3(rayleigh_density, mie_density, ozone_density);

    /* the density and in-scattering of each segment is evaluated at its middle */
    vec3 pos = ray.pos; float march_dst = 0.0;
    for (int i = 0; i < 64; i++)
    {
        pos = ray.pos + march_dst * ray.dir;

        /* height above sea level */
        float height = get_height(pos);

        /* evaluate and accumulate optical depth along the ray */
        vec3 density = density_scale * vec3(density_rayleigh(height),
                                            density_mie(height),
                                            density_ozone(height));

        optical_depth += segment_length * density;

        /* if the Earth isn't in the way, evaluate inscattering from the sun */
        Ray light_ray = Ray(pos, light.dir);
        if (!surface_intersection(light_ray)) {
            vec3 light_optical_depth = density_scale * ray_optical_depth(light_ray);
            vec3 total_optical_depth = optical_depth + light_optical_depth;
            
            for (int wl = 0; wl < num_wavelengths; wl++) {

                vec3 extinction_density = total_optical_depth * vec3(rayleigh_coeff[wl],
                                                                     mie_coeff,
                                                                     ozone_coeff[wl]);

                float attenuation = exp(-reduce_add(extinction_density));
                vec3 scattering_density = density * vec3(rayleigh_coeff[wl], mie_coeff, 0.0);

                r_spectrum[wl] += attenuation * reduce_add(phase_function * scattering_density) * irradiance[wl] * segment_length;
            }
        }
        march_dst += segment_length;
    }
    return vec4(spec_to_rgb(r_spectrum), 1.0);
}

vec4 atmo_raymarch(Ray ray, Light light, vec3 ray_end) 
{
    /* this code computes single-inscattering along a ray through the atmosphere */
    float ray_length = distance(ray.pos, ray_end);

    float segment_length = ray_length / 64.0;
    vec3 segment = segment_length * ray.dir;

    vec3 optical_depth = vec3(0.0, 0.0, 0.0);

    /* zero out light accumulation */
    float r_spectrum[num_wavelengths];
    for (int wl = 0; wl < num_wavelengths; wl++) {
        r_spectrum[wl] = 0.0;
    }

    /* phase function for scattering and the density scale factor */
    float mu = dot(ray.dir, light.dir);
    vec3 phase_function = vec3(phase_rayleigh(mu), phase_mie(mu, mie_G), 0.0);
    vec3 density_scale = vec3(rayleigh_density, mie_density, ozone_density);

    /* the density and in-scattering of each segment is evaluated at its middle */
    vec3 pos = ray.pos; float march_dst = 0.0;
    for (int i = 0; i < 64; i++)
    {
        pos = ray.pos + march_dst * ray.dir;

        /* height above sea level */
        float height = get_height(pos);

        /* evaluate and accumulate optical depth along the ray */
        vec3 density = density_scale * vec3(density_rayleigh(height),
                                            density_mie(height),
                                            density_ozone(height));

        optical_depth += segment_length * density;

        /* if the Earth isn't in the way, evaluate inscattering from the sun */
        Ray light_ray = Ray(pos, light.dir);
        if (!surface_intersection(light_ray)) {

            vec3 light_optical_depth = density_scale * ray_optical_depth(light_ray);
            vec3 total_optical_depth = optical_depth + light_optical_depth;
            
            for (int wl = 0; wl < num_wavelengths; wl++) {

                vec3 extinction_density = total_optical_depth * vec3(rayleigh_coeff[wl],
                                                                     mie_coeff,
                                                                     ozone_coeff[wl]);

                float attenuation = exp(-reduce_add(extinction_density));
                vec3 scattering_density = density * vec3(rayleigh_coeff[wl], mie_coeff, 0.0);

                r_spectrum[wl] += attenuation * reduce_add(phase_function * scattering_density) * irradiance[wl] * segment_length;
            }
        }
        march_dst += segment_length;
    }
    return vec4(spec_to_rgb(r_spectrum), 1.0);
}

vec3 sun_radiation(Ray ray, float solid_angle, bool ignore_earth = false)
{
    vec3 optical_depth = ray_optical_depth(ray, ignore_earth);

    bool hit_surface = false;
    if (!ignore_earth) {
        hit_surface = surface_intersection(ray);
    }

    if (!hit_surface) {
        float r_spectrum[num_wavelengths];
        for (int wl = 0; wl < num_wavelengths; wl++) {
            r_spectrum[wl] = 0.0;
        }

        /* compute final spectrum */
        for (int i = 0; i < num_wavelengths; i++) {
            /* combine spectra and the optical depth into transmittance */
            float transmittance = rayleigh_coeff[i] * optical_depth.x * rayleigh_density +
                                    1.11f * mie_coeff * optical_depth.y * mie_density;
            r_spectrum[i] = irradiance[i] * exp(-transmittance) / solid_angle;
        }

        return spec_to_rgb(r_spectrum);
    } else {
        return vec3(0.0);
    }
}
/* ---------------------------- Celestial Objects --------------------------- */

const float moon_dist = 500.0;

bool hit_moon(vec3 dir)
{
    Ray ray = Ray(vec3(0.0), dir);

    vec3 moon_pos = moon.dir * moon_dist;

    float moon_solid_angle = M_2PI * (1.0 - cos(moon_half_angular * 1.05));
    float moon_radius = sqrt(moon_solid_angle * moon_dist*moon_dist * M_1_PI);

    //float moon_radius = (moon_half_angular * 1.05) * moon_dist;

    float t0, t1;
    return sphere_intersect(ray, moon_pos, moon_radius, t0, t1);
}

vec4 draw_moon(Ray ray) 
{
    vec3 color = vec3(0.0);
    float opacity = 0.0;

    if (surface_intersection(ray)) return vec4(color, opacity);

    Ray moon_ray = Ray(vec3(0.0), ray.dir);

    vec3 moon_pos = moon.dir * moon_dist;

    float moon_solid_angle = M_2PI * (1.0 - cos(moon_half_angular));
    float moon_radius = sqrt(moon_solid_angle * moon_dist*moon_dist * M_1_PI);

    float t0, t1;
    if (sphere_intersect(moon_ray, moon_pos, moon_radius, t0, t1)) 
    {
        vec3 sphere_pos = moon_ray.pos + moon_ray.dir * t0;
        vec3 sphere_norm = normalize(sphere_pos-moon_pos);

        vec3 sp = normalize(vec3(moon_rot_mat * vec4(sphere_norm, 0.0)));
        vec2 uv = sample_spherical_map(sp);

        vec3 norm = texture(moon_normal_tex, uv).rgb;
        norm = (norm * 2.0 - 1.0);

        vec3 T = normalize(tangent(sp));
        vec3 B = normalize(cross(sp, T));

        mat3 TBN = mat3(T,B,sp);
        norm = TBN*norm;

        vec3 L = min(sun_radiation(ray, moon_solid_angle) * 0.000025 * moon.intsty, MAX_RADIATION);

        vec3 trans_moon_phase_dir = normalize(vec3(moon_rot_mat * vec4(moon_phase_dir, 0.0)));

        float diff = max(dot(trans_moon_phase_dir, norm), 0.0);
        color = (L * (diff + moon_ambient_intsty) * texture(moon_albedo_tex, uv).rgb);
        opacity = 1.0;
    }

    return vec4(color, opacity);
}

vec4 draw_sun(Ray ray) 
{
  vec3 color = vec3(0.0);
  float opacity = 0.0;

  if (surface_intersection(ray)) return vec4(color, opacity);

  float min_cos_theta = cos(sun_half_angular);

  float cos_theta = dot(ray.dir, sun.dir);
  if (cos_theta >= min_cos_theta) {
    color = vec3(1.0);
    opacity = 1.0;
  } else {
    float offset = min_cos_theta - cos_theta;
    float scale_factor = 3000.0 / (sun_half_angular*2.0);
    float gaussian_bloom = exp(-offset*scale_factor);
    color = vec3(gaussian_bloom);
    opacity = gaussian_bloom;
  }

  if (length(color) > 0.00001) {
    float sun_solid_angle = M_2PI * (1.0 - cos(sun_half_angular));
    vec3 L = min(sun_radiation(ray, sun_solid_angle) * sun.intsty, MAX_RADIATION);
    color.rgb *= L;
  }

  return vec4(color, opacity);
}

vec3 star_color(float temp) {
  float pt = pow(temp,-1.5)*1e5,
        lt = log(temp);
  return clamp(vec3(
    561. * pt + 148.,
    temp > 6500. ? 352. * pt + 184. : 100.04 * lt - 623.6,
    194.18 * lt - 1448.6)/255., 0., 1.);
}

vec4 draw_stars(Ray ray) 
{
  vec3 L = vec3(0.0);
  float opacity = 0.0;

  if (surface_intersection(ray)) return vec4(L, opacity);

  vec3 rd = normalize(vec3(stars_rot_mat * vec4(ray.dir, 0.0)));

  /* ------------------------------- Blue Stars ------------------------------- */
  {
    vec4 n = worley(rd*150.);
    
    float t = mix(8000.0, 10000.0, n.y); // Absolute Temperature (K)
    float d = mix(1.0, 50., n.z);        // Light Years (m)
    float r = mix(1.0, 50.0, n.w);      // Stellar Radius (m)

    // radiant_flux = 4pi * sigma * t^4 * r^2 (W)
    // radiant_intensity = radiant_flux / (4pi * d^2) (W * sr^-1)

    float I = (t*t*t*t) * (r*r) * RATIO / (d*d);
    L += vec3(exp(-n.x * mix(20., 40., n.y))) * star_color(t) * I;
    opacity = exp(-n.x * mix(20., 40., n.y));
  }

  /* -------------------------------- Red Stars ------------------------------- */
  {
    vec4 n = worley(rd*150.);
    
    float t = mix(2000.0, 6000.0, n.y);
    float d = mix(1.0, 10., n.z);
    float r = mix(1000.0, 1800.0, n.w);

    float I = (t*t*t*t) * (r*r) * RATIO / (d*d);
    L += vec3(exp(-n.x * mix(20., 35., n.y))) * star_color(t) * I;
    opacity = exp(-n.x * mix(20., 40., n.y));
  }

  if (ray.dir.z < 0.0) {
      opacity = 0.0;
  }

  return vec4(L * stars_intsty, opacity);
}

vec4 draw_pole_visualizer(Ray ray)
{
  vec4 color = vec4(0.0);
  float min_cos_theta = cos(0.00872665);

  float cos_theta_0 = dot(ray.dir, pole_dir);
  float cos_theta_1 = dot(ray.dir, -pole_dir);
  if (cos_theta_0 >= min_cos_theta || cos_theta_1 >= min_cos_theta) {
      color = vec4(1.0,0.0,0.0,1.0);
  }

  return color;
}
/* -------------------------------------------------------------------------- */
/*                                   CLOUDS                                   */
/* -------------------------------------------------------------------------- */

float sample_curl_tex(vec2 p)
{
   return texture(noise_tex_2D_2048, p).b;
   //return perlinfbm(vec3(p,0.), 2.0, 3);
}

vec2 curl(vec2 pos)
{ 
    pos *= 1.0;
    vec2 e = vec2(0.15, 0);
    
    float p = sample_curl_tex(pos);
    
    float dx = (sample_curl_tex(pos + e.xy) - p) / (e.x);
    float dy = (sample_curl_tex(pos + e.yx) - p) / (e.x);
       
   	return vec2(-dy, dx);
}

vec2 curl_noise(vec2 pos, int octaves)
{
    vec2 dir = vec2(0.70710678118); // norm(vec2(1.))
	for (int i = 0; i < octaves; i++)
	{
		vec2 new_pos = curl(pos) * .00625;
		pos += new_pos;
        dir += new_pos;
	}
    return dir;
}

float sample_blue_noise()
{
    vec2 uv = gl_FragCoord.xy / img_size.xy;
    return 2.0 * texture(blue_noise, uv*128.0).r - 1.0;
}

void shell_intersection(Ray ray, vec3 center, float radius_inner, float radius_outer, out float t_start, out float t_end) 
{
    t_start = 0.0;
    t_end = 0.0;

    float t0, t1;
    bool hit_outer = sphere_intersect(ray, center, radius_outer, t0, t1);

    float s0, s1;
    bool hit_inner = sphere_intersect(ray, center, radius_inner, s0, s1);

    t_start = (hit_inner) ? s1 : 0.0;
    t_end = (hit_outer) ? t1 : 0.0;
}

bool cld_sample( 
    Cloud cloud,
    vec3 pos,
    out float ds, 
    out float dist, 
    out float h_p) 
{
    float inner_shell = sdf_sphere(pos, cloud.radius);
    float outer_shell = sdf_sphere(pos, cloud.radius + cloud.shell_thickness);
    float cld_shell = sdf_op_sub(inner_shell, outer_shell);

    ds = 0.0;
    dist = 0.0;
    h_p = 0.0;

    bool hit = false;

    if (cld_shell < 0.0) 
    {
        h_p = saturate(clamp(length(pos) - cloud.radius, 0.0, cloud.shell_thickness) / (cloud.shell_thickness));

        /* -------------------------- Sample Noise Textures ------------------------- */
        float curl_scale = 0.75; // Just a "magic number" that looks good.
        vec3 pos_curl = pos + vec3(curl_noise((pos.xy + cloud.pos_offset) * cloud.coverage_scale * curl_scale, cloud.curl_octaves),0.) * 100000.0;

        vec2 c_sp = (pos_curl.xy + cloud.pos_offset + cloud.coverage_offset) * cloud.coverage_scale;
        vec4 cns = texture(noise_tex_2D_2048, c_sp);

        vec3 s_sp = (pos_curl + vec3(cloud.pos_offset + cloud.coverage_offset + cloud.shape_offset, 0.0)) * cloud.shape_scale;
        vec4 sns = texture(noise_tex_3D_128, s_sp);
        
        vec3 d_sp = (pos + vec3(cloud.pos_offset + cloud.coverage_offset + cloud.detail_offset, 0.0)) * cloud.detail_scale;
        vec4 dns = texture(noise_tex_3D_64, d_sp);

        /* -------------------------------------------------------------------------- */

        float coverage_area = texture(noise_tex_2D_2048, (pos_curl.xy + cloud.pos_offset) * scale_3).y * cloud.coverage_intsty;
        //float coverage_area = texture(noise_tex_2D_2048, (pos.xy + cloud.coverage_offset) * 0.000001).y * cloud.coverage_intsty;
        float CN = mix(cns.x, cns.y, cloud.coverage_shape);
        float wh = CN * cloud.thickness;

        /* ------------------------- Shape-Height Functions ------------------------- */

        float SR_t = saturate(1.0 - pow(h_p, (wh - h_p) / (wh - wh*cloud.top_roundness)));
        float SR_b = saturate(1.0 - (pow(1.0 - h_p, 1.0 / cloud.btm_roundness)));
        float SA = SR_t * SR_b;

        /* ------------------------ Density-Height Functions ------------------------ */

        float DR_t = 1.0;
        float DR_b = saturate(pow(h_p, 1.0 / (1.0 - cloud.density_height)));
        float DA = DR_t * DR_b;

        /* -------------------------------------------------------------------------- */

        float cld_coverage = remap(CN * coverage_area * SA * 1.33, 0.0, 1.0, -1.0, 1.0);
        float _cld_shell = sdf_op_sub(cld_coverage, cld_shell);

        if (_cld_shell < 0.0) 
        {
            float tst_0 = 1.0;  float tst_1 = 1.0;
            float SN    = 1.0;  float DN    = 1.0;

            if (cloud.layer == 0) 
            {
                float c = clamp(1.66667*cloud.shape_intsty, 0.0, 1.0);
                float d = clamp(1.66667*cloud.detail_intsty, 0.0, 1.0);

                tst_0 = mix(1.0, mix(.8, .7, cloud.shape_inverse), c);

                float a = mix(0.9, 0.6, cloud.detail_shape);
                float b = mix(0.7, 0.75, cloud.detail_shape);
                tst_1 = mix(1.0, mix(a, b, cloud.detail_inverse), d);

                SN = mix(mix(1.0-sns.r, sns.r, cloud.shape_inverse), mix(1.0-sns.g, sns.g, cloud.shape_inverse), cloud.shape_shape);
                DN = mix(mix(1.0-dns.r, dns.r, cloud.detail_inverse), mix(1.0-dns.a, dns.a, cloud.detail_inverse), cloud.detail_shape);
            } 
            else if (cloud.layer == 1) 
            {
                float h1 = 7.0;
                float h2 = 4.0;
                
                tst_0 = mix(1.0, mix(.35, .35, saturate(h_p * h1)), cloud.shape_intsty);
                tst_1 = mix(1.0, mix(0.4, 0.12, saturate(h_p * h2)), cloud.detail_intsty);

                float SN_t = sns.r;
                float SN_b = 1.0 - sns.g;
                SN = mix(SN_b, SN_t, saturate(h_p * h1));

                float DN_t = dns.r;
                float DN_b = 1.0 - dns.a;
                DN = mix(DN_b, DN_t, saturate(h_p * h2));
            }

            float cld_shape = SN * -abs(cloud.shape_intsty) * tst_1;
            float cld_detail = DN * -abs(cloud.detail_intsty);

            cld_coverage = remap(CN * coverage_area * SA * tst_0 * tst_1, 0.0, 1.0, -1.0, 1.0);
            cld_shell = sdf_op_sub(cld_coverage, cld_shell);
            cld_shell = clamp((cld_detail + cld_shape), -1.0, 1.0) + cld_shell;
        } 
        else 
        {
            cld_coverage = remap(CN * coverage_area * SA, 0.0, 1.0, -1.0, 1.0);
            cld_shell = sdf_op_sub(cld_coverage, cld_shell);
        }

        if (cld_shell < 0.f) 
        {
            ds = cloud.density * min(abs(cld_shell), 1.0) * DA;
            dist = cld_shell;
            hit = true;
        } 
        else 
        {
            ds = 0.0;
            dist = cld_shell;
            hit = false;
        }
    }
    return hit;
}

bool cloud_density(
    Cloud cloud,
    vec3 pos, 
    out float ds, 
    out float dist, 
    out float h_p) 
{
    dist = 0.0;
    h_p = 0.0;
    ds = 0.0;

    vec3 t_pos = vec3(cloud.transform * vec4(pos, 1.0));
    bool hit = cld_sample(cloud, t_pos, ds, dist, h_p);

    ds = max(ds, 0.000000001);

    return hit;
}

float ray_optical_depth(Cloud cloud, Ray ray)
{
    float t_start, t_end;
    shell_intersection(
        ray, 
        cld_domain_center + vec3(0, 0, earth_radius), 
        cloud.radius, 
        cloud.radius + cloud.shell_thickness, 
        t_start, 
        t_end);

    float optical_depth = 0.0;

    vec3 start_pos = ray.pos;
    vec3 end_pos = (ray.pos + ray.dir * t_end);
    float ray_length = distance(start_pos, end_pos);

    ray_length = min(ray_length, 5000.0);

    float segment_length = ray_length / cloud.max_light_steps;
    float segment = segment_length;

    float noise_offset = sample_blue_noise();
    noise_offset *= segment;

    float march_dst = noise_offset;
    for (int i = 0; i < cloud.max_light_steps; i++)
    {
        vec3 pos = start_pos + ray.dir * march_dst;

        float ds, dist, h_p;
        bool in_cloud = cloud_density(cloud, pos, ds, dist, h_p);
        if (in_cloud) {
            optical_depth += ds * segment;
        }

        segment = in_cloud ? segment_length : max(dist, segment_length);
        march_dst += segment;
    }
    return optical_depth;
}

vec3 ambient_light_sample(Cloud cloud, float h_p, Ray ray) 
{

    float remap_hp = saturate(remap(h_p, cloud.btm_roundness, 1.0, 0.0, 1.0));

    vec3 top_color = texture(irra_tex, sample_spherical_map2(ray.dir)).rgb;
    vec3 bottom_color = texture(irra_tex, clamp(vec2(0.5, remap_hp), vec2(0.01), vec2(0.1))).rgb;

    float t = 1.0 - (pow(1.0 - remap_hp, 5.0));
    vec3 ambient_color = mix(bottom_color, top_color, t) * cloud.ambient_intsty;

    return ambient_color;
}

/* Multiple scattering approximation: */
/* Oz: the great and volumetric       */
/* DOI: 10.1145/2504459.2504518       */
vec3 multi_scatter(Cloud cloud, Light light, float optical_depth, float mu)
{
    float _ai = 1.0; /* attenuation */
    float _bi = 1.0; /* contribution */
    float _ci = 1.0; /* eccentricity attenuation */

    vec3 L = vec3(0.0);
    for (int i = 0; i < 8; i++) 
    {
        float _phase = mix(phase_hg(mu, -0.1 * _ci), phase_hg(mu, 0.8 * _ci), 0.5);
        L += _bi * _phase * exp(-_ai * optical_depth * cloud.sigma_t);

        _ai *= cloud.atten;
        _bi *= cloud.contr;
        _ci *= cloud.eccen;
    }
    return L;
}

vec3 direct_light_sample(Cloud cloud, Ray ray, Light light)
{
    Ray light_ray;
    light_ray.pos = ray.pos;
    light_ray.dir = light.dir;

    vec3 L_light = sun_radiation(light_ray, 0.1, true);

    if (length(L_light) > 1e-3) {
        float mu = dot(light.dir, ray.dir);
        float phase = mix(phase_hg(mu, -0.1), phase_hg(mu, 0.8), 0.5);

        float optical_depth = ray_optical_depth(cloud, light_ray);
        vec3 L_scatter = multi_scatter(cloud, light, optical_depth, mu);

        vec3 powder = 2.0 * (1.0 - (exp(-optical_depth * 2.0 * cloud.sigma_t)));
        return mix(L_scatter, L_scatter * powder, 0.5 + 0.5 * mu) * L_light * phase;
    } else {
        return vec3(0.0);
    }

}

vec4 cloud_raymarch(Cloud cloud, Ray ray, out float depth) 
{
    depth = 0.0;
    
    float opacity = 0.0;
    float tt = 1.0;
    vec3 transmittance = vec3(1.0);
    vec3 scattered_light = vec3(0.0, 0.0, 0.0);

    if (surface_intersection(ray)) return vec4(scattered_light, opacity);

    float t_start, t_end;
    shell_intersection(
        ray, 
        cld_domain_center + vec3(0, 0, earth_radius), 
        cloud.radius, 
        cloud.radius + cloud.shell_thickness, 
        t_start, 
        t_end);

    vec3 start_pos = (ray.pos + ray.dir * t_start);
    vec3 end_pos = (ray.pos + ray.dir * t_end);
    float ray_length = distance(start_pos, end_pos);

    depth = distance(ray.pos, start_pos);

    float segment_length = ray_length / float(cloud.max_steps);
    float segment = segment_length;

    float noise_offset = sample_blue_noise();
    noise_offset *= segment;

    float march_dst = noise_offset;
    for (int i = 0; i < cloud.max_steps; i++) {
        ray.pos = start_pos + march_dst * ray.dir;

        float ds, dist, h_p;
        bool in_cloud = cloud_density(cloud, ray.pos, ds, dist, h_p);

        vec3 s_sigma_s = cloud.sigma_s * ds;
        vec3 s_sigma_t = cloud.sigma_t * ds;

        if (in_cloud) 
        {
            vec3 direct_light = vec3(0.0);
            direct_light += (enable_sun && enable_sun_as_light) ? direct_light_sample(cloud, ray, sun) : vec3(0.0);
            direct_light += (enable_moon && enable_moon_as_light) ? direct_light_sample(cloud, ray, moon) * 0.000025 : vec3(0.0);
            vec3 ambient_light = ambient_light_sample(cloud, h_p, ray);

            vec3 Li = (direct_light + ambient_light) * s_sigma_s;
            scattered_light += transmittance * (Li - Li * exp(-s_sigma_t * segment)) / s_sigma_t;
            transmittance *= exp(-s_sigma_t * segment);
            tt *= exp(-segment * ds);
        }

        if (tt < 0.0001) {
            tt = 0.0;
            break;
        }

        segment = in_cloud ? segment_length : max(dist, segment_length);
        march_dst += segment;
    }

    opacity = 1.0 - tt;

    return vec4(scattered_light, opacity);
}

out vec4 fragColor;

uniform mat4 inv_vp_mat;

vec4 compute_cld(Cloud cloud, Ray ray)
{
    float   cld_depth     = 0.0;
    vec4    cld_color     = vec4(0.0);
    cld_color = cloud_raymarch(cloud, ray, cld_depth);

    vec3 cld_point = ray.pos + ray.dir * cld_depth;

    vec4 cld_ap = vec4(0.0);
    cld_ap += (enable_atm && enable_sun && enable_sun_as_light) ? atmo_raymarch(ray, sun, cld_point) : vec4(0.0);
    cld_ap += (enable_atm && enable_moon && enable_moon_as_light) ? atmo_raymarch(ray, moon, cld_point) * 0.000025 : vec4(0.0); 

    float ap_clouds = exp(-cld_depth / cloud.ap_intsty);
    cld_color.rgb = _mix(cld_ap.rgb * cld_color.a, cld_color.rgb, ap_clouds);

    return cld_color;
}

void main()
{       
    if (gl_FragCoord.x > img_size.x || gl_FragCoord.y > img_size.y) return;

    /* ------------------------------- Set up ray ------------------------------- */

    vec2 p_NDC; // [-1, 1] x [-1, 1]
    p_NDC = 2.0 * ((gl_FragCoord.xy + 0.5) / img_size.xy) - 1.0;

    vec4 p_near_NDC = inv_vp_mat * vec4(p_NDC.x, p_NDC.y, -1.0, 1.0);
    vec4 p_far_NDC = inv_vp_mat * vec4(p_NDC.x, p_NDC.y, 1.0, 1.0);

    vec3 p_near = vec3(p_near_NDC.xyz) / p_near_NDC.w;
    vec3 p_far = vec3(p_far_NDC.xyz) / p_far_NDC.w;

    Ray ray;
    ray.pos = vec3(0.0, 0.0, earth_radius + atmo_camera_offset);
    ray.dir = normalize(p_far - p_near);

    /* ---------------------------- Render Atmosphere --------------------------- */

    vec4 atmo_color = vec4(0.0);
    atmo_color += (enable_atm && enable_sun && enable_sun_as_light) ? atmo_raymarch(ray, sun) : vec4(0.0);
    atmo_color += (enable_atm && enable_moon && enable_moon_as_light) ? atmo_raymarch(ray, moon) * 0.000025 : vec4(0.0);

    vec4 stars_color = (enable_stars) ? draw_stars(ray) : vec4(0.0);

    precise vec4 sun_color = (enable_sun) ? draw_sun(ray) : vec4(0.0);

    sun_color = _mix(stars_color, sun_color, sun_color.a);

    vec4 pole_visualizer = vec4(0.0);
    pole_visualizer = (enable_pole_visualizer) ? draw_pole_visualizer(ray) : vec4(0.0);

    vec4 moon_color = (enable_moon) ? draw_moon(ray) : vec4(0.0);

    precise vec4 moon_sun_color = _mix(sun_color, moon_color, moon_color.a);

    /* ------------------------------ Render Clouds ----------------------------- */

    precise vec4 sky_color = vec4(0.0);
    
    if (enable_cld) {

        vec4 cld_0_color = vec4(0.0);
        vec4 cld_1_color = vec4(0.0);

        if (enable_cld_0) cld_0_color = compute_cld(cloud_0, ray);
        if (enable_cld_1) cld_1_color = compute_cld(cloud_1, ray);

        atmo_color += moon_sun_color;

        sky_color = atmo_color*(1.0 - cld_0_color.a) + cld_0_color;
        sky_color = sky_color*(1.0 - cld_1_color.a) + cld_1_color;

    } else {
        sky_color = atmo_color + moon_sun_color;
    }

    /* --------------------------------- Send it -------------------------------- */
    precise vec4 tst = _mix(sky_color, pole_visualizer, pole_visualizer.a);

    fragColor = sky_color + tst;
}


