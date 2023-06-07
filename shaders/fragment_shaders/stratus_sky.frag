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
const float mie_coeff = 21e-5;

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

out vec4 fragColor;

void main() {
    vec2 uv = gl_FragCoord.xy / img_size.xy;

    Ray ray;
    ray.pos = vec3(0.0, 0.0, earth_radius + atmo_camera_offset);
    ray.dir = sample_spherical_direction(uv);
 
    vec4 atmo_color = vec4(0.0);
    atmo_color += (enable_sun && enable_sun_as_light) ? atmo_raymarch(ray, sun) : vec4(0.0);
    atmo_color += (enable_moon && enable_moon_as_light) ? atmo_raymarch(ray, moon) * 0.000025 : vec4(0.0); 

    fragColor = atmo_color;
}